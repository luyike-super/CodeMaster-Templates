import logging
import subprocess
from typing import Annotated
from langchain_core.tools import tool


# 初始化日志记录器
logger = logging.getLogger(__name__)


@tool
def bash_tool(
    cmd: Annotated[str, "要执行的bash命令。"],
):
    """使用此工具执行bash命令并进行必要的操作。"""
    logger.info(f"Executing Bash Command: {cmd}")
    try:
        # 执行命令并捕获输出
        result = subprocess.run(
            cmd, shell=True, check=True, text=True, capture_output=True
        )
        # 返回标准输出作为结果
        return result.stdout
    except subprocess.CalledProcessError as e:
        # 如果命令失败，返回错误信息
        error_message = f"Command failed with exit code {e.returncode}.\nStdout: {e.stdout}\nStderr: {e.stderr}"
        logger.error(error_message)
        return error_message
    except Exception as e:
        # 捕获任何其他异常
        error_message = f"Error executing command: {str(e)}"
        logger.error(error_message)
        return error_message


if __name__ == "__main__":
    print(bash_tool.invoke("dir"))
