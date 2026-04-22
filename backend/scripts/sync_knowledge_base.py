"""
同步MySQL知识库到ChromaDB向量库

用法:
    python scripts/sync_knowledge_base.py

功能:
    1. 从MySQL读取knowledge_base表中的FAQ
    2. 构建文本向量化（使用ChromaDB内置embedding）
    3. 批量插入到ChromaDB向量库
"""
import asyncio
import logging
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.knowledge import KnowledgeBase
from app.services.knowledge_base import knowledge_base

logger = logging.getLogger("app")


async def sync_mysql_to_chroma():
    """
    从MySQL同步FAQ到ChromaDB向量库

    流程：
    1. 从MySQL读取knowledge_base表数据
    2. 批量插入ChromaDB
    """
    logger.info("[Sync] Starting MySQL -> ChromaDB sync")

    async with AsyncSessionLocal() as db:
        # 从MySQL读取所有活跃的FAQ
        result = await db.execute(
            select(KnowledgeBase).where(
                KnowledgeBase.is_active == True,
                KnowledgeBase.is_deleted == False
            )
        )
        records = result.scalars().all()
        logger.info(f"[Sync] Found {len(records)} records in MySQL")

        # 准备数据
        docs_to_add = []
        for record in records:
            # 构建文档内容：question + answer
            if record.answer:
                doc_text = f"问题：{record.question or ''}\n回答：{record.answer}"
            elif record.content:
                doc_text = record.content
            else:
                continue

            docs_to_add.append({
                "id": str(record.id),
                "text": doc_text,
                "metadata": {
                    "category": record.category or "",
                    "source": record.source or "",
                    "question": record.question or ""
                }
            })

        logger.info(f"[Sync] Prepared {len(docs_to_add)} documents for ChromaDB")

        # 批量添加到ChromaDB
        if docs_to_add:
            count = knowledge_base.add_batch(docs_to_add)
            logger.info(f"[Sync] Successfully synced {count} documents to ChromaDB")
            return count
        else:
            logger.warning("[Sync] No documents to sync")
            return 0


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)8s] [%(name)s] %(message)s'
    )
    result = asyncio.run(sync_mysql_to_chroma())
    print(f"Sync completed: {result} records synced")