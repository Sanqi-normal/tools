import http.server
import socketserver
import os
import cgi
from urllib.parse import urljoin
import socket

# 配置参数
PORT = 8000  # 本地服务器端口
DIRECTORY = "uploads"  # 存储上传文件的目录

# 确保上传目录存在并可写入
def ensure_directory():
    try:
        if not os.path.exists(DIRECTORY):
            os.makedirs(DIRECTORY)
        # 测试写入权限
        test_file = os.path.join(DIRECTORY, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        os.remove(test_file)
    except PermissionError:
        raise Exception(f"没有权限在 {os.getcwd()} 创建或写入 {DIRECTORY} 目录")
    except Exception as e:
        raise Exception(f"创建目录 {DIRECTORY} 失败: {str(e)}")

# 获取本地 IP 地址
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

LOCAL_IP = get_local_ip()
BASE_URL = f"http://{LOCAL_IP}:{PORT}/{DIRECTORY}/"

# 自定义请求处理类
class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            html = """
            <html>
                <body>
                    <h2>上传文件</h2>
                    <form enctype="multipart/form-data" method="post">
                        <input type="file" name="file">
                        <input type="submit" value="上传">
                    </form>
                </body>
            </html>
            """
            self.wfile.write(html.encode('utf-8'))
        else:
            super().do_GET()

    def do_POST(self):
        try:
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD': 'POST'}
            )
            if "file" not in form:
                self.send_error(400, "没有选择文件")
                return

            file_item = form["file"]
            filename = os.path.basename(file_item.filename)
            if not filename:
                self.send_error(400, "文件名为空")
                return

            file_path = os.path.join(DIRECTORY, filename)
            with open(file_path, 'wb') as f:
                f.write(file_item.file.read())

            file_url = urljoin(BASE_URL, filename)
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            response = f"""
            <html>
                <body>
                    <h2>文件上传成功！</h2>
                    <p>访问链接: <a href="{file_url}">{file_url}</a></p>
                    <a href="/">返回上传页面</a>
                </body>
            </html>
            """
            self.wfile.write(response.encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"上传失败: {str(e)}")

# 设置服务器
Handler = CustomHandler
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 启动前检查目录
try:
    ensure_directory()
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"服务器运行在: http://{LOCAL_IP}:{PORT}")
        print("按 Ctrl+C 退出")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n服务器已关闭")
            httpd.server_close()
except Exception as e:
    print(f"启动失败: {str(e)}")
