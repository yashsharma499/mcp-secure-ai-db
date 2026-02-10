import re
from typing import Optional, List


class SQLUtilError(Exception):
    pass


_IDENTIFIER_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def normalize_identifier(value: str) -> str:
    if not value or not isinstance(value, str):
        raise SQLUtilError("Invalid identifier")
    name = value.strip().lower()
    if not _IDENTIFIER_RE.match(name):
        raise SQLUtilError("Invalid identifier format")
    return name


def normalize_identifiers(values: List[str]) -> List[str]:
    if not isinstance(values, list):
        raise SQLUtilError("Identifiers must be a list")
    result = []
    for v in values:
        result.append(normalize_identifier(v))
    return list(dict.fromkeys(result))


def strip_trailing_semicolon(sql: str) -> str:
    if not isinstance(sql, str):
        raise SQLUtilError("Invalid SQL")
    return sql.strip().rstrip(";")


def ensure_single_statement(sql: str) -> str:
    cleaned = strip_trailing_semicolon(sql)
    if ";" in cleaned:
        raise SQLUtilError("Multiple SQL statements are not allowed")
    return cleaned


def extract_simple_table(sql: str) -> Optional[str]:
    if not isinstance(sql, str):
        raise SQLUtilError("Invalid SQL")

    tokens = re.split(r"\s+", sql.strip())
    if not tokens:
        return None

    first = tokens[0].lower()

    if first == "select":
        m = re.search(r"\bfrom\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql, re.IGNORECASE)
        if not m:
            return None
        return normalize_identifier(m.group(1))

    if first in {"insert", "update", "delete"}:
        if first == "insert":
            m = re.search(r"\binto\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql, re.IGNORECASE)
        elif first == "update":
            m = re.search(r"\bupdate\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql, re.IGNORECASE)
        else:
            m = re.search(r"\bfrom\s+([a-zA-Z_][a-zA-Z0-9_]*)", sql, re.IGNORECASE)

        if not m:
            return None

        return normalize_identifier(m.group(1))

    return None


def has_limit(sql: str) -> bool:
    if not isinstance(sql, str):
        raise SQLUtilError("Invalid SQL")
    return bool(re.search(r"\blimit\s+\d+\b", sql, re.IGNORECASE))


def enforce_limit(sql: str, limit: int) -> str:
    if not isinstance(sql, str):
        raise SQLUtilError("Invalid SQL")

    if limit <= 0:
        raise SQLUtilError("Invalid limit")

    base = strip_trailing_semicolon(sql)

    if has_limit(base):
        return base

    return f"{base} limit {int(limit)}"
