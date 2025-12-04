import time
import uuid
import pandas as pd
from google.cloud import dialogflowcx_v3beta1 as dialogflow
from vertexai.preview.evaluation import EvalTask, MetricPromptTemplateExamples, PointwiseMetric

# --- CONFIGURATION ---
PROJECT_ID = "qwiklabs-gcp-03-5dc51bd29ec6"
LOCATION_ID = "us-central1"
AGENT_ID = "a9b0bb43-711c-45ba-bc3c-d0bc31a5fad7"
LANGUAGE_CODE = "en"

def get_agent_response(text, session_id):
    """Interacts with the Vertex AI Agent and returns the response text."""
    session_path = f"projects/{PROJECT_ID}/locations/{LOCATION_ID}/agents/{AGENT_ID}/sessions/{session_id}"
    client_options = {"api_endpoint": f"{LOCATION_ID}-dialogflow.googleapis.com"}
    session_client = dialogflow.SessionsClient(client_options=client_options)

    text_input = dialogflow.TextInput(text=text)
    query_input = dialogflow.QueryInput(text=text_input, language_code=LANGUAGE_CODE)
    request = dialogflow.DetectIntentRequest(session=session_path, query_input=query_input)

    response = session_client.detect_intent(request=request)
    
    bot_text = ""
    for message in response.query_result.response_messages:
        if message.text:
            bot_text += message.text.text[0] + " "
    return bot_text.strip()

def run_unit_tests():
    """Runs functional unit tests."""
    print("--- STARTING UNIT TESTS ---")
    session_id = str(uuid.uuid4())
    
    test_cases = [
        {"input": "Hello", "expected_keyword": "", "desc": "Greeting Check"},
        {"input": "What is the snow plow priority?", "expected_keyword": "priority", "desc": "RAG Knowledge Check"},
    ]

    results = []
    
    for test in test_cases:
        print(f"Testing: {test['desc']}...")
        response = get_agent_response(test['input'], session_id)
        print(f"   Response: {response}")
        
        # Simple Assertion Logic
        passed = True
        if test['expected_keyword'] and test['expected_keyword'].lower() not in response.lower():
            passed = False
            
        results.append({
            "prompt": test['input'],
            "response": response,
            "passed": passed
        })
        time.sleep(1) # Avoid rate limits

    print("--- UNIT TESTS COMPLETE ---\n")
    return results

def run_evaluation(test_data):
    """Uses Vertex AI Evaluation API to score the responses."""
    print("--- STARTING VERTEX AI EVALUATION ---")
    
    # Prepare data for evaluation
    eval_dataset = pd.DataFrame({
        "prompt": [t['prompt'] for t in test_data],
        "response": [t['response'] for t in test_data],
    })

    # Define Metrics (We evaluate Text Quality and Safety)
    # Note: Custom Pointwise metrics can be defined here if needed
    metrics = [
        MetricPromptTemplateExamples.Pointwise.TEXT_QUALITY,
        MetricPromptTemplateExamples.Pointwise.SAFETY,
    ]

    # Create Eval Task
    eval_task = EvalTask(
        dataset=eval_dataset,
        metrics=metrics,
        experiment="alaska-snow-agent-eval"
    )

    # Run Evaluation
    eval_results = eval_task.evaluate()
    
    print("\n--- EVALUATION RESULTS ---")
    print(eval_results.metrics_table)
    return eval_results

if __name__ == "__main__":
    # 1. Run Unit Tests (Functional)
    test_results = run_unit_tests()
    
    # 2. Run Evaluation (Quality)
    try:
        import vertexai
        vertexai.init(project=PROJECT_ID, location=LOCATION_ID)
        run_evaluation(test_results)
    except Exception as e:
        print(f"Skipping Evaluation Step (Deps missing or API not enabled): {e}")
        print("Install 'google-cloud-aiplatform' and 'pandas' to run eval.")
