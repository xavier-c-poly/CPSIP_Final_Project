import asyncio
import os
import time

from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec
# run ingestion.py before main.py to populate your Pinecone index with embedded chunks from the source document.
load_dotenv()

EMBEDDING_MODEL = "gemini-embedding-001"
INDEX_NAME = os.environ["INDEX_NAME"]
TEXT_FILE = os.path.join(os.path.dirname(__file__), "stardew_crop_descriptions.txt")

# Free-tier rate limit: 1,500 requests/min
# batch size and inter-batch sleep.
BATCH_SIZE = 5      # documents per batch
BATCH_DELAY = 2.0   # seconds between batches
EMBED_DIMENSION = 3072  # gemini-embedding-001 output dimension

embeddings = GoogleGenerativeAIEmbeddings(
model=EMBEDDING_MODEL,
google_api_key=os.environ["GOOGLE_API_KEY"],
)
llm = ChatGoogleGenerativeAI(
model="gemini-2.5-flash", # gemini-2.5-flash
google_api_key=os.environ["GOOGLE_API_KEY"],
temperature=0.2,
)
pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index(INDEX_NAME)


def load_and_split() -> list:
    loader = TextLoader(TEXT_FILE)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks from {len(documents)} document(s).")
    return chunks


def ensure_index(pc: Pinecone) -> None:
    existing = [idx.name for idx in pc.list_indexes()]
    if INDEX_NAME not in existing:
        print(f"Creating Pinecone index '{INDEX_NAME}'...")
        pc.create_index(
            name=INDEX_NAME,
            dimension=EMBED_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        while not pc.describe_index(INDEX_NAME).status["ready"]:
            time.sleep(1)
        print("Index ready.")
    else:
        print(f"Index '{INDEX_NAME}' already exists.")


def upsert_batch(index, embeddings_model, batch: list, batch_num: int, total: int) -> None:
    """Embed and upsert one batch of LangChain Document objects into Pinecone."""
    texts = [doc.page_content for doc in batch]
    vectors = embeddings_model.embed_documents(texts)

    records = [
        {
            "id": f"doc-{batch_num}-{i}",
            "values": vec,
            "metadata": {"text": text, **doc.metadata},
        }
        for i, (text, vec, doc) in enumerate(zip(texts, vectors, batch))
    ]
    index.upsert(vectors=records)
    print(f"  Uploaded batch {batch_num}/{total} ({len(batch)} chunks)")


async def ingest_chunks_async(chunks: list, pc: Pinecone, embeddings_model) -> None:
    """Process chunks in small batches with async delays between each batch
    to avoid hitting Gemini's free-tier embedding rate limit."""
    index = pc.Index(INDEX_NAME)
    batches = [chunks[i : i + BATCH_SIZE] for i in range(0, len(chunks), BATCH_SIZE)]
    total = len(batches)
    print(f"Ingesting {len(chunks)} chunks in {total} batches (batch size={BATCH_SIZE})…")

    loop = asyncio.get_event_loop()
    for idx, batch in enumerate(batches, start=1):
        # Run the blocking embed+upsert in a thread pool so the event loop stays free.
        await loop.run_in_executor(
            None,
            lambda b=batch, n=idx: upsert_batch(index, embeddings_model, b, n, total),
        )
        if idx < total:
            print(f"  Sleeping {BATCH_DELAY}s to respect rate limits…")
            await asyncio.sleep(BATCH_DELAY)

    print("Ingestion complete.")


def main() -> None:
    print("=== Begin Ingestion ===")

    # 1. Load and chunk the source document
    chunks = load_and_split()

    # 2. Initialise Pinecone
    pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
    ensure_index(pc)

    # 3. Build embedding model.
    embeddings_model = GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=os.environ["GOOGLE_API_KEY"],
    )

    # 4. Run async ingestion.
    asyncio.run(ingest_chunks_async(chunks, pc, embeddings_model))


if __name__ == "__main__":
    main()