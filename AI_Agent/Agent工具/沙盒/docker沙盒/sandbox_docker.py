import docker
import os
import tempfile
import time
import sys

class DockerSandboxConfig:
    """Docker沙盒配置类，包含所有可配置参数"""
    def __init__(self, 
                 image="python:3.10-slim",            # 使用的Docker镜像
                 temp_file_name="temp_code.py",      # 临时文件名
                 container_path="/code",             # 容器内代码路径
                 command_prefix="python",            # 执行代码的命令
                 mem_limit="100m",                   # 内存限制
                 cpu_quota=50000,                    # CPU限制（相当于0.5个核心）
                 mount_mode="ro",                    # 挂载模式（ro=只读）
                 default_timeout=10,                 # 默认执行超时时间(秒)
                 polling_interval=0.5                # 轮询容器状态的间隔(秒)
                ):
        self.image = image
        self.temp_file_name = temp_file_name
        self.container_path = container_path
        self.command_prefix = command_prefix
        self.mem_limit = mem_limit
        self.cpu_quota = cpu_quota
        self.mount_mode = mount_mode
        self.default_timeout = default_timeout
        self.polling_interval = polling_interval


class DockerSandbox:
    """Docker沙盒执行类，用于在隔离的Docker环境中执行代码"""
    def __init__(self, config=None):
        """初始化Docker沙盒
        
        Args:
            config: DockerSandboxConfig对象，如果为None则使用默认配置
        """
        self.config = config or DockerSandboxConfig()
    
    def is_docker_running(self):
        """检查Docker是否正在运行
        
        Returns:
            bool: Docker是否运行中
        """
        try:
            client = docker.from_env()
            client.ping()
            return True
        except Exception:
            return False
    
    def run(self, code_string, timeout=None):
        """在Docker容器中运行代码
        
        Args:
            code_string: 要执行的Python代码字符串
            timeout: 执行超时时间(秒)，如不指定则使用配置中的默认值
            
        Returns:
            str: 执行结果或错误信息
        """
        # 使用配置中的默认超时时间（如果未指定）
        timeout = timeout if timeout is not None else self.config.default_timeout
        
        # 首先检查Docker是否在运行
        if not self.is_docker_running():
            return "错误：Docker未运行，请启动Docker Desktop后再试"
        
        client = None
        try:
            client = docker.from_env()
        except docker.errors.DockerException as e:
            error_msg = str(e)
            if "Error while fetching server API version" in error_msg:
                return "错误：无法连接到Docker守护进程，请确保Docker Desktop已启动并正在运行"
            return f"Docker连接错误：{error_msg}"
        
        # 创建临时文件
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, self.config.temp_file_name)
        
        try:
            # 写入代码到临时文件
            with open(temp_file_path, 'w', encoding='utf-8') as f:
                f.write(code_string)
            
            # 获取临时文件的绝对路径
            abs_temp_dir = os.path.abspath(temp_dir)
            
            # 构建容器命令
            command = f"{self.config.command_prefix} {self.config.container_path}/{self.config.temp_file_name}"
            
            # 运行容器，挂载临时文件
            container = client.containers.run(
                self.config.image,
                command=command,
                volumes={abs_temp_dir: {'bind': self.config.container_path, 'mode': self.config.mount_mode}},
                mem_limit=self.config.mem_limit,
                cpu_quota=self.config.cpu_quota,
                detach=True,
                remove=False  # 暂时不移除，方便获取日志
            )
            
            # 等待容器执行完毕，设置超时
            start_time = time.time()
            status = None
            
            while time.time() - start_time < timeout:
                container.reload()
                status = container.status
                if status != 'running':
                    break
                time.sleep(self.config.polling_interval)
            
            # 如果容器仍在运行，强制停止
            if status == 'running':
                container.stop()
                return "执行超时，已强制停止"
            
            # 获取输出
            output = container.logs().decode('utf-8')
            
            # 清理容器
            container.remove()
            
            return output
        
        except docker.errors.ImageNotFound:
            return f"错误：未找到Docker镜像，请确保已下载{self.config.image}镜像"
        except docker.errors.APIError as e:
            return f"Docker API错误：{str(e)}"
        except Exception as e:
            return f"执行错误：{str(e)}"
        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)


# 为了保持向后兼容，提供与原始API相同的函数
def is_docker_running():
    """检查Docker是否正在运行"""
    sandbox = DockerSandbox()
    return sandbox.is_docker_running()

def run_in_docker(code_string, timeout=None):
    """在Docker容器中运行代码（兼容旧API）"""
    sandbox = DockerSandbox()
    return sandbox.run(code_string, timeout)


if __name__ == "__main__":
    if not is_docker_running():
        print("错误：Docker未运行，请启动Docker Desktop后再试")
        sys.exit(1)
        
    # 使用默认配置
    sandbox = DockerSandbox()
    
    # 示例：自定义配置
    # custom_config = DockerSandboxConfig(
    #     image="python:3.11-slim", 
    #     mem_limit="200m",
    #     cpu_quota=100000  # 1个CPU核心
    # )
    # sandbox = DockerSandbox(custom_config)
    
    code_string = """
import os
import sys

print("Hello, Docker!")
print(f"Python版本: {sys.version}")
print(f"当前工作目录: {os.getcwd()}")
print(f"目录内容: {os.listdir('/')}")
print(f"Code目录内容: {os.listdir('/code')}")
"""
    print(sandbox.run(code_string)) 