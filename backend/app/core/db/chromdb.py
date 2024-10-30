import logging

from haystack_integrations.document_stores.chroma import ChromaDocumentStore

from app.core.config import settings

logger = logging.getLogger("app")

# Initialize parameters with mandatory fields only
chroma_params = {
    "persist_path": settings.CHROMA_PERSIST_PATH,
    "collection_name": settings.CHROMA_COLLECTION_NAME,
    "distance_function": settings.CHROMA_DISTANCE_FUNCTION,
}

# Add optional parameters only if they are set in settings
if settings.CHROMA_HOST:
    chroma_params["host"] = settings.CHROMA_HOST
if settings.CHROMA_PORT:
    chroma_params["port"] = settings.CHROMA_PORT
try:
    document_store = ChromaDocumentStore(**chroma_params)
except ValueError as e:
    logger.error("Configuration error in ChromaDocumentStore parameters: %s", e)
except ConnectionError as e:
    logger.error("Failed to connect to ChromaDocumentStore: %s", e)
except Exception as e:
    logger.exception("An unexpected error occurred with ChromaDocumentStore.")
    # Raise the error if it should halt further execution
    raise e
