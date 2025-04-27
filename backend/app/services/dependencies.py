from fastapi import Depends
from app.services.llm import LLMService

# 全局服务实例
llm_service = None
analysis_service = None
chat_service = None

# 示例服务实例
example_service = None

async def get_llm_service():
    """获取LLM服务实例的依赖"""
    global llm_service
    if llm_service is None:
        llm_service = LLMService()
    return llm_service

async def get_analysis_service():
    """获取分析服务实例的依赖"""
    global analysis_service
    if analysis_service is None:
        # 延迟导入，避免循环引用
        from app.services.analysis import AnalysisService
        analysis_service = AnalysisService()
    return analysis_service

async def get_chat_service():
    """获取聊天服务实例的依赖"""
    global chat_service
    if chat_service is None:
        # 延迟导入，避免循环引用
        from app.services.chat import ChatService
        chat_service = ChatService()
    return chat_service

async def get_example_service():
    """获取示例服务实例的依赖"""
    global example_service
    if example_service is None:
        from app.services.example_service import ExampleService
        example_service = ExampleService(storage_path="data/examples")
    return example_service

async def close_llm_service():
    """关闭LLM服务"""
    global llm_service
    if llm_service is not None:
        await llm_service.close()
        llm_service = None 