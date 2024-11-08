# feedback.py
import logging
import numpy as np
from typing import Dict, List
from services.nvidia_embeddings import NvidiaEmbeddingService  # Correct import
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class FeedbackGenerator:
    def __init__(self):
        try:
            # Initialize EmbeddingService with the embedding model
            self.embedding_service = NvidiaEmbeddingService(model_name="nvidia/nv-embedqa-e5-v5")
            logger.info("FeedbackGenerator initialized.")
        except Exception as e:
            logger.error(f"Error initializing FeedbackGenerator: {e}")
            raise

    def get_embedding(self, text: str):
        """Generate embeddings for a given text using EmbeddingService."""
        try:
            return self.embedding_service.get_job_description_embedding(text)
        except Exception as e:
            logger.error(f"Failed to get embedding for text: {e}")
            raise

    def calculate_keyword_match(self, job_description: str, resume_text: str) -> Dict:
        """Calculate the similarity score for keywords using NVIDIA embeddings."""
        try:
            job_embedding = self.get_embedding(job_description)
            resume_embedding = self.get_embedding(resume_text)
            similarity = np.dot(job_embedding, resume_embedding) / (np.linalg.norm(job_embedding) * np.linalg.norm(resume_embedding))
            return {"match_score": round(similarity * 100, 2)}
        except Exception as e:
            logger.error(f"Error in calculating keyword match: {e}")
            return {"match_score": 0.0}

    def generate_feedback(self, job_description: str, resume_text: str, match_score: float) -> Dict:
        """Generate feedback based on match score and content analysis."""
        missing_keywords = self.analyze_keywords(job_description, resume_text)

        feedback = {
            "overall_match": {
                "assessment": f"The resume matches the job description with a score of {match_score}."
            },
            "keywords_analysis": {
                "missing_keywords": missing_keywords
            },
            "detailed_recommendations": self.get_improvement_suggestions()
        }
        return feedback

    def analyze_keywords(self, job_description: str, resume_text: str) -> List[str]:
        """Identify missing keywords from job description in resume."""
        job_keywords = set(job_description.lower().split())
        resume_keywords = set(resume_text.lower().split())
        missing_keywords = list(job_keywords - resume_keywords)
        return missing_keywords[:15]  # Limit to top 15 missing keywords for brevity

    def get_improvement_suggestions(self, feedback: Dict = None) -> List[str]:
        """Provide improvement suggestions based on feedback or return generic suggestions."""
        if feedback:
            return feedback.get("detailed_recommendations", [])
        else:
            return [
                "Consider adding more specific skills related to the job requirements.",
                "Emphasize relevant experience in the job field."
            ]

    def chat_response(self, user_query: str, job_description: str, resume_text: str) -> str:
        """Generate a response for the chatbot based on user query."""
        if "improve" in user_query.lower() or "suggestions" in user_query.lower():
            suggestions = self.get_improvement_suggestions()
            return "Here are some suggestions to improve your resume: " + "; ".join(suggestions)

        elif "keywords" in user_query.lower() or "missing" in user_query.lower():
            missing_keywords = self.analyze_keywords(job_description, resume_text)
            return f"Consider including these keywords: {', '.join(missing_keywords[:5])}"

        elif "match score" in user_query.lower():
            match_data = self.calculate_keyword_match(job_description, resume_text)
            return f"Your resume match score with this job description is: {match_data['match_score']} / 100"

        return "I'm here to help! Please ask specific questions about improving your resume or matching it to the job description."
