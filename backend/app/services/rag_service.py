# ============================================================
# AI Medical Consultant - RAG Service (检索增强生成)
# ============================================================
# 基于文档 3.1.2 RAG核心代码逻辑 实现
# ============================================================
import os
import json
import numpy as np
from typing import List, Optional, Dict
from loguru import logger

from app.config import settings


class RAGService:
    """
    RAG检索增强生成服务

    核心流程:
    1. 离线阶段: 文档 → 分块 → Embedding → FAISS索引
    2. 在线阶段: 用户Query → 问题改写 → 多路检索 → 融合排序 → 上下文组装
    """

    def __init__(self):
        self.embedding_model = None
        self.index = None  # FAISS index
        self.documents: List[str] = []       # 文档内容
        self.metadata: List[Dict] = []       # 文档元数据
        self._dimension = settings.VECTOR_DIMENSION

    # ==================== 初始化 ====================

    async def initialize(self):
        """初始化RAG服务 - 加载Embedding模型和已有索引"""
        # Map known embedding model names to local SentenceTransformer models
        _LOCAL_MODEL_MAP = {
            "text-embedding-v1": "BAAI/bge-small-zh-v1.5",
            "text-embedding-v2": "BAAI/bge-large-zh-v1.5",
        }

        local_model_name = _LOCAL_MODEL_MAP.get(
            settings.EMBEDDING_MODEL,
            settings.EMBEDDING_MODEL
        )

        self.embedding_model = None
        try:
            from sentence_transformers import SentenceTransformer
            self.embedding_model = SentenceTransformer(local_model_name)
            logger.info(f"Embedding model loaded locally: {local_model_name} -> {settings.EMBEDDING_MODEL}")
        except Exception as e:
            logger.warning(f"Local embedding model load failed, will use API: {e}")
            self.embedding_model = None

        self._load_index()

    def _load_index(self):
        """加载已有FAISS索引"""
        try:
            import faiss
            index_path = os.path.join(settings.FAISS_INDEX_PATH, "medical.index")
            docs_path = os.path.join(settings.FAISS_INDEX_PATH, "documents.json")

            if os.path.exists(index_path) and os.path.exists(docs_path):
                self.index = faiss.read_index(index_path)
                with open(docs_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.documents = data.get("documents", [])
                    self.metadata = data.get("metadata", [])
                logger.info(f"Loaded FAISS index: {self.index.ntotal} vectors")
            else:
                logger.info("No existing FAISS index found, starting fresh")
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {e}")

    # ==================== 离线索引构建 ====================

    async def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict]] = None
    ) -> int:
        """
        添加文档到知识库（离线操作）

        流程:
        1. texts: ["文档1内容", "文档2内容", ...]
        2. embedding_model.encode(texts): 将文本转为N维向量
        3. index.add(vectors): 添加到FAISS索引
        4. 保存原始文档和元数据
        """
        if metadatas is None:
            metadatas = [{} for _ in texts]

        # Step 1: 文本向量化
        embeddings = await self._embed_texts(texts)
        embeddings = np.array(embeddings).astype("float32")

        # Step 2: 添加到FAISS索引
        import faiss
        if self.index is None:
            self._dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(self._dimension)

        self.index.add(embeddings)

        # Step 3: 保存原始文档
        self.documents.extend(texts)
        self.metadata.extend(metadatas)

        # Step 4: 持久化保存
        self._save_index()

        logger.info(f"Added {len(texts)} documents, total: {self.index.ntotal}")
        return len(texts)

    async def _embed_texts(self, texts: List[str]) -> List[List[float]]:
        """文本向量化 - 支持本地模型和DashScope API"""
        if self.embedding_model is not None:
            # 本地模型
            return self.embedding_model.encode(texts, show_progress_bar=False).tolist()

        # 使用DashScope API
        import dashscope
        from dashscope import TextEmbedding

        embeddings = []
        for text in texts:
            resp = TextEmbedding.call(
                model=settings.EMBEDDING_MODEL,
                input=text,
                api_key=settings.EMBEDDING_API_KEY,
            )
            if resp.status_code == 200:
                embeddings.append(resp.output["embeddings"][0]["embedding"])
            else:
                logger.error(f"Embedding failed: {resp.message}")
                # Fallback: zero vector
                embeddings.append([0.0] * self._dimension)

        return embeddings

    def _save_index(self):
        """持久化保存FAISS索引和文档"""
        os.makedirs(settings.FAISS_INDEX_PATH, exist_ok=True)
        index_path = os.path.join(settings.FAISS_INDEX_PATH, "medical.index")
        docs_path = os.path.join(settings.FAISS_INDEX_PATH, "documents.json")

        if self.index is not None:
            import faiss
            faiss.write_index(self.index, index_path)

        with open(docs_path, "w", encoding="utf-8") as f:
            json.dump({
                "documents": self.documents,
                "metadata": self.metadata,
            }, f, ensure_ascii=False, indent=2)

    # ==================== 问题改写 (Query Expansion) ====================

    async def _expand_query(self, query: str) -> str:
        """
        Query Expansion - 问题改写
        - 同义词替换: 头痛 → 头疼
        - 症状标准化: "发烧" → "发热"
        - 问句补全: "胃疼" → "胃部疼痛"
        """
        # 医学同义词映射
        synonyms = {
            "头痛": "头疼",
            "肚子疼": "腹痛",
            "发烧": "发热",
            "胃疼": "胃痛 胃部疼痛",
            "咳嗽": "咳嗽 咳痰",
            "拉肚子": "腹泻",
            "感冒": "上呼吸道感染 感冒",
            "睡不着": "失眠 睡眠障碍",
            "胸闷": "胸闷 胸痛 心慌",
            "头晕": "头晕 眩晕 头昏",
        }

        expanded_terms = [query]
        for key, val in synonyms.items():
            if key in query:
                expanded_terms.append(val)

        return " ".join(expanded_terms)

    # ==================== 多路检索 ====================

    async def search(
        self,
        query: str,
        top_k: int = None,
        score_threshold: float = 0.0,
        category: Optional[str] = None,
    ) -> List[Dict]:
        """
        向量相似度检索（在线操作）+ 关键词检索 + RRF融合

        流程:
        1. 问题改写 (Query Expansion)
        2. 稠密检索 (Dense - FAISS向量相似度)
        3. 稀疏检索 (Sparse - BM25关键词)
        4. RRF融合排序 (Reciprocal Rank Fusion)
        5. 返回Top-K结果
        """
        if top_k is None:
            top_k = settings.TOP_K_RETRIEVAL

        if self.index is None or self.index.ntotal == 0:
            return []

        # Step 1: 问题改写
        expanded_query = await self._expand_query(query)

        # Step 2: 稠密检索 - FAISS向量相似度
        dense_results = await self._dense_search(expanded_query, top_k * 2)

        # Step 3: 稀疏检索 - 关键词匹配
        sparse_results = self._sparse_search(query, top_k * 2)

        # Step 4: RRF融合排序
        fused = self._rrf_fusion(dense_results, sparse_results, top_k)

        # Step 5: 按分类过滤
        if category:
            fused = [r for r in fused if r.get("category") == category]

        return fused[:top_k]

    async def _dense_search(self, query: str, top_k: int) -> List[Dict]:
        """稠密检索 - FAISS向量搜索"""
        query_vec = await self._embed_texts([query])
        query_vec = np.array(query_vec).astype("float32")

        distances, indices = self.index.search(query_vec, min(top_k, self.index.ntotal))

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents) and idx >= 0:
                # Convert L2 distance to similarity score
                score = 1.0 / (1.0 + float(dist))
                meta = self.metadata[idx] if idx < len(self.metadata) else {}
                results.append({
                    "content": self.documents[idx],
                    "score": score,
                    "method": "dense",
                    "index": int(idx),
                    "category": meta.get("category", ""),
                    "title": meta.get("title", ""),
                    "source": meta.get("source", ""),
                })

        return sorted(results, key=lambda x: x["score"], reverse=True)

    def _sparse_search(self, query: str, top_k: int) -> List[Dict]:
        """稀疏检索 - BM25关键词匹配风格"""
        query_terms = set(query)
        scored = []

        for i, doc in enumerate(self.documents):
            # Simple keyword overlap scoring
            doc_lower = doc.lower()
            matches = sum(1 for term in query_terms if term in doc_lower)
            if matches > 0:
                score = matches / len(query_terms)
                meta = self.metadata[i] if i < len(self.metadata) else {}
                scored.append({
                    "content": doc,
                    "score": score,
                    "method": "sparse",
                    "index": i,
                    "category": meta.get("category", ""),
                    "title": meta.get("title", ""),
                    "source": meta.get("source", ""),
                })

        return sorted(scored, key=lambda x: x["score"], reverse=True)[:top_k]

    def _rrf_fusion(
        self,
        dense_results: List[Dict],
        sparse_results: List[Dict],
        top_k: int,
        k: int = 60,
    ) -> List[Dict]:
        """
        RRF (Reciprocal Rank Fusion) 融合排序

        RRF_score = Σ 1/(k + rank_i)
        - k=60 是推荐参数
        - 综合多路检索结果
        - 去除重复/低相关
        """
        scores = {}
        docs = {}

        # Dense rankings
        for rank, item in enumerate(dense_results, start=1):
            idx = item["index"]
            scores[idx] = scores.get(idx, 0) + 1.0 / (k + rank)
            docs[idx] = item

        # Sparse rankings
        for rank, item in enumerate(sparse_results, start=1):
            idx = item["index"]
            scores[idx] = scores.get(idx, 0) + 1.0 / (k + rank)
            if idx not in docs:
                docs[idx] = item

        # Sort by RRF score
        sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        result = []
        for idx, rrf_score in sorted_items[:top_k]:
            item = docs[idx].copy()
            item["rrf_score"] = rrf_score
            result.append(item)

        return result

    # ==================== 上下文组装 ====================

    async def build_context(
        self,
        query: str,
        top_k: int = None,
        conversation_history: Optional[List[Dict]] = None,
    ) -> Dict:
        """
        上下文组装 (Context Assembly)

        组装内容:
        - System Prompt (角色设定)
        - Retrieved Docs (检索到的医学知识)
        - User Question (用户问题)
        - Chat History (对话历史)
        """
        retrieved = await self.search(query, top_k=top_k)

        # 构建检索知识文本
        knowledge_texts = []
        for i, doc in enumerate(retrieved):
            source = doc.get("source", f"来源{i+1}")
            knowledge_texts.append(f"[{source}] {doc['content']}")

        return {
            "query": query,
            "retrieved_docs": retrieved,
            "knowledge_context": "\n\n".join(knowledge_texts),
            "conversation_history": conversation_history or [],
            "retrieved_count": len(retrieved),
        }

    # ==================== 知识库管理 ====================

    async def delete_document(self, index: int):
        """删除指定文档（需要重建索引）"""
        if 0 <= index < len(self.documents):
            self.documents.pop(index)
            self.metadata.pop(index)
            await self._rebuild_index()

    async def _rebuild_index(self):
        """重建FAISS索引"""
        import faiss
        if not self.documents:
            self.index = None
        else:
            embeddings = await self._embed_texts(self.documents)
            embeddings = np.array(embeddings).astype("float32")
            self.index = faiss.IndexFlatL2(embeddings.shape[1])
            self.index.add(embeddings)
        self._save_index()

    @property
    def document_count(self) -> int:
        return len(self.documents)


# Global instance
rag_service = RAGService()
