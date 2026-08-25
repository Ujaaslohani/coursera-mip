#Testing the retrieval and llm sythesis basic model on mock documents
import os
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
load_dotenv()
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from schemadefine import InsightRecommendation

# -------------------------------------------------------------
# 1. Mock Evidence Data
# -------------------------------------------------------------
MOCK_DOCUMENTS = [
    Document(
        page_content="Question 3 asks: 'Which method directly mitigates high variance in deep networks?' Over 68% of incorrect submissions selected 'Increasing learning rate' rather than 'L2 Regularization' or 'Dropout'.",
        metadata={
            "source_id": "QUIZ_MOD2_Q3",
            "modality": "quiz",
            "location": "Question 3",
        },
    ),
    Document(
        page_content="Several students in thread #412 are confused about why increasing model complexity doesn't solve high variance. A student wrote: 'If the training error is 1% and validation error is 35%, why wouldn't making the network larger fix it?'",
        metadata={
            "source_id": "FORUM_THREAD_412",
            "modality": "discussion",
            "location": "Post #1 to #5",
        },
    ),
    Document(
        page_content="In this clip, the instructor explains the difference between bias and variance, but skips directly from defining high variance to gradient descent tuning without showing the effect of weight decay on weight matrices.",
        metadata={
            "source_id": "VID_REG_02",
            "modality": "video",
            "location": "04:12 - 05:40",
        },
    ),
    Document(
        page_content="Slide 14 lists regularization techniques: Dropout, L1/L2 Norms, Early Stopping, and Data Augmentation. The slide lacks visual diagrams comparing high variance vs. high bias decision boundaries.",
        metadata={
            "source_id": "SLIDE_DECK_W2",
            "modality": "slide",
            "location": "Slide 14",
        },
    ),
]

# -------------------------------------------------------------
# 3. Grounded LLM Synthesis Engine
# -------------------------------------------------------------
SYSTEM_PROMPT = """
You are the Multimodal Intelligence Assistant for Coursera course operations.
Analyze the provided RETRIEVED EVIDENCE regarding learner friction.

STRICT RULES:
1. ONLY make claims directly supported by the RETRIEVED EVIDENCE below.
2. Every item in 'citations' must specify the source_id, modality, and location from the evidence.
3. If the evidence is incomplete or ambiguous, set confidence_level to 'LOW' or 'MEDIUM'.

RETRIEVED EVIDENCE:
{context}
"""

def generate_multimodal_insight(
    user_query: str, mock_docs: list[Document] | None = None
) -> InsightRecommendation:
    # Use mock documents if provided, otherwise retrieve from Qdrant
    if mock_docs is not None:
        print("[Mock Mode] Using in-memory mock document chunks...")
        retrieved_docs = mock_docs
    else:
        # Placeholder for live Qdrant retriever call
        raise NotImplementedError("Live Qdrant retrieval is bypassed in mock mode.")

    # Format Document Context
    context_blocks = []
    for doc in retrieved_docs:
        meta = doc.metadata
        source_id = meta.get("source_id", meta.get("asset_id", "UNKNOWN"))
        modality = meta.get("modality", "text")
        location = meta.get("location", meta.get("timestamp", "N/A"))

        context_blocks.append(
            f"- [Source: {source_id} | Modality: {modality} | Location: {location}]\n"
            f"  Content: {doc.page_content}"
        )

    context_str = "\n\n".join(context_blocks)

    # model_name = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
    structured_llm = llm.with_structured_output(InsightRecommendation)

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", "Educator Question: {query}"),
    ])

    chain = prompt_template | structured_llm

    print("[Synthesis] Generating structured insight pack with citations...")
    insight_pack: InsightRecommendation = chain.invoke({
        "context": context_str,
        "query": user_query,
    })

    return insight_pack    


if __name__ == "__main__":
    test_query = (
        "Why are students struggling with Quiz Question 3 on Overfitting?"
    )

    try:
        result = generate_multimodal_insight(
            user_query=test_query, mock_docs=MOCK_DOCUMENTS
        )
        print("\n=== GENERATED INSIGHT PACK (Valid JSON) ===")
        print(result.model_dump_json(indent=2))
    except Exception as e:
        print(f"\nError running pipeline: {e}")
