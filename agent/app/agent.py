from typing import Any, Dict, List

from app.mcp_client import mcp_client, MCPClientError
from app.memory import memory_store
from app.schemas import ChatResponse, MemoryState
from app.planner import query_planner, PlanningError


class AgentError(Exception):
    pass


class OrchestratingAgent:
    async def handle_message(
        self,
        *,
        conversation_key: str,
        user_message: str,
        jwt_token: str
    ) -> ChatResponse:
        try:
            memory = memory_store.get(conversation_key)

            if memory is None:
                memory = MemoryState(
                    last_intent=None,
                    last_tables=[],
                    last_filters={},
                    last_summary=None,
                )

            schema = await mcp_client.call_tool(
                tool_name="get_schema",
                jwt_token=jwt_token,
                arguments={}
            )

            perm_resp = await mcp_client.call_tool(
                tool_name="get_user_permissions",
                jwt_token=jwt_token,
                arguments={}
            )

            if isinstance(perm_resp, dict):
                permissions = perm_resp.get("permissions", [])
            else:
                permissions = perm_resp

            plan = await query_planner.build_plan(
                user_message=user_message,
                memory=memory,
                schema=schema,
                permissions=permissions
            )

            if plan.intent == "chat":
                return ChatResponse(
                    text="Hello! How can I help you with your data today?",
                    data=None
                )

            if plan.intent == "vague":
                return ChatResponse(
                    text="I could not clearly understand your request. Please rephrase it with more details.",
                    data=None
                )

            if plan.intent == "forbidden":
                memory_store.set(
                    conversation_key,
                    MemoryState(
                        last_intent="forbidden",
                        last_tables=memory.last_tables,
                        last_filters=memory.last_filters,
                        last_summary=memory.last_summary,
                    )
                )
                return ChatResponse(
                    text="You do not have permission to perform this operation on the requested data.",
                    data=None
                )

            final_data: List[Dict[str, Any]] | None = None
            last_sql: str | None = None
            last_tool: str | None = None

            for action in plan.actions:
                tool = action.tool
                sql = action.sql
                print("PLANNER SQL:", sql)

                if not sql:
                    raise AgentError("Planner produced action without SQL")

                if tool in {
                    "validate_query",
                    "dry_run_query",
                    "run_read_query",
                    "run_write_query",
                    "explain_query",
                    "estimate_query_cost"
                }:
                    result = await mcp_client.call_tool(
                        tool_name=tool,
                        jwt_token=jwt_token,
                        arguments={"sql": sql}
                    )
                else:
                    raise AgentError(f"Unsupported tool: {tool}")

                if tool == "run_read_query":
                    final_data = result

                elif tool in {
                    "run_write_query",
                    "explain_query",
                    "estimate_query_cost"
                }:
                    final_data = [result] if result is not None else []

                last_sql = sql
                last_tool = tool

            new_memory = self._update_memory(
                old=memory,
                user_message=user_message,
                sql=last_sql,
                data=final_data
            )

            memory_store.set(conversation_key, new_memory)

            return ChatResponse(
                text=self._build_text(last_tool, final_data),
                data=final_data
            )

        except MCPClientError as e:
            msg = str(e).lower()

            if (
                "permission" in msg
                 or "not allowed" in msg
                 or "forbidden" in msg
                 or "unauthorized" in msg
                ):
                return ChatResponse(
                   text="You do not have permission to perform this operation on the requested data.",
                   data=None
                )

            raise AgentError(str(e))

        except Exception as e:
            import traceback
            traceback.print_exc()
            raise AgentError(str(e))

    def _update_memory(
        self,
        *,
        old: MemoryState,
        user_message: str,
        sql: str | None,
        data: List[Dict[str, Any]] | None
    ) -> MemoryState:
        summary = None
        if data is not None:
            summary = f"{len(data)} rows" if isinstance(data, list) else "result produced"

        tables: List[str] = []
        if sql:
            tokens = sql.lower().split()
            if "from" in tokens:
                i = tokens.index("from")
                if i + 1 < len(tokens):
                    tables.append(tokens[i + 1])
            elif tokens and tokens[0] == "update" and len(tokens) > 1:
                tables.append(tokens[1])
            elif tokens and tokens[0] == "insert" and "into" in tokens:
                i = tokens.index("into")
                if i + 1 < len(tokens):
                    tables.append(tokens[i + 1])

        return MemoryState(
            last_intent=user_message,
            last_tables=tables or old.last_tables,
            last_filters=old.last_filters,
            last_summary=summary
        )

    def _build_text(
        self,
        tool: str | None,
        data: List[Dict[str, Any]] | None
    ) -> str:
        if not tool:
            return "No action executed."

        if tool == "run_read_query":
            count = len(data) if data else 0
            return f"Query executed successfully. Returned {count} rows."

        if tool == "run_write_query":
            return "Write operation executed successfully."

        if tool == "explain_query":
            return "Query plan generated successfully."

        if tool == "estimate_query_cost":
            return "Query cost estimated successfully."

        return "Operation completed successfully."


agent = OrchestratingAgent()
