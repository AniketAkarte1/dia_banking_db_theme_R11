"""
Simple test for core/rag.py

This test does NOT require:
- OpenAI
- Azure OpenAI
- Vector Database
- Knowledge Base

It only verifies that RAGEngine correctly orchestrates:
Retriever -> Prompt Builder -> LLM
"""

from core.rag import RAGEngine


# ------------------------------------------------------------------
# Fake implementations
# ------------------------------------------------------------------

def fake_retriever(question: str):
    print("[Retriever] Called")
    return [
        "PAN card is mandatory for KYC.",
        "Customer signature is required."
    ]


def fake_prompt_builder(question: str, document: str, knowledge):
    print("[Prompt Builder] Called")

    return f"""
Question:
{question}

Document:
{document}

Knowledge:
{knowledge}
"""


def fake_llm(prompt: str):
    print("[LLM] Called")
    print("\n----- Prompt Sent to LLM -----")
    print(prompt)
    print("------------------------------\n")

    return "Fake answer generated successfully."


# ------------------------------------------------------------------
# Test
# ------------------------------------------------------------------

rag = RAGEngine(
    retriever=fake_retriever,
    prompt_builder=fake_prompt_builder,
    llm=fake_llm,
)

response = rag.answer(
    question="Is PAN mandatory?",
    document_text="Customer submitted Aadhaar only."
)

print("\n===== FINAL RESPONSE =====")
print("Answer:")
print(response.answer)

print("\nRetrieved Chunks:")
for chunk in response.retrieved_chunks:
    print("-", chunk)

print("\n✅ Test Passed!")