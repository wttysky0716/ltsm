import os
import sys

# 直接运行后端应用并显示输出
print("手动启动后端应用...")

# 使用Python解释器运行后端应用
python_executable = sys.executable
result = os.system(f"{python_executable} backend/simple_app.py")

# 输出返回码
print(f"后端应用退出，返回码: {result}") 