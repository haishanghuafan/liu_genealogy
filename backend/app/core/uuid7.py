"""
UUID7 生成工具模块

UUID7 特点：
- 时间戳前缀，天然有序
- 更好的数据库性能（顺序插入）
- 可提取创建时间信息
"""

from uuid6 import uuid7
from uuid import UUID


def generate_uuid() -> UUID:
    """生成 UUID7"""
    return uuid7()


def uuid7_str() -> str:
    """生成 UUID7 字符串"""
    return str(uuid7())
