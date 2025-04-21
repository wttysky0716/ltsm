import requests
import json

# 测试登录API
try:
    response = requests.post('http://localhost:5001/api/auth/login', json={"username": "admin", "password": "admin"})
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f"请求失败: {e}") 