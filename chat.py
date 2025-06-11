import json
import re
from langchain.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.memory import ConversationBufferMemory

# Load API key
with open("./resources/api_key.txt", "r") as f:
    openai_api_key = f.read().strip()

# Load FAISS index
embedding = OpenAIEmbeddings(openai_api_key=openai_api_key)
vectorstore = FAISS.load_local(
    "./rag_index",
    embedding,
    allow_dangerous_deserialization=True
)
retriever = vectorstore.as_retriever(search_kwargs={"k": 8})

# Your main PromptTemplate
template = """
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
- If the user says "stop", "exit", "bye", "goodbye", "don't say anything", or similar, respond with: "Goodbye!" and do not provide additional information.

Chat History:
{chat_history}

Context:
{context}

Question: {question}
Answer:
"""

prompt = PromptTemplate(
    template=template,
    input_variables=["context", "question"]
)

# Create LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=openai_api_key)

# Question generator PromptTemplate
question_generator_template = """
Given the following conversation and a follow-up question, rephrase the follow-up question to be a standalone question.

Chat History:
{chat_history}

Follow Up Question: {question}

Standalone question:
"""

question_generator_prompt = PromptTemplate(
    template=question_generator_template,
    input_variables=["chat_history", "question"]
)

# Question generator chain
question_generator = LLMChain(llm=llm, prompt=question_generator_prompt)


# Create combine_docs_chain (StuffDocumentsChain)
llm_chain = LLMChain(llm=llm, prompt=prompt)
combine_docs_chain = StuffDocumentsChain(
    llm_chain=llm_chain,
    document_variable_name="context"
)

# Setup memory for chat history
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="answer"  # <--- this solves your error!
)

# Setup ConversationalRetrievalChain (stable)
conversational_chain = ConversationalRetrievalChain(
    retriever=retriever,
    combine_docs_chain=combine_docs_chain,
    memory=memory,
    question_generator=question_generator,
    return_source_documents=True
)

# Helper: extract URL from text
def extract_url_from_text(text):
    match = re.search(r'^URL:\s*(.+\.pdf)', text, re.MULTILINE)
    if match:
        return match.group(1).strip()

    match = re.search(r'(\./manuals/.+?\.pdf)', text)
    if match:
        return match.group(1).strip()

    match = re.search(r'located at:\s*(.+\.pdf)', text)
    if match:
        return match.group(1).strip()

    match = re.search(r'manual.*?:\s*(.+\.pdf)', text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    return None

# Helper: extract URL from source documents
def extract_url_from_source_documents(source_documents):
    for doc in source_documents:
        url = extract_url_from_text(doc.page_content)
        if url:
            return url
    return None


# Check if response contains a Python code block
def extract_python_code(text):
    match = re.search(r'```python(.*?)```', text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

import matplotlib.pyplot as plt
import os
import uuid

# Create graphs/ folder if not exists
os.makedirs("./graphs", exist_ok=True)

def execute_and_save_plot(code_str):
    # Prepare safe globals
    safe_globals = {
        "__builtins__": __builtins__,
        "plt": plt
    }
    safe_locals = {}

    try:
        # Optional: set a clean style
        plt.style.use('ggplot')  # or 'ggplot', 'seaborn-darkgrid', etc.

        # Execute code
        exec(code_str, safe_globals, safe_locals)

        # Save plot
        graph_id = str(uuid.uuid4())
        output_path = f"./graphs/{graph_id}.png"
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        return output_path

    except Exception as e:
        print(f"⚠️ Error executing generated code: {e}")
        plt.close()
        return None

def remove_python_code_block(text):
    cleaned_text = re.sub(r'```python.*?```', '', text, flags=re.DOTALL).strip()
    return cleaned_text

# Main chat loop
print("🤖 Chatbot ready. Type your question (type 'exit' to quit):")
while True:
    user_query = input("\nYou: ")
    if user_query.lower() in ["exit", "quit"]:
        print("👋 Goodbye!")
        break

    # Provide RAG-based answer with memory
    response = conversational_chain.invoke({"question": user_query})

    response_text = response["answer"]
    source_documents = response.get("source_documents", [])

    # Extract code if present
    python_code = extract_python_code(response_text)
    response_text_cleaned = remove_python_code_block(response_text)

    # Print clean answer (no code shown)
    print(response_text_cleaned)

    # Execute code if present
    if python_code:
        print("\n🖼️ Detected Python code block → executing...")
        # Remove any plt.savefig(...) from code
        code_str = re.sub(r'plt\.savefig\(.*?\)', '', python_code, flags=re.DOTALL)
        graph_path = execute_and_save_plot(code_str)
        if graph_path:
            print(f"\n👉 Generated graph saved here: {graph_path}")
            # Automatically open the image (Windows)
            os.startfile(graph_path)
        else:
            print("\n⚠️ Failed to execute generated code.")

    # Extract URL if present
    url_found = extract_url_from_source_documents(source_documents)
    if url_found:
        print(f"\n👉 If you want more details, please refer to the official procedure here: {url_found}")
