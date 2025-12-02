import re

def cleanup_latex(latex: str) -> str:
    latex = re.sub(r"```.*?```", "", latex, flags=re.S)
    latex = re.sub(r"\\documentclass.*?\n", "", latex)
    latex = latex.replace("\\begin{document}", "")
    latex = latex.replace("\\end{document}", "")
    return latex.strip()