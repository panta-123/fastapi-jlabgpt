import secrets
import warnings
from typing import Annotated, Any, Literal, Optional

from pydantic import AnyUrl, BeforeValidator, FilePath, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",")]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


class Settings(BaseSettings):
    """
    This is the main configuration class for the application.
    """

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_ignore_empty=True,
        extra="ignore",
    )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"
    FRONTEND_HOST: str = "http://localhost:5173"

    BACKEND_CORS_ORIGINS: Annotated[list[AnyUrl] | str, BeforeValidator(parse_cors)] = (
        []
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        """return all cors origins"""
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    PROJECT_NAME: str = "JLABGPT"

    MISTRAL_API_KEY: str = "uSOqHX7amGxJnfPkh1qRQj5uSfU2M6f1"
    # Optional environment variables
    OPENAI_API_KEY: Optional[str] = None
    CHROMA_PERSIST_PATH: Optional[str] = "/Users/panta/fastapi-jlabgpt/backend/chromadb"
    CHROMA_COLLECTION_NAME: str = "Documents"
    CHROMA_DISTANCE_FUNCTION: str = "cosine"
    CHROMA_HOST: Optional[str] = None
    CHROMA_PORT: Optional[int] = None
    UPLOAD_DIR: Optional[str] = "/Users/panta/fastapi-jlabgpt/backend/filesupload/uploads"
    MD_DIR: str = "/Users/panta/fastapi-jlabgpt/backend/filesupload/mds"

    # SSL paths
    SSL_CERT_FILE: str = "/Users/panta/jlabgpt/huggingface-chain.pem"
    REQUESTS_CA_BUNDLE: str = "/Users/panta/jlabgpt/huggingface-chain.pem"



settings = Settings()  # type: ignore
