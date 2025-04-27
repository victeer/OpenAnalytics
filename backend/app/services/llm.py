from openai import AsyncOpenAI
from app.core.config import settings
import os
import json
import httpx
import asyncio
import re

class LLMService:
    def __init__(self):
        # 创建不带代理的httpx异步客户端
        self.http_client = httpx.AsyncClient(
            timeout=60.0,
            follow_redirects=True
        )
        
        # 使用自定义的http客户端初始化OpenAI客户端
        self.client = AsyncOpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE_URL,
            http_client=self.http_client
        )
        self.model = settings.OPENAI_MODEL
    
    async def close(self):
        """关闭异步客户端"""
        await self.http_client.aclose()
    
    def __del__(self):
        """在对象销毁时关闭客户端"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.close())
            else:
                loop.run_until_complete(self.close())
        except Exception:
            # 如果无法获取事件循环（例如在应用程序退出时），则忽略错误
            pass
    
    async def chat_completion(self, messages, temperature=0.8, max_tokens=1000):
        """通用的大模型对话接口"""
        try:
            # 打印输入信息用于调试
            print("\n=============== 大模型调用输入 ===============")
            print(f"模型: {self.model}")
            print(f"温度: {temperature}")
            print(f"最大token数: {max_tokens}")
            print("消息内容:")
            for idx, msg in enumerate(messages):
                print(f"[{idx}] {msg['role']}:")
                print(f"{msg['content']}")
            print("==========================================\n")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            content = response.choices[0].message.content
            
            # 打印输出结果用于调试
            print("\n=============== 大模型调用输出 ===============")
            print("输出内容:")
            print(f"{content}")
            print("==========================================\n")
            
            return content
        except Exception as e:
            print("\n=============== 大模型调用错误 ===============")
            print(f"错误信息: {str(e)}")
            print("==========================================\n")
            raise Exception(f"大模型调用失败: {str(e)}")
    
    async def generate_analysis_plan(self, data_info: str, query: str):
        """生成分析计划"""
        messages = [
            {"role": "system", "content": """你是一个数据分析专家，请根据用户的需求和数据信息，生成一句话的分析计划。
            请用浅显易懂的语言描述，避免使用技术术语。"""},
            {"role": "user", "content": f"数据信息:\n{data_info}\n\n用户需求：{query}"}
        ]
        return await self.chat_completion(messages)
    
    async def generate_analysis_code(self, analysis_plan: str, data_info: str, query: str):
        """生成分析代码"""
        messages = [
            {"role": "system", "content": """你是一个Python数据分析专家，请根据用户需求和分析计划生成Python代码。
            代码要求：
            1. 使用pandas处理数据
            2. 包含必要的注释
            3. 不需要考虑异常情况，有异常直接报错即可。
            4. 如果关键数据有空值, 可以进行合理的推断填充，但不要过度推断。
            4. 将分析结果存储在变量'result'中, 类型为DataFrame, 不要返回任何其他内容, 也不需要打印信息。
            5. 使用变量名'df'表示输入数据
            6. 只能使用pandas和numpy模块
            7. 不要添加任何解释和代码块标记。"""},
            {"role": "user", "content": f"用户需求：\n{query}\n\n分析计划：\n{analysis_plan}\n\n数据信息：\n{data_info}\n\n请直接生成Python代码。"}
        ]
        return await self.chat_completion(messages)
    
    async def fix_code(self, code: str, error: str, query: str, data_info: str):
        """修复执行失败的代码"""
        messages = [
            {"role": "system", "content": """你是一个Python代码修复专家，请修复代码中的错误。
            修复要求：
            1. 保持原有功能不变
            2. 处理所有可能的异常
            3. 添加必要的错误处理
            4. 确保代码可以正确执行
            5. 只能使用pandas和numpy模块    
            6. 请直接返回修复后的代码，不要包含任何解释或代码块标记。
            """},
            {"role": "user", "content": f"用户需求: {query}\n\n数据信息: {data_info}\n\n原始代码：\n{code}\n\n错误信息：\n{error}\n\n请修复代码。"}
        ]
        return await self.chat_completion(messages)
    
    async def explain_result(self, result: dict, query: str):
        """解释分析结果"""
        messages = [
            {"role": "system", "content": """你是一个数据分析专家，请用通俗易懂的语言解释分析结果。
            解释要求：
            1. 说明结果的含义
            2. 指出关键发现
            3. 给出可能的建议
            4. 使用非技术性语言"""},
            {"role": "user", "content": f"分析结果：\n{json.dumps(result, ensure_ascii=False, indent=2)}\n\n原始查询：{query}"}
        ]
        return await self.chat_completion(messages)
    
    async def suggest_visualization(self, result: dict, query: str):
        """建议可视化方案"""
        messages = [
            {"role": "system", "content": """你是一个数据可视化专家，请根据分析结果建议合适的可视化方案。
            建议要求：
            1. 推荐合适的图表类型
            2. 说明选择理由
            3. 指出需要展示的关键数据
            4. 考虑数据的特性和展示效果"""},
            {"role": "user", "content": f"分析结果：\n{json.dumps(result, ensure_ascii=False, indent=2)}\n\n原始查询：{query}"}
        ]
        return await self.chat_completion(messages)
    
    async def analyze_error(self, code: str, error: str, query: str = None, data_info: str = None, 
              info_code: str = None, run_info_result: str = None):
        """分析错误并提出下一步计划"""
        info_prompt = ""
        info = {"用户需求": query, "数据信息": data_info, "错误信息": error, "原始代码": code, 
                "获取信息代码": info_code, "运行结果": run_info_result}
        for key in ["用户需求", "数据信息", "原始代码", "错误信息", "获取信息代码", "运行结果"]:
            if info[key]:
                info_prompt += f"{key}：\n{info[key]}\n\n"

        messages = [
            {"role": "system", "content": """你是一个数据分析专家，擅长调试和修复Python数据分析代码。 请根据当前的信息, 提供下一步计划和相应的代码。
            请判断最适合的处理方案:
            1. 需要获取额外信息 - 如果需要了解数据的更多信息才能解决问题, 请提供获取信息的Python代码, 通过打印信息的方式输出结果。
            2. 直接修复原始代码 - 如果错误原因已经明确，可以直接修复
            
            请按照 "下一步计划"、"判断理由"、"代码"三个模块给出结果。
            其中, 下一步计划只能选择 "获取信息" 或 "修复代码"，不要选择其他内容。
            代码模块: 如果选择获取信息，提供获取信息的Python代码；如果选择修复代码，提供修复后的完整代码。代码使用```python```包裹。
            示例: 
            ### 下一步计划
            获取信息
            ### 判断理由
            需要获取列名，以了解df的结构.
            ### 代码
            ```python
            print(df.columns)
            ```
            """},
            {"role": "user", "content": info_prompt}
        ]
        result = await self.chat_completion(messages)
        parsed_result = self.parse_llm_response(result)
        if parsed_result["plan"] not in ["获取信息", "修复代码"]:
            print(f"大模型返回的计划不是获取信息或修复代码，使用兜底方案返回结果")
            return {
                "plan": "修复代码",
                "reason": "大模型返回的计划不是获取信息或修复代码，使用兜底方案返回结果，默认选择修复代码",
                "code": await self.fix_code(code, error, query, data_info)
            }
        else:
            return parsed_result

            return {
                "plan": "修复代码",
                "reason": "无法解析大模型返回的JSON，默认选择修复代码",
                "code": await self.fix_code(code, error, query, data_info)
            }
    
    async def analyze_with_additional_info(self, original_code: str, error_message: str, 
                                          info_code: str, info_result: str, data_info: str = None):
        """根据额外获取的信息，分析并修复代码"""
        messages = [
            {"role": "system", "content": """你是一个Python数据分析专家，现在你获得了额外的数据信息，请修复原始代码。
            请提供修复后的完整代码，确保代码可以正确执行。
            
            回复格式:
            请直接返回修复后的代码，不要包含任何解释或代码块标记。"""},
            {"role": "user", "content": f"""原始代码：
{original_code}

错误信息：
{error_message}

获取信息的代码：
{info_code}

获取信息的结果：
{info_result}

数据信息：
{data_info if data_info else '无'}

请修复原始代码，使其能够正确执行。"""}
        ]
        return await self.chat_completion(messages)
    
    async def notify_user_too_many_attempts(self, original_code: str, attempts_history: list, query: str):
        """通知用户尝试次数过多，提供错误分析和建议"""
        attempts_str = "\n\n".join([
            f"尝试 {i+1}:\n代码: {attempt.get('code', '无')}\n错误: {attempt.get('error', '无')}"
            for i, attempt in enumerate(attempts_history)
        ])
        
        messages = [
            {"role": "system", "content": """你是一个Python数据分析专家，请分析多次尝试失败的原因并提供建议。
            请提供:
            1. 失败的主要原因分析
            2. 给用户的具体建议，包括可能需要提供的额外信息
            3. 用简洁明了的语言表达"""},
            {"role": "user", "content": f"""用户查询：{query}
            
原始代码：
{original_code}

尝试历史：
{attempts_str}

请分析失败原因并给出建议。"""}
        ]
        return await self.chat_completion(messages)
    
    def parse_llm_response(self, result):
        """
        解析大模型返回的结构化响应
        
        参数:
        result (str): 大模型返回的原始文本
        
        返回:
        dict: 包含plan, reason, code三个字段的字典
        """
        parsed_result = {}
        
        # 使用正则表达式提取三个部分
        plan_match = re.search(r'###\s*下一步计划\s*(.*?)(?=###|$)', result, re.DOTALL)
        reason_match = re.search(r'###\s*判断理由\s*(.*?)(?=###|$)', result, re.DOTALL)
        code_match = re.search(r'###\s*代码\s*```python\s*(.*?)```', result, re.DOTALL)
        
        # 提取下一步计划
        if plan_match:
            plan = plan_match.group(1).strip()
            parsed_result["plan"] = plan
        else:
            parsed_result["plan"] = ""  # 如果无法提取到plan，则返回空字符串
        
        # 提取判断理由
        if reason_match:
            reason = reason_match.group(1).strip()
            parsed_result["reason"] = reason
        else:
            parsed_result["reason"] = "无法识别判断理由"
        
        # 提取代码
        if code_match:
            code = code_match.group(1).strip()
            parsed_result["code"] = code
        else:
            # 尝试匹配没有python标记的代码块
            code_alt_match = re.search(r'###\s*代码\s*```\s*(.*?)```', result, re.DOTALL)
            if code_alt_match:
                code = code_alt_match.group(1).strip()
                parsed_result["code"] = code
            else:
                # 最后尝试提取代码部分（无代码块标记的情况）
                if "### 代码" in result:
                    code_section = result.split("### 代码")[-1].strip()
                    parsed_result["code"] = code_section
                else:
                    parsed_result["code"] = ""
        
        return parsed_result 