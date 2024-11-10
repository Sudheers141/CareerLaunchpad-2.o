# nvidia_chat.py
from openai import OpenAI
import os
import logging
import re
import torch  # Import PyTorch to enable GPU usage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NvidiaChatService:
    def __init__(self, api_key=None, model_name="nvidia/llama-3.1-nemotron-70b-instruct", device=None):
        """
        Initialize the NVIDIA chat service with the specified model and set up GPU compatibility.
        """
        api_key = api_key or os.getenv("NVIDIA_API_KEY_NEW")
        self.client = OpenAI(api_key=api_key, base_url="https://integrate.api.nvidia.com/v1")
        self.model_name = model_name
        # Set the device to GPU if available
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.chat_memory = []  # Initialize chat memory to store conversation history
        logger.info("NvidiaChatService initialized with model: %s on device: %s", self.model_name, self.device)

    def get_chat_response(self, user_query: str, context: dict = None):
        """
        Generate a response from the NVIDIA chat model based on user query and optional context.
        
        Parameters:
        - user_query (str): The query from the user.
        - context (dict): Optional dictionary containing job application details.
        
        Returns:
        - str: The response from the chat model.
        """
        if not self.client:
            logger.error("Chat client not initialized. NVIDIA API key is required.")
            return "Chat service unavailable."

        # Prepare context details to provide to the chat model
        context_message = "You are a helpful assistant for job applications and resume guidance."
        if context:
            logger.info("Received context for chat: %s", context)
            
            # Construct context details, truncating long fields for API constraints
            details = [
                f"Company: {context.get('company', 'N/A')}",
                f"Job Title: {context.get('job_title', 'N/A')}",
                f"Job Description: {context.get('job_description', 'N/A')[:500]}...",  # limit job description
                f"Match Score: {context.get('match_score', 'N/A')}",
                f"Feedback Assessment: {context.get('feedback', {}).get('overall_match', {}).get('assessment', '')}",
                f"Suggestions: {', '.join(context.get('suggestions', [])[:5])}"  # limit suggestions
            ]
            # Add resume text, truncated for length
            resume_text = context.get('resume_text', 'N/A')[:500]
            context_message += f" Here are the details of the job application: {' '.join(details)} Resume: {resume_text}"

        # Store the query in memory
        self.chat_memory.append({"role": "user", "content": user_query})

        try:
            logger.info("Sending query to NVIDIA chat API with context: %s", context_message)
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "system", "content": context_message}] + self.chat_memory,
                temperature=0.2,
                max_tokens=1024
            )

            if response and response.choices:
                bot_response = response.choices[0].message.content
                self.chat_memory.append({"role": "assistant", "content": bot_response})  # Save response in memory
                logger.info("Received response from NVIDIA chat API")
                return self.format_response(bot_response)
            else:
                logger.warning("Unexpected response structure from NVIDIA API: %s", response)
                return "An error occurred while generating a response."

        except Exception as e:
            logger.error(f"Error generating chat response: {e}")
            return "An error occurred while generating a response."

    def clear_memory(self):
        """Clear the chat memory."""
        self.chat_memory = []
        logger.info("Chat memory cleared.")

    def format_response(self, response: str) -> str:
        """
        Format the chat response for readability.
        
        Parameters:
        - response (str): Raw response text from the chat model.
        
        Returns:
        - str: Formatted response with HTML styling.
        """
        # Convert markdown-like syntax to HTML for bold and italic
        response = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', response)  # Bold
        response = re.sub(r'\*(.*?)\*', r'<em>\1</em>', response)  # Italic
        response = response.replace('\n', '<br>')  # Add line breaks for readability
        return response
