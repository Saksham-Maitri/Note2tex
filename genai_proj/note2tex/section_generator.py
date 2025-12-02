# note2tex/section_generator.py

from .bedrock_llm import call_bedrock_raw
from .utils.constants import STRICT_RULES
from .utils.cleanup import cleanup_latex

# Specific instructions based on verbosity
VERBOSITY_GUIDES = {
    "tiny": "Write a concise summary (1 paragraph). Focus only on the main outcome.",
    "medium": "Write 2-3 paragraphs. Explain the 'Why' and 'How'. Use standard academic depth.",
    "long": """
    CRITICAL INSTRUCTION: MAXIMUM DETAIL REQUIRED.
    - Write a deep-dive analysis (4-6 paragraphs).
    - If explaining Theory: Derive equations step-by-step. Don't just state them.
    - If explaining Code: Reference specific variable names and logic flows. Explain 'Why this parameter was chosen'.
    - If explaining Results: Analyze the metrics deeply. Discuss outliers. Discuss the visual artifacts in images.
    - DO NOT summarize. Expand on every detail provided in the context.
    """
}

SECTION_PROMPTS = {
    "title_abstract": "Generate \\title{}, \\author{}, \\date{}, and \\begin{abstract}. Abstract must be comprehensive.",
    "problem": "Define the optimization problem formally. Use mathematical notation ($x, W, \eta$). Define every term.",
    "theory": "Provide the complete theoretical background. Explain the MM algorithm properties (Lipschitz constant, convexity).",
    "method": "Detail the algorithm. Use \\begin{algorithm} for pseudo-code. Explain the update steps $w^{(k)}$ in detail.",
    "code": "Walk through the code logic. Use \\verb|| for variables. Explain how the data flows through the functions.",
    "experiments": "Describe the setup: Datasets, Noise levels ($\sigma$), Sampling rates, and Regularization ($\lambda$).",
    "results": "Present the results. Compare PSNR values. Use \\ref{...} to refer to figures. Be quantitative.",
    "figures": "Output ONLY \\includegraphics lines for the relevant images mentioned in outputs. Do not add captions yet.",
    "limitations": "Discuss computational cost, convergence speed, and failure cases.",
    "future": "Propose specific algorithmic improvements (e.g., FISTA, different priors).",
    "conclusion": "Summarize the entire project impact.",
}

def build_prompt(section_key, assignment, code, outputs, rag, verbosity):
    instruction = SECTION_PROMPTS.get(section_key, "")
    verbosity_rule = VERBOSITY_GUIDES.get(verbosity, VERBOSITY_GUIDES["medium"])

    # Context Slicing
    if section_key in ["problem", "theory"]:
        context = f"ASSIGNMENT MATH:\n{assignment[:15000]}"
    elif section_key in ["code", "method"]:
        context = f"CODE:\n{code[:20000]}\nMETHODOLOGY:\n{assignment[:5000]}"
    elif section_key in ["results", "experiments", "figures"]:
        context = f"LOGS & OUTPUTS:\n{outputs[:15000]}\nRAG:\n{rag}"
    else:
        context = f"RAG:\n{rag}\nASSIGNMENT:\n{assignment[:5000]}"

    return f"""
{STRICT_RULES}

You are an expert Academic Researcher writing a report.
Current Section: **{section_key.upper()}**

VERBOSITY SETTING: {verbosity.upper()}
{verbosity_rule}

INSTRUCTION:
{instruction}

CONTEXT:
{context}

TASK:
1. Write the LaTeX body for this section.
2. If the context implies an image (e.g., "Figure 1 shows..."), insert: \\includegraphics{{images/placeholder.png}}
3. Arrange images near the text describing them.

OUTPUT RAW LATEX ONLY.
"""

class SectionGenerator:
    def __init__(self, verbosity="medium"):
        self.verbosity = verbosity

    def generate(self, key, assignment, code, outputs, rag):
        system_prompt = "You are an expert LaTeX Academic Writer. You output ONLY valid LaTeX code."
        prompt = build_prompt(key, assignment, code, outputs, rag, self.verbosity)
        raw = call_bedrock_raw(prompt, system_prompt=system_prompt)
        return cleanup_latex(raw)