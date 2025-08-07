#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import httpx
from nonebot.log import logger

from ..config import config
from ..utils.time_utils import get_current_date

class AstrologyService:
    """占卜与黄历服务"""
    service_name = "astrology"

    def __init__(self):
        self.cache_dir = config.data_dir / "astrology_cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        # 初始化星座数据
        self.constellations = self._load_constellation_data()
        self.horoscope_cache = {}
        self.last_fetch_time = None

    def _load_constellation_data(self) -> Dict:
        """加载星座基础数据"""
        data_file = Path(__file__).parent / "data" / "constellations.json"
        with open(data_file, "r", encoding="utf-8") as f:
            return json.load(f)

    async def get_daily_horoscope(self, constellation: str) -> Dict[str, str]:
        """
        获取每日运势
        返回: {
            "date": "2023-11-15",
            "constellation": "白羊座",
            "lucky_level": "大吉",
            "description": "今日运势极佳...",
            "recommendation": "适合开展新项目"
        }
        """
        # 验证星座
        if constellation not in self.constellations:
            raise ValueError(f"无效星座: {constellation}")

        # 检查缓存
        cache_key = f"{get_current_date()}_{constellation}"
        if cache_key in self.horoscope_cache:
            return self.horoscope_cache[cache_key]

        # 从网络获取实时数据（失败时使用本地生成）
        try:
            result = await self._fetch_online_horoscope(constellation)
        except Exception as e:
            logger.warning(f"获取在线运势失败: {e}, 使用本地生成")
            result = self._generate_local_horoscope(constellation)

        # 缓存结果
        self.horoscope_cache[cache_key] = result
        return result

    async def _fetch_online_horoscope(self, constellation: str) -> Dict:
        """
        从网络API获取实时运势数据
        实际开发时需要替换为真实的API调用
        """
        # 示例API请求（实际使用时需要替换）
        api_url = "https://api.example.com/horoscope"
        params = {
            "date": get_current_date(),
            "constellation": constellation,
            "lang": "zh"
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()

            return {
                "date": get_current_date(),
                "constellation": constellation,
                "lucky_level": data.get("lucky_level", "中吉"),
                "description": data.get("description", "运势平稳"),
                "recommendation": data.get("recommendation", "保持现状")
            }

    def _generate_local_horoscope(self, constellation: str) -> Dict:
        """本地生成运势数据"""
        # 权重配置
        levels = {
            "大吉": 0.15,
            "中吉": 0.35,
            "小吉": 0.3,
            "凶": 0.15,
            "大凶": 0.05
        }

        # 星座特性调整
        adjustments = self.constellations[constellation].get("adjustments", {})
        for level, adj in adjustments.items():
            levels[level] = min(max(levels[level] + adj, 0), 1)

        # 归一化权重
        total = sum(levels.values())
        normalized = {k: v/total for k, v in levels.items()}

        # 随机选择运势等级
        level = random.choices(
            list(normalized.keys()),
            weights=list(normalized.values()),
            k=1
        )[0]

        # 获取对应描述
        descriptions = {
            "大吉": [
                "今日鸿运当头，诸事皆宜",
                "贵人相助，事业爱情双丰收",
                "创意迸发，适合开展新项目"
            ],
            "中吉": [
                "整体运势平稳，小有收获",
                "人际关系和谐，易得助力",
                "财运尚可，适合小额投资"
            ],
            "凶": [
                "今日易遇波折，重要决策需谨慎",
                "注意健康问题，适当休息",
                "财务往来需仔细核对"
            ]
        }

        # 默认描述
        desc = random.choice(descriptions.get(level, ["运势平稳，按部就班"])
        
        return {
            "date": get_current_date(),
            "constellation": constellation,
            "lucky_level": level,
            "description": desc,
            "recommendation": self._get_recommendation(level, constellation)
        }

    def _get_recommendation(self, level: str, constellation: str) -> str:
        """生成个性化建议"""
        # 星座特定建议
        const_rec = {
            "白羊座": "控制冲动，三思后行",
            "金牛座": "财务方面需谨慎",
            "双子座": "注意沟通方式",
            "巨蟹座": "关注家庭关系",
            "狮子座": "适当收敛锋芒",
            "处女座": "细节决定成败",
            "天秤座": "保持平衡之道",
            "天蝎座": "信任是关系基础",
            "射手座": "旅行带来好运",
            "摩羯座": "工作需劳逸结合",
            "水瓶座": "创新带来突破",
            "双鱼座": "直觉指引方向"
        }.get(constellation, "")

        # 运势级别建议
        level_rec = {
            "大吉": "大胆行动，把握机遇",
            "中吉": "稳中求进，小步尝试",
            "小吉": "保持现状，巩固成果",
            "凶": "谨慎行事，避免冒险",
            "大凶": "以静制动，修身养性"
        }.get(level, "")

        return f"{const_rec}；{level_rec}"

    async def get_daily_almanac(self) -> str:
        """
        获取今日黄历
        返回格式: "2023-11-15 宜：出行 忌：争吵"
        """
        # 检查缓存
        cache_file = self.cache_dir / f"almanac_{get_current_date()}.json"
        if cache_file.exists():
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f).get("text", "")

        # 从网络获取
        try:
            text = await self._fetch_online_almanac()
        except Exception as e:
            logger.error(f"获取黄历失败: {e}")
            text = self._generate_default_almanac()

        # 写入缓存
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump({"date": get_current_date(), "text": text}, f)

        return text

    async def _fetch_online_almanac(self) -> str:
        """从网络获取黄历数据"""
        url = "https://www.huangli123.net/huangli/"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10.0)
            resp.raise_for_status()
            
            # 示例解析（实际需要根据网页结构调整）
            content = resp.text
            if "今日宜" in content and "今日忌" in content:
                start = content.index("今日宜")
                end = content.index("今日忌") + 10
                return content[start:end].strip()
            
            return self._generate_default_almanac()

    def _generate_default_almanac(self) -> str:
        """生成默认黄历"""
        actions = {
            "宜": ["出行", "会友", "签约", "搬家", "装修"],
            "忌": ["争吵", "借贷", "投资", "理发", "手术"]
        }
        lucky = random.sample(actions["宜"], 2)
        unlucky = random.sample(actions["忌"], 2)
        return f"{get_current_date()} 宜：{' '.join(lucky)} 忌：{' '.join(unlucky)}"

# 服务实例
astrology_service = AstrologyService()