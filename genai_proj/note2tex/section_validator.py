# note2tex/section_validator.py

import re
from .utils.constants import FORBIDDEN_LATEX
from .utils.cleanup import cleanup_latex

class SectionValidator:
    def __init__(self):
        pass

    def check_balanced_braces(self, text):
        """Simple counter check for { }."""
        balance = 0
        for char in text:
            if char == '{': balance += 1
            elif char == '}': balance -= 1
            if balance < 0: return False # Closed before opening
        return balance == 0

    def validate(self, key: str, text: str):
        """Return (ok: bool, issues: list[str])"""
        issues = []
        clean = cleanup_latex(text)

        # 1. Hard forbidden patterns
        # Exception: Allow title commands ONLY in the title_abstract section
        for bad in FORBIDDEN_LATEX:
            if key == "title_abstract" and bad in ["\\title", "\\author", "\\date", "\\maketitle"]:
                continue
            if bad in clean:
                issues.append(f"forbidden command: {bad}")

        # 2. Markdown fences
        if "```" in clean:
            issues.append("markdown code fences detected")

        # 3. Critical: Check for balanced braces
        if not self.check_balanced_braces(clean):
            issues.append("unbalanced curly braces { }")
        
        # 4. Check for balanced environments
        begins = clean.count("\\begin{")
        ends = clean.count("\\end{")
        if begins != ends:
            # title_abstract might not have environments, so ignore if both are 0
            if begins > 0 or ends > 0:
                issues.append(f"unbalanced environments (begin={begins}, end={ends})")

        # 5. Missing Filenames
        fig_refs = re.findall(r"\\includegraphics\{(.*?)\}", clean)
        for f in fig_refs:
            if not f.strip(): issues.append("empty \\includegraphics filename")

        # 6. Length check (skip for title)
        if key != "title_abstract" and len(clean.strip()) < 50:
            issues.append("section too short")

        ok = len(issues) == 0
        return ok, issues