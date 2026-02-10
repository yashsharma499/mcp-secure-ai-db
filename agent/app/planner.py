import json
import re
from typing import Any, Dict

from openai import AsyncOpenAI

from app.config import get_settings
from app.schemas import Plan, MemoryState


class PlanningError(Exception):
    pass


class QueryPlanner:
    def __init__(self):
        self._settings = get_settings()
        self._client = AsyncOpenAI(api_key=self._settings.openai_api_key)

        self._allowed_tools = {
            "validate_query",
            "dry_run_query",
            "run_read_query",
            "run_write_query",
            "explain_query",
            "estimate_query_cost",
        }

        self._allowed_intents = {"chat", "vague", "forbidden", "db"}

    async def build_plan(
        self,
        *,
        user_message: str,
        memory: MemoryState,
        schema: Dict[str, Any],
        permissions: Any,
    ) -> Plan:

        if memory is None:
            memory = MemoryState(
                last_intent=None,
                last_tables=[],
                last_filters=None,
                last_summary=None,
            )

        prompt = self._build_prompt(
            user_message=user_message,
            memory=memory,
            schema=schema,
            permissions=permissions,
        )

        try:
            response = await self._client.chat.completions.create(
                model=self._settings.openai_model,
                messages=[
                    {"role": "system", "content": self._system_prompt()},
                    {"role": "user", "content": prompt},
                ],
                temperature=0,
            )

            content = response.choices[0].message.content
            if not content:
                raise PlanningError("Empty planner response")

            data = self._extract_json(content)
            plan = Plan.model_validate(data)

            for a in plan.actions:
                if a.sql:
                    a.sql = self._normalize_table_names(a.sql, schema)

            for a in plan.actions:
                if a.tool == "run_read_query":
                    a.sql = self._enforce_projection(a.sql, permissions)

            self._validate_plan(plan, user_message)

            return plan

        except PlanningError:
            raise
        except Exception as e:
            raise PlanningError("Failed to build execution plan") from e

    def _normalize_table_names(self, sql: str, schema: Dict[str, Any]) -> str:
        tables = set(schema.keys())

        def repl(match):
            name = match.group(1)
            lname = name.lower()
            if lname not in tables and lname + "s" in tables:
                return match.group(0).replace(name, lname + "s")
            return match.group(0)

        sql = re.sub(r"\bfrom\s+([a-zA-Z_][a-zA-Z0-9_]*)", repl, sql, flags=re.IGNORECASE)
        sql = re.sub(r"\bupdate\s+([a-zA-Z_][a-zA-Z0-9_]*)", repl, sql, flags=re.IGNORECASE)
        sql = re.sub(r"\binto\s+([a-zA-Z_][a-zA-Z0-9_]*)", repl, sql, flags=re.IGNORECASE)

        return sql

    def _get_allowed_columns_for_table(self, permissions, table: str):
        if not isinstance(permissions, list):
            return None

        for p in permissions:
            if p.get("table_name") == table:
                return p.get("allowed_columns")

        return None

    def _enforce_projection(self, sql: str, permissions) -> str:
        m = re.match(
            r"^\s*select\s+\*\s+from\s+([a-zA-Z_][a-zA-Z0-9_]*)\b(.*)$",
            sql,
            flags=re.IGNORECASE | re.DOTALL,
        )

        if not m:
            return sql

        table = m.group(1)
        rest = m.group(2)

        allowed = self._get_allowed_columns_for_table(permissions, table)

        if allowed is None:
            return sql

        if not allowed:
            raise PlanningError("No readable columns for this table")

        cols = ", ".join(allowed)

        return f"SELECT {cols} FROM {table}{rest}"

    def _validate_plan(self, plan: Plan, user_message: str) -> None:

        if plan.intent not in self._allowed_intents:
            raise PlanningError("Invalid intent returned by planner")

        if plan.intent != "db":
            if plan.actions:
                raise PlanningError("Non-db intent must not contain actions")
            return

        if not plan.actions:
            raise PlanningError("DB intent requires at least one action")

        if len(plan.actions) > 1:
            tools = [a.tool for a in plan.actions]
            if tools != ["validate_query", "dry_run_query", "run_write_query"]:
                raise PlanningError("Invalid tool sequence")

        for a in plan.actions:
            if a.tool not in self._allowed_tools:
                raise PlanningError(f"Unsupported tool in plan: {a.tool}")

            if not a.sql or not a.sql.strip():
                raise PlanningError("Planner produced empty SQL")

            upper = a.sql.strip().upper()

            if upper.startswith(("DROP", "TRUNCATE", "ALTER")):
                raise PlanningError("Destructive SQL detected")

            if a.tool == "run_read_query":
                if not self._is_aggregation_query(upper):
                    if "LIMIT" not in upper:
                        raise PlanningError("Read query must contain LIMIT")

    def _is_aggregation_query(self, upper_sql: str) -> bool:
        return any(fn in upper_sql for fn in ("COUNT(", "SUM(", "AVG(", "MIN(", "MAX("))

    def _system_prompt(self) -> str:
        return (
            "You are a production-grade query planning agent for a secure MCP governed "
            "database platform.\n"
            "You DO NOT execute queries.\n"
            "You ONLY generate a JSON plan that will be executed by MCP tools.\n\n"
            "Your most important responsibility is:\n"
            "- correctly extracting filters, joins and aggregations from natural language\n"
            "- never ignoring user constraints\n"
            "- never widening the result set beyond what the user asked\n\n"
            "If the user request mentions any condition (city, email, id, status, name, "
            "date, range, latest, count, etc.), you MUST translate it into SQL.\n\n"
            "If a filter can be inferred, it is an ERROR to omit it.\n"
        )

    def _build_prompt(
        self,
        *,
        user_message: str,
        memory: MemoryState,
        schema: Dict[str, Any],
        permissions: Any,
    ) -> str:

        return f"""
You will receive a natural language user request.

Your task:
1. Identify intent
2. Identify tables
3. Identify requested columns
4. Identify all filters and constraints
5. Produce a permission-safe SQL plan

User message:
{user_message}

Conversation memory:
{json.dumps(memory.model_dump(), indent=2)}

Database schema:
{json.dumps(schema, indent=2)}

User permissions:
{json.dumps(permissions, indent=2)}

You must return ONLY a JSON object of the form:

{{
  "intent": "chat | vague | forbidden | db",
  "actions": [
    {{
      "tool": "validate_query | dry_run_query | run_read_query | run_write_query | explain_query | estimate_query_cost",
      "sql": "single SQL statement only",
      "reason": "short reason"
    }}
  ]
}}

------------------------------------
INTERPRETATION & PLANNING RULES
------------------------------------

TABLE DETECTION
- You must map natural language table names to schema tables.
- Singular/plural and partial names must be resolved.
- Phrases like "all candidates", "all records", "all rows" must be treated
  as a normal read request on the identified table.

FILTER EXTRACTION (STRICT)
- If the user uses:
  in, from, located in, with, having, whose, where
  → you MUST create a WHERE clause.

Examples:
"show candidates in Delhi"
→ WHERE city = 'Delhi'

"candidates from Noida"
→ WHERE city = 'Noida'

"candidate with email test@example.com"
→ WHERE email = 'test@example.com'

If a value clearly belongs to a column (email, city, status, name, id, phone),
you MUST map it.

SPECIAL RULE FOR PERSON NAME:
- If the user mentions a person name and the name contains ONLY ONE WORD,
  you MUST treat it as a partial match and use LIKE on the name column.

Example:
"name is rahul"
→ WHERE LOWER(full_name) LIKE LOWER('%rahul%')

- Use exact equality for name ONLY when the user provides a full multi-word name.

Example:
"name is rahul sharma"
→ WHERE full_name = 'Rahul Sharma'

It is NOT allowed to drop filters.

If the user uses the phrase "similar to <value>" and does NOT clearly mention a specific column,
you MUST apply the similarity filter to ALL text-like columns (string / varchar) that are allowed
by permissions, using OR conditions.

When the phrase "similar to" is present, ONLY the text that appears AFTER the words
"similar to" must be used as the search value.

All words that appear BEFORE "similar to" must be ignored for filtering purposes.

Do NOT try to infer a column from words like "name", "email", "city" appearing in the sentence.


COLUMN SELECTION
- If the user explicitly names columns → select only those columns.
- Otherwise → select ONLY columns allowed by permissions.

AGGREGATIONS
- count / total → COUNT
- average → AVG
- min / max → MIN / MAX

ORDERING
- latest / newest / recent → ORDER BY <datetime or id> DESC LIMIT
- oldest / earliest → ORDER BY ASC LIMIT

JOINS
- Only if more than one table is clearly referenced.
- Only use FK-like columns present in schema (candidate_id, interviewer_id, etc.).

WRITE INTENT
- create, add, insert, update, change, set, mark, delete, cancel, reschedule
→ write request.

SMALL TALK
- greetings, help, thanks → intent chat.

If no table can be identified → intent vague.

------------------------------------
PERMISSION RULES (STRICT)
------------------------------------

- You may only access tables listed in permissions.
- You may only use columns listed in allowed_columns.
- If allowed_columns is null → all columns allowed.
- If any requested column is not allowed → forbidden.
- If table is not present in permission list → forbidden.
- If write is requested and can_write is false → forbidden.

------------------------------------
SQL RULES
------------------------------------

- Exactly one SQL statement per action.
- Must use table and column names exactly from schema.
- Never invent tables or columns.
- Never use SELECT *.
- When no WHERE clause exists, still apply LIMIT 50.
- For filtered queries, also apply LIMIT 50.
- Never generate DROP, TRUNCATE, ALTER.

- For any string column comparison in WHERE clauses
  (for example: full_name, email, city, phone, etc),
  you MUST use case-insensitive matching using LOWER() on both sides.

Examples:
WHERE LOWER(full_name) = LOWER('raj')
WHERE LOWER(city) LIKE LOWER('%noi%')
WHERE LOWER(email) LIKE LOWER('%test%')

------------------------------------
TOOL RULES
------------------------------------

READ:
- exactly one action:
  run_read_query

WRITE:
- exactly this sequence:
  validate_query
  dry_run_query
  run_write_query

------------------------------------
INTENT RULES
------------------------------------


- If a valid DB operation exists:
  {{ "intent": "db", "actions": [...] }}

- If permission violation:
  {{ "intent": "forbidden", "actions": [] }}

- If no safe plan possible:
  {{ "intent": "vague", "actions": [] }}

------------------------------------
IMPORTANT
------------------------------------

If the user request contains a filter but you do not generate a WHERE clause,
your answer is INVALID.

Return ONLY JSON.
Do not include markdown.
""".strip()

    def _extract_json(self, text: str) -> Dict[str, Any]:
        try:
            start = text.find("{")
            end = text.rfind("}")
            if start == -1 or end == -1:
                raise PlanningError("Planner did not return JSON")

            raw = text[start:end + 1]
            return json.loads(raw)
        except Exception as e:
            raise PlanningError("Invalid JSON from planner") from e


query_planner = QueryPlanner()
