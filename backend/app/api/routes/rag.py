import os

from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.core.config import settings
from app.utils import unique_filename

router = APIRouter()


class InputString(BaseModel):
    """
    A simple input model for a text string.
    """

    text: str


@router.post("/query")
async def query(input_string: InputString):
    """
    A simple query endpoint that converts the input text to uppercase.
    """
    # Example processing: Convert to uppercase
    processed_text = input_string.text.upper()
    return {"original_text": input_string.text, "processed_text": processed_text}


@router.post("/uploadfile/")
async def create_upload_file(
    file: UploadFile = File(
        description="A file to be stored into vectorDB as UploadFile"
    ),
    metadata: UploadFile = File(None)
):
    """Upload for processing"""
    # Generate unique file paths for the PDF and JSON metadata
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Uploaded file must be a valid PDF")
    if metadata and not metadata.filename.lower().endswith('.json'):
        raise HTTPException(status_code=400, detail="Metadata file must be a valid JSON")

    fname = unique_filename(file.filename)
    rootfilename, _ = os.path.splitext(fname)
    unique_name = unique_filename(rootfilename)

    pdf_filename = f"{unique_name}.pdf"
    pdf_path = os.path.join(settings.UPLOAD_DIR, pdf_filename)

    metadata_filename = f"{unique_name}.json"
    metadata_path = (
        os.path.join(settings.UPLOAD_DIR, metadata_filename)
        if metadata
        else None
    )

    # Save the PDF file
    with open(pdf_path, "wb") as buffer:
        buffer.write(await file.read())

    # Save the metadata JSON file, if provided
    if metadata:
        with open(metadata_path, "wb") as buffer:
            buffer.write(await metadata.read())

    # Check if the uploaded file is a PDF
    #if file.filename.endswith(".pdf"):
        # Run PDF processing in the background
    #    background_tasks.add_task(process_pdf, pdf_path, model_lst, metadata_path)

    return {
        "filename": file.filename,
        "metadata_filename": metadata.filename if metadata else None,
        "status": "Uploaded successfully",
    }


"""
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import streamlit as st
import json
import faiss
import numpy as np

model = "open-mixtral-8x7b"
mistral_api_key = st.secrets["MISTRAL_API_KEY"]
client = MistralClient(api_key=mistral_api_key)

st.title("Assistant ChatBot catalogue 2024")

def load_json(rep:str):
    f = open(rep, encoding='UTF-8')
    return json.load(f)

def split_chunk(data, chunk_size):
    data_str = [json.dumps(entry) for entry in data]
    chunk_size = chunk_size
    chunks = [data_str[i:i + chunk_size] for i in range(0, len(data_str), chunk_size)]
    print(f"Nb. chunks = {len(chunks)}")
    return chunks

def get_text_embedding(input):
    embeddings_batch_response = client.embeddings(
          model='mistral-embed',
          input=input
      )
    return embeddings_batch_response.data[0].embedding

def load_vector_db(text_embedded):
    d = text_embedded.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(text_embedded)
    return index

def find_similar_chunk(index, question_embeddings, chunks):
    D, I = index.search(question_embeddings, k=2) # distance, index
    return [chunks[i] for i in I.tolist()[0]]

def prompt_chat(retrieved_chunk, question):
    return "
    Les informations contextuelles sont les suivantes.
    ---------------------
    {retrieved_chunk}
    ---------------------
    Compte tenu des informations contextuelles et sans connaissances préalables,
    réponds en français à la question suivante de manière concise.
    Utilise des listes pour plus de lisibilité.
    Question: {question}
    Réponse:"


# Chargement des données
data = load_json('catalogue_2024.json')
chunks = split_chunk(data, 3)
text_embeddings = np.load("catalogue_embeddings.npy")
index = load_vector_db(text_embeddings)

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Comment puis-je vous aider?"}]
    st.session_state["History"] = []
    st.session_state.History.append(ChatMessage(role="assitant", content="Comment puis-je vous aider?"))

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    question_embeddings = np.array([get_text_embedding(prompt)])
    retrieved_chunk = find_similar_chunk(index, question_embeddings, chunks)
    p = prompt_chat(retrieved_chunk=retrieved_chunk, question=prompt)

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.History.append(ChatMessage(role="user", content=p))
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        for response in client.chat_stream(
            model=model,
            messages=st.session_state.History[1:]
        ):
            full_response += (response.choices[0].delta.content or "")
            message_placeholder.markdown(full_response + "|")

        message_placeholder.markdown(full_response)

        st.session_state.History.append(ChatMessage(role="assistant", content=full_response))
        st.session_state.messages.append({"role": "assistant", "content": full_response})

"""
