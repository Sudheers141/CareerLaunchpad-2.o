from openai import OpenAI
import os
import logging
import torch  # Import PyTorch for GPU compatibility
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NvidiaEmbeddingService:
    def __init__(self, api_key=None, model_name="nvidia/nv-embedqa-e5-v5", device=None):
        """Initialize the NVIDIA embedding service with the specified model and set up GPU compatibility."""
        api_key = api_key or os.getenv("NVIDIA_API_KEY")
        self.client = OpenAI(api_key=api_key, base_url="https://integrate.api.nvidia.com/v1")
        self.model_name = model_name
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info("NvidiaEmbeddingService initialized on device: %s", self.device)

    def get_embedding(self, text: str) -> torch.Tensor:
        """Get embeddings for the given text using NVIDIA's embedding API and move it to the GPU if available."""
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
            # Convert the embedding to a PyTorch tensor and move it to the specified device
            embedding_tensor = torch.tensor(embedding, dtype=torch.float32).to(self.device)
            logger.info("Embedding retrieved and moved to device %s successfully.", self.device)
            return embedding_tensor
        except Exception as e:
            logger.error(f"Failed to get embedding for text: {e}")
            return None
