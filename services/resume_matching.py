from openai import OpenAI
import logging
import numpy as np
import os
import torch  # Import PyTorch for GPU compatibility
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

class ResumeMatchingService:
    def __init__(self, device=None):
        """Initialize the OpenAI client for NVIDIA API with the provided API key."""
        try:
            self.client = OpenAI(
                api_key=os.getenv("NVIDIA_API_KEY"),  # Load API key from environment
                base_url="https://integrate.api.nvidia.com/v1"
            )
            self.model_name = "nvidia/nv-embedqa-e5-v5"
            self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
            logger.info("ResumeMatchingService initialized on device: %s", self.device)
        except Exception as e:
            logger.error(f"Error initializing ResumeMatchingService: {e}")
            raise

    def truncate_text(self, text: str, max_length: int = 512) -> str:
        """Truncate text to a specified maximum length."""
        return text[:max_length]

    def get_embedding(self, text: str) -> Optional[torch.Tensor]:
        """Generate embeddings for a given text using NVIDIA's model."""
        try:
            truncated_text = self.truncate_text(text)
            response = self.client.embeddings.create(
                input=[truncated_text],
                model=self.model_name,
                encoding_format="float",
                extra_body={"input_type": "query", "truncate": "NONE"}
            )
            # Accessing the embedding from the correct response structure
            embedding = response.data[0].embedding
            # Convert the embedding to a PyTorch tensor and move to the specified device
            return torch.tensor(embedding, dtype=torch.float32).to(self.device)
        except Exception as e:
            logger.error(f"Failed to get embedding for text: {e}")
            return None

    def calculate_match_score(self, job_description: str, resume_text: str) -> float:
        """Calculate the similarity score between job description and resume using NVIDIA embeddings."""
        try:
            # Get embeddings for both texts
            job_embedding = self.get_embedding(job_description)
            resume_embedding = self.get_embedding(resume_text)

            if job_embedding is None or resume_embedding is None:
                logger.error("One or both embeddings could not be retrieved.")
                return 0.0

            # Calculate cosine similarity using PyTorch (on GPU if available)
            similarity = torch.dot(job_embedding, resume_embedding) / (
                torch.norm(job_embedding) * torch.norm(resume_embedding)
            )
            return round(similarity.item() * 100, 2)  # Convert to percentage and return as float
        except Exception as e:
            logger.error(f"Error in calculating match score: {e}")
            return 0.0
