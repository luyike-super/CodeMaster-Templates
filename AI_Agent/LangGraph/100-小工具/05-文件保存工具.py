import logging
from langchain_community.tools.file_management import WriteFileTool
# 优点带日志
# 日志工具类
# py项目通用找个
from .decorators import create_logged_tool

logger = logging.getLogger(__name__)

# Initialize file management tool with logging
LoggedWriteFile = create_logged_tool(WriteFileTool)
write_file_tool = LoggedWriteFile()







print("=========================日志工具类================================")
import logging
import functools
from typing import Any, Callable, Type, TypeVar, Optional, Union

logger = logging.getLogger(__name__)

T = TypeVar("T")

# 配置日志   logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def log_func(func: Callable = None, *, level: Union[int, str] = logging.DEBUG) -> Callable:
    """
    一个装饰器，用于记录工具函数的输入参数和输出。

    参数:
        func: 要被装饰的工具函数
        level: 日志级别，可以是int类型(如logging.DEBUG)或字符串类型(如'DEBUG')，默认为DEBUG级别

    返回:
        带有输入/输出日志记录的包装函数
    """
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # 记录输入参数
            func_name = fn.__name__
            params = ", ".join(
                [*(str(arg) for arg in args), *(f"{k}={v}" for k, v in kwargs.items())]
            )
            
            # 根据传入的level参数记录日志
            if isinstance(level, str):
                log_level = getattr(logging, level.upper(), logging.DEBUG)
            else:
                log_level = level
                
            logger.log(log_level, f"Tool {func_name} called with parameters: {params}")

            # 执行函数
            result = fn(*args, **kwargs)

            # 记录输出结果
            logger.log(log_level, f"Tool {func_name} returned: {result}")

            return result

        return wrapper
    
    # 支持直接装饰和带参数装饰两种方式
    if func is None:
        return decorator
    else:
        return decorator(func)


class LoggedToolMixin:
    """一个为任何工具添加日志功能的混入类。"""

    def _log_operation(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        """记录工具操作的辅助方法。"""
        tool_name = self.__class__.__name__.replace("Logged", "")
        params = ", ".join(
            [*(str(arg) for arg in args), *(f"{k}={v}" for k, v in kwargs.items())]
        )
        logger.debug(f"Tool {tool_name}.{method_name} called with parameters: {params}")

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """重写_run方法以添加日志记录。"""
        self._log_operation("_run", *args, **kwargs)
        result = super()._run(*args, **kwargs)
        logger.debug(
            f"Tool {self.__class__.__name__.replace('Logged', '')} returned: {result}"
        )
        return result

def create_logged_tool(base_tool_class: Type[T]) -> Type[T]:
    """
    Factory function to create a logged version of any tool class.

    Args:
        base_tool_class: The original tool class to be enhanced with logging

    Returns:
        A new class that inherits from both LoggedToolMixin and the base tool class
    """

    class LoggedTool(LoggedToolMixin, base_tool_class):
        pass

    # Set a more descriptive name for the class
    LoggedTool.__name__ = f"Logged{base_tool_class.__name__}"
    return LoggedTool
