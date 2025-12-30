import requests
import json
import base64
from typing import Dict, Any
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

class VLMClient:
    def __init__(self):
        self.base_url = os.getenv("BASE_URL")
        self.api_key = os.getenv("API_KEY")
        self.vlm_model = os.getenv("VLM_MODEL")
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def encode_image(self, image_path: str) -> str:
        """将图片编码为base64字符串"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def analyze_composition(self, reference_image_path: str) -> Dict[str, Any]:
        """
        分析构图参考图，提取结构化约束
        
        Args:
            reference_image_path: 构图参考图路径
            
        Returns:
            包含景别、关键点、透视、位姿等信息的字典
        """
        # 编码图片
        base64_image = self.encode_image(reference_image_path)
        
        # 构造消息
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text", 
                        "text": """请分析这张构图参考图，并严格按照以下JSON格式返回分析结果：

{
  "shot_type": "full_shot / medium_shot / closeup", // 景别判定
  "body_box": [x1, y1, x2, y2], // 占位人物边界框
  "keypoints": { 
    "l_ankle": [x,y], 
    "r_ankle": [x,y], 
    "nose": [x,y], 
    "hip": [x,y] 
  }, // 关键点坐标
  "perspective": { 
    "horizon_y": 0.5, // 地平线位置（相对于图片高度的比例）
    "is_slanted_ground": true // 是否为斜面地面
  }, 
  "pose_type": "standing / sitting / others" // 位姿判定
}

请确保返回有效的JSON格式，不要添加任何其他解释文本。"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
        
        # 发送请求
        payload = {
            "model": self.vlm_model,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 1024
        }
        
        response = requests.post(self.base_url, headers=self.headers, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"VLM API调用失败: {response.status_code} - {response.text}")
        
        # 解析响应
        result = response.json()
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        # 提取JSON部分
        try:
            # 查找JSON部分
            start_idx = content.find('{')
            end_idx = content.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = content[start_idx:end_idx]
                return json.loads(json_str)
            else:
                raise Exception(f"无法从响应中提取JSON: {content}")
        except json.JSONDecodeError:
            raise Exception(f"JSON解析失败: {content}")

    def validate_analysis_result(self, result: Dict[str, Any]) -> bool:
        """
        验证分析结果是否符合要求格式
        """
        required_keys = ["shot_type", "body_box", "keypoints", "perspective", "pose_type"]
        
        for key in required_keys:
            if key not in result:
                return False
        
        # 验证body_box格式
        if not isinstance(result["body_box"], list) or len(result["body_box"]) != 4:
            return False
        
        # 验证keypoints格式
        required_keypoints = ["l_ankle", "r_ankle", "nose", "hip"]
        for kp in required_keypoints:
            if kp not in result["keypoints"] or len(result["keypoints"][kp]) != 2:
                return False
        
        # 验证perspective格式
        if not isinstance(result["perspective"], dict) or "horizon_y" not in result["perspective"]:
            return False
        
        return True

# 测试用例
if __name__ == "__main__":
    client = VLMClient()
    # 示例调用（需要有实际图片路径）
    # result = client.analyze_composition("path/to/reference_image.jpg")
    # print(result)