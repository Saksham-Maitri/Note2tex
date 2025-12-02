# note2tex/latex_assembler.py
import os
from .utils.cleanup import cleanup_latex

class LatexAssembler:
    """
    Assembles all validated sections into a single LaTeX body (without preamble).
    Then beautifier_agent will polish layout.
    """

    SECTION_ORDER = [
        "title_abstract",
        "problem",
        "theory",
        "method",
        "code",
        "experiments",
        "results",
        "figures",
        "limitations",
        "future",
        "conclusion"
    ]

    def __init__(self):
        pass

    def assemble_body(self, sections_dict):
        """
        sections_dict : {section_key: latex_body_string}
        Returns a unified LaTeX document body (no preamble).
        """
        out = []
        for key in self.SECTION_ORDER:
            if key not in sections_dict:
                continue

            body = cleanup_latex(sections_dict[key]).strip()
            if not body:
                continue

            if key == "title_abstract":
                out.append(body)
                out.append("")  
                continue

            title = self._section_title(key)
            out.append(f"\\section{{{title}}}")
            out.append(body)
            out.append("")

        return "\n".join(out)

    def _section_title(self, key):
        titles = {
            "problem": "Problem Description",
            "theory": "Theoretical Background",
            "method": "Methodology",
            "code": "Detailed Code Walkthrough",
            "experiments": "Experimental Setup",
            "results": "Results and Analysis",
            "figures": "Figures and Visualizations",
            "limitations": "Limitations",
            "future": "Future Work",
            "conclusion": "Conclusion"
        }
        return titles.get(key, key.capitalize())