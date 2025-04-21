import socket

def check_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

# 检查端口是否被占用
port_5001_used = check_port(5001)
print(f"端口5001是否被占用: {port_5001_used}")

# 如果端口被占用，提供解决建议
if port_5001_used:
    print("建议: 端口5001已被占用，请尝试使用其他端口或停止占用该端口的应用")
else:
    print("端口5001可用，如果后端仍无法启动，请检查其他问题") 