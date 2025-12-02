# note2tex/utils/constants.py

FORBIDDEN_LATEX = [
    "\\documentclass", "\\begin{document}", "\\end{document}",
    "\\usepackage", "```", "\\maketitle",
    "\\author", "\\date", "\\title", "\\chapter",
]

# Removed specific topic bans (like GAN, MNIST) to make the tool generic.
STRICT_RULES = """
ABSOLUTE RULES (DO NOT VIOLATE):
- NEVER output \\documentclass, \\usepackage, \\begin{document}, \\end{document}.
- NEVER output \\maketitle, \\title, \\author, \\date (except in title_abstract).
- NEVER output Markdown code fences (```).
- NEVER output HTML or pseudo-LaTeX.
- ONLY output raw LaTeX for SINGLE section.
- NEVER include unrelated topics.
- NEVER repeat previous sections.
- Ensure all braces { } and environments \\begin{}...\\end{} are balanced.
- Avoid placeholders like “Here is…”.
"""