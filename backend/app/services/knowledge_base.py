"""
RAG知识库服务

基于ChromaDB的向量知识库实现
"""
from typing import List, Dict, Any, Optional
import logging
from app.config import settings

logger = logging.getLogger("app")

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    logger.warning("ChromaDB not installed, knowledge base will use mock mode")


class KnowledgeBase:
    """RAG知识库类"""

    def __init__(self):
        self.logger = logging.getLogger("app")
        self.collection_name = "knowledge_base"

        if CHROMA_AVAILABLE:
            # 使用PersistentClient支持数据持久化
            import os
            os.makedirs(settings.CHROMA_DB_PATH, exist_ok=True)
            self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "AI小商校园知识库"}
            )
            self.logger.info(f"[KnowledgeBase] Initialized with persistent path: {settings.CHROMA_DB_PATH}")
        else:
            self.client = None
            self.collection = None
            self.logger.warning("ChromaDB not available, using mock mode")

    def add(
        self,
        id: str,
        text: str,
        metadata: Dict[str, Any],
        vector: Optional[List[float]] = None
    ) -> bool:
        """
        添加知识条目

        Args:
            id: 知识ID
            text: 知识文本内容
            metadata: 元数据( category, source等 )
            vector: 向量(可选，不传则使用ChromaDB自动embedding)

        Returns:
            是否添加成功
        """
        self.logger.info(f"[KnowledgeBase] add called, id: {id}")

        if not CHROMA_AVAILABLE:
            self.logger.warning("[KnowledgeBase] ChromaDB not available, skipping")
            return False

        try:
            self.collection.add(
                ids=[id],
                documents=[text],
                metadatas=[metadata],
                embeddings=[vector] if vector else None  # None则使用ChromaDB内置embedding
            )
            return True
        except Exception as e:
            self.logger.error(f"[KnowledgeBase] Failed to add: {str(e)}")
            return False

    def add_batch(self, docs: List[Dict[str, Any]]) -> int:
        """
        批量添加知识条目

        Args:
            docs: 文档列表，每个文档包含 id, text, metadata

        Returns:
            成功添加的数量
        """
        self.logger.info(f"[KnowledgeBase] add_batch called with {len(docs)} documents")

        if not CHROMA_AVAILABLE:
            self.logger.warning("[KnowledgeBase] ChromaDB not available, skipping")
            return 0

        if not docs:
            return 0

        try:
            ids = [doc["id"] for doc in docs]
            texts = [doc["text"] for doc in docs]
            metadatas = [doc["metadata"] for doc in docs]

            self.collection.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas
            )

            self.logger.info(f"[KnowledgeBase] Batch add successful: {len(docs)} documents")
            return len(docs)
        except Exception as e:
            self.logger.error(f"[KnowledgeBase] Batch add failed: {str(e)}")
            return 0

    def clear(self) -> bool:
        """
        清空知识库（删除所有文档）

        Returns:
            是否清空成功
        """
        self.logger.info(f"[KnowledgeBase] clear called")

        if not CHROMA_AVAILABLE:
            return False

        try:
            # 删除整个collection然后重建
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "AI小商校园知识库"}
            )
            self.logger.info("[KnowledgeBase] Knowledge base cleared")
            return True
        except Exception as e:
            self.logger.error(f"[KnowledgeBase] Clear failed: {str(e)}")
            return False

    def search(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        语义检索

        Args:
            query: 查询文本
            top_k: 返回数量
            category: 可选的分类过滤

        Returns:
            匹配的知识条目列表
        """
        self.logger.info(f"[KnowledgeBase] search called, query: {query}")

        if not CHROMA_AVAILABLE:
            self.logger.warning("[KnowledgeBase] ChromaDB not available, returning empty")
            return []

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                where={"category": category} if category else None
            )

            knowledge_list = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    knowledge_list.append({
                        "id": results["ids"][0][i],
                        "content": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else None
                    })

            return knowledge_list
        except Exception as e:
            self.logger.error(f"[KnowledgeBase] Search failed: {str(e)}")
            return []

    def delete(self, id: str) -> bool:
        """
        删除知识条目

        Args:
            id: 知识ID

        Returns:
            是否删除成功
        """
        self.logger.info(f"[KnowledgeBase] delete called, id: {id}")

        if not CHROMA_AVAILABLE:
            return False

        try:
            self.collection.delete(ids=[id])
            return True
        except Exception as e:
            self.logger.error(f"[KnowledgeBase] Failed to delete: {str(e)}")
            return False

    def update_views(self, id: str) -> bool:
        """更新知识条目查询次数"""
        self.logger.debug(f"[KnowledgeBase] update_views called, id: {id}")

        # TODO: 实现查询次数更新
        # 可以存储在MySQL的knowledge_base表中

        return True

    def get_by_category(self, category: str, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """
        按分类获取知识条目

        Args:
            category: 分类
            skip: 跳过数量
            limit: 返回数量

        Returns:
            知识条目列表
        """
        self.logger.info(f"[KnowledgeBase] get_by_category called, category: {category}")

        # TODO: 从MySQL获取知识库数据

        return []

    def build_from_mysql(self, records: List[Dict[str, Any]]) -> int:
        """
        从MySQL数据构建向量库

        Args:
            records: MySQL中的知识库记录

        Returns:
            成功导入的数量
        """
        self.logger.info(f"[KnowledgeBase] build_from_mysql called, records: {len(records)}")

        count = 0
        for record in records:
            success = self.add(
                id=str(record["id"]),
                text=record.get("content") or record.get("answer") or "",
                metadata={
                    "category": record.get("category", ""),
                    "source": record.get("source", "")
                }
            )
            if success:
                count += 1

        return count


# 单例实例
knowledge_base = KnowledgeBase()
