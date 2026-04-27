import sys
import os

sys.path.append(os.getcwd())

from logic.agent_tools import crop_analyzer


import asyncio
import os
import time

from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from operator import itemgetter

#import sys
#sys.path.append("../")
#from logic import agent_tools


load_dotenv()

EMBEDDING_MODEL = "gemini-embedding-001"
INDEX_NAME = os.environ["INDEX_NAME"]
TEXT_FILE = os.path.join(os.path.dirname(__file__), "stardew_crop_descriptions.txt")

# Free-tier rate limit: 1,500 requests/min
# batch size and inter-batch sleep.
BATCH_SIZE = 5      # documents per batch
BATCH_DELAY = 2.0   # seconds between batches
EMBED_DIMENSION = 3072  # gemini-embedding-001 output dimension
TOP_K = 4

embeddings = GoogleGenerativeAIEmbeddings(
model=EMBEDDING_MODEL,
google_api_key=os.environ["GOOGLE_API_KEY"],
)

llm = ChatGoogleGenerativeAI(
model="gemini-2.5-flash",
google_api_key=os.environ["GOOGLE_API_KEY"],
temperature=0.2,
)

llm.bind_tools([crop_analyzer])

pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index(INDEX_NAME)

prompt_template = ChatPromptTemplate.from_template(
    """You are a helpful but neutral summarizer.
You should speak on how a given crop compares to others for the given time that it is being planted.
Answer the question using ONLY the context provided below.
If the answer is not in the context, say so clearly.

Context:
{context}

Question:
{question}

Answer:"""
)


def load_and_split() -> list:
    loader = TextLoader(TEXT_FILE)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
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


def retrieve_docs(query: str) -> list[Document]:
    """Embed the query and search Pinecone; return a list of LangChain Documents."""
    query_vector = embeddings.embed_query(query)
    results = index.query(vector=query_vector, top_k=TOP_K, include_metadata=True)
    docs = []
    for match in results.get("matches", []):
        text = match["metadata"].get("text", "")
        meta = {k: v for k, v in match["metadata"].items() if k != "text"}
        docs.append(Document(page_content=text, metadata=meta))
    return docs


def format_docs(docs: list[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def build_rag_chain():
    retriever = RunnableLambda(lambda q: retrieve_docs(q))
 
    chain = (
        RunnablePassthrough.assign(
            context=itemgetter("question") | retriever | format_docs
        )
        | prompt_template
        | llm
        | StrOutputParser()
    )
    return chain


def load_model() -> None:
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

    # 5. Create rag chain model.
    global rag_chain
    rag_chain = build_rag_chain()


def query_model(crop_type: str, season: str, day: int) -> str:
    """
    Calculates important financial information about a crop
    Args:
    crop_type (str): The name of the crop to be queried,
    season (str): either "Spring", "Summer", "Fall", or "Winter",
    day (int): day in month ranging from 1 to 28
    
    Returns:
    str: response from model
    """

    question = f"How viable is {crop_type} to plant on {season} {day} relative to other plants in {season}? Each season lasts 28 days."
    return rag_chain.invoke({"question": question})


    


if __name__ == "__main__":
    load_model()

    inp = input("Enter 'crop season date' to query or 'exit' to exit: ")
    while inp.lower().strip() != 'exit':
        split_inp = inp.split()
        print(query_model(split_inp[0], split_inp[1], int(split_inp[2])))
        inp = input("Enter 'crop season date' to query or 'exit' to exit: ")
