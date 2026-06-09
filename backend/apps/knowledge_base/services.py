from django.conf import settings
from django.db import transaction

from .document_processor import DocumentProcessingError, extract_text, get_file_type
from .embeddings import generate_embeddings
from .models import KBDocument, KBChunk
from .smart_chunker import split_clean_text_into_chunks
from .text_cleaner import clean_uploaded_text
from .vector_store import VectorStoreService


def process_kb_document(document: KBDocument) -> KBDocument:
    try:
        file_path = document.file.path
        file_type = get_file_type(document.file.name)

        document.file_type = file_type
        document.status = KBDocument.Status.PROCESSING
        document.error_message = ""
        document.save(
            update_fields=[
                "file_type",
                "status",
                "error_message",
                "updated_at",
            ]
        )

        raw_text = extract_text(file_path=file_path, file_type=file_type)

        if getattr(settings, "KB_CLEAN_TEXT_ENABLED", True):
            cleaned_text = clean_uploaded_text(raw_text)
        else:
            cleaned_text = raw_text

        chunks = split_clean_text_into_chunks(cleaned_text)

        if not chunks:
            raise DocumentProcessingError("No clean chunks generated from document.")

        embeddings = generate_embeddings(chunks)

        vector_ids = []
        metadatas = []

        file_name = document.file.name.split("/")[-1]

        for index, chunk in enumerate(chunks):
            vector_id = f"kb-doc-{document.id}-chunk-{index}"
            vector_ids.append(vector_id)

            metadatas.append(
                {
                    "document_id": document.id,
                    "document_title": document.title,
                    "file_name": file_name,
                    "chunk_index": index,
                    "source": document.title,
                    "cleaned": True,
                    "chunk_word_count": len(chunk.split()),
                }
            )

        vector_store = VectorStoreService()

        try:
            vector_store.delete_document_chunks(document.id)
        except Exception:
            pass

        with transaction.atomic():
            KBChunk.objects.filter(document=document).delete()

        vector_store.add_chunks(
            ids=vector_ids,
            texts=chunks,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        with transaction.atomic():
            chunk_objects = []

            for index, chunk in enumerate(chunks):
                chunk_objects.append(
                    KBChunk(
                        document=document,
                        chunk_text=chunk,
                        chunk_index=index,
                        vector_id=vector_ids[index],
                        source_title=document.title,
                        source_file_name=file_name,
                    )
                )

            KBChunk.objects.bulk_create(chunk_objects)

            document.status = KBDocument.Status.COMPLETED
            document.total_chunks = len(chunks)
            document.error_message = ""
            document.save(
                update_fields=[
                    "status",
                    "total_chunks",
                    "error_message",
                    "updated_at",
                ]
            )

        return document

    except Exception as exc:
        document.status = KBDocument.Status.FAILED
        document.error_message = str(exc)
        document.save(
            update_fields=[
                "status",
                "error_message",
                "updated_at",
            ]
        )
        return document