import requests
import json
import base64
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

class ImageGenerator:
    def __init__(self):
        self.base_url = os.getenv("BASE_URL")
        self.api_key = os.getenv("API_KEY")
        self.image_gen_model = os.getenv("IMAGE_GEN_MODEL")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def encode_image(self, image_path: str) -> str:
        """将图片编码为base64字符串"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def generate_image(self, 
                     prompt: str, 
                     reference_image_path: Optional[str] = None,
                     character_image_path: Optional[str] = None,
                     width: int = 1024, 
                     height: int = 1024) -> str:
        """
        生成图像
        
        Args:
            prompt: 生成提示词
            reference_image_path: 参考图路径（可选）
            character_image_path: 角色图路径（可选）
            width: 图像宽度
            height: 图像高度
            
        Returns:
            生成的图像保存路径
        """
        # 构造消息
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": prompt
                    }
                ]
            }
        ]
        
        # 如果有参考图或角色图，添加到消息中
        if reference_image_path:
            base64_ref_image = self.encode_image(reference_image_path)
            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_ref_image}"
                }
            })
        
        if character_image_path:
            base64_char_image = self.encode_image(character_image_path)
            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_char_image}"
                }
            })
        
        # 发送请求
        payload = {
            "model": self.image_gen_model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1024,
            "response_format": {"type": "image", "image": {"size": f"{width}x{height}"}}
        }
        
        response = requests.post(self.base_url, headers=self.headers, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"图像生成API调用失败: {response.status_code} - {response.text}")
        
        # 解析响应
        result = response.json()
        image_data = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # 保存生成的图像
        output_path = self.save_generated_image(image_data, width, height)
        return output_path

    def construct_structured_prompt(self, 
                                  scene_description: str, 
                                  character_features: str,
                                  original_scene_weight: float = 0.3,
                                  target_character_weight: float = 0.7) -> str:
        """
        构造带权重的结构化Prompt
        
        Args:
            scene_description: 场景描述
            character_features: 角色特征
            original_scene_weight: 原场景权重
            target_character_weight: 目标角色权重
            
        Returns:
            结构化Prompt字符串
        """
        prompt = f"{scene_description} <Original Scene: weight={original_scene_weight}> + {character_features} <Target Character ID: weight={target_character_weight}>"
        return prompt

    def save_generated_image(self, image_data: str, width: int, height: int) -> str:
        """
        保存生成的图像
        """
        # 简化处理：实际应用中需要根据API返回格式处理
        # 这里假设image_data是base64编码的图像数据
        import time
        timestamp = int(time.time())
        output_path = f"output/generated_image_{timestamp}.jpg"
        
        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 如果image_data是base64格式，保存为图片
        if image_data.startswith("data:image"):
            # 提取base64部分
            header, encoded = image_data.split(",", 1)
            image_bytes = base64.b64decode(encoded)
            
            with open(output_path, "wb") as f:
                f.write(image_bytes)
        else:
            # 如果是URL或其他格式，需要根据实际API返回格式处理
            # 这里简化处理，创建一个占位图片
            import cv2
            import numpy as np
            img = np.zeros((height, width, 3), dtype=np.uint8)
            img[:] = (100, 100, 100)  # 灰色占位图
            cv2.imwrite(output_path, img)
        
        return output_path