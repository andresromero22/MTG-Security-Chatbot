from __future__ import annotations

import re
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import shutil
import uvicorn

from functions.chat_utils import (
    build_chat_chain,
    extract_python_code,
    remove_python_code_block,
    execute_and_save_plot,
    extract_url_from_source_documents,
)

manual_dir = "./manuals"

app = FastAPI()
app.mount("/manuals", StaticFiles(directory=manual_dir), name="manuals")

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


@app.get("/manuals")
def list_manuals():
    files = [f for f in os.listdir(manual_dir) if f.lower().endswith(".pdf")]
    return {"files": files}


@app.post("/manuals")
async def upload_manual(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    dest_path = os.path.join(manual_dir, file.filename)
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"success": True}


@app.delete("/manuals/{filename}")
def delete_manual(filename: str):
    file_path = os.path.join(manual_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    os.remove(file_path)
    return {"success": True}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

