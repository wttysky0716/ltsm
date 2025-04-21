import os
import sys
import subprocess
import time
import platform
import webbrowser
from pathlib import Path

def is_windows():
    return platform.system().lower() == 'windows'

def get_python_executable():
    """获取当前Python解释器路径"""
    return sys.executable

def is_dependency_installed(dependency, directory):
    """检查依赖是否已安装"""
    if dependency == 'python':
        try:
            # 尝试导入Flask
            import flask
            return True
        except ImportError:
            return False
    elif dependency == 'node':
        # 检查node_modules目录是否存在
        node_modules = Path(directory) / 'node_modules'
        return node_modules.exists()
    return False

def install_dependencies():
    """安装必要的依赖"""
    print("正在检查后端依赖...")
    if not is_dependency_installed('python', 'backend'):
        print("正在安装后端依赖...")
        backend_cmd = [get_python_executable(), '-m', 'pip', 'install', '-r', 'backend/requirements.txt']
        subprocess.run(backend_cmd, check=True)
    else:
        print("后端依赖已安装")

    print("正在检查前端依赖...")
    if not is_dependency_installed('node', 'frontend'):
        print("正在安装前端依赖...")
        # 切换到前端目录
        os.chdir('frontend')
        try:
            if is_windows():
                subprocess.run(['npm.cmd', 'install'], check=True)
            else:
                subprocess.run(['npm', 'install'], check=True)
        except subprocess.CalledProcessError:
            print("前端依赖安装失败，请手动执行 'cd frontend && npm install'")
        finally:
            # 切回根目录
            os.chdir('..')
    else:
        print("前端依赖已安装")

def start_backend():
    """启动后端服务"""
    print("正在启动后端服务...")
    # 使用非调试模式启动后端
    if is_windows():
        # 在Windows上使用waitress作为生产服务器
        return subprocess.Popen([get_python_executable(), 'backend/app.py'])
    else:
        # 在Linux/Mac上使用gunicorn作为生产服务器
        return subprocess.Popen([get_python_executable(), 'backend/app.py'])

def start_frontend():
    """启动前端服务"""
    print("正在启动前端服务...")
    # 切换到前端目录
    os.chdir('frontend')
    
    if is_windows():
        process = subprocess.Popen(['npm.cmd', 'run', 'serve'])
    else:
        process = subprocess.Popen(['npm', 'run', 'serve'])
    
    # 切回根目录
    os.chdir('..')
    return process

def open_browser():
    """在浏览器中打开应用"""
    print("正在打开浏览器...")
    time.sleep(5)  # 等待服务启动
    webbrowser.open('http://localhost:8080')

if __name__ == "__main__":
    print("=== 日志态势感知分析系统启动脚本 ===")
    
    # 检查并安装依赖
    install_dependencies()
    
    # 启动服务
    backend_process = start_backend()
    frontend_process = start_frontend()
    
    # 打开浏览器
    open_browser()
    
    print("\n=== 系统已启动 ===")
    print("前端地址: http://localhost:8080")
    print("后端API地址: http://localhost:5000")
    print("\n要停止服务，请按 Ctrl+C")
    
    try:
        # 保持脚本运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在关闭服务...")
        backend_process.terminate()
        frontend_process.terminate()
        print("服务已关闭") 