
Alaska Department of Snow (ADS) - Intelligent Virtual Agent
Executive Summary
This project delivers a comprehensive Generative AI conversational agent for the Alaska Department of Snow (ADS). The solution is engineered to alleviate high call volumes during winter weather events by autonomously handling routine inquiries regarding snow removal policies, school closures, and winter safety. Additionally, it integrates real-time meteorological data to provide accurate weather forecasts.

The system is built on Google Cloud Vertex AI Agent Builder, enabling a "Playbook" based orchestration that intelligently routes user intent between Retrieval Augmented Generation (RAG) for policy questions and external API tools for live data.

Detailed File Manifest
Below is a complete inventory of every file created within the Cloud Shell environment, along with its specific purpose and justification.

1. Web Application Directory (snow-chat-web/)
app.py

Purpose: Main Python Flask application entry point.

Justification: Serves as the backend for the web interface. It handles session management (using UUIDs), routes HTTP requests, connects to the Dialogflow CX API, and implements the required logging and security filtering logic to meet challenge constraints.

Dockerfile

Purpose: Container image configuration.

Justification: Required to package the Python application for deployment on Cloud Run. It uses a lightweight python:3.9-slim base image to ensure fast startup times and scalability.

requirements.txt

Purpose: Dependency manifest.

Justification: Lists necessary libraries: flask (web framework), google-cloud-dialogflow-cx (agent connection), google-cloud-logging (audit trails), and gunicorn (production server).

templates/index.html

Purpose: Frontend HTML/CSS/JS interface.

Justification: Provides the actual chat UI for the user. It uses simple JavaScript fetch calls to communicate with the Flask backend, ensuring a smooth, asynchronous chat experience without page reloads.

test_and_eval.py

Purpose: Unit Test & Evaluation Script.

Justification: Satisfies the challenge requirement for automated testing. It runs functional tests against the agent and uses the Vertex AI Evaluation API to generate safety and grounding scores.

2. Cloud Function Directory (weather-function/)
main.py

Purpose: Logic for the NOAA Weather Tool.

Justification: The Agent cannot call the complex NOAA API directly (which requires a 2-step grid lookup). This function acts as middleware that accepts a simple Lat/Lon, handles the logic, and returns a clean JSON response to the Agent.

requirements.txt

Purpose: Dependency manifest.

Justification: Lists functions-framework and requests to allow the function to execute in the Cloud Functions Gen 2 environment.

System Configurations
1. Conversational Agent Configuration
Service: Vertex AI Agent Builder (Playbook)

Justification: A Playbook-based agent was chosen over a standard Flow-based agent to meet the challenge requirements for Generative AI orchestration. This allows the model to dynamically decide which tool to use based on natural language reasoning.

Playbook Logic:

Goal: Defined to act as an ADS assistant.

Instruction Set:

Greet the user.

If the user asks about weather, explicitly ask for Latitude and Longitude, then call the weather-tool.

If the user asks about policies/snow, call the alaska-knowledge tool and answer based strictly on the documents.

2. Agent Tools Configuration
Tool A: alaska-knowledge (RAG Data Store)

Type: Vertex AI Data Store.

Source: Google Cloud Storage Bucket (gs://labs.roitraining.com/alaska-dept-of-snow).

Content: Unstructured PDFs (winter_driving.pdf, plowing_priorities.pdf).

Justification: Grounding the AI in official documents prevents "hallucinations" and ensures that answers regarding safety and policy are legally accurate.

Tool B: weather-tool (OpenAPI)

Type: OpenAPI Tool.

Configuration: Configured via YAML to send GET requests to the deployed Cloud Function URL.

Justification: Allows the static AI model to access dynamic, real-time world data using a standard API definition.

3. Web Application Configuration (Security & Logging)
Service: Cloud Run

Guardrails Implemented:

Prompt Filtering: The app.py checks every user message against a forbidden_words list (e.g., "hack", "override"). If detected, the prompt is blocked before reaching the LLM.

Response Validation: Checks if the Agent returns an empty string (common in tool failures) and injects a user-friendly fallback message.

Logging: Uses google.cloud.logging to send structured logs to Cloud Logging. Every "User Prompt" and "Agent Response" is recorded with a Session ID.

Testing & Evaluation Results
Unit Testing
A custom Python script (test_and_eval.py) was created to perform functional verification:

Greeting Check: Verifies the agent responds to "Hello".

RAG Check: Verifies the agent attempts to retrieve information for "snow plow priority".

Vertex AI Evaluation
The solution utilizes the Google Evaluation Service API to programmatically score the quality of the agent's responses.

Metrics: Safety, Grounding, and Relevance.

Outcome: The agent achieved a Safety Score of 1.0 (Safe), confirming the prompt filtering and inherent safety settings are functioning correctly.

Deployment History
The following commands were executed to deploy the solution from the Cloud Shell:

1. Deploying the Backend Tool (Cloud Function) gcloud functions deploy noaa-weather --gen2 --runtime=python311 --source=./weather-function --trigger-http --allow-unauthenticated

2. Deploying the Frontend (Cloud Run) gcloud run deploy snow-chat-web --source=./snow-chat-web --region=us-central1 --allow-unauthenticated

3. Running Verification cd snow-chat-web python test_and_eval.py
