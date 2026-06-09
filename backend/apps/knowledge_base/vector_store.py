import chromadb
from django.conf import settings


class VectorStoreService:
    def __init__(self):
        settings.CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(settings.CHROMA_DB_PATH),
        )

        self.collection = self.client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def add_chunks(
        self,
        ids: list[str],
        texts: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict],
    ) -> None:
        if not ids:
            return

        self.collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
        )

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[dict]:
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]
        ids = results.get("ids", [[]])[0]

        final_results = []

        for index, document in enumerate(documents):
            distance = distances[index] if index < len(distances) else 1.0
            similarity_score = max(0.0, 1.0 - float(distance))

            final_results.append(
                {
                    "id": ids[index] if index < len(ids) else "",
                    "text": document,
                    "metadata": metadatas[index] if index < len(metadatas) else {},
                    "distance": distance,
                    "similarity_score": similarity_score,
                }
            )

        return final_results

    def delete_document_chunks(self, document_id: int) -> None:
        self.collection.delete(
            where={"document_id": document_id},
        )