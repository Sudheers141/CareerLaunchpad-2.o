from flask import Flask, render_template, request, jsonify, session
from database.models import initialize_database, add_job_application, add_resume, get_job_application_by_id, get_resume
from services.resume_matching import ResumeMatchingService
from services.feedback import FeedbackGenerator
from services.nvidia_chat import NvidiaChatService
from services.nvidia_embeddings import NvidiaEmbeddingService
from config import Config
from docx import Document
import PyPDF2
import os
import logging
import json

# Initialize the Flask app and logging
app = Flask(__name__)
app.secret_key = os.urandom(24)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize the database and services
initialize_database()
resume_matcher = ResumeMatchingService()
feedback_generator = FeedbackGenerator()
embedding_service = NvidiaEmbeddingService(api_key=Config.NVIDIA_API_KEY)
chat_service = NvidiaChatService(api_key=Config.NVIDIA_API_KEY_NEW)

logger.info("NVIDIA services initialized for resume matching, feedback, and chat.")

@app.route('/')
def home():
    return render_template('index.html')

# Helper functions to read PDF and DOCX files
def read_pdf(file):
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = "".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())
        return text
    except Exception as e:
        logger.error(f"Failed to read PDF file: {e}")
        raise

def read_docx(file):
    try:
        doc = Document(file)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    except Exception as e:
        logger.error(f"Failed to read DOCX file: {e}")
        raise

@app.route('/submit_application', methods=['POST'])
def submit_application():
    try:
        # Gather form data
        company_name = request.form.get('company')
        job_title = request.form.get('job_title')
        job_description = request.form.get('job_description')
        resume_text = request.form.get('resume_text')

        job_file = request.files.get('job_file')
        resume_file = request.files.get('resume_file')

        # Check for required fields
        if not company_name or not job_title:
            return jsonify({"error": "Company name and job title are required."}), 400

        # Read job and resume file if provided
        if job_file and not job_description:
            job_description = job_file.read().decode('utf-8', errors='replace')
        if resume_file:
            if resume_file.filename.endswith('.pdf'):
                resume_text = read_pdf(resume_file)
            elif resume_file.filename.endswith('.docx'):
                resume_text = read_docx(resume_file)
            elif resume_file.filename.endswith('.txt'):
                resume_text = resume_file.read().decode('utf-8', errors='replace')

        # Ensure job description or resume text is provided
        if not job_description and not resume_text:
            return jsonify({"error": "Job description or resume text must be provided."}), 400

        # Calculate match score and generate feedback
        match_score = resume_matcher.calculate_match_score(job_description, resume_text)
        feedback = feedback_generator.generate_feedback(job_description, resume_text, match_score)
        suggestions = feedback_generator.get_improvement_suggestions(feedback)

        # Save job application and resume to database
        application_id = add_job_application(
            company_name, job_title, job_description, application_status="Pending", 
            match_score=match_score, feedback=json.dumps(feedback), suggestions=json.dumps(suggestions)
        )
        resume_id = add_resume("User", resume_text)  # Replace "User" with actual user identifier if available

        # Store only application_id in the session
        session['application_id'] = application_id
        logger.info("Application submitted with ID: %s", application_id)

        # Return response to frontend
        response = {
            'application_id': application_id,
            'match_score': match_score,
            'feedback': feedback,
            'suggestions': suggestions
        }

        return jsonify(response)

    except Exception as e:
        logger.error(f"Error in /submit_application: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred. Please check the server logs for more details."}), 500

@app.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint to provide contextualized responses based on user query and previous application data."""
    try:
        user_query = request.json.get("query")
        if not user_query:
            return jsonify({"error": "Query is required."}), 400

        # Retrieve application data from the database using application_id in session
        application_id = session.get('application_id')
        if application_id:
            application_data = get_job_application_by_id(application_id)
            resume_data = get_resume(application_id)  # Fetch resume data based on application ID
            
            # Convert stored JSON strings back to dictionaries/lists and include resume text
            application_data['feedback'] = json.loads(application_data['feedback'])
            application_data['suggestions'] = json.loads(application_data['suggestions'])
            application_data['resume_text'] = resume_data['resume_text'] if resume_data else "N/A"  # Add resume text to context
            
            context = application_data
        else:
            context = {}

        # Log the user query and context data for debugging
        logger.info("User query: %s", user_query)
        logger.info("Context data for chat: %s", context)

        # Pass context to chat service for response generation
        response = chat_service.get_chat_response(user_query, context=context)

        return jsonify({"response": response})

    except Exception as e:
        logger.error(f"Error in /chat: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred. Please check the server logs for more details."}), 500

if __name__ == '__main__':
    app.run(debug=True)
