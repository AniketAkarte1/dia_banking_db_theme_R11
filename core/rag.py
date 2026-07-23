"""
core/rag.py

Retrieval-Augmented Generation (RAG) Engine

Responsibilities
----------------
1. Retrieve relevant knowledge from the knowledge base.
2. Build the final prompt.
3. Send the prompt to the LLM.
4. Return the generated answer.

This module should NOT know:
- how embeddings work
- how OpenAI/Azure OpenAI works
- how Streamlit works
"""

from dataclasses import dataclass
from typing import Callable
import logging

import services.knowledge_base as kb
import core.prompts as prompts
import core.llm as llm


logger = logging.getLogger(__name__)


@dataclass
class RAGResponse:
    """
    Standard response returned by the RAG engine.
    """

    answer: str
    retrieved_chunks: list[str]


class RAGEngine:
    """
    Main Retrieval-Augmented Generation engine.
    """

    def __init__(
        self,
        retriever: Callable[[str], list[str]] = kb.search_knowledge,
        prompt_builder: Callable[..., str] = prompts.build_chat_prompt,
        llm_client: Callable[[str], str] = llm.generate_response,
    ) -> None:
        """
        Parameters
        ----------
        retriever
            Function responsible for retrieving relevant knowledge.

        prompt_builder
            Function responsible for building the final prompt.

        llm_client
            Function responsible for generating the final answer.
        """

        self.retriever = retriever
        self.prompt_builder = prompt_builder
        self.llm_client = llm_client

        logger.info("RAG Engine initialized")

    def retrieve(self, question: str) -> list[str]:
        """
        Retrieve relevant knowledge base chunks.
        """

        logger.info("Searching knowledge base")

        return self.retriever(question) or []

    def build_prompt(
        self,
        question: str,
        document_text: str,
        knowledge: list[str],
    ) -> str:
        """
        Build the final prompt for the LLM.
        """

        logger.info("Building prompt")

        return self.prompt_builder(
            question=question,
            document=document_text,
            knowledge=knowledge,
        )

    def generate(self, prompt: str) -> str:
        """
        Generate the final response using the LLM.
        """

        logger.info("Generating response")

        return self.llm_client(prompt)

    def answer(
        self,
        question: str,
        document_text: str = "",
    ) -> RAGResponse:
        """
        Execute the complete Retrieval-Augmented Generation pipeline.
        """

        try:

            # Step 1: Retrieve relevant knowledge
            knowledge = self.retrieve(question)

            # Step 2: Build prompt
            prompt = self.build_prompt(
                question=question,
                document_text=document_text,
                knowledge=knowledge,
            )

            # Step 3: Generate answer
            answer = self.generate(prompt)

            # Step 4: Return response
            return RAGResponse(
                answer=answer,
                retrieved_chunks=knowledge,
            )

        except Exception:
            logger.exception("RAG pipeline failed")

            return RAGResponse(
                answer="Sorry, something went wrong while processing your request.",
                retrieved_chunks=[],
            )
        