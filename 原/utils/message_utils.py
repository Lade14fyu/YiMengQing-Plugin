#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from typing import List, Tuple, Dict, Optional, Union
from nonebot.adapters.onebot.v11 import Message, MessageSegment

class MessageParser:
    """消息解析工具类"""

    @staticmethod
    def extract_command(text: str, prefixes: List[str] = None) -> Tuple[str, str]:
        """从消息中提取命令和参数
        
        Args:
            text: 原始消息文本
            prefixes: 可选的前缀列表，默认为["/", "!", "！", "怡", "占卜"]
            
        Returns:
            tuple: (命令前缀, 命令内容) 或 ("", 原始消息)
        """
        if prefixes is None:
            prefixes = ["/", "!", "！", "怡", "占卜"]
        
        for prefix in prefixes:
            if text.startswith(prefix):
                return prefix, text[len(prefix):].strip()
        return "", text

    @staticmethod
    def split_message(msg: Union[str, Message], max_len: int = 500) -> List[str]:
        """分割长消息为多个片段
        
        Args:
            msg: 要分割的消息
            max_len: 每个片段的最大长度
            
        Returns:
            list: 分割后的消息列表
        """
        text = str(msg)
        if len(text) <= max_len:
            return [text]
        
        # 按段落分割
        paragraphs = text.split('\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) + 1 > max_len:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                
                # 处理超长段落
                if len(para) > max_len:
                    chunks.extend([para[i:i+max_len] for i in range(0, len(para), max_len)])
                    continue
            
            if current_chunk:
                current_chunk += "\n" + para
            else:
                current_chunk = para
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks

    @staticmethod
    def extract_at_users(message: Message) -> List[int]:
        """提取消息中被@的用户列表
        
        Args:
            message: 消息对象
            
        Returns:
            list: 被@的用户QQ号列表
        """
        return [
            int(seg.data["qq"])
            for seg in message
            if seg.type == "at" and "qq" in seg.data
        ]

    @staticmethod
    def build_reply(message: Message, reply: str, at_sender: bool = True) -> Message:
        """构建回复消息
        
        Args:
            message: 原始消息
            reply: 回复内容
            at_sender: 是否@发送者
            
        Returns:
            Message: 构造的消息对象
        """
        msg = Message()
        if at_sender:
            user_id = message.get("user_id")
            if user_id:
                msg.append(MessageSegment.at(user_id))
                msg.append(MessageSegment.text(" "))
        
        msg.append(MessageSegment.text(reply))
        return msg

    @staticmethod
    def contains_image(message: Message) -> bool:
        """检查消息是否包含图片
        
        Args:
            message: 消息对象
            
        Returns:
            bool: 是否包含图片
        """
        return any(seg.type == "image" for seg in message)

    @staticmethod
    def extract_images(message: Message) -> List[str]:
        """提取消息中的图片链接
        
        Args:
            message: 消息对象
            
        Returns:
            list: 图片URL列表
        """
        return [
            seg.data["url"]
            for seg in message
            if seg.type == "image" and "url" in seg.data
        ]

    @staticmethod
    def remove_sensitive_words(text: str, words: List[str]) -> str:
        """移除敏感词
        
        Args:
            text: 原始文本
            words: 敏感词列表
            
        Returns:
            str: 处理后的文本
        """
        for word in words:
            text = text.replace(word, "***")
        return text

    @staticmethod
    def parse_cq_code(text: str) -> List[Dict]:
        """解析CQ码消息
        
        Args:
            text: 包含CQ码的原始文本
            
        Returns:
            list: 解析后的CQ码字典列表
        """
        pattern = re.compile(r'\[CQ:(\w+)((?:,[^=]+=[^,\]]+)*)\]')
        result = []
        
        for match in pattern.finditer(text):
            cq_type = match.group(1)
            params_str = match.group(2)
            params = {}
            
            if params_str:
                for param in params_str.split(','):
                    if '=' in param:
                        key, value = param.split('=', 1)
                        params[key.strip()] = value.strip()
            
            result.append({"type": cq_type, "data": params})
        
        return result

    @staticmethod
    def is_plain_text(message: Message) -> bool:
        """检查是否为纯文本消息
        
        Args:
            message: 消息对象
            
        Returns:
            bool: 是否纯文本
        """
        return all(seg.type == "text" for seg in message)

# 实例化工具类
message_parser = MessageParser()

# 快捷函数
def extract_command(text: str, prefixes: List[str] = None) -> Tuple[str, str]:
    return message_parser.extract_command(text, prefixes)

def split_message(msg: Union[str, Message], max_len: int = 500) -> List[str]:
    return message_parser.split_message(msg, max_len)

def extract_at_users(message: Message) -> List[int]:
    return message_parser.extract_at_users(message)

def build_reply(message: Message, reply: str, at_sender: bool = True) -> Message:
    return message_parser.build_reply(message, reply, at_sender)

# 导出接口
__all__ = [
    'message_parser',
    'extract_command',
    'split_message',
    'extract_at_users',
    'build_reply'
]