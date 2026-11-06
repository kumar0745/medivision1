from .knowledge import retrieve
from ..core.config import settings

async def answer_question(question: str):
    # Retrieval step: select the most relevant curated reference snippets.
    docs = retrieve(question)
    context = "\n\n".join(
        f"{d['title']} ({d['source']}): {d['text']} Source: {d['url']}"
        for d in docs
    )
    fallback = (
        "I can share general health information, but I cannot diagnose, prescribe, or determine whether a condition is present. "
        "Please use the references below as educational starting points and speak with a qualified clinician for personal advice.\n\n"
        + (context if context else "I could not find a directly relevant item in the local reference library. Please consult a qualified healthcare professional.")
    )
    if not settings.openai_api_key:
        return {"answer": fallback, "mode": "retrieval-only", "sources": docs}
    try:
        # LangChain handles the model invocation; the API key remains server-side.
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import SystemMessage, HumanMessage
        model = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0.2,
        )
        system = (
            "You are MediVision AI, a cautious health education assistant. You are not a clinician. "
            "Do not diagnose, prescribe, or claim certainty. Ground factual health statements only in the supplied reference context. "
            "If context is insufficient, say so. Encourage professional care and urgent local emergency help for potentially life-threatening symptoms. "
            "Do not claim to call emergency services. Use plain language.\n\n"
            "Retrieved reference context:\n" + context
        )
        response = await model.ainvoke([
            SystemMessage(content=system),
            HumanMessage(content=question),
        ])
        return {"answer": str(response.content), "mode": "langchain-rag", "sources": docs}
    except Exception:
        return {"answer": fallback, "mode": "retrieval-fallback", "sources": docs}
