import os
import sys

# 更改工作目录到脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# 添加backend目录到系统路径
sys.path.append('backend')

# 直接运行后端app
os.system(f"{sys.executable} backend/app.py") 