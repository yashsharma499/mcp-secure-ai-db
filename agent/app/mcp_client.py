from typing import Any, Dict, List, Optional

import httpx

from app.config import get_settings


class MCPClientError(Exception):
    pass


class MCPClient:
    def __init__(self):
        self._settings = get_settings()
        self._base = self._settings.mcp_base_url.rstrip("/")
        self._timeout = self._settings.mcp_timeout_seconds

        self._tool_map: Dict[str, Dict[str, Any]] = {
            "get_schema": {"method": "GET", "path": "/mcp/tools/get_schema"},
            "get_user_permissions": {"method": "GET", "path": "/mcp/tools/get_user_permissions"},
            "validate_query": {"method": "POST", "path": "/mcp/tools/validate_query"},
            "dry_run_query": {"method": "POST", "path": "/mcp/tools/dry_run_query"},
            "run_read_query": {"method": "POST", "path": "/mcp/tools/run_read_query"},
            "run_write_query": {"method": "POST", "path": "/mcp/tools/run_write_query"},
            "explain_query": {"method": "POST", "path": "/mcp/tools/explain_query"},
            "estimate_query_cost": {"method": "POST", "path": "/mcp/tools/estimate_query_cost"},
            "audit_query_history": {"method": "GET", "path": "/mcp/tools/audit_query_history"},
        }

    def _headers(self, jwt_token: str) -> Dict[str, str]:
        if not jwt_token:
            raise MCPClientError("Missing JWT token")

        return {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json",
        }

    async def call_tool(
        self,
        *,
        tool_name: str,
        jwt_token: str,
        arguments: Optional[Dict[str, Any]] = None,
    ) -> Any:
        if tool_name not in self._tool_map:
            raise MCPClientError(f"Unknown MCP tool: {tool_name}")

        tool = self._tool_map[tool_name]
        method = tool["method"]
        path = tool["path"]
        url = f"{self._base}{path}"

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                if method == "GET":
                    resp = await client.get(
                        url,
                        headers=self._headers(jwt_token),
                        params=arguments or {},
                    )
                else:
                    resp = await client.post(
                        url,
                        headers=self._headers(jwt_token),
                        json=arguments or {},
                    )

                if resp.status_code >= 400:
                    try:
                        payload = resp.json()
                        message = (
                            payload.get("detail")
                            or payload.get("message")
                            or resp.text
                        )
                    except Exception:
                        message = resp.text

                    raise MCPClientError(message)

                if not resp.content:
                    return None

                return resp.json()

        except httpx.RequestError as e:
            raise MCPClientError(str(e)) from e

    async def get_schema(self, jwt_token: str) -> Dict[str, List[str]]:
        return await self.call_tool(
            tool_name="get_schema",
            jwt_token=jwt_token,
            arguments={},
        )

    async def get_user_permissions(self, jwt_token: str):
        return await self.call_tool(
            tool_name="get_user_permissions",
            jwt_token=jwt_token,
            arguments={},
        )

    async def validate_query(self, jwt_token: str, sql: str) -> Dict[str, Any]:
        return await self.call_tool(
            tool_name="validate_query",
            jwt_token=jwt_token,
            arguments={"sql": sql},
        )

    async def dry_run_query(self, jwt_token: str, sql: str) -> Dict[str, Any]:
        return await self.call_tool(
            tool_name="dry_run_query",
            jwt_token=jwt_token,
            arguments={"sql": sql},
        )

    async def run_read_query(self, jwt_token: str, sql: str) -> List[Dict[str, Any]]:
        return await self.call_tool(
            tool_name="run_read_query",
            jwt_token=jwt_token,
            arguments={"sql": sql},
        )

    async def run_write_query(self, jwt_token: str, sql: str) -> Dict[str, Any]:
        return await self.call_tool(
            tool_name="run_write_query",
            jwt_token=jwt_token,
            arguments={"sql": sql},
        )

    async def explain_query(self, jwt_token: str, sql: str) -> Dict[str, Any]:
        return await self.call_tool(
            tool_name="explain_query",
            jwt_token=jwt_token,
            arguments={"sql": sql},
        )

    async def estimate_query_cost(self, jwt_token: str, sql: str) -> Dict[str, Any]:
        return await self.call_tool(
            tool_name="estimate_query_cost",
            jwt_token=jwt_token,
            arguments={"sql": sql},
        )

    async def audit_query_history(
        self,
        jwt_token: str,
        user_id: Optional[int] = None,
        limit: int = 100,
    ):
        args: Dict[str, Any] = {"limit": limit}
        if user_id is not None:
            args["user_id"] = user_id

        return await self.call_tool(
            tool_name="audit_query_history",
            jwt_token=jwt_token,
            arguments=args,
        )


mcp_client = MCPClient()
