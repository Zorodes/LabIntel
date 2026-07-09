from pathlib import Path

from tools.rag_service import load_documents


def test_load_documents_extracts_pdf_text():
    docs_dir = Path(__file__).resolve().parents[1] / "documents"
    docs = load_documents(docs_dir)

    pdf_doc = next((doc for doc in docs if doc.metadata.get("file_name") == "sampledoc.pdf"), None)
    assert pdf_doc is not None

    text = pdf_doc.text.lower()
    assert "distillation" in text
    assert "ethanol" in text
    assert "feed" in text
