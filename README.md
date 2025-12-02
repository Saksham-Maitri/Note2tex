# Note2tex

# -> genai_proj

## ⚙️ Environment Setup

This tool uses **AWS Bedrock** (Llama 3 70B) for generating and refining the LaTeX code. You must provide valid AWS credentials with access to the `bedrock-runtime` service.

### Method 1: Export Variables (Mac/Linux)
Run these commands in your terminal before running the tool:

```bash
export AWS_ACCESS_KEY_ID="your_access_key_here"
export AWS_SECRET_ACCESS_KEY="your_secret_key_here"
export AWS_SESSION_TOKEN="optional_session_token_if_using_sso"
export BEDROCK_REGION="us-east-1"  # Or your specific region (e.g., us-west-2)
