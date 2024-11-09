Career Launchpad:

Career Launchpad is a job application tracking tool with personalized resume feedback. It allows users to upload job descriptions and resumes, calculates a match score, and provides actionable feedback on how to improve their resumes to align with job requirements.

Features:

    Track Job Applications: Track job applications with details like company, job title, and status.
    Resume and Job Description Uploads: Upload job descriptions and resumes in multiple formats (.txt, .pdf, .docx).
    Match Score Calculation: Calculate a match score based on the similarity between the resume and job description.
    Tailored Feedback: Receive tailored feedback to enhance resume alignment with job requirements.
    Autocomplete: Auto-complete dropdowns for company names and job titles, which build up over time.
    User-Friendly Interface: Simple, user-friendly web interface.

Project Setup:

Create a Virtual Environment
    Run the following command in your project directory to create a virtual environment:
    
    python3 -m venv myenv_Version1

Activate the Virtual Environment
    Once the virtual environment is created, activate it:
        - On Windows:
            source myenv_Version1/bin/activate
        - On macOS/Linux:
            source myenv_Version1/bin/activate
            
Install Dependencies:

    With the virtual environment activated, install the dependencies from the requirements.txt file:

        pip install -r requirements.txt

Running the Application:

    After setting up the environment and installing dependencies, start the Flask application:
        
        python app.py
        
Your application should now be running at http://127.0.0.1:5000

Project Structure: 

CareerLaunchpad/
    ├── app.py                    # Main Flask application to run the app
    ├── config.py                 # Configuration settings (e.g., API keys, database paths)
    ├── requirements.txt          # List of dependencies required for the project
    ├── README.md                 # Project documentation
    │
    ├── database/                 # Database-related files
    │   ├── db_setup.py           # Database initialization and schema creation
    │   └── models.py             # Database models, ORM classes, and helper functions
    │
    ├── services/                 # Service layer for business logic and processing
    │   ├── feedback.py           # Generate tailored feedback for resumes based on job description
    │   ├── nvidia_chat.py        # Chat service for NVIDIA-powered conversational assistant
    │   ├── nvidia_embeddings.py  # Integrates NVIDIA embeddings for similarity scoring
    │   └── resume_matching.py    # Calculate match score between resume and job description
    │
    ├── static/                   # Static assets such as JavaScript and CSS files
    │   ├── script.js             # Frontend JavaScript logic for UI interactions
    │   └── styles.css            # Stylesheet for the application UI
    │
    ├── templates/                # HTML templates for rendering the frontend
    │   └── index.html            # Main HTML template for the web interface
    │
    └── utils/                    # Utility functions for file handling, text processing, and validation
        └── utils.py              # Functions for text extraction, file validation, and preprocessing

New Components in Version 2.o

    -NVIDIA Embedding Integration (nvidia_embeddings.py): Integrates NVIDIA API for generating embeddings for both job descriptions and resumes, enhancing match scoring accuracy.
    
    -NVIDIA Chat Integration (nvidia_chat.py): A chat service for providing interactive feedback and assistance using NVIDIA's LLM.
    
    -Enhanced Feedback (feedback.py): Provides detailed feedback using keyword analysis and match scores, helping users improve their resumes.

    -Truncate Text Functionality (resume_matching.py): Ensures that text inputs meet the token length requirements for NVIDIA’s API.
    
    -Utility Enhancements (utils.py): Includes functions for PDF/DOCX processing, character encoding detection, and MIME type validation.
    
    
API Key Setup:

    To use the Career Launchpad application, you need to set up an NVIDIA API key to enable resume matching and feedback functionality. Follow these steps to configure the API key securely:
    
    Get an NVIDIA API Key

        Register or log in to NVIDIA's API Platform to obtain your API key.

    Create a .env File
    
        -In the root directory of the project, create a file named .env. Open the .env file in a text editor and add your NVIDIA API key as shown below:
    
            NVIDIA_API_KEY=your_actual_api_key_here
            
    Replace your_actual_api_key_here with your actual API key from NVIDIA.

    Install python-dotenv:

    Ensure that python-dotenv is listed in the requirements.txt file. If it isn’t, you can install it manually by running:
    
        pip install python-dotenv

Verify Environment Variable Loading
    
    The application is set up to load the API key from the .env file, ensuring your key is not directly embedded in the code. The application will use this key when making requests to the NVIDIA API for generating embeddings and feedback.

    Important Security Note: Ensure that the .env file is added to .gitignore so it is not accidentally uploaded to version control. This protects your API key from being exposed publicly.

    
    
Developer Notes:

Testing NVIDIA API Integration:

    For developers, the file test_nvidia_api.py is provided to test the connection and response from the NVIDIA API. This can be useful for verifying API setup or troubleshooting.

    To use it, make sure your .env file is set up with the necessary API key, then run:
    
            python test_nvidia_api.py
            
    This script checks that the API is correctly configured and returns a sample response.
    

Version 2.0.1 - Minor Update

- Enabled GPU compatibility: Modified the application to leverage GPU where available, enhancing processing speed for embedding and other compute-intensive tasks.
- Optimized NVIDIA API integration: Refined the chat and embedding services to ensure efficient use of cloud resources for faster response times.
- Hardware testing clarification: Aligned the project’s hardware testing setup with NVIDIA's cloud infrastructure, utilizing cloud GPUs for model operations.
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

