#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict
import pytz

# 时区配置
BEIJING = pytz.timezone('Asia/Shanghai')

def get_current_time() -> str:
    """获取当前北京时间（字符串格式）
    
    Returns:
        str: 格式化的时间字符串，如"2023-11-15 14:30:00"
    """
    return datetime.now(BEIJING).strftime("%Y-%m-%d %H:%M:%S")

def get_current_date() -> str:
    """获取当前北京日期
    
    Returns:
        str: 格式化的日期字符串，如"2023-11-15"
    """
    return datetime.now(BEIJING).strftime("%Y-%m-%d")

def get_time_period() -> str:
    """获取当前时间段（北京时间）
    
    Returns:
        str: 
            "morning"   - 早上 (5:00-12:00)
            "afternoon" - 下午 (12:00-20:00) 
            "night"     - 晚上 (20:00-5:00)
    """
    now = datetime.now(BEIJING)
    hour = now.hour
    
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 20:
        return "afternoon"
    else:
        return "night"

def format_timestamp(timestamp: float) -> str:
    """格式化时间戳为北京时间
    
    Args:
        timestamp: Unix时间戳
        
    Returns:
        str: 格式化的时间字符串
    """
    return datetime.fromtimestamp(timestamp, BEIJING).strftime("%Y-%m-%d %H:%M:%S")

def parse_time_str(time_str: str) -> Optional[datetime]:
    """解析时间字符串为datetime对象（自动补全日期）
    
    Args:
        time_str: 时间字符串，支持格式：
            "14:30"     -> 当天14:30
            "2023-11-15 14:30:00" -> 完整时间
            
    Returns:
        datetime: 对应的datetime对象（北京时区）
        None: 如果解析失败
    """
    try:
        # 尝试解析完整时间
        if " " in time_str:
            return datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=BEIJING)
        
        # 仅时间格式，补全为当天
        today = datetime.now(BEIJING).date()
        time_part = datetime.strptime(time_str, "%H:%M").time()
        return datetime.combine(today, time_part).replace(tzinfo=BEIJING)
    except ValueError:
        return None

def get_time_delta(start: datetime, end: datetime) -> Dict[str, int]:
    """计算两个时间的差值
    
    Args:
        start: 开始时间
        end: 结束时间
        
    Returns:
        dict: 包含差值各部分，如
            {"days": 1, "hours": 2, "minutes": 30}
    """
    delta = end - start if end > start else start - end
    return {
        "days": delta.days,
        "hours": delta.seconds // 3600,
        "minutes": (delta.seconds % 3600) // 60,
        "seconds": delta.seconds % 60
    }

def is_same_day(time1: datetime, time2: datetime) -> bool:
    """检查两个时间是否在同一天（北京时区）
    
    Args:
        time1: 第一个时间
        time2: 第二个时间
        
    Returns:
        bool: 是否同一天
    """
    return time1.astimezone(BEIJING).date() == time2.astimezone(BEIJING).date()

def get_next_time(target_time: str) -> datetime:
    """获取下一个指定时间点的datetime对象
    
    Args:
        target_time: 目标时间字符串，如"14:30"
        
    Returns:
        datetime: 下一个到达该时间的时间点
    """
    now = datetime.now(BEIJING)
    target = parse_time_str(target_time)
    
    if not target:
        raise ValueError(f"无效的时间格式: {target_time}")
    
    # 如果今天的时间已过，则取明天
    if now.time() > target.time():
        target += timedelta(days=1)
    
    return target

def humanize_time(dt: datetime) -> str:
    """将时间转换为人类可读的相对时间描述
    
    Args:
        dt: 目标时间
        
    Returns:
        str: 如"5分钟前", "2小时前", "昨天", "3天前"等
    """
    now = datetime.now(BEIJING)
    delta = now - dt if now > dt else dt - now
    
    if delta.days > 7:
        return dt.strftime("%Y-%m-%d")
    elif delta.days > 1:
        return f"{delta.days}天前"
    elif delta.days == 1:
        return "昨天"
    elif delta.seconds >= 3600:
        return f"{delta.seconds // 3600}小时前"
    elif delta.seconds >= 60:
        return f"{delta.seconds // 60}分钟前"
    else:
        return "刚刚"

# 测试代码
if __name__ == "__main__":
    print(f"当前时间: {get_current_time()}")
    print(f"当前时段: {get_time_period()}")
    
    test_time = "14:30"
    print(f"下一个{test_time}将在: {get_next_time(test_time)}")
    
    past_time = datetime.now(BEIJING) - timedelta(hours=3)
    print(f"相对时间描述: {humanize_time(past_time)}")