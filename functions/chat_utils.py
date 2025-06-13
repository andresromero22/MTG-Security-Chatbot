"""Utility functions used by the chatbot script."""

from __future__ import annotations

import os
import re
import subprocess
import sys
import textwrap
import uuid
from typing import List, Optional

import matplotlib.pyplot as plt
from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

__all__ = [
    "build_chat_chain",
    "extract_python_code",
    "remove_python_code_block",
    "execute_and_save_plot",
    "extract_url_from_text",
    "extract_url_from_source_documents",
    "chat_loop",
]


def build_chat_chain(index_dir: str = "./rag_index") -> ConversationalRetrievalChain:
    """Build the conversational retrieval chain used by the chatbot."""
    openai_api_key = os.getenv("OPEN_AI_KEY")
    if not openai_api_key:
        raise RuntimeError("OPEN_AI_KEY environment variable not set")

    embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)
    vectorstore = FAISS.load_local(
        index_dir,
        embedding,
        allow_dangerous_deserialization=True,
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 8})

    template = textwrap.dedent(
        """
        You are an expert assistant for mining tire maintenance safety.

        - Always answer in the same language as the question.
        - If the question is about PPE or EPP, treat it as 'Personal Protective Equipment'.
        - If the question is about the manual, link, or URL for an equipment, return the corresponding Manual URL section.
        - If the user asks for a chart or graph, generate Python matplotlib graph.
        - Use appropriate figure sizes when generating charts (example: figsize=(8, 6)).
        - Do not call plt.show(), the system will handle saving the figure.
        - If the data is not available or in the context, you can say: "I'm sorry, there is not enough data to generate this chart."
        - If you generate Python code, include it in a proper markdown ```python ``` block.
        - Format the answer using Markdown if appropriate.
        - Use numbered lists, bullet points, and bold text where useful.
        - Do not use markdown tables.
        - If the user says "stop", "exit", "bye", "goodbye", "don't say anything", or similar, respond with: "Goodbye!" and do not provide additional information.

        Chat History:
        {chat_history}

        Context:
        {context}

        Question: {question}
        Answer:
        """
    )
    prompt = PromptTemplate(template=template, input_variables=["context", "question"])
    llm = ChatOpenAI(model="gpt-4.1", openai_api_key=openai_api_key)

    question_generator_template = textwrap.dedent(
        """
        Given the following conversation and a follow-up question, rephrase the follow-up question to be a standalone question.

        Chat History:
        {chat_history}

        Follow Up Question: {question}

        Standalone question:
        """
    )
    question_generator_prompt = PromptTemplate(
        template=question_generator_template,
        input_variables=["chat_history", "question"],
    )
    question_generator = LLMChain(llm=llm, prompt=question_generator_prompt)

    llm_chain = LLMChain(llm=llm, prompt=prompt)
    combine_docs_chain = StuffDocumentsChain(
        llm_chain=llm_chain,
        document_variable_name="context",
    )

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer",
    )

    chain = ConversationalRetrievalChain(
        retriever=retriever,
        combine_docs_chain=combine_docs_chain,
        memory=memory,
        question_generator=question_generator,
        return_source_documents=True,
    )
    return chain


def extract_url_from_text(text: str) -> Optional[str]:
    """Extract the first PDF URL found in a text string."""
    patterns = [
        r"^URL:\s*(.+\.pdf)",
        r"(\./manuals/.+?\.pdf)",
        r"located at:\s*(.+\.pdf)",
        r"manual.*?:\s*(.+\.pdf)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None


def extract_url_from_source_documents(source_documents: List) -> Optional[str]:
    """Extract a PDF URL from source documents."""
    for doc in source_documents:
        url = extract_url_from_text(doc.page_content)
        if url:
            return url
    return None


def extract_python_code(text: str) -> Optional[str]:
    """Return Python code from a markdown block in ``text``."""
    match = re.search(r"```python(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None


def remove_python_code_block(text: str) -> str:
    """Remove Python code blocks from ``text``."""
    return re.sub(r"```python.*?```", "", text, flags=re.DOTALL).strip()


os.makedirs("./graphs", exist_ok=True)


def execute_and_save_plot(code_str: str) -> Optional[str]:
    """Execute Python ``code_str`` and save the resulting plot."""
    safe_globals = {"__builtins__": __builtins__, "plt": plt}
    safe_locals: dict = {}
    try:
        plt.style.use("ggplot")
        exec(code_str, safe_globals, safe_locals)
        graph_id = str(uuid.uuid4())
        output_path = f"./graphs/{graph_id}.png"
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()
        return output_path
    except Exception as exc:  # pragma: no cover - runtime errors only
        print(f"⚠️ Error executing generated code: {exc}")
        plt.close()
        return None


def chat_loop(chain: ConversationalRetrievalChain) -> None:
    """Run the interactive chat loop."""
    print("🤖 Chatbot ready. Type your question (type 'exit' to quit):")
    while True:
        user_query = input("\nYou: ")
        if user_query.lower() in {"exit", "quit"}:
            print("👋 Goodbye!")
            break

        response = chain.invoke({"question": user_query})
        response_text = response["answer"]
        source_documents = response.get("source_documents", [])

        python_code = extract_python_code(response_text)
        response_text_cleaned = remove_python_code_block(response_text)
        print(response_text_cleaned)

        if python_code:
            print("\n🖼️ Detected Python code block → executing...")
            code_str = re.sub(r"plt\.savefig\(.*?\)", "", python_code, flags=re.DOTALL)
            graph_path = execute_and_save_plot(code_str)
            if graph_path:
                print(f"\n👉 Generated graph saved here: {graph_path}")
                try:
                    if hasattr(os, "startfile"):
                        os.startfile(graph_path)
                    elif sys.platform == "darwin":
                        subprocess.call(["open", graph_path])
                    else:
                        subprocess.call(["xdg-open", graph_path])
                except Exception as exc:  # pragma: no cover - platform dependant
                    print(f"⚠️ Unable to open image automatically: {exc}")
            else:
                print("\n⚠️ Failed to execute generated code.")

        url_found = extract_url_from_source_documents(source_documents)
        if url_found:
            print(f"\n👉 If you want more details, please refer to the official procedure here: {url_found}")
