#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

import httpx
from nonebot import Bot
from nonebot.log import logger

from ..config import config
from ..utils.time_utils import get_time_period, get_current_time

class CheckinHandler:
    def __init__(self):
        self.data_path = config.data_dir / "checkin_data.json"
        self._init_data_file()
        self.horoscope_cache = None
        self.cache_time = None

    def _init_data_file(self):
        """初始化签到数据文件"""
        if not self.data_path.exists():
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=4)

    async def _get_horoscope(self) -> str:
        """获取今日黄历 (带缓存机制)"""
        # 检查缓存有效性（每6小时更新）
        if self.horoscope_cache and self.cache_time:
            if (datetime.now() - self.cache_time) < timedelta(hours=6):
                return self.horoscope_cache

        try:
            url = "https://www.huangli123.net/huangli/"
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                
                # 示例解析（实际需根据网页结构调整）
                content = resp.text
                if "今日宜" in content and "今日忌" in content:
                    start = content.index("今日宜")
                    end = content.index("今日忌") + 10
                    self.horoscope_cache = content[start:end]
                else:
                    self.horoscope_cache = "今日宜：占卜 交友；忌：争吵"
                
                self.cache_time = datetime.now()
                return self.horoscope_cache

        except Exception as e:
            logger.error(f"获取黄历失败: {e}")
            return "今日黄历获取失败，宜谨慎行事"

    async def _load_checkin_data(self) -> Dict[str, Any]:
        """加载签到数据"""
        with open(self.data_path, "r", encoding="utf-8") as f:
            return json.load(f)

    async def _save_checkin_data(self, data: Dict[str, Any]):
        """保存签到数据"""
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    async def _get_user_record(self, user_id: int, group_id: int) -> Dict[str, Any]:
        """获取用户签到记录"""
        key = f"{user_id}_{group_id}"
        data = await self._load_checkin_data()
        return data.get(key, {})

    async def handle_checkin(self, bot: Bot, user_id: int, group_id: int):
        """处理签到请求"""
        # 检查时间段
        period = get_time_period()
        if period == "night":  # 20:00-5:00不能签到
            msg = "啊~(打哈欠)，还没睡呢客官?半夜来光顾我这荒山野岭的小店?真是有兴致……不能打卡了，早上五点再来吧……"
            await bot.send_group_msg(group_id=group_id, message=msg)
            return

        # 获取当前日期
        today = datetime.now().strftime("%Y-%m-%d")
        now_time = datetime.now().strftime("%H:%M:%S")
        key = f"{user_id}_{group_id}"

        # 加载数据
        data = await self._load_checkin_data()
        record = data.get(key, {
            "user_id": user_id,
            "group_id": group_id,
            "first_date": today,
            "last_date": "",
            "total_days": 0,
            "continuous_days": 0,
            "history": []
        })

        # 检查是否已签到
        if record.get("last_date") == today:
            await bot.send_group_msg(
                group_id=group_id,
                message="客官今天已经签过到了，明天再来吧~"
            )
            return

        # 更新连续签到
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        continuous_days = 1
        if record["last_date"] == yesterday:
            continuous_days = record["continuous_days"] + 1
        elif record["last_date"]:  # 昨天没签，连续中断
            continuous_days = 1

        # 更新记录
        new_record = {
            **record,
            "last_date": today,
            "total_days": record["total_days"] + 1,
            "continuous_days": continuous_days,
            "history": record["history"] + [{
                "date": today,
                "time": now_time,
                "period": period
            }]
        }
        data[key] = new_record
        await self._save_checkin_data(data)

        # 准备回复消息
        await self._send_checkin_response(bot, group_id, new_record, period)

    async def _send_checkin_response(self, bot: Bot, group_id: int, record: Dict[str, Any], period: str):
        """发送签到回复"""
        days = record["total_days"]
        continuous_days = record["continuous_days"]
        
        if period == "morning":  # 5:00-12:00
            horoscope = await self._get_horoscope()
            msg = (
                f"嗯哼~又有顾客了，签到成功噢，{horoscope}\n"
                f"这位客官，你已经签到{days}天了呢（连续{continuous_days}天）"
                "要不要占卜一下你的运势呀?"
            )
        elif period == "afternoon":  # 12:00-20:00
            msg = (
                f"下午好啊客官~真是让我等着急了呢，签到成功噢~\n"
                f"这是您第{days}次光顾小店（连续签到{continuous_days}天）"
            )
        else:
            msg = "系统错误：无效的时间段"

        # 随机添加后缀
        suffixes = [
            "愿星辰指引你的道路~",
            "今日的卦象似乎不错呢",
            "要喝杯茶再走吗？",
            "小店新到了上好的茶叶哦"
        ]
        msg += random.choice(suffixes)

        await bot.send_group_msg(group_id=group_id, message=msg)

# 实例化签到处理器
checkin_handler = CheckinHandler()