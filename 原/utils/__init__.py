#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
怡梦卿插件工具包
集中提供各类实用功能函数
"""

from pathlib import Path
from typing import Any, Dict, Optional
import importlib
import sys

# 工具模块注册表
_utils_registry: Dict[str, Any] = {}

def _auto_import_utils():
    """自动导入utils目录下的所有模块"""
    utils_dir = Path(__file__).parent
    for py_file in utils_dir.glob("*.py"):
        if py_file.name.startswith("_") or py_file.name == "__init__.py":
            continue
        
        module_name = f".{py_file.stem}"
        module = importlib.import_module(module_name, package="plugins.yimengqing.utils")
        
        # 注册模块中的工具函数
        for attr_name in dir(module):
            if not attr_name.startswith("_"):
                _utils_registry[attr_name] = getattr(module, attr_name)

# 自动导入工具模块
_auto_import_utils()

def get_util(name: str) -> Any:
    """获取工具函数"""
    if name not in _utils_registry:
        raise ValueError(f"工具函数未注册: {name}")
    return _utils_registry[name]

# 将工具函数暴露到模块命名空间
globals().update(_utils_registry)

# 导出接口
__all__ = list(_utils_registry.keys()) + ['get_util']

# 版本兼容检查
if sys.version_info < (3, 8):
    raise RuntimeError("怡梦卿插件需要Python 3.8或更高版本")

# 初始化日志
import logging
logging.getLogger('yimengqing.utils').info('工具模块初始化完成')