import asyncio
import base64
import sys
sys.path.insert(0, '.')

from app.services.ocr_service import ocr_service
from app.config import settings

async def test():
    print(f"APP_ID: {settings.XFYUN_APP_ID}")
    print(f"API_URL: {ocr_service.API_URL}")
    
    # 测试一个简单的PDF文件
    test_data = b"%PDF-1.4 test"
    try:
        result = await ocr_service.recognize_pdf(test_data, "test.pdf")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test())
