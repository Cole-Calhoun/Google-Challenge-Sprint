import logging
import uuid
from flask import Flask, render_template, request, jsonify
from google.cloud import dialogflowcx_v3beta1 as dialogflow
from google.cloud import logging as cloud_logging

app = Flask(__name__)

# --- CONFIGURATION (FILLED IN FOR YOU) ---
PROJECT_ID = "qwiklabs-gcp-03-5dc51bd29ec6"     # Extracted from your terminal session
LOCATION_ID = "us-central1"                      # Extracted from your Agent path
AGENT_ID = "a9b0bb43-711c-45ba-bc3c-d0bc31a5fad7" # Extracted from your provided path
LANGUAGE_CODE = "en"

# --- LOGGING SETUP ---
# Connects to Cloud Logging so you can see "User Prompt" and "Agent Response" in the Google Cloud Console
log_client = cloud_logging.Client()
log_handler = log_client.get_default_handler()
cloud_logger = logging.getLogger("cloudLogger")
cloud_logger.setLevel(logging.INFO)
cloud_logger.addHandler(log_handler)

@app.route("/")
def home():
    # Generate a unique session ID for every new page load
    session_id = str(uuid.uuid4())
    return render_template("index.html", session_id=session_id)

@app.route("/chat", methods=["POST"])
def chat():
    # Get data from frontend
    user_message = request.json.get("message")
    session_id = request.json.get("session_id")

    # --- REQUIREMENT: PROMPT FILTERING ---
    # We filter out specific keywords to save costs or prevent misuse
    forbidden_words = ["hack", "ignore instructions", "system override", "admin"]
    if any(word in user_message.lower() for word in forbidden_words):
        cloud_logger.warning(f"BLOCKED PROMPT: {user_message}")
        return jsonify({"response": "I cannot process that request due to security filters."})

    # --- REQUIREMENT: LOG PROMPT ---
    cloud_logger.info(f"User Prompt: {user_message} | Session: {session_id}")

    try:
        # Build the full session path required by the API
        session_path = f"projects/{PROJECT_ID}/locations/{LOCATION_ID}/agents/{AGENT_ID}/sessions/{session_id}"
        
        # Initialize the Dialogflow CX (Agent Builder) Client
        # We must specify the correct regional endpoint
        client_options = {"api_endpoint": f"{LOCATION_ID}-dialogflow.googleapis.com"}
        session_client = dialogflow.SessionsClient(client_options=client_options)

        # Construct the input object
        text_input = dialogflow.TextInput(text=user_message)
        query_input = dialogflow.QueryInput(text=text_input, language_code=LANGUAGE_CODE)

        # Send request to Vertex AI Agent
        request_payload = dialogflow.DetectIntentRequest(
            session=session_path, query_input=query_input
        )
        response = session_client.detect_intent(request=request_payload)

        # Extract the text response from the Agent
        bot_text = ""
        for message in response.query_result.response_messages:
            if message.text:
                # Concatenate all parts of the response
                bot_text += message.text.text[0] + " "

        # --- REQUIREMENT: RESPONSE VALIDATION ---
        # If the agent returns nothing (e.g., tool failure), provide a fallback
        if not bot_text:
            bot_text = "I'm sorry, I couldn't find an answer to that in the provided documents."
            cloud_logger.error("Empty response received from Agent.")

        # --- REQUIREMENT: LOG RESPONSE ---
        cloud_logger.info(f"Agent Response: {bot_text}")

        return jsonify({"response": bot_text})

    except Exception as e:
        # Log the full error for debugging in Cloud Logging
        cloud_logger.error(f"API Error: {str(e)}")
        return jsonify({"response": "System Error: Please check the logs."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
