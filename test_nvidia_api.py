from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file (make sure NVIDIA_API_KEY and NVIDIA_API_KEY_NEW are set)
load_dotenv()

def test_embedding_api():
    """Test the NVIDIA embedding API for resume matching."""
    try:
        embedding_client = OpenAI(
            api_key=os.getenv("NVIDIA_API_KEY"),
            base_url="https://integrate.api.nvidia.com/v1"
        )
        
        # Sample input for embedding API
        response = embedding_client.embeddings.create(
            input=["What is the capital of France?"],
            model="nvidia/nv-embedqa-e5-v5",
            encoding_format="float",
            extra_body={"input_type": "query", "truncate": "NONE"}
        )
        
        # Output the embedding result
        embedding = response.data[0].embedding
        print("Embedding API call successful. Embedding received:", embedding[:10], "...")  # Display first 10 values
        return True
    
    except Exception as e:
        print("Error during Embedding API call:", e)
        return False

def test_chat_api():
    """Test the NVIDIA chat API for generating responses."""
    try:
        chat_client = OpenAI(
            api_key=os.getenv("NVIDIA_API_KEY_NEW"),
            base_url="https://integrate.api.nvidia.com/v1"
        )
        
        # Sample input for chat API
        completion = chat_client.chat.completions.create(
            model="nvidia/llama-3.1-nemotron-70b-instruct",
            messages=[{"role": "user", "content": "Write a limerick about the wonders of GPU computing."}],
            temperature=0.5,
            top_p=1,
            max_tokens=1024,
            stream=True
        )
        
        # Stream and print the chat response
        print("Chat API response:")
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")
        print("\nChat API call completed successfully.")
        return True

    except Exception as e:
        print("Error during Chat API call:", e)
        return False

# Run the tests
if __name__ == "__main__":
    print("Testing NVIDIA Embedding API...")
    embedding_success = test_embedding_api()
    print("\nTesting NVIDIA Chat API...")
    chat_success = test_chat_api()

    # Summary of test results
    if embedding_success and chat_success:
        print("\nAll NVIDIA API tests passed.")
    else:
        print("\nOne or more NVIDIA API tests failed.")
