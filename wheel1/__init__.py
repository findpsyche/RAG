"""
Wheel系统 - 初始化文件
"""

# 版本信息
__version__ = "1.0.0"
__author__ = "Wheel Team"
__email__ = "team@wheel.ai"

# 导出核心类
from wheel1 import WheelSystem, WheelSystemConfig
from core.modes import ProcessingMode, ModeConfig

__all__ = [
    "WheelSystem",
    "WheelSystemConfig",
    "ProcessingMode",
    "ModeConfig",
]
