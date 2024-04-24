# LLM with RAG Demonstration

This repository features a Docker Compose setup designed to demonstrate a simple language learning model (LLM) augmented with Retrieval-Augmented Generation (RAG). It utilizes various components including vLLM, Ollama, and Gradio for the user interface. This setup specifically assumes the use of a fine-tuned model located in the ./model folder. We are using the open ai server from vllm, so we can not use custom models for llama index, thus we are using ollama for the llamaindex. If we don't want the open ai compatabile features from vllm server we could use the non open ai server and just use vllm for both llama index and querying the llm. Or We could do this without vllm and just use ollama for llamaindex and rag as well as the llm for query but then we would need to import the model into ollama 
https://github.com/ollama/ollama/blob/main/docs/modelfile.md
```If 
Currently, llama_index prevents using custom models with their OpenAI class because they need to be able to infer some metadata from the model name.
https://docs.llamaindex.ai/en/stable/api_reference/llms/openai_like/
```
leveraging an open-source model without fine-tuning, the process could be simplified: vLLM could then be used for both LlamaIndex retrieval and LLM response generation.

## Components

### vLLM Service
- **Description**: The vLLM service serves a fine-tuned model located in the `./model` directory.
- **Technical Details**: Utilizes the `vllm/vllm-openai:latest` image to run the model on a specified port with GPU support.
- **Configuration**:
  - Image: vllm/vllm-openai:latest
  - Ports: 8001
  - Volumes: Maps the local `./model` directory to `/tmp/local_model` in the container.

### Gradio
- **Description**: Gradio is used to provide a user interface for interacting with the LLM.
- **Build Context**: Root directory with the Dockerfile named `DockerfileGradio`.
- **Ports**: 8002

### RAG
- **Description**: Handles retrieval-augmented generation, leveraging both Ollama and LlamaIndex for optimal functionality.
- **Build Context**: `./RAG` with the Dockerfile named `DockerfileRag`.
- **Ports**: 8003
- **Volumes**: Maps the `./RAG/data` directory to `/data` in the container.
- **Note**: The integration with LlamaIndex through Ollama is crucial as LlamaIndex alone does not support custom models for vLLM 

### Ollama
- **Description**: Ollama is used for providing the LlamaIndex functionality as RAG requires retrieval support which is provided by LlamaIndex.
- **Image**: ollama/ollama
- **Configuration**: Ensures that the Ollama service always pulls the latest image and restarts unless manually stopped.
- **Ports**: 11434
- **Volumes**: Persistent volume for Ollama's data.

## Network
All services are connected via a custom network named `vllm-network` to ensure they can communicate internally without exposure to external networks.

## Volumes
A dedicated volume named `ollama` is used to store Ollama's data persistently.

## Usage
To start the demonstration, ensure Docker is installed and run the following command from the root of this repository:
```bash
docker-compose up
```



