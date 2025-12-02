# note2tex/section_refiner.py
from .bedrock_llm import call_bedrock_raw
from .utils.cleanup import cleanup_latex
import re

REFINE_PROMPT = r"""
You are a LaTeX Debugging Expert. 
The user generated a section but it failed validation or requires syntax checking.

SECTION NAME: {{SECTION_NAME}}
ISSUES DETECTED: {{ISSUES}}

CURRENT LATEX:
{{SECTION_TEXT}}

CONTEXT SUMMARY:
{{RAG}}

STRICT SYNTAX RULES:
1. **ALGORITHMS:** You MUST use the 'algorithmic' package syntax:
   - Use \begin{algorithm} \begin{algorithmic} ... \end{algorithmic} \end{algorithm}
   - Use commands: \STATE, \REQUIRE, \ENSURE, \IF{}, \FOR{}.
   - DO NOT use \SetKwInOut or \RestyleAlgo (these belong to algorithm2e, which we do not have).
2. **MATH:** Use \norm{} and \diag{} (these are defined).
3. **FIGURES:** Ensure \includegraphics has a valid filename (or placeholder).
4. **BRACES:** Check that every { has a matching }.

TASK:
- Fix the issues listed.
- Ensure the syntax matches the rules above.
- Return ONLY the corrected LaTeX body.
"""

def refine_section(section_name, section_text, issues,
                   assignment, code, outputs, rag, model_id=None):

    section_text_clean = cleanup_latex(section_text)

    prompt = REFINE_PROMPT
    prompt = prompt.replace("{{SECTION_NAME}}", section_name)
    prompt = prompt.replace("{{SECTION_TEXT}}", section_text_clean)
    prompt = prompt.replace("{{ISSUES}}", str(issues))
    prompt = prompt.replace("{{RAG}}", str(rag)[:2000])

    try:
        # We use a specific system prompt for debugging
        system_prompt = "You are a LaTeX Code Fixer. Output raw LaTeX only. No explanations."
        
        corrected_raw = call_bedrock_raw(prompt, system_prompt=system_prompt, model_id=model_id)
        corrected = cleanup_latex(corrected_raw)

        if len(corrected.strip()) < 20:
            return section_text_clean 

        return corrected

    except Exception as e:
        print(f"Refine Error: {e}")
        return section_text_clean