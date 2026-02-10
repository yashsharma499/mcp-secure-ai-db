from fastapi import FastAPI, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import ChatRequest, ChatResponse
from app.agent import agent, AgentError
from app.mcp_client import mcp_client   


app = FastAPI(title="MCP Agent Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    authorization: str | None = Header(default=None),
):
    try:
        if not authorization or not authorization.lower().startswith("bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header",
            )

        jwt_token = authorization.split(" ", 1)[1].strip()

        conversation_key = f"user:{request.user_id}"

        response = await agent.handle_message(
            conversation_key=conversation_key,
            user_message=request.message,
            jwt_token=jwt_token,
        )

        return response

    except AgentError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except HTTPException:
        raise

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )



@app.get("/me/permissions")
async def get_my_permissions(
    authorization: str | None = Header(default=None),
):
    try:
        if not authorization or not authorization.lower().startswith("bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authorization header",
            )

        jwt_token = authorization.split(" ", 1)[1].strip()

        tool_resp = await mcp_client.call_tool(
            tool_name="get_user_permissions",
            jwt_token=jwt_token,
            arguments={}
        )

       
        if isinstance(tool_resp, dict):
            return tool_resp.get("permissions", [])

        return tool_resp

    except AgentError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except HTTPException:
        raise

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
