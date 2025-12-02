# note2tex/bedrock_llm.py
import boto3
import json
import os
import time
import random

DEFAULT_MODEL = "meta.llama3-70b-instruct-v1:0"

def _invoke_bedrock(payload, model_id):
    client = boto3.client(
        "bedrock-runtime",
        region_name=os.getenv("BEDROCK_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        aws_session_token=os.getenv("AWS_SESSION_TOKEN")
    )

    # If the user passed None explicitly, fallback to default
    if not model_id:
        model_id = DEFAULT_MODEL

    for attempt in range(5):
        try:
            response = client.invoke_model(
                modelId=model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(payload)
            )
            body = json.loads(response["body"].read())
            
            if "generation" in body: return body["generation"]
            if "output_text" in body: return body["output_text"]
            if "outputs" in body: return body["outputs"][0]["text"]
            
            return str(body)

        except client.exceptions.ThrottlingException:
            wait = (2 ** attempt) + random.uniform(0, 1.5)
            print(f"⏳ Throttled. Waiting {wait:.1f}s...")
            time.sleep(wait)
        except Exception as e:
            print(f"⚠️ Bedrock Error ({model_id}): {e}")
            if attempt == 4: raise e
            time.sleep(2)
            
    raise RuntimeError("Bedrock failed after retries.")

def call_bedrock_raw(prompt, system_prompt=None, model_id=None):
    # FALLBACK PROTECTION
    if model_id is None:
        model_id = DEFAULT_MODEL

    formatted_prompt = f"""
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_prompt if system_prompt else "You are a helpful LaTeX assistant."}
<|eot_id|><|start_header_id|>user<|end_header_id|>

{prompt}
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
    
    payload = {
        "prompt": formatted_prompt,
        "temperature": 0.2,
        "top_p": 0.9,
        "max_gen_len": 4096 
    }
    
    return _invoke_bedrock(payload, model_id)