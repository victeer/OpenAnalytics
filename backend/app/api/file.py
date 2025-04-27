from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
from typing import Optional
import os
import tempfile

router = APIRouter()

# 文件上传目录
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    上传CSV或Excel文件
    """
    try:
        # 检查文件类型
        if not file.filename.endswith(('.csv', '.xlsx')):
            raise HTTPException(status_code=400, detail="只支持CSV和Excel文件")
        
        # 保存文件
        file_path = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 读取文件内容
        if file.filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        # 获取基本信息
        info = {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "file_name": file.filename
        }
        
        return JSONResponse(content=info)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/info/{filename}")
async def get_file_info(filename: str):
    """
    获取文件的基本信息
    """
    try:
        file_path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")
        
        if filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        info = {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "sample_data": df.head().to_dict(orient='records')
        }
        
        return JSONResponse(content=info)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 