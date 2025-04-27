import pandas as pd
import os
from dotenv import load_dotenv
import traceback
import json
import time
import numpy as np
from app.services.dependencies import get_llm_service
import matplotlib.pyplot as plt
import io
from io import StringIO
import base64
import seaborn as sns
import shutil
from fastapi import UploadFile
import uuid

load_dotenv()

class AnalysisService:
    def __init__(self):
        self.sessions = {}
        self.common_queries = {}
        self.download_cache = {}  # 用于存储可下载的数据
        # 允许使用的模块
        self.allowed_modules = {
            'pandas': pd,
            'numpy': np
        }
        # 允许使用的函数
        self.allowed_functions = {
            'len': len,
            'list': list,
            'dict': dict,
            'str': str,
            'int': int,
            'float': float,
            'sum': sum,
            'min': min,
            'max': max,
            'sorted': sorted,
            'isinstance': isinstance,
            'print': print,
            '__import__': self._safe_import  # 添加安全的导入函数
        }
        
        # 确保上传目录存在
        os.makedirs("uploads", exist_ok=True)
        # 确保数据目录存在
        os.makedirs("data/common_queries", exist_ok=True)
        # 加载常用查询
        self._load_common_queries()
    
    def _safe_import(self, name, *args, **kwargs):
        """安全的导入函数，只允许导入预定义的模块"""
        # 只允许导入pandas和numpy
        allowed_imports = {
            'pandas': pd,
            'numpy': np
        }
        if name in allowed_imports:
            return allowed_imports[name]
        else:
            raise ImportError(f"导入 '{name}' 被禁止，只允许导入: {', '.join(allowed_imports.keys())}")
    
    async def upload_file(self, session_id: str, file: UploadFile) -> dict:
        """
        上传文件到服务器
        """
        try:
            # 创建会话目录
            session_dir = os.path.join("uploads", session_id)
            os.makedirs(session_dir, exist_ok=True)
            
            # 保存文件
            file_path = os.path.join(session_dir, file.filename)
            
            # 确保文件流指针在开始位置
            await file.seek(0)
            
            # 将文件内容写入磁盘
            with open(file_path, "wb") as buffer:
                # 读取所有内容并写入文件
                contents = await file.read()
                buffer.write(contents)
            
            # 重置文件指针以便后续操作可以再次读取
            await file.seek(0)
            
            # 加载数据
            if file.filename.endswith('.csv'):
                data = pd.read_csv(file_path)
            elif file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
                data = pd.read_excel(file_path)
            else:
                # 如果文件格式不支持，删除已创建的文件
                if os.path.exists(file_path):
                    os.remove(file_path)
                return {
                    "status": "error",
                    "message": "不支持的文件格式，请上传CSV或Excel文件"
                }
            
            # 生成数据信息
            data_info = get_data_info(data)
            
            # 存储会话数据
            self.sessions[session_id] = {
                "data": data,
                "data_info": data_info,
                "file_path": file_path,
                "analysis_history": []
            }
            
            # 记录日志
            print(f"文件已保存到: {file_path}")
            print(f"会话 {session_id} 已成功加载数据: {file.filename}")
            
            # 获取数据详情
            data_details = self.get_data_details(session_id)
            
            return {
                "status": "success",
                "message": f"文件上传并加载成功",
                "data_details": data_details
            }
        except Exception as e:
            # 记录错误信息
            print(f"文件上传失败: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return {
                "status": "error",
                "message": f"文件上传失败: {str(e)}"
            }
    
    async def load_data(self, session_id: str, filename: str) -> dict:
        """
        加载数据文件到内存
        """
        try:
            # 构建文件路径
            file_path = os.path.join("uploads", session_id, filename)
            if not os.path.exists(file_path):
                # 尝试在uploads根目录查找
                file_path = os.path.join("uploads", filename)
                if not os.path.exists(file_path):
                    return {
                        "status": "error",
                        "message": f"文件 {filename} 不存在"
                    }
            
            # 根据文件类型加载数据
            if filename.endswith('.csv'):
                data = pd.read_csv(file_path)
            elif filename.endswith('.xlsx') or filename.endswith('.xls'):
                data = pd.read_excel(file_path)
            else:
                return {
                    "status": "error",
                    "message": "不支持的文件格式，请上传CSV或Excel文件"
                }
            
            # 生成数据信息
            data_info = get_data_info(data)
            
            # 存储会话数据
            self.sessions[session_id] = {
                "data": data,
                "data_info": data_info,
                "file_path": file_path,
                "analysis_history": []
            }
            
            # 获取数据详情
            data_details = self.get_data_details(session_id)
            
            return {
                "status": "success",
                "message": f"数据文件 {filename} 加载成功",
                "data_details": data_details
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"加载数据失败: {str(e)}"
            }
    
    async def load_file(self, file_path: str, session_id: str):
        """
        加载数据文件到指定会话（兼容旧接口）
        """
        try:
            if file_path.endswith('.csv'):
                data = pd.read_csv(file_path)
            elif file_path.endswith('.xlsx'):
                data = pd.read_excel(file_path)
            else:
                raise ValueError("不支持的文件格式")
            
            # 生成数据信息
            data_info = get_data_info(data)
            
            # 存储会话数据
            self.sessions[session_id] = {
                "data": data,
                "data_info": data_info,
                "file_path": file_path,
                "analysis_history": []
            }
            
            return {
                "status": "success",
                "data_info": data_info
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_data_info(self, session_id: str):
        """获取会话数据基本信息"""
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        df = session["data"]
        if df is None:
            return None
        
        info = get_data_info(df)
        return info
    
    def get_data_details(self, session_id: str):
        """获取数据的详细信息，包括文件名、行列数、数据类型和前10行数据"""
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        df = session["data"]
        if df is None:
            return None
        
        # 获取文件路径
        file_path = session.get("file_path", "")
        file_name = os.path.basename(file_path) if file_path else "unknown"
        
        # 处理前10行数据，将 nan 值替换为空字符串
        sample_data = df.head(10).fillna('').to_dict(orient='records')
        
        # 构建详细信息
        details = {
            "file_name": file_name,
            "shape": {
                "rows": len(df),
                "columns": len(df.columns)
            },
            "columns": df.columns.tolist(),
            "dtypes": df.dtypes.astype(str).to_dict(),
            "sample_data": sample_data
        }
        
        return details
    
    async def analyze(self, query: str, session_id: str):
        """
        分析用户查询
        """
        try:
            # 获取会话数据
            session = self.sessions.get(session_id)
            if not session:
                # 如果会话不存在，创建一个空会话
                self.sessions[session_id] = {
                    "data": None,
                    "data_info": None,
                    "file_path": None,
                    "analysis_history": []
                }
                # 返回更友好的错误消息
                return {
                    "status": "error",
                    "message": f"会话 {session_id} 未加载数据，请先上传数据文件"
                }
            
            data = session["data"]
            data_info = session["data_info"]
            
            if data is None:
                return {
                    "status": "error",
                    "message": "请先上传并加载数据文件"
                }
            
            # 获取LLM服务
            llm_service = await get_llm_service()
            
            # 生成分析计划
            analysis_plan = await llm_service.generate_analysis_plan(
                data_info=data_info,
                query=query
            )
            
            # 生成分析代码
            analysis_code = await llm_service.generate_analysis_code(
                analysis_plan=analysis_plan,
                data_info=data_info,
                query=query
            )
            
            # 先记录初始流程，后续会根据执行情况更新
            analysis_record = {
                "timestamp": time.time(),
                "query": query,
                "plan": analysis_plan,
                "code": analysis_code,
                "result": None,
                "status": "started",
                "process_steps": [
                    {
                        "type": "analysis_plan",
                        "content": analysis_plan
                    },
                    {
                        "type": "initial_code",
                        "content": analysis_code
                    }
                ]
            }
            
            # 添加到会话历史
            session["analysis_history"].append(analysis_record)
            
            # 开始执行和错误处理流程
            max_attempts = 5
            attempt = 0
            attempts_history = []
            
            # 当前正在处理的代码
            current_code = analysis_code
            
            while attempt < max_attempts:
                attempt += 1
                
                try:
                    # 创建一个隔离的命名空间
                    code_globals = {
                        "pd": pd,
                        "np": np,
                        "StringIO": StringIO,
                        "io": io,
                        "base64": base64,
                    }
        
                    # 创建一个临时模块来执行代码
                    import sys
                    module = type(sys)('data_analysis_module')
                    # 打印执行的代码
                    print(f"\n=============== 执行分析代码 (尝试 {attempt}/{max_attempts}) ===============")
                    print(current_code)
                    print("==========================================\n")
                    code_obj = compile(current_code, '<string>', 'exec')
                    local_vars = {"df": session["data"]}
                    exec(code_obj, code_globals, local_vars)
                    
                    # 获取分析结果
                    result = local_vars.get("result", None)
                    
                    # 格式化结果
                    formatted_result = self._format_result(result)
                    
                    # 更新分析记录
                    analysis_record["result"] = formatted_result
                    analysis_record["status"] = "success"
                    analysis_record["process_steps"].append({
                        "type": "success",
                        "content": "代码执行成功",
                        "attempt": attempt
                    })
                    
                    # 执行成功，返回结果
                    return {
                        "status": "success",
                        "analysis_plan": analysis_plan,
                        "analysis_code": current_code,
                        "result": formatted_result,
                        "process_steps": analysis_record["process_steps"]
                    }
                
                except Exception as e:
                    error_message = f"{type(e).__name__}: {str(e)}"
                    traceback_message = traceback.format_exc()
                    
                    # 记录完整错误信息用于调试
                    print(f"\n=============== 执行错误 (尝试 {attempt}/{max_attempts}) ===============")
                    print(error_message)
                    print(traceback_message)
                    print("==========================================\n")
                    
                    # 记录本次尝试
                    attempt_record = {
                        "code": current_code,
                        "error": error_message,
                        "traceback": traceback_message
                    }
                    attempts_history.append(attempt_record)
                    
                    # 更新流程记录
                    analysis_record["process_steps"].append({
                        "type": "error",
                        "content": error_message,
                        "traceback": traceback_message,
                        "attempt": attempt
                    })
                    
                    # 如果已达到最大尝试次数，退出循环
                    if attempt >= max_attempts:
                        break

                    result = await self.process_error(current_code, error_message, traceback_message,
                        data, data_info, max_attempts, attempt, analysis_record, attempts_history, query)
                    if result['status'] == 'fixed_code':
                        current_code = result['code']
                        attempt = result['attempt']
                    else: # result['status'] == 'max_retry':
                        break

            # 如果达到最大尝试次数仍未成功
            # 生成用户友好的错误分析和建议
            user_notice = await llm_service.notify_user_too_many_attempts(
                original_code=analysis_code,
                attempts_history=attempts_history,
                query=query
            )
            
            # 更新分析记录
            analysis_record["status"] = "failed_max_attempts"
            analysis_record["user_notice"] = user_notice
            analysis_record["process_steps"].append({
                "type": "user_notice",
                "content": user_notice
            })
            
            return {
                "status": "error",
                "message": "执行分析代码失败，已达到最大尝试次数",
                "analysis_plan": analysis_plan,
                "analysis_code": current_code,
                "process_steps": analysis_record["process_steps"],
                "user_notice": user_notice
            }
            
        except Exception as e:
            # 捕获整个分析过程中的异常
            error_message = f"{type(e).__name__}: {str(e)}"
            traceback_msg = traceback.format_exc()
            
            print(f"\n=============== 分析过程异常 ===============")
            print(error_message)
            print(traceback_msg)
            print("==========================================\n")
            
            # 如果已创建分析记录，更新状态
            if 'analysis_record' in locals():
                analysis_record["status"] = "error"
                analysis_record["error_message"] = error_message
                analysis_record["process_steps"].append({
                    "type": "process_error",
                    "content": error_message
                })
            
            return {
                "status": "error",
                "message": f"分析过程出错: {str(e)}",
                "process_steps": analysis_record["process_steps"] if 'analysis_record' in locals() else []
            }
    
    async def process_error(self, current_code, error_message, traceback_message, 
            data, data_info, max_attempts, attempt, analysis_record, 
            attempts_history, query):
        llm_service = await get_llm_service()
        try:
            # 进入处理错误流程。
            error_analysis = await llm_service.analyze_error(
                code=current_code, 
                error=f"{error_message}\n{traceback_message}"
            )
            while attempt < max_attempts and error_analysis['plan'] == '获取信息':
                # 记录大模型的判断
                analysis_record["process_steps"].append({
                    "type": "error_analysis",
                    "content": error_analysis,
                    "attempt": attempt
                })
                
                info_code = error_analysis["code"]
                
                analysis_record["process_steps"].append({
                    "type": "info_code",
                    "content": info_code,
                    "attempt": attempt
                })
                
                # 执行获取信息的代码
                try:
                    info_globals = {
                        '__builtins__': self.allowed_functions,
                        **self.allowed_modules
                    }
                    info_locals = {"df": data}
                    
                    # 创建一个StringIO对象来捕获print输出
                    info_output = StringIO()
                    
                    # 修改代码，将结果打印出来
                    info_code_with_print = info_code
                    
                    # 重定向标准输出到StringIO
                    import sys
                    original_stdout = sys.stdout
                    sys.stdout = info_output
                    
                    # 执行代码
                    exec(info_code_with_print, info_globals, info_locals)
                    
                    # 恢复标准输出
                    sys.stdout = original_stdout
                    
                    # 获取输出内容
                    info_result = info_output.getvalue()
                    
                    analysis_record["process_steps"].append({
                        "type": "info_result",
                        "content": info_result,
                        "attempt": attempt
                    })
                    
                    # 使用获取的信息继续分析下一步结果。
                    error_analysis = await llm_service.analyze_error(
                        code=current_code,
                        error=error_message,
                        info_code=info_code,
                        run_info_result=info_result
                    )
                    attempt += 1

                except Exception as info_error:
                    # 获取信息时出错，记录错误
                    info_error_message = f"{type(info_error).__name__}: {str(info_error)}"
                    traceback_message = traceback.format_exc()
                    print(f"\n=============== 获取信息时出错 ===============")
                    print(info_error_message)
                    print(traceback_message)
                    print("==========================================\n")
                    analysis_record["process_steps"].append({
                        "type": "info_error",
                        "content": info_error_message,
                        "attempt": attempt
                    })

                    attempt_record = {
                        "code": info_code,
                        "error": info_error_message,
                        "traceback": traceback_message
                    }
                    attempts_history.append(attempt_record)

                    # 将错误信息作为下一步分析的输入。
                    error_analysis = await llm_service.analyze_error(
                        code=current_code,
                        error_message=error_message,
                        info_code=info_code,
                        run_info_result="{info_error_message}\n{traceback_message}"
                    )
                    attempt += 1

            if error_analysis['plan'] == '修复代码':
                fixed_code = error_analysis['code']
                analysis_record["process_steps"].append({
                    "type": "fixed_code",
                    "content": fixed_code,
                    "attempt": attempt,
                    "reason": error_analysis.get("reason", "")
                })
                result = {
                    'status': 'fixed_code',
                    'code': fixed_code,
                    'attempt': attempt
                }
            else:
                result = {
                    'status': 'max_retry',
                    'attempt': attempt
                }
        except Exception as fix_error:
            # 修复代码时出错，直接使用fix_code方法
            fix_error_message = f"{type(fix_error).__name__}: {str(fix_error)}"
            traceback_message = traceback.format_exc()
            print(f"\n=============== 修复代码时出错 ===============")
            print(fix_error_message)
            print(traceback_message)
            print("==========================================\n")
            analysis_record["process_steps"].append({
                "type": "fix_error",
                "content": fix_error_message,
                "traceback": traceback_message,
                "attempt": attempt
            })
            
            # 降级为使用简单的修复方法
            fixed_code = await llm_service.fix_code(
                code=current_code,
                error=error_message,
                query=query,
                data_info=data_info
            )
            
            analysis_record["process_steps"].append({
                "type": "fixed_code_fallback",
                "content": fixed_code,
                "attempt": attempt
            })

            result = {
                'status': 'fixed_code',
                'code': fixed_code,
                'attempt': attempt
            }

        return result

    def _format_result(self, result):
        """格式化分析结果"""
        if result is None:
            return None
        elif isinstance(result, pd.DataFrame):
            # 限制预览数据为30行
            preview_data = result.head(30).fillna('').to_dict(orient='records')
            # 生成完整数据的下载链接
            download_id = str(uuid.uuid4())
            self.download_cache[download_id] = result
            return {
                "type": "dataframe",
                "preview_data": preview_data,
                "columns": result.columns.tolist(),
                "total_rows": len(result),
                "download_id": download_id
            }
        elif isinstance(result, dict):
            return {
                "type": "dict",
                "data": result
            }
        elif isinstance(result, (list, tuple)):
            return {
                "type": "list",
                "data": result
            }
        else:
            return {
                "type": "other",
                "data": str(result)
            }
    
    def get_analysis_history(self, session_id: str):
        """获取分析历史"""
        session = self.sessions.get(session_id)
        if not session:
            return []
        return session.get("analysis_history", [])
    
    def _load_common_queries(self):
        """加载常用查询"""
        try:
            common_queries_file = "data/common_queries/common_queries.json"
            if os.path.exists(common_queries_file):
                with open(common_queries_file, 'r', encoding='utf-8') as f:
                    self.common_queries = json.load(f)
            else:
                self.common_queries = {}
        except Exception as e:
            print(f"加载常用查询失败: {str(e)}")
            self.common_queries = {}
    
    def _save_common_queries(self):
        """保存常用查询到文件"""
        try:
            common_queries_file = "data/common_queries/common_queries.json"
            with open(common_queries_file, 'w', encoding='utf-8') as f:
                json.dump(self.common_queries, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存常用查询失败: {str(e)}")
    
    def save_common_query(self, session_id: str, query: str, name: str = None):
        """保存常用查询"""
        session = self.sessions.get(session_id)
        if not session:
            return {"status": "error", "message": "会话不存在"}
        
        # 检查是否已存在相同的查询
        if session_id in self.common_queries:
            for q in self.common_queries[session_id]:
                if q["query"] == query:
                    return {"status": "error", "message": "该查询已存在"}
        
        # 添加新查询到全局存储
        query_data = {
            "query": query,
            "name": name or query[:30] + "..." if len(query) > 30 else query,
            "timestamp": time.time()
        }
        
        if session_id not in self.common_queries:
            self.common_queries[session_id] = []
        self.common_queries[session_id].append(query_data)
        
        # 保存到文件
        self._save_common_queries()
        
        # 更新会话中的引用
        session["common_queries"] = self.common_queries[session_id]
        
        return {"status": "success", "message": "查询保存成功"}
    
    def get_common_queries(self, session_id: str):
        """获取常用查询列表"""
        session = self.sessions.get(session_id)
        if not session:
            return []
        
        # 直接从全局存储获取
        return self.common_queries.get(session_id, [])
    
    def delete_common_query(self, session_id: str, query: str):
        """删除常用查询"""
        session = self.sessions.get(session_id)
        if not session:
            return {"status": "error", "message": "会话不存在"}
        
        if session_id not in self.common_queries:
            return {"status": "error", "message": "没有常用查询"}
        
        # 从全局存储中删除
        self.common_queries[session_id] = [q for q in self.common_queries[session_id] if q["query"] != query]
        self._save_common_queries()
        
        # 更新会话中的引用
        session["common_queries"] = self.common_queries[session_id]
        
        return {"status": "success", "message": "查询删除成功"}
    
    def list_sessions(self):
        """列出所有会话"""
        return list(self.sessions.keys())
    
    def close_session(self, session_id: str):
        """关闭会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return {"status": "success", "message": f"会话 {session_id} 已关闭"}
        return {"status": "error", "message": f"会话 {session_id} 不存在"}
    

def get_data_info(df):
    """获取数据的基本信息"""
    info_output = StringIO()
    
    # 记录基本信息
    df_info = StringIO()
    df.info(buf=df_info)
    print(df_info.getvalue(), file=info_output)
    
    # 查看数据集行数和列数
    rows, columns = df.shape
    print(f"\n数据规模: {rows}行 × {columns}列", file=info_output)
    
    if rows < 100 and columns < 20:
        # 短表数据查看全量数据信息
        print('\n数据全部内容信息：', file=info_output)
        print(df.to_csv(sep='\t', index=False, na_rep='nan'), file=info_output)
    else:
        # 长表数据查看数据前几行信息
        print('\n数据前几行内容信息：', file=info_output)
        print(df.head(10).to_csv(sep='\t', index=False, na_rep='nan'), file=info_output)
    
    return info_output.getvalue()