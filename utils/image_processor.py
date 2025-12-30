import cv2
import numpy as np
from PIL import Image
import os
from typing import Dict, Tuple, List, Any
import math

class ImageProcessor:
    def __init__(self):
        pass

    def resize_image(self, image_path: str, max_size: int = 1024) -> str:
        """
        调整图片大小，保持宽高比，最长边不超过max_size
        """
        img = cv2.imread(image_path)
        h, w = img.shape[:2]
        
        # 计算缩放比例
        scale = min(max_size / w, max_size / h, 1.0)
        new_w, new_h = int(w * scale), int(h * scale)
        
        # 调整图片大小
        resized_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        # 生成输出路径
        dir_path, file_name = os.path.split(image_path)
        name, ext = os.path.splitext(file_name)
        output_path = os.path.join(dir_path, f"{name}_resized{ext}")
        
        cv2.imwrite(output_path, resized_img)
        return output_path

    def outpaint_image(self, image_path: str, target_size: Tuple[int, int], 
                      position: str = "bottom") -> str:
        """
        扩图功能 - 在图片边缘扩展背景
        """
        img = cv2.imread(image_path)
        h, w = img.shape[:2]
        target_w, target_h = target_size
        
        # 计算需要扩展的尺寸
        if position == "bottom":
            # 向下扩展，保持上部内容
            new_img = np.zeros((target_h, target_w, 3), dtype=np.uint8)
            new_img[:] = (255, 255, 255)  # 白色背景
            new_img[:h, :w] = img
        elif position == "center":
            # 居中放置，四周扩展
            new_img = np.zeros((target_h, target_w, 3), dtype=np.uint8)
            new_img[:] = (255, 255, 255)  # 白色背景
            start_y = (target_h - h) // 2
            start_x = (target_w - w) // 2
            new_img[start_y:start_y+h, start_x:start_x+w] = img
        else:
            # 默认扩展方式
            new_img = np.zeros((target_h, target_w, 3), dtype=np.uint8)
            new_img[:] = (255, 255, 255)  # 白色背景
            new_img[:h, :w] = img
            
        # 生成输出路径
        dir_path, file_name = os.path.split(image_path)
        name, ext = os.path.splitext(file_name)
        output_path = os.path.join(dir_path, f"{name}_outpainted{ext}")
        
        cv2.imwrite(output_path, new_img)
        return output_path

    def crop_image(self, image_path: str, crop_box: Tuple[int, int, int, int]) -> str:
        """
        根据边界框裁切图片
        """
        img = cv2.imread(image_path)
        x1, y1, x2, y2 = crop_box
        
        # 确保边界框在图片范围内
        h, w = img.shape[:2]
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(w, x2)
        y2 = min(h, y2)
        
        cropped_img = img[y1:y2, x1:x2]
        
        # 生成输出路径
        dir_path, file_name = os.path.split(image_path)
        name, ext = os.path.splitext(file_name)
        output_path = os.path.join(dir_path, f"{name}_cropped{ext}")
        
        cv2.imwrite(output_path, cropped_img)
        return output_path

    def apply_perspective_transform(self, image_path: str, analysis_result: Dict[str, Any]) -> str:
        """
        应用透视变换，根据分析结果调整角色图的透视
        """
        img = cv2.imread(image_path)
        h, w = img.shape[:2]
        
        # 获取透视信息
        perspective = analysis_result.get("perspective", {})
        horizon_y = perspective.get("horizon_y", 0.5)
        is_slanted_ground = perspective.get("is_slanted_ground", False)
        
        # 计算缩放比例 S
        # 这里简化处理，实际应用中需要更精确的计算
        target_horizon_y = int(h * horizon_y)
        original_center_y = h // 2
        
        # 根据地平线位置调整缩放
        if original_center_y > target_horizon_y:
            # 角色在地平线以下，需要根据距离调整大小
            scale_factor = max(0.5, min(1.5, (h - original_center_y) / (h - target_horizon_y)))
        else:
            scale_factor = 1.0
        
        # 应用缩放
        new_w, new_h = int(w * scale_factor), int(h * scale_factor)
        scaled_img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        # 如果是斜面地面，应用仿射变换
        if is_slanted_ground:
            # 定义变换点，模拟斜面效果
            # 这里简化处理，实际应用中需要根据具体地面倾斜角度计算
            center_x, center_y = new_w // 2, new_h // 2
            
            # 创建仿射变换矩阵（简单模拟倾斜效果）
            pts1 = np.float32([[0, 0], [new_w, 0], [0, new_h]])
            # 简单倾斜变换，底部向一侧偏移
            offset = int(new_w * 0.1)  # 10%的偏移
            pts2 = np.float32([[0, 0], [new_w, 0], [offset, new_h]])
            
            matrix = cv2.getAffineTransform(pts1, pts2)
            scaled_img = cv2.warpAffine(scaled_img, matrix, (new_w, new_h))
        
        # 生成输出路径
        dir_path, file_name = os.path.split(image_path)
        name, ext = os.path.splitext(file_name)
        output_path = os.path.join(dir_path, f"{name}_perspective_adjusted{ext}")
        
        cv2.imwrite(output_path, scaled_img)
        return output_path

    def apply_character_mask(self, reference_image_path: str, body_box: List[int]) -> str:
        """
        对参考图中的原人物应用遮罩和高斯模糊，实现语义特征隔离
        """
        img = cv2.imread(reference_image_path)
        
        # 提取人物区域
        x1, y1, x2, y2 = body_box
        h, w = img.shape[:2]
        
        # 确保边界框在图片范围内
        x1 = max(0, x1)
        y1 = max(0, y1)
        x2 = min(w, x2)
        y2 = min(h, y2)
        
        # 对人物区域应用高斯模糊
        face_region = img[y1:y2, x1:x2]
        blurred_region = cv2.GaussianBlur(face_region, (99, 99), 30)
        
        # 将模糊区域放回原图
        img[y1:y2, x1:x2] = blurred_region
        
        # 生成输出路径
        dir_path, file_name = os.path.split(reference_image_path)
        name, ext = os.path.splitext(file_name)
        output_path = os.path.join(dir_path, f"{name}_masked{ext}")
        
        cv2.imwrite(output_path, img)
        return output_path

    def adjust_character_proportions(self, character_image_path: str, analysis_result: Dict[str, Any]) -> str:
        """
        根据分析结果调整角色图的部位完整度
        """
        shot_type = analysis_result.get("shot_type", "medium_shot")
        keypoints = analysis_result.get("keypoints", {})
        
        # 检查角色图是否缺少脚部（用于判断是否需要扩图）
        character_img = cv2.imread(character_image_path)
        char_h, char_w = character_img.shape[:2]
        
        # 检查是否缺少脚部
        ankles_present = False
        if "l_ankle" in keypoints and "r_ankle" in keypoints:
            l_ankle = keypoints["l_ankle"]
            r_ankle = keypoints["r_ankle"]
            # 如果脚踝坐标在参考图中存在，检查角色图是否需要扩展
            if l_ankle and r_ankle:
                # 简单判断：如果角色图高度小于参考图中人物的脚部位置，则需要扩图
                avg_ankle_y = (l_ankle[1] + r_ankle[1]) / 2
                # 这里假设参考图和角色图的比例关系
                # 实际应用中需要更精确的尺寸对比
                ankles_present = True
        
        if shot_type == "full_shot" and not ankles_present:
            # 需要扩图补全腿部
            # 这里简化处理，实际应用中需要更精确的判断
            target_h = int(char_h * 1.5)  # 假设需要增加50%的高度
            target_w = char_w
            return self.outpaint_image(character_image_path, (target_w, target_h), position="bottom")
        elif shot_type == "closeup":
            # 需要裁切为特写
            nose_pos = keypoints.get("nose", [char_w//2, char_h//3])
            center_x, center_y = nose_pos[0], nose_pos[1]
            
            # 计算裁切区域，以鼻子为中心
            crop_size = min(char_w, char_h) // 2
            x1 = max(0, center_x - crop_size//2)
            y1 = max(0, center_y - crop_size//2)
            x2 = min(char_w, x1 + crop_size)
            y2 = min(char_h, y1 + crop_size)
            
            return self.crop_image(character_image_path, (x1, y1, x2, y2))
        else:
            # 中景或其他情况，可能需要轻微调整
            return character_image_path

    def create_adapted_reference(self, reference_image_path: str, analysis_result: Dict[str, Any]) -> str:
        """
        创建适配后的参考图，对原人物进行遮罩处理
        """
        body_box = analysis_result.get("body_box", [0, 0, 100, 100])
        return self.apply_character_mask(reference_image_path, body_box)