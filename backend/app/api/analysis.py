from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from pydantic import BaseModel
from app.services.analysis import AnalysisService
from app.services.dependencies import get_analysis_service
import os
import uuid
from typing import List, Dict, Any, Optional
from io import StringIO
from fastapi.responses import StreamingResponse

router = APIRouter()

class AnalysisRequest(BaseModel):
    query: str
    session_id: str

class ProcessStep(BaseModel):
    type: str
    content: Any
    attempt: Optional[int] = None
    traceback: Optional[str] = None
    reason: Optional[str] = None

class AnalysisResponse(BaseModel):
    status: str
    analysis_plan: Optional[str] = None
    analysis_code: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    fixed_code: Optional[str] = None
    process_steps: Optional[List[ProcessStep]] = None
    user_notice: Optional[str] = None

class CreateSessionRequest(BaseModel):
    session_name: str = None

class SessionResponse(BaseModel):
    session_id: str
    message: str

class AnalysisRequestBody(BaseModel):
    query: str

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_with_body(request: AnalysisRequest):
    """
    分析数据并返回结果（请求体中包含会话ID）
    """
    try:
        result = await analysis_service.analyze(request.query, request.session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/load/{filename}/{session_id}")
async def load_file(filename: str, session_id: str):
    """
    加载数据文件到指定会话（老接口，建议使用/load/{session_id}/{filename}）
    """
    try:
        file_path = os.path.join("uploads", filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")
        
        result = await analysis_service.load_file(file_path, session_id)
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        return {"status": "success", "message": "文件加载成功", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions", response_model=SessionResponse)
async def create_session(request: CreateSessionRequest = None):
    """
    创建新的分析会话
    """
    session_id = request.session_name if request and request.session_name else f"session_{uuid.uuid4().hex[:8]}"
    return {"session_id": session_id, "message": "会话创建成功"}

@router.get("/sessions")
async def list_sessions(analysis_service: AnalysisService = Depends(get_analysis_service)):
    """
    列出所有会话
    """
    try:
        sessions = analysis_service.list_sessions()
        return {"status": "success", "sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def close_session(
    session_id: str,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    关闭指定会话
    """
    try:
        result = analysis_service.close_session(session_id)
        if result["status"] == "error":
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{session_id}")
async def get_history(session_id: str):
    """
    获取指定会话的分析历史
    """
    history = analysis_service.get_analysis_history(session_id)
    return {"session_id": session_id, "history": history}

@router.post("/create_session")
async def create_session_legacy(analysis_service: AnalysisService = Depends(get_analysis_service)):
    """
    创建新的分析会话（老接口，建议使用/sessions）
    """
    try:
        session_id = str(uuid.uuid4())
        return {"status": "success", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload/{session_id}")
async def upload_file(
    session_id: str,
    file: UploadFile = File(...),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    上传数据文件
    """
    try:
        print(f"接收到文件上传请求: 会话ID={session_id}, 文件名={file.filename}")
        
        # 检查文件类型
        if not file.filename.endswith(('.csv', '.xlsx', '.xls')):
            error_msg = "不支持的文件格式，请上传CSV或Excel文件"
            print(f"文件上传失败: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)
        
        result = await analysis_service.upload_file(session_id, file)
        print(f"文件上传处理结果: {result}")
        
        if result.get("status") == "error":
            print(f"文件上传服务错误: {result.get('message')}")
            raise HTTPException(status_code=500, detail=result.get("message"))
        
        return result
    except Exception as e:
        print(f"文件上传异常: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/load/{session_id}/{filename}")
async def load_data(
    session_id: str,
    filename: str,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    加载数据文件
    """
    try:
        result = await analysis_service.load_data(session_id, filename)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/{session_id}")
async def analyze_data(
    session_id: str,
    request: AnalysisRequestBody,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    执行数据分析
    """
    try:
        result = await analysis_service.analyze(request.query, session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/session/{session_id}")
async def close_session_legacy(
    session_id: str,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    关闭会话（老接口，建议使用/sessions/{session_id}）
    """
    try:
        result = analysis_service.close_session(session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analyze/{session_id}")
async def get_analysis_result(
    session_id: str,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    获取分析结果
    """
    try:
        # 获取最新的分析历史记录
        history = analysis_service.get_analysis_history(session_id)
        if not history:
            return {"status": "error", "message": "没有找到分析历史"}
        
        # 返回最近的分析结果
        latest_result = history[-1]
        
        response = {
            "status": "success",
            "result": latest_result.get("result"),
            "analysis_plan": latest_result.get("plan"),
            "analysis_code": latest_result.get("code"),
            "query": latest_result.get("query"),
        }
        
        # 添加处理步骤信息（如果存在）
        if "process_steps" in latest_result:
            response["process_steps"] = latest_result["process_steps"]
            
        # 添加用户通知（如果存在）
        if "user_notice" in latest_result:
            response["user_notice"] = latest_result["user_notice"]
            
        # 添加执行状态
        if "status" in latest_result:
            response["execution_status"] = latest_result["status"]
            
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions/{session_id}")
async def get_session_info(
    session_id: str,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    获取指定会话的详细信息
    """
    try:
        # 检查会话是否存在
        session = analysis_service.sessions.get(session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"会话 {session_id} 不存在")
        
        # 提取会话信息（排除大型数据对象）
        session_info = {
            "session_id": session_id,
            "exists": True,
            "has_data": session.get("data") is not None,
            "file_path": session.get("file_path"),
            "history_count": len(session.get("analysis_history", [])),
            "data_summary": {
                "shape": session.get("data").shape if session.get("data") is not None else None,
                "columns": session.get("data").columns.tolist() if session.get("data") is not None else None
            }
        }
        
        return session_info
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/common-queries/{session_id}")
async def save_common_query(
    session_id: str,
    query: str = Query(..., description="要保存的查询内容"),
    name: str = Query(None, description="查询名称"),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    保存常用查询
    """
    result = analysis_service.save_common_query(session_id, query, name)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.get("/common-queries/{session_id}")
async def get_common_queries(
    session_id: str,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    获取常用查询列表
    """
    queries = analysis_service.get_common_queries(session_id)
    return {"session_id": session_id, "queries": queries}

@router.delete("/common-queries/{session_id}")
async def delete_common_query(
    session_id: str,
    query: str = Query(..., description="要删除的查询内容"),
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    删除常用查询
    """
    result = analysis_service.delete_common_query(session_id, query)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result

@router.get("/download/{download_id}")
async def download_data(
    download_id: str,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    下载完整数据
    """
    try:
        df = analysis_service.download_cache.get(download_id)
        if df is None:
            raise HTTPException(status_code=404, detail="下载链接已过期")
        
        # 将DataFrame转换为CSV
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)
        
        # 生成文件名
        filename = f"analysis_result_{download_id[:8]}.csv"
        
        return StreamingResponse(
            iter([csv_buffer.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 