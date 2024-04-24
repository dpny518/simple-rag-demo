# LLM with RAG Demonstration

This repository features a Docker Compose setup designed to demonstrate a language learning model (LLM) augmented with Retrieval-Augmented Generation (RAG). It utilizes components including vLLM, Ollama, and Gradio for the user interface. This setup specifically uses a fine-tuned model located in the ./model folder. We are leveraging the OpenAI server from vLLM, which currently does not support custom models for LlamaIndex, necessitating the use of Ollama for the LlamaIndex functionality.

"Currently, LlamaIndex does not allow the use of custom models with their OpenAI class because it requires specific metadata from the model name." - See more: https://docs.llamaindex.ai/en/stable/api_reference/llms/openai_like/

For scenarios leveraging an openai supported models without fine-tuning, the process could be simplified: vLLM could then be used for both LlamaIndex retrieval and LLM response generation.

Alternatively, we could entirely omit vLLM and utilize Ollama for LlamaIndex, RAG, and LLM query functionalities, but this would require importing the model into Ollama:
```
https://github.com/ollama/ollama/blob/main/docs/modelfile.md
```




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



