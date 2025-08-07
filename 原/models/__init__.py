#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field
from datetime import datetime
from pathlib import Path
import json

class BaseDataModel(BaseModel):
    """基础数据模型"""
    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S"),
            Path: lambda v: str(v)
        }
        extra = "ignore"

    def save(self, file_path: Path):
        """保存模型到文件"""
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.dict(), f, ensure_ascii=False, indent=4)

    @classmethod
    def load(cls, file_path: Path):
        """从文件加载模型"""
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return cls(**data)
        return None

class UserModel(BaseDataModel):
    """用户数据模型"""
    user_id: int = Field(..., description="用户QQ号")
    nickname: str = Field("未知用户", description="用户昵称")
    checkin_days: int = Field(0, description="累计签到天数")
    last_checkin: Optional[datetime] = Field(None, description="最后签到时间")
    is_vip: bool = Field(False, description="是否是VIP用户")
    violation_count: int = Field(0, description="违规次数")
    settings: Dict[str, Any] = Field({}, description="用户个性化设置")

    def get_checkin_streak(self) -> int:
        """计算连续签到天数"""
        if not self.last_checkin:
            return 0
        today = datetime.now().date()
        last_date = self.last_checkin.date()
        return (today - last_date).days if today == last_date else 0

class GroupModel(BaseDataModel):
    """群组数据模型"""
    group_id: int = Field(..., description="群号")
    group_name: str = Field("未知群组", description="群名称")
    welcome_msg: str = Field("欢迎新人！", description="欢迎消息")
    admin_list: List[int] = Field([], description="管理员列表")
    settings: Dict[str, Any] = Field({}, description="群组设置")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")

    def add_admin(self, user_id: int):
        """添加管理员"""
        if user_id not in self.admin_list:
            self.admin_list.append(user_id)

    def remove_admin(self, user_id: int):
        """移除管理员"""
        if user_id in self.admin_list:
            self.admin_list.remove(user_id)

class PluginConfigModel(BaseDataModel):
    """插件配置模型"""
    version: str = Field("1.0.0", description="配置版本")
    data_dir: Path = Field(Path("data/yimengqing"), description="数据目录路径")
    log_level: str = Field("INFO", description="日志级别")
    enable_features: List[str] = Field(["checkin", "divination"], description="启用功能")

# 导出模型
__all__ = ["BaseDataModel", "UserModel", "GroupModel", "PluginConfigModel"]