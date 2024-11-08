import json
import time
import os
from pathlib import Path

from celery import Celery, chain, shared_task

from app.core.config import settings

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://some-redis:6379/0")
celery.conf.result_backend = os.environ.get(
    "CELERY_RESULT_BACKEND", "redis://some-redis:6379/0"
)


@celery.task(name="create_task")
def process_pdf(pdf_path: str, metadata_path: str):
    """
    This task processes pdf files and coverts to markdown using marker
    
    from marker.convert import convert_single_pdf
    from marker.models import load_all_models
    from marker.output import save_markdown

    model_lst = load_all_models()
    # Your existing PDF processing logic here
    with open(metadata_path) as f:
        metadata = json.load(f)
    full_text, images, out_metadata = convert_single_pdf(
        pdf_path, model_lst, metadata=metadata, batch_multiplier=1
    )
    fname = os.path.basename(pdf_path)
    if len(full_text.strip()) > 0:
        save_markdown(settings.MD_DIR, fname, full_text, images, out_metadata)
    """
    time.spleep(20)
    markdown_path = "/Users/panta/fastapi-jlabgpt/backend/filesupload/mds/a.md"
    return  markdown_path


@celery.task(name="process_markdown")
def process_markdown(markdown_path: str):

    from haystack import Pipeline
    
    from haystack.components.converters import MarkdownToDocument
    from haystack.components.embedders import SentenceTransformersDocumentEmbedder
    from haystack.components.preprocessors import DocumentSplitter
    from haystack.components.writers import DocumentWriter
    from haystack.document_stores.types import DuplicatePolicy
    from app.core.db.chromdb import document_store

    indexing_pipeline = Pipeline()
    indexing_pipeline.add_component("markdown_converter", MarkdownToDocument())

    indexing_pipeline.add_component(
        instance=DocumentSplitter(split_by="sentence", split_length=3, split_overlap=0),
        name="splitter",
    )

    embedding_model_name = "intfloat/e5-large-v2"
    meta_fields_to_embed: list[str] = ["title"]
    embedder = SentenceTransformersDocumentEmbedder(
        model=embedding_model_name,
        prefix="passage",
        #meta_fields_to_embed=meta_fields_to_embed,
    )
    #embedder.warm_up()
    indexing_pipeline.add_component("embedder", embedder)



    #document_store = ChromaDocumentStore(persist_path="/home/chromadb")

    # Writer
    writer = DocumentWriter(document_store=document_store, policy=DuplicatePolicy.SKIP)
    indexing_pipeline.add_component("writer", writer)

    # Connect components
    #indexing_pipeline.connect("nougat_converter.sources", "markdown_converter.sources")
    #indexing_pipeline.connect("nougat_converter.meta", "markdown_converter.meta")
    # indexing_pipeline.connect("pydf_converter", "splitter")

    indexing_pipeline.connect("markdown_converter", "splitter")
    indexing_pipeline.connect("splitter", "embedder")
    indexing_pipeline.connect("embedder", "writer")

    indexing_pipeline.run({"markdown_converter": {"sources": [Path(markdown_path)]}})
    return True

"""
def chain_pdf_processing(pdf_path, metadata_path):
    return chain(
        process_pdf.s(pdf_path, metadata_path),
        process_markdown.s()
    )()

@shared_task(name="start_pdf_processing")
def start_pdf_processing(pdf_path, metadata_path):
    return chain_pdf_processing(pdf_path, metadata_path)
"""