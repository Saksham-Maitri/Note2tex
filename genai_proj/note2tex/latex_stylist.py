# note2tex/latex_stylist.py
import os
from .beautifier_agent import beautify
from .utils.cleanup import cleanup_latex

class LatexStylist:
    """
    Final-stage LaTeX beautifier + wrapper with preamble.
    """

    def __init__(self, preamble_path=None, model_id=None):
        self.model_id = model_id
        self.preamble_path = preamble_path

    def wrap_with_preamble(self, body):
        if self.preamble_path and os.path.exists(self.preamble_path):
            with open(self.preamble_path, "r") as f:
                pre = f.read()
            # Ensure we replace the placeholder correctly
            if "% ... body goes here ..." in pre:
                return pre.replace("% ... body goes here ...", body)
            else:
                # Fallback: append before end document
                return pre.replace("\\end{document}", f"\n{body}\n\\end{{document}}")
        else:
            # Fallback if preamble file missing
            return f"\\documentclass[12pt]{{article}}\n\\begin{{document}}\n{body}\n\\end{{document}}"

    def style(self, raw_body_tex):
        # 1. Run the Agentic Beautifier (Grouping + Boxing)
        styled_body = beautify(raw_body_tex, model_id=self.model_id)
        
        # 2. Cleanup formatting
        clean_body = cleanup_latex(styled_body)
        
        # 3. Add Preamble
        final_doc = self.wrap_with_preamble(clean_body)
        
        return final_doc