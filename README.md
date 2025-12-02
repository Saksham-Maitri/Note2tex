# Note2tex

# -> genai_proj

## ⚙️ Environment Setup

This tool uses **AWS Bedrock** (Llama 3 70B) for generating and refining the LaTeX code. You must provide valid AWS credentials with access to the `bedrock-runtime` service.

# Export Variables (Mac/Linux)
Run these commands in your terminal before running the tool:

```bash
export AWS_ACCESS_KEY_ID="your_access_key_here"
export AWS_SECRET_ACCESS_KEY="your_secret_key_here"
export BEDROCK_REGION="us-east-1"
```

# Running 🚀
Put your assignment.pdf and main.ipynb in the genai-proj folder and run the following command:
```bash
note2tex --file assignment.pdf --ipynb main.ipynb \
         --name generateed \ #<-- name of the .tex file
         --verbosity long \ #<-- tiny/medium/long
         --max_refines 2 \ #<-- number of validator-refiner pass
         --wait_between_calls 2 #<-- time between throtle for api requests for bedrock
```
