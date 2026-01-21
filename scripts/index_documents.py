#!/usr/bin/env python3
"""
Script to index enterprise documents into the RAG knowledge base.
Run this once after setting up the database to populate the embeddings.

Usage:
    python scripts/index_documents.py

Or from project root:
    python -m scripts.index_documents
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.rag_service import RAGService


def main():
    print("=" * 60)
    print("RAG Document Indexer")
    print("=" * 60)

    # Initialize RAG service
    print("\nInitializing RAG service...")
    try:
        rag = RAGService()
        print("RAG service initialized successfully")
    except Exception as e:
        print(f"ERROR: Failed to initialize RAG service: {e}")
        print("\nMake sure:")
        print("  1. Your .env file has SUPABASE_URL, SUPABASE_SECRET_KEY, and GEMINI_API_KEY")
        print("  2. You've run the SQL setup script in Supabase")
        sys.exit(1)

    # Path to enterprise documents
    docs_path = project_root / "assets/enterprise_documents"

    if not docs_path.exists():
        print(f"ERROR: Documents directory not found: {docs_path}")
        sys.exit(1)

    # Count markdown files
    md_files = list(docs_path.glob("*.md"))
    print(f"\nFound {len(md_files)} markdown files in {docs_path}")

    for f in md_files:
        print(f"  - {f.name}")

    # Index documents
    print("\n" + "-" * 60)
    print("Starting document indexing...")
    print("-" * 60)

    result = rag.index_documents_from_directory(str(docs_path))

    # Report results
    print("\n" + "=" * 60)
    print("INDEXING COMPLETE")
    print("=" * 60)

    if result.get("success"):
        print(f"\nDocuments processed: {result.get('documents_processed', 0)}")
        print(f"Total chunks created: {result.get('total_chunks', 0)}")
        print("\nAll documents indexed successfully!")
    else:
        print(f"\nDocuments processed: {result.get('documents_processed', 0)}")
        print(f"Total chunks created: {result.get('total_chunks', 0)}")
        print(f"Errors: {len(result.get('errors', []))}")

        if result.get('errors'):
            print("\nErrors encountered:")
            for err in result['errors']:
                print(f"  - {err.get('file')}: {err.get('error')}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
