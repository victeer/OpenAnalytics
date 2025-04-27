from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.services.chat import ChatService
from app.services.dependencies import get_chat_service
import uuid

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: str = None

class ChatResponse(BaseModel):
    response: str
    status: str
    session_id: str

class SessionResponse(BaseModel):
    session_id: str
    message: str

@router.post("/send", response_model=ChatResponse)
async def send_message(request: ChatRequest, chat_service: ChatService = Depends(get_chat_service)):
    """
    发送消息并获取AI响应
    """
    try:
        response = await chat_service.chat(request.message, request.session_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear/{session_id}")
async def clear_history(session_id: str, chat_service: ChatService = Depends(get_chat_service)):
    """
    清空指定会话的对话历史
    """
    try:
        result = chat_service.clear_history(session_id)
        if result["status"] == "error":
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions", response_model=SessionResponse)
async def create_session(chat_service: ChatService = Depends(get_chat_service)):
    """
    创建新的聊天会话
    """
    try:
        session_id = str(uuid.uuid4())
        return {"session_id": session_id, "message": "会话创建成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def list_sessions(chat_service: ChatService = Depends(get_chat_service)):
    """
    获取所有聊天会话
    """
    try:
        result = chat_service.list_sessions()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def close_session(session_id: str, chat_service: ChatService = Depends(get_chat_service)):
    """
    关闭指定会话
    """
    try:
        result = chat_service.close_session(session_id)
        if result["status"] == "error":
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}")
async def get_history(session_id: str, chat_service: ChatService = Depends(get_chat_service)):
    """
    获取指定会话的历史记录
    """
    try:
        result = chat_service.get_history(session_id)
        if result["status"] == "error":
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 