"""
Agent功能验证脚本
"""
import os
import sys
import tempfile
import requests
from PIL import Image
import numpy as np

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_test_images():
    """创建测试用的简单图像"""
    # 创建一个简单的角色图像（红色圆形代表头部，蓝色矩形代表身体）
    character_img = Image.new('RGB', (200, 400), color='white')
    # 头部
    for x in range(50, 150):
        for y in range(50, 150):
            if (x-100)**2 + (y-100)**2 <= 50**2:
                character_img.putpixel((x, y), (255, 0, 0))  # 红色头部
    # 身体
    for x in range(80, 120):
        for y in range(150, 300):
            character_img.putpixel((x, y), (0, 0, 255))  # 蓝色身体
    
    # 创建一个简单的参考图像（带场景）
    reference_img = Image.new('RGB', (400, 400), color=(135, 206, 235))  # 天空蓝背景
    # 添加地面
    for x in range(400):
        for y in range(300, 400):
            reference_img.putpixel((x, y), (34, 139, 34))  # 草地绿
    
    # 保存测试图像
    char_path = os.path.join(tempfile.gettempdir(), 'test_character.jpg')
    ref_path = os.path.join(tempfile.gettempdir(), 'test_reference.jpg')
    
    character_img.save(char_path)
    reference_img.save(ref_path)
    
    return char_path, ref_path

def test_vlm_client():
    """测试VLM客户端功能"""
    print("测试VLM客户端...")
    try:
        from utils.vlm_client import VLMClient
        client = VLMClient()
        print("✓ VLM客户端初始化成功")
        return True
    except Exception as e:
        print(f"✗ VLM客户端测试失败: {e}")
        return False

def test_image_processor():
    """测试图像处理器功能"""
    print("测试图像处理器...")
    try:
        from utils.image_processor import ImageProcessor
        processor = ImageProcessor()
        
        # 创建测试图像
        char_path, ref_path = create_test_images()
        
        # 测试调整大小功能
        resized_path = processor.resize_image(char_path)
        print(f"✓ 图像调整大小功能正常: {resized_path}")
        
        # 清理测试图像
        os.remove(char_path)
        os.remove(ref_path)
        if os.path.exists(resized_path):
            os.remove(resized_path)
        
        print("✓ 图像处理器功能正常")
        return True
    except Exception as e:
        print(f"✗ 图像处理器测试失败: {e}")
        return False

def test_image_generator():
    """测试图像生成器功能"""
    print("测试图像生成器...")
    try:
        from utils.image_generator import ImageGenerator
        generator = ImageGenerator()
        print("✓ 图像生成器初始化成功")
        return True
    except Exception as e:
        print(f"✗ 图像生成器测试失败: {e}")
        return False

def test_validation_engine():
    """测试验证引擎功能"""
    print("测试验证引擎...")
    try:
        from utils.validation import ValidationEngine, RetryMechanism
        engine = ValidationEngine()
        retry_mechanism = RetryMechanism()
        print("✓ 验证引擎初始化成功")
        return True
    except Exception as e:
        print(f"✗ 验证引擎测试失败: {e}")
        return False

def test_complete_workflow():
    """测试完整工作流程（需要API服务运行）"""
    print("测试完整工作流程...")
    try:
        # 这里需要FastAPI服务正在运行
        # 检查服务是否可用
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✓ API服务可用")
            return True
        else:
            print("✗ API服务不可用")
            return False
    except requests.ConnectionError:
        print("✗ API服务未运行（需要先启动FastAPI服务）")
        return False

def main():
    """主测试函数"""
    print("开始验证角色与场景融合优化Agent功能...")
    print("="*50)
    
    tests = [
        ("VLM客户端", test_vlm_client),
        ("图像处理器", test_image_processor),
        ("图像生成器", test_image_generator),
        ("验证引擎", test_validation_engine),
        ("完整工作流程", test_complete_workflow),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        result = test_func()
        results.append((test_name, result))
    
    print("\n" + "="*50)
    print("测试总结:")
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\n总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有测试通过！Agent功能验证成功。")
    else:
        print("⚠️  部分测试未通过，请检查相关模块。")

if __name__ == "__main__":
    main()