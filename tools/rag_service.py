import os
import shutil
from pathlib import Path

import pypdf
from dotenv import load_dotenv
from llama_index.core import (
    Document,
    Settings,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.groq import Groq


BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENTS_DIR = BASE_DIR / "documents"
PERSIST_DIR = BASE_DIR / "storage"
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".docx"}

load_dotenv(BASE_DIR / "apis.env")


def get_embed_model():
    return OllamaEmbedding(
        model_name="nomic-embed-text",
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )


def configure_llama_index():
    Settings.embed_model = get_embed_model()
    Settings.chunk_size = 512
    Settings.chunk_overlap = 50

    groq_api_key = os.getenv("GROQ_API_KEY")
    if groq_api_key:
        Settings.llm = Groq(model="llama-3.3-70b-versatile", api_key=groq_api_key)


def list_document_files(documents_dir: Path = DOCUMENTS_DIR) -> list[Path]:
    if not documents_dir.exists():
        return []

    return sorted(
        path
        for path in documents_dir.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def load_documents(documents_dir: Path = DOCUMENTS_DIR):
    document_files = list_document_files(documents_dir)
    if not document_files:
        return []

    documents = []
    for path in document_files:
        if path.suffix.lower() == ".pdf":
            try:
                reader = pypdf.PdfReader(str(path))
                text = "\n".join(page.extract_text() or "" for page in reader.pages)
            except Exception as exc:
                raise ValueError(f"Failed to read PDF {path.name}: {exc}") from exc
        else:
            text = path.read_text(encoding="utf-8", errors="ignore")

        documents.append(
            Document(
                text=text,
                metadata={
                    "file_path": str(path),
                    "file_name": path.name,
                    "file_type": path.suffix.lower(),
                    "file_size": path.stat().st_size,
                },
            )
        )

    return documents


def build_index(
    documents_dir: Path = DOCUMENTS_DIR,
    persist_dir: Path = PERSIST_DIR,
    rebuild: bool = True,
):
    documents = load_documents(documents_dir)
    if not documents:
        raise ValueError(
            f"No supported documents found in {documents_dir}. "
            f"Supported extensions: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    configure_llama_index()

    if rebuild and persist_dir.exists():
        shutil.rmtree(persist_dir)

    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=str(persist_dir))
    return index, len(documents), [path.name for path in list_document_files(documents_dir)]


def load_index(persist_dir: Path = PERSIST_DIR):
    configure_llama_index()
    storage_context = StorageContext.from_defaults(persist_dir=str(persist_dir))
    return load_index_from_storage(storage_context, embed_model=get_embed_model())


def storage_mtime(persist_dir: Path = PERSIST_DIR) -> float:
    if not persist_dir.exists():
        return 0.0

    mtimes = [
        path.stat().st_mtime
        for path in persist_dir.rglob("*")
        if path.is_file()
    ]
    return max(mtimes, default=0.0)
