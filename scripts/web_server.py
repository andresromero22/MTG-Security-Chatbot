from __future__ import annotations

import re
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from functions.chat_utils import (
    build_chat_chain,
    extract_python_code,
    remove_python_code_block,
    execute_and_save_plot,
    extract_url_from_source_documents,
)

app = FastAPI()
chain = build_chat_chain()


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat(request: ChatRequest):
    response = chain.invoke({"question": request.message})
    answer = response["answer"]
    source_docs = response.get("source_documents", [])

    code = extract_python_code(answer)
    clean_text = remove_python_code_block(answer)
    image_path = None
    if code:
        code_str = re.sub(r"plt\.savefig\(.*?\)", "", code, flags=re.DOTALL)
        image_path = execute_and_save_plot(code_str)

    url_found = extract_url_from_source_documents(source_docs)
    return {
        "response": clean_text,
        "image": image_path,
        "url": url_found,
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

