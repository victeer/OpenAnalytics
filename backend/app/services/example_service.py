from typing import List, Optional
from datetime import datetime
import json
import os
import shutil
from pathlib import Path

class ExampleService:
    def __init__(self, storage_path: str):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.example_files_path = self.storage_path.parent / 'example_files'
        self.example_files_path.mkdir(parents=True, exist_ok=True)

    def _get_example_path(self, example_id: str) -> Path:
        return self.storage_path / f"{example_id}.json"

    def _get_example_file_path(self, example_id: str, filename: str) -> Path:
        return self.example_files_path / f"{example_id}_{filename}"

    async def save_example(self, example_data: dict, session_id: str) -> dict:
        """保存分析示例"""
        example_id = str(datetime.now().timestamp())
        example_data['id'] = example_id
        example_data['createdAt'] = datetime.now().isoformat()

        # 保存原始文件
        if 'originalFile' in example_data.get('analysisProcess', {}):
            original_file = example_data['analysisProcess']['originalFile']
            if 'file_name' in original_file:
                # 从上传目录复制文件
                upload_path = Path("uploads") / session_id / original_file['file_name']
                if upload_path.exists():
                    new_file_path = self._get_example_file_path(
                        example_id, 
                        original_file['file_name']
                    )
                    shutil.copy2(upload_path, new_file_path)
                    original_file['saved_file_path'] = str(new_file_path)

        example_path = self._get_example_path(example_id)
        with open(example_path, 'w', encoding='utf-8') as f:
            json.dump(example_data, f, ensure_ascii=False, indent=2)

        return example_data

    async def get_example(self, example_id: str) -> Optional[dict]:
        """获取单个示例"""
        example_path = self._get_example_path(example_id)
        if not example_path.exists():
            return None

        with open(example_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    async def get_example_file(self, example_id: str, filename: str) -> Optional[Path]:
        """获取示例文件路径"""
        file_path = self._get_example_file_path(example_id, filename)
        if not file_path.exists():
            return None
        return file_path

    async def list_examples(self) -> List[dict]:
        """获取示例列表"""
        examples = []
        for file_path in self.storage_path.glob('*.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                example = json.load(f)
                examples.append(example)
        
        # 按创建时间倒序排序
        examples.sort(key=lambda x: x['createdAt'], reverse=True)
        return examples

    async def update_example(self, example_id: str, example_data: dict) -> Optional[dict]:
        """更新示例"""
        example_path = self._get_example_path(example_id)
        if not example_path.exists():
            return None

        with open(example_path, 'w', encoding='utf-8') as f:
            json.dump(example_data, f, ensure_ascii=False, indent=2)

        return example_data

    async def delete_example(self, example_id: str) -> bool:
        """删除示例"""
        example_path = self._get_example_path(example_id)
        if not example_path.exists():
            return False

        example_path.unlink()
        return True 