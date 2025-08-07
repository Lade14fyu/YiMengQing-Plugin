#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field, validator
from ..config import config

class UserData(BaseModel):
    """用户核心数据模型"""
    user_id: int = Field(..., description="用户QQ号", gt=10000)
    nickname: str = Field("未知用户", description="用户昵称", max_length=30)
    join_date: datetime = Field(default_factory=datetime.now, description="首次记录时间")
    last_active: datetime = Field(default_factory=datetime.now, description="最后活跃时间")
    permissions: List[str] = Field(["basic"], description="权限列表")
    settings: Dict[str, Any] = Field({}, description="个性化设置")
    
    @validator('user_id')
    def validate_user_id(cls, v):
        if v < 10000:
            raise ValueError("无效的用户ID")
        return v

class CheckinRecord(BaseModel):
    """签到记录模型"""
    date: str = Field(..., description="签到日期(YYYY-MM-DD)")
    time: str = Field(..., description="签到时间(HH:MM:SS)")
    period: str = Field(..., description="时间段(morning/afternoon/night)")

class UserStats(BaseModel):
    """用户统计模型"""
    total_checkins: int = Field(0, description="累计签到次数")
    current_streak: int = Field(0, description="当前连续签到天数")
    max_streak: int = Field(0, description="历史最大连续签到")
    violation_count: int = Field(0, description="违规次数")

class UserModel:
    """用户数据操作类"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.data_path = config.data_dir / "users" / f"{user_id}.json"
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 初始化数据
        self.data = self._load_or_create()
        self.stats = self._load_stats()
    
    def _load_or_create(self) -> UserData:
        """加载或创建用户数据"""
        if self.data_path.exists():
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return UserData(**data)
        return UserData(user_id=self.user_id)
    
    def _load_stats(self) -> UserStats:
        """加载统计信息"""
        stats_path = self.data_path.with_name(f"{self.user_id}_stats.json")
        if stats_path.exists():
            with open(stats_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return UserStats(**data)
        return UserStats()
    
    def save(self):
        """保存用户数据"""
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(self.data.dict(), f, ensure_ascii=False, indent=4)
        
        stats_path = self.data_path.with_name(f"{self.user_id}_stats.json")
        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(self.stats.dict(), f, ensure_ascii=False, indent=4)
    
    def update_activity(self):
        """更新活跃时间"""
        self.data.last_active = datetime.now()
        self.save()
    
    def add_checkin_record(self, record: CheckinRecord):
        """添加签到记录"""
        # 计算连续签到
        today = datetime.now().date()
        last_date = datetime.strptime(record.date, "%Y-%m-%d").date()
        
        if (today - last_date).days == 1:
            self.stats.current_streak += 1
        else:
            self.stats.current_streak = 1
        
        # 更新最大连续签到
        if self.stats.current_streak > self.stats.max_streak:
            self.stats.max_streak = self.stats.current_streak
        
        # 更新总签到次数
        self.stats.total_checkins += 1
        
        self.save()
    
    def add_violation(self, reason: str):
        """添加违规记录"""
        self.stats.violation_count += 1
        
        # 添加到历史记录
        violation_path = self.data_path.with_name(f"{self.user_id}_violations.json")
        violations = []
        if violation_path.exists():
            with open(violation_path, "r", encoding="utf-8") as f:
                violations = json.load(f)
        
        violations.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "reason": reason
        })
        
        with open(violation_path, "w", encoding="utf-8") as f:
            json.dump(violations, f, ensure_ascii=False, indent=4)
        
        self.save()
    
    def is_vip(self) -> bool:
        """检查是否是VIP用户"""
        return self.user_id in config.config.vip_users
    
    def get_checkin_status(self) -> Dict[str, Any]:
        """获取签到状态"""
        return {
            "total": self.stats.total_checkins,
            "current_streak": self.stats.current_streak,
            "max_streak": self.stats.max_streak,
            "last_active": self.data.last_active
        }

# 示例使用
if __name__ == "__main__":
    # 初始化用户
    user = UserModel(123456789)
    
    # 更新签到记录
    record = CheckinRecord(
        date="2023-11-15",
        time="14:30:00",
        period="afternoon"
    )
    user.add_checkin_record(record)
    
    # 获取签到状态
    print(user.get_checkin_status())