# nvidia_embeddings.py
from openai import OpenAI
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NvidiaEmbeddingService:
    def __init__(self, api_key=None, model_name="nvidia/nv-embedqa-e5-v5"):
        """Initialize the NVIDIA embedding service with the specified model."""
        api_key = api_key or os.getenv("NVIDIA_API_KEY")
        self.client = OpenAI(api_key=api_key, base_url="https://integrate.api.nvidia.com/v1")
        self.model_name = model_name

    def get_embedding(self, text: str):
        """Get embeddings for the given text using NVIDIA's embedding API."""
        if not self.client:
            logger.error("Embedding client not initialized. NVIDIA API key is required.")
            return None

        try:
            response = self.client.embeddings.create(
                input=[text],
                model=self.model_name,
                encoding_format="float",
                extra_body={"input_type": "query", "truncate": "NONE"}
            )
            embedding = response.data[0].embedding
            logger.info("Embedding retrieved successfully.")
            return embedding
        except Exception as e:
            logger.error(f"Failed to get embedding for text: {e}")
            return None
