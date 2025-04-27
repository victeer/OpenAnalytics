from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from ..services.example_service import ExampleService
from ..services.dependencies import get_example_service
from pathlib import Path
import urllib.parse
from pydantic import BaseModel, Field
from typing import List, Optional

router = APIRouter()

class ExampleCreate(BaseModel):
    name: str = Field(..., description="示例名称")
    description: str = Field(..., description="示例描述")
    tags: List[str] = Field(default_factory=list, description="示例标签列表")
    analysisProcess: dict = Field(..., description="分析过程数据")
    sessionId: str = Field(..., description="会话ID")

@router.post("/examples")
async def create_example(
    example_data: ExampleCreate,
    example_service: ExampleService = Depends(get_example_service)
):
    """创建分析示例"""
    try:
        # 确保 tags 是列表类型
        if not isinstance(example_data.tags, list):
            example_data.tags = [example_data.tags]
            
        example = await example_service.save_example(example_data.dict(), example_data.sessionId)
        return example
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/examples")
async def list_examples(
    example_service: ExampleService = Depends(get_example_service)
):
    """获取示例列表"""
    try:
        examples = await example_service.list_examples()
        return examples
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/examples/{example_id}")
async def get_example(
    example_id: str,
    example_service: ExampleService = Depends(get_example_service)
):
    """获取单个示例"""
    example = await example_service.get_example(example_id)
    if not example:
        raise HTTPException(status_code=404, detail="示例不存在")
    return example

@router.put("/examples/{example_id}")
async def update_example(
    example_id: str,
    example_data: dict,
    example_service: ExampleService = Depends(get_example_service)
):
    """更新示例"""
    example = await example_service.update_example(example_id, example_data)
    if not example:
        raise HTTPException(status_code=404, detail="示例不存在")
    return example

@router.delete("/examples/{example_id}")
async def delete_example(
    example_id: str,
    example_service: ExampleService = Depends(get_example_service)
):
    """删除示例"""
    success = await example_service.delete_example(example_id)
    if not success:
        raise HTTPException(status_code=404, detail="示例不存在")
    return {"message": "示例删除成功"}

@router.get("/examples/{example_id}/file/{filename}")
async def download_example_file(
    example_id: str,
    filename: str,
    example_service: ExampleService = Depends(get_example_service)
):
    """下载示例文件"""
    # 解码文件名
    decoded_filename = urllib.parse.unquote(filename)
    
    # 获取示例信息
    example = await example_service.get_example(example_id)
    if not example:
        raise HTTPException(status_code=404, detail="示例不存在")
    
    # 获取文件路径
    file_path = None
    if 'originalFile' in example.get('analysisProcess', {}):
        original_file = example['analysisProcess']['originalFile']
        if 'saved_file_path' in original_file:
            file_path = Path(original_file['saved_file_path'])
    
    if not file_path or not file_path.exists():
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=file_path,
        filename=decoded_filename,
        media_type='application/octet-stream'
    ) 