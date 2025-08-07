#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator
from ..config import config

class GroupSettings(BaseModel):
    """群组设置模型"""
    welcome_msg: str = Field(
        "欢迎新人入群！请遵守群规~",
        description="欢迎消息模板"
    )
    checkin_enabled: bool = Field(True, description="是否启用签到功能")
    divination_enabled: bool = Field(True, description="是否启用占卜功能")
    admin_roles: List[str] = Field(
        ["owner", "admin", "moderator"],
        description="管理员角色列表"
    )
    custom_commands: Dict[str, str] = Field(
        {},
        description="自定义命令响应"
    )

class GroupMember(BaseModel):
    """群成员模型"""
    user_id: int = Field(..., description="成员QQ号")
    nickname: str = Field("", description="群内昵称")
    join_time: datetime = Field(..., description="入群时间")
    last_speak: Optional[datetime] = Field(None, description="最后发言时间")
    role: str = Field("member", description="成员角色")

class GroupModel:
    """群组数据操作类"""

    def __init__(self, group_id: int):
        self.group_id = group_id
        self.data_dir = config.data_dir / "groups" / str(group_id)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 核心数据文件
        self.settings_file = self.data_dir / "settings.json"
        self.members_file = self.data_dir / "members.json"
        self.blacklist_file = self.data_dir / "blacklist.json"
        
        # 初始化数据
        self.settings = self._load_settings()
        self.members = self._load_members()
        self.blacklist = self._load_blacklist()

    def _load_settings(self) -> GroupSettings:
        """加载群设置"""
        if self.settings_file.exists():
            with open(self.settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return GroupSettings(**data)
        return GroupSettings()

    def _load_members(self) -> Dict[int, GroupMember]:
        """加载成员数据"""
        if self.members_file.exists():
            with open(self.members_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {int(k): GroupMember(**v) for k, v in data.items()}
        return {}

    def _load_blacklist(self) -> List[int]:
        """加载黑名单"""
        if self.blacklist_file.exists():
            with open(self.blacklist_file, "r", encoding="utf-8") as f:
                return json.load(f).get("users", [])
        return []

    def save_settings(self):
        """保存群设置"""
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(self.settings.dict(), f, ensure_ascii=False, indent=4)

    def save_members(self):
        """保存成员数据"""
        with open(self.members_file, "w", encoding="utf-8") as f:
            data = {k: v.dict() for k, v in self.members.items()}
            json.dump(data, f, ensure_ascii=False, indent=4)

    def save_blacklist(self):
        """保存黑名单"""
        with open(self.blacklist_file, "w", encoding="utf-8") as f:
            json.dump({"users": self.blacklist}, f, ensure_ascii=False, indent=4)

    def update_member(self, user_id: int, nickname: str = "", role: str = "member"):
        """更新成员信息"""
        now = datetime.now()
        
        if user_id in self.members:
            self.members[user_id].nickname = nickname or self.members[user_id].nickname
            self.members[user_id].role = role
            self.members[user_id].last_speak = now
        else:
            self.members[user_id] = GroupMember(
                user_id=user_id,
                nickname=nickname,
                join_time=now,
                last_speak=now,
                role=role
            )
        
        self.save_members()

    def remove_member(self, user_id: int):
        """移除成员"""
        if user_id in self.members:
            del self.members[user_id]
            self.save_members()

    def add_to_blacklist(self, user_id: int):
        """添加到黑名单"""
        if user_id not in self.blacklist:
            self.blacklist.append(user_id)
            self.save_blacklist()
            self.remove_member(user_id)

    def remove_from_blacklist(self, user_id: int):
        """从黑名单移除"""
        if user_id in self.blacklist:
            self.blacklist.remove(user_id)
            self.save_blacklist()

    def is_banned(self, user_id: int) -> bool:
        """检查是否在黑名单"""
        return user_id in self.blacklist

    def get_welcome_message(self) -> str:
        """获取欢迎消息"""
        return self.settings.welcome_msg

    def set_welcome_message(self, message: str):
        """设置欢迎消息"""
        self.settings.welcome_msg = message
        self.save_settings()

    def get_active_members(self, days: int = 7) -> List[Dict]:
        """获取活跃成员列表"""
        cutoff = datetime.now() - timedelta(days=days)
        return [
            {
                "user_id": m.user_id,
                "nickname": m.nickname,
                "last_active": m.last_speak
            }
            for m in self.members.values()
            if m.last_speak and m.last_speak >= cutoff
        ]

    def get_admin_ids(self) -> List[int]:
        """获取管理员ID列表"""
        return [
            user_id for user_id, member in self.members.items()
            if member.role in self.settings.admin_roles
        ]

# 示例使用
if __name__ == "__main__":
    # 初始化群组
    group = GroupModel(123456)
    
    # 更新成员
    group.update_member(987654321, nickname="测试用户", role="member")
    
    # 设置欢迎消息
    group.set_welcome_message("欢迎加入我们的交流群！")
    
    # 获取管理员列表
    admins = group.get_admin_ids()
    print(f"群管理员: {admins}")