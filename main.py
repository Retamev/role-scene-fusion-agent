from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv
import tempfile
import shutil
from typing import Dict, Any, Optional
import asyncio

from utils.vlm_client import VLMClient
from utils.image_processor import ImageProcessor
from utils.image_generator import ImageGenerator
from utils.validation import ValidationEngine, RetryMechanism, ValidationResult

# 加载环境变量
load_dotenv()

app = FastAPI(
    title="角色与场景融合优化 Agent",
    description="通过前置处理解决角色与构图参考图不匹配的问题",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "角色与场景融合优化 Agent API"}

@app.post("/process")
async def process_images(
    character_image: UploadFile = File(...),
    reference_image: UploadFile = File(...),
    prompt: str = Form(None)
):
    """
    处理角色图和参考图，生成融合图像
    """
    # 创建临时目录存储上传的文件
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 保存上传的图片
        character_path = os.path.join(temp_dir, character_image.filename)
        reference_path = os.path.join(temp_dir, reference_image.filename)
        
        with open(character_path, "wb") as f:
            shutil.copyfileobj(character_image.file, f)
        
        with open(reference_path, "wb") as f:
            shutil.copyfileobj(reference_image.file, f)
        
        # 初始化各组件
        vlm_client = VLMClient()
        image_processor = ImageProcessor()
        image_generator = ImageGenerator()
        validation_engine = ValidationEngine()
        retry_mechanism = RetryMechanism()
        
        # 步骤1: Think - 分析参考图并提取结构化约束
        analysis_result = vlm_client.analyze_composition(reference_path)
        
        # 步骤2: Action - 图像预处理
        # 调整角色图以适应参考图的景别要求
        adjusted_character_path = image_processor.adjust_character_proportions(
            character_path, analysis_result
        )
        
        # 应用透视变换
        perspective_adjusted_path = image_processor.apply_perspective_transform(
            adjusted_character_path, analysis_result
        )
        
        # 创建适配后的参考图（对原人物进行遮罩处理）
        adapted_reference_path = image_processor.create_adapted_reference(
            reference_path, analysis_result
        )
        
        # 步骤3: 生成带权重的结构化Prompt
        if not prompt:
            prompt = "A detailed scene composition with character integration"
        
        structured_prompt = image_generator.construct_structured_prompt(
            scene_description=prompt,
            character_features="Character features from uploaded image",
            original_scene_weight=0.3,
            target_character_weight=0.7
        )
        
        # 步骤4: 生成图像
        params = {
            "scale_factor": 1.0,
            "target_character_weight": 0.7,
            "original_scene_weight": 0.3,
            "perspective_adjustment": 0.0
        }
        
        retry_count = 0
        generated_image_path = None
        
        while True:
            # 生成图像
            generated_image_path = image_generator.generate_image(
                prompt=structured_prompt,
                reference_image_path=adapted_reference_path,
                character_image_path=perspective_adjusted_path,
                width=1024,
                height=1024
            )
            
            # 验证生成结果
            validation_results = validation_engine.comprehensive_validation(
                generated_image_path, analysis_result, character_path
            )
            
            # 检查是否需要重试
            if not retry_mechanism.should_retry(validation_results, retry_count):
                break
            
            # 调整参数进行重试
            params = retry_mechanism.adjust_parameters_for_retry(
                params, validation_results, retry_count
            )
            
            # 更新prompt权重
            structured_prompt = image_generator.construct_structured_prompt(
                scene_description=prompt,
                character_features="Character features from uploaded image",
                original_scene_weight=params["original_scene_weight"],
                target_character_weight=params["target_character_weight"]
            )
            
            retry_count += 1
            
            if retry_count >= retry_mechanism.max_retries:
                break
        
        # 返回结果
        result = {
            "status": "success",
            "message": "图像处理完成",
            "analysis_result": analysis_result,
            "validation_results": {
                k: {"success": v.success, "score": v.score, "feedback": v.feedback}
                for k, v in validation_results.items()
            },
            "generated_image_path": generated_image_path,
            "retry_count": retry_count,
            "intermediate_files": {
                "adjusted_character_path": adjusted_character_path,
                "perspective_adjusted_path": perspective_adjusted_path,
                "adapted_reference_path": adapted_reference_path
            }
        }
        
        return result
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        # 清理临时文件
        try:
            shutil.rmtree(temp_dir)
        except:
            pass  # 忽略清理错误

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )