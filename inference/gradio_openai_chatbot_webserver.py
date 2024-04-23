import argparse
import asyncio
import os
from typing import List, Optional
import async_timeout
import gradio as gr
import httpx
from dotenv import load_dotenv
from loguru import logger
import logging
from openai import OpenAI
import gradio as gr
import requests
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)  # Set logging level to INFO

# Initialize argparse
parser = argparse.ArgumentParser(description='Chatbot configuration')
parser.add_argument('--model-url',
                    type=str,
                    default='http://vllm:8001/v1',
                    help='Model URL')
parser.add_argument('-m',
                    '--model',
                    type=str,
                    required=True,
                    help='Model name for the chatbot')
parser.add_argument("--host", type=str, default='0.0.0.0')
parser.add_argument("--port", type=int, default=8002)
parser.add_argument("--query-url", type=str, default='http://rag:8003/query')
args = parser.parse_args()

OPENAI_API_KEY = "EMPTY"
OPENAI_API_BASE = args.model_url
MODEL_NAME = args.model
HOST = args.host
PORT = args.port

# Define the Message class for chat history
class Message(BaseModel):
    role: str
    content: str

async def search_data(query):
    try:
        headers = {"Content-Type": "application/json"}  # Specify the content type
        response = requests.post(args.query_url, json={"query": query}, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            logging.error("Error: Unexpected status code %s while fetching guidelines.", response.status_code)
    except Exception as e:
        logging.error("Error occurred while fetching guidelines: %s", e)
    return ""

async def make_completion(
    messages: List[Message], nb_retries: int = 3, delay: int = 30
) -> Optional[str]:
    """
    Sends a request to the ChatGPT API to retrieve a response based on a list of previous messages.
    """
    header = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}",
    }
  
    try:
        async with async_timeout.timeout(delay=delay):
            async with httpx.AsyncClient(headers=header) as aio_client:
                counter = 0
                keep_loop = True
                while keep_loop:
                    logger.debug(f"Chat/Completions Nb Retries : {counter}")
                    try:
                        resp = await aio_client.post(
                            url=f"{OPENAI_API_BASE}/chat/completions",
                            json={"model": MODEL_NAME, "messages": messages},
                        )
                        logger.debug(f"Status Code : {resp.status_code}")
                        if resp.status_code == 200:
                            return resp.json()["choices"][0]["message"]["content"]
                        else:
                            logger.warning(resp.content)
                            keep_loop = False
                    except Exception as e:
                        logger.error(e)
                        counter = counter + 1
                        keep_loop = counter < nb_retries
    except asyncio.TimeoutError as e:
        logger.error(f"Timeout {delay} seconds !")
    return None

async def predict(input, history):
    """
    Predict the response of the chatbot and complete a running list of chat history.
    """
    user_message = input  # Get the user input message
    
    # Retrieve guidelines based on user input
    rag_message = await search_data(user_message)
    if guideline_message:
        history.append({"role": "user", "content": f"Here is the user input: '{user_message}', and here is RAG search result: {rag_message}"})
    else:
        history.append({"role": "user", "content": f"Here is the user input: '{user_message}'"})
 
    # Generate response from chatbot
    response = await make_completion(history)
    history.append({"role": "assistant", "content": f"Here is the AI response taking into the user input and search result: {response}"})
    
    # Construct messages to display in the UI
    messages_to_display = [
        (history[i]["content"], history[i + 1]["content"])
        for i in range(0, len(history) - 1, 2)
    ]
    
    return messages_to_display, history

"""
Gradio Blocks low-level API that allows to create custom web applications (here our chat app)
"""
with gr.Blocks() as demo:
    logger.info("Starting Demo...")
   
    # Chatbot component
    chatbot = gr.Chatbot(label="RAGDemoGPT")
    
    # Define the state
    state = gr.State([])
  
    # Clinical Question textbox
    with gr.Row():
        txt = gr.Textbox(
            label="Chat with the data", show_label=False, placeholder="Enter your question here here"
        )
    
    # Submit button
    submit_button = gr.Button()
    
    # Event handling
    submit_button.click(predict, [txt, state], [chatbot, state])

demo.launch(server_port=PORT, share=False, server_name=HOST)
