#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, validator, Field
from nonebot import get_driver

class PluginConfig(BaseModel):
    # 主人QQ号 (必须设置)
    master_qq: int = Field(0, description="机器人主人的QQ号")
    
    # 代理人QQ列表 (最多2个)
    agents: List[int] = Field([], description="代理人QQ列表，最多2个", max_items=2)
    
    # VIP用户列表
    vip_users: List[int] = Field([1055411737], description="VIP用户QQ列表")
    
    # 调试模式
    debug_mode: bool = Field(False, description="是否启用调试模式")
    
    # 权限申请模式
    permission_mode: bool = Field(False, description="是否启用权限申请模式")
    
    # 入群审核模式
    group_approve_mode: bool = Field(False, description="是否接管入群申请")
    
    # 关闭验证码
    shutdown_code: Optional[str] = Field(None, description="关闭验证码(8位16进制)")
    
    # 数据文件路径
    data_dir: Path = Field(Path(__file__).parent / "data", description="数据目录路径")
    
    # 验证主人QQ号
    @validator('master_qq')
    def validate_master_qq(cls, v):
        if v == 0:
            raise ValueError("主人QQ号不能为0，请在配置中设置")
        return v
    
    # 验证代理人数量
    @validator('agents')
    def validate_agents(cls, v):
        if len(v) > 2:
            raise ValueError("代理人数量不能超过2个")
        return v
    
    class Config:
        extra = "ignore"

class ConfigManager:
    def __init__(self):
        # 加载nonebot配置
        driver = get_driver()
        self.config = PluginConfig.parse_obj(driver.config.dict())
        
        # 确保数据目录存在
        self._ensure_data_dir()
        
        # 加载数据文件
        self._load_data_files()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        if not self.config.data_dir.exists():
            self.config.data_dir.mkdir(parents=True)
        
        # 初始化必要的数据文件
        required_files = {
            "blacklist.json": {"users": [], "words": []},
            "whitelist.json": {"users": []},
            "checkin_data.json": {},
            "blocked_words.json": [],
            "user_settings.json": {}
        }
        
        for filename, default_content in required_files.items():
            file_path = self.config.data_dir / filename
            if not file_path.exists():
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(default_content, f, ensure_ascii=False, indent=4)
    
    def _load_data_files(self):
        """加载数据文件到内存"""
        self.blacklist = self._load_json("blacklist.json")
        self.whitelist = self._load_json("whitelist.json")
        self.checkin_data = self._load_json("checkin_data.json")
        self.blocked_words = self._load_json("blocked_words.json")
        self.user_settings = self._load_json("user_settings.json")
    
    def _load_json(self, filename: str) -> Union[Dict, List]:
        """加载JSON文件"""
        file_path = self.config.data_dir / filename
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_json(self, filename: str, data: Union[Dict, List]):
        """保存JSON文件"""
        file_path = self.config.data_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    # 权限检查方法
    def is_master(self, user_id: int) -> bool:
        """检查是否是主人"""
        return user_id == self.config.master_qq
    
    def is_agent(self, user_id: int) -> bool:
        """检查是否是代理人"""
        return user_id in self.config.agents
    
    def is_admin(self, user_id: int) -> bool:
        """检查是否是主人或代理人"""
        return self.is_master(user_id) or self.is_agent(user_id)
    
    def is_vip(self, user_id: int) -> bool:
        """检查是否是VIP用户"""
        return user_id in self.config.vip_users
    
    # 黑名单管理
    def add_to_blacklist(self, user_id: int):
        """添加到黑名单"""
        if user_id not in self.blacklist["users"]:
            self.blacklist["users"].append(user_id)
            self._save_json("blacklist.json", self.blacklist)
    
    def remove_from_blacklist(self, user_id: int):
        """从黑名单移除"""
        if user_id in self.blacklist["users"]:
            self.blacklist["users"].remove(user_id)
            self._save_json("blacklist.json", self.blacklist)
    
    def is_blacklisted(self, user_id: int) -> bool:
        """检查是否在黑名单"""
        return user_id in self.blacklist["users"]
    
    # 白名单管理
    def add_to_whitelist(self, user_id: int):
        """添加到白名单"""
        if user_id not in self.whitelist["users"]:
            self.whitelist["users"].append(user_id)
            self._save_json("whitelist.json", self.whitelist)
    
    def remove_from_whitelist(self, user_id: int):
        """从白名单移除"""
        if user_id in self.whitelist["users"]:
            self.whitelist["users"].remove(user_id)
            self._save_json("whitelist.json", self.whitelist)
    
    def is_white