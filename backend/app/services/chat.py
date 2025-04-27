from app.services.dependencies import get_llm_service
import uuid

class ChatService:
    def __init__(self):
        # 存储不同会话的消息历史
        self.sessions = {}
    
    async def chat(self, message: str, session_id: str = None):
        """
        处理用户消息并返回AI响应
        """
        try:
            # 如果未提供会话ID，创建一个新的
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # 确保会话存在
            if session_id not in self.sessions:
                self.sessions[session_id] = []
            
            # 获取当前会话的消息历史
            messages = self.sessions[session_id]
            
            # 添加用户消息到历史记录
            messages.append({"role": "user", "content": message})
            
            # 获取LLM服务
            llm_service = await get_llm_service()
            
            # 调用大模型服务
            response = await llm_service.chat_completion(messages)
            
            # 添加AI响应到历史记录
            messages.append({"role": "assistant", "content": response})
            
            return {
                "response": response,
                "status": "success",
                "session_id": session_id
            }
            
        except Exception as e:
            return {
                "response": f"发生错误: {str(e)}",
                "status": "error",
                "session_id": session_id
            }
    
    def clear_history(self, session_id: str = None):
        """
        清空指定会话的对话历史
        """
        if session_id and session_id in self.sessions:
            self.sessions[session_id] = []
            return {"status": "success", "message": "对话历史已清空"}
        elif not session_id:
            self.sessions = {}
            return {"status": "success", "message": "所有会话历史已清空"}
        else:
            return {"status": "error", "message": "指定的会话不存在"}
    
    def get_history(self, session_id: str):
        """
        获取指定会话的历史记录
        """
        if session_id in self.sessions:
            return {
                "status": "success", 
                "history": self.sessions[session_id]
            }
        return {
            "status": "error", 
            "message": "指定的会话不存在"
        }
    
    def list_sessions(self):
        """
        列出所有活跃会话
        """
        return {
            "status": "success",
            "sessions": list(self.sessions.keys())
        }
    
    def close_session(self, session_id: str):
        """
        关闭并删除指定会话
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return {"status": "success", "message": f"会话 {session_id} 已关闭"}
        return {"status": "error", "message": f"会话 {session_id} 不存在"} 