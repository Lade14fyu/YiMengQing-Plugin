#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
怡梦卿插件服务层初始化
集中管理所有服务模块的导入和初始化
"""

import importlib
from pathlib import Path
from typing import Dict, Type, Any
from ..config import config

# 服务注册表
_service_registry: Dict[str, Any] = {}

def _auto_import_services():
    """自动导入services目录下的所有模块"""
    services_dir = Path(__file__).parent
    for py_file in services_dir.glob("*.py"):
        if py_file.name.startswith("_") or py_file.name == "__init__.py":
            continue
        
        module_name = f".{py_file.stem}"
        module = importlib.import_module(module_name, package="plugins.yimengqing.services")
        
        # 查找并注册服务类（命名规则：*Service）
        for attr_name in dir(module):
            if attr_name.endswith("Service"):
                service_class = getattr(module, attr_name)
                if hasattr(service_class, "service_name"):
                    _service_registry[service_class.service_name] = service_class()

# 自动导入服务
_auto_import_services()

def get_service(service_name: str) -> Any:
    """获取指定服务实例"""
    if service_name not in _service_registry:
        raise ValueError(f"服务未注册: {service_name}")
    return _service_registry[service_name]

def init_services():
    """初始化所有服务"""
    for service in _service_registry.values():
        if hasattr(service, "initialize"):
            service.initialize(config)

# 导出接口
__all__ = [
    'get_service',
    'init_services'
]

# 服务初始化
init_services()