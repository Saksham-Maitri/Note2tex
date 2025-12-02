# note2tex/beautifier_agent.py
import re
from .utils.cleanup import cleanup_latex
from .utils.image_grouping import group_images_smartly
from .bedrock_llm import call_bedrock_raw

BEAUTIFY_PROMPT = r"""
You are a LaTeX Layout Expert (70B).
Your task is to POLISH the final LaTeX document body.

INPUT DOCUMENT:
{{TEX}}

CRITICAL SYNTAX RULES (DO NOT VIOLATE):
1. **NO NESTING:** NEVER put \begin{figure} inside another \begin{figure}.
2. **NO FLOATS IN BOXES:** - NEVER put \begin{figure} or \begin{algorithm} inside \begin{tcolorbox}.
   - If a section has a float, Close the \end{tcolorbox}, place the float, and then Open a new box.
3. **MATH FIXES:** Ensure \norm{...} and \diag{...} are used correctly.

INSTRUCTIONS:
1. Wrap "Problem Description", "Results", and "Conclusion" in \begin{tcolorbox}[sectionbox].
2. Keep images and algorithms OUTSIDE the tcolorbox.
3. Output ONLY the raw LaTeX body.
"""

def fix_nested_floats(tex):
    """
    Emergency cleanup: 
    1. Removes nested figures.
    2. Ensures Algorithms are not wrapped in weird ways.
    """
    # 1. Fix nested figures (double starts)
    tex = re.sub(r"(\\begin\{figure\}\[.*?\])(\s*\\centering\s*)(\\begin\{figure\})", r"\3", tex, flags=re.DOTALL)
    tex = re.sub(r"(\\begin\{figure\})(\s*\\centering\s*)(\\begin\{figure\})", r"\3", tex, flags=re.DOTALL)
    
    # 2. Fix nested figures (double ends)
    tex = re.sub(r"(\\end\{figure\})(\s*)(\\end\{figure\})", r"\1", tex, flags=re.DOTALL)

    return tex

def wrap_section_bodies_selectively(tex):
    """
    Python-based fallback. Stops wrapping if it encounters a Figure OR Algorithm.
    """
    WRAP_TARGETS = ["problem", "results", "conclusion"]
    lines = tex.splitlines()
    out = []
    
    in_box = False
    current_section_is_target = False

    sec_pattern = re.compile(r"^(\\section\s*\{)(.+?)(\}.*)$", re.IGNORECASE)

    def close_box_if_open():
        nonlocal in_box
        if in_box:
            out.append(r"\end{tcolorbox}")
            in_box = False

    for line in lines:
        stripped = line.strip()
        
        # 1. Detect New Section
        match = sec_pattern.match(stripped)
        if match:
            close_box_if_open()
            out.append(line)
            title = match.group(2).lower()
            current_section_is_target = any(t in title for t in WRAP_TARGETS)
            
            if current_section_is_target:
                out.append(r"\begin{tcolorbox}[sectionbox]")
                in_box = True
            continue

        # 2. Detect Floats (Figures OR Algorithms) -> STOP BOXING
        if "\\begin{figure}" in stripped or "\\begin{algorithm}" in stripped:
            close_box_if_open() 
            out.append(line)
            continue
        
        # 3. Detect End of Float -> RESUME BOXING
        if "\\end{figure}" in stripped or "\\end{algorithm}" in stripped:
            out.append(line)
            if current_section_is_target:
                out.append(r"\begin{tcolorbox}[sectionbox]")
                in_box = True
            continue

        # 4. Standard Line
        out.append(line)

    close_box_if_open()
    return "\n".join(out)

def beautify(tex: str, model_id=None):
    clean = cleanup_latex(tex)
    clean = group_images_smartly(clean)
    clean = clean.replace("width=0.75\\linewidth", "width=0.55\\linewidth")
    
    try:
        if model_id:
            print("   ...calling 70B stylist for layout polish...")
            prompt = BEAUTIFY_PROMPT.replace("{{TEX}}", clean)
            system = "You are a LaTeX Expert. Never nest figures."
            styled = call_bedrock_raw(prompt, system_prompt=system, model_id=model_id)
            
            if "\\documentclass" in styled: 
                return wrap_section_bodies_selectively(clean)
            
            return fix_nested_floats(styled)
            
    except Exception as e:
        print(f"⚠️ Stylist LLM failed: {e}")

    return wrap_section_bodies_selectively(clean)