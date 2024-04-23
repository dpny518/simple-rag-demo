from flask import Flask, request, jsonify
from llama_index import (
    ServiceContext,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    set_global_service_context,
)
from llama_index.llms import Ollama

app = Flask(__name__)

# Initialize Ollama and other required components
# Override the base_url parameter to point to the Docker container
ollama_base_url = "http://ollama:11434"  # Assuming 'ollama' is the name of the Docker container
llm = Ollama(model="tinyllama", base_url=ollama_base_url)
#llm = Ollama(model="tinyllama")
service_context = (
    ServiceContext
    .from_defaults(
        llm=llm, 
        embed_model="local:BAAI/bge-small-en-v1.5", 
        chunk_size=300
    )
)
set_global_service_context(service_context)

# Create VectorStoreIndex
documents = SimpleDirectoryReader(input_dir='/data', required_exts=[".pdf"]).load_data()
storage_context = StorageContext.from_defaults()
nodes = service_context.node_parser.get_nodes_from_documents(documents)
storage_context.docstore.add_documents(nodes)
index = VectorStoreIndex.from_documents(documents, storage_context=storage_context, llm=llm)

# Create query engine from index
query_engine = index.as_query_engine()

# Endpoint to handle POST requests
@app.route('/query', methods=['POST'])
def query():
    # Get the JSON data from the request
    data = request.json
    
    # Extract the query from the JSON data
    query_text = data.get('query', '')
    
    # Perform the query using the query engine
    response = query_engine.query(query_text)
    
    # Format the response as JSON
    result = {
        'query': query_text,
        'response': response
    }
    
    # Return the JSON response
     #return jsonify(result)
    # Return the text response
    return str(response)
# Run the Flask app on port 8003
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8003)
