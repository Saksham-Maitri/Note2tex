# note2tex/cli.py
import argparse
import os
import time
import sys
from pathlib import Path

# Core Modules
from .section_generator import SectionGenerator
from .section_validator import SectionValidator
from .section_refiner import refine_section
from .latex_assembler import LatexAssembler
from .latex_stylist import LatexStylist

# Optional Extractors
try: from .ocr import extract_text_from_file
except ImportError: extract_text_from_file = None

try: from .ipynb_parser import extract_ipynb
except ImportError: extract_ipynb = None

try: from .rag import RAG
except ImportError: RAG = None

def safe_read_text_file(path):
    """Reads simple text files (txt, md, py). DO NOT USE FOR PDF."""
    if not path: return ""
    p = Path(path)
    if p.exists(): 
        try:
            return p.read_text(encoding="utf-8")
        except Exception:
            # Fallback for weird encodings
            return p.read_text(encoding="latin-1", errors="ignore")
    return ""

def extract_pdf_fallback(path):
    """Fallback: Extracts text from PDF using pypdf if OCR fails."""
    try:
        import pypdf
        reader = pypdf.PdfReader(path)
        text = []
        for page in reader.pages:
            text.append(page.extract_text())
        return "\n".join(text)
    except ImportError:
        print("⚠️ pypdf not installed. Run: pip install pypdf")
        return ""
    except Exception as e:
        print(f"⚠️ PDF Fallback failed: {e}")
        return ""

def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def main():
    parser = argparse.ArgumentParser(description="note2tex — AI Report Generator")
    parser.add_argument("--file", required=True, help="Assignment PDF/TXT")
    parser.add_argument("--ipynb", required=True, help="Notebook file")
    parser.add_argument("--name", default="report", help="Output filename base")
    parser.add_argument("--verbosity", default="medium", choices=["tiny", "medium", "long"])
    parser.add_argument("--max_refines", type=int, default=2, help="Max Refiner passes")
    parser.add_argument("--stylist_model", default=None, help="Model ID for final stylist")
    parser.add_argument("--wait_between_calls", type=float, default=1.0, help="Anti-throttle delay")
    args = parser.parse_args()

    OUTDIR = Path("output")
    ensure_dir(OUTDIR)

    print("\n📄 note2tex — Starting Pipeline")
    
    # --- 1. Extraction Phase ---
    print("   [1/5] Extracting Materials...")
    
    # HANDLER FOR ASSIGNMENT FILE
    assignment_text = ""
    if args.file.lower().endswith(".pdf"):
        # Try primary extractor (OCR)
        if extract_text_from_file:
            try:
                assignment_text = extract_text_from_file(args.file)
            except Exception as e:
                print(f"⚠️ Primary OCR failed: {e}")
        
        # If primary failed or returned empty, try fallback
        if not assignment_text:
            print("   ...attempting pypdf fallback...")
            assignment_text = extract_pdf_fallback(args.file)
            
        if not assignment_text:
            print("❌ CRITICAL ERROR: Could not read text from PDF. (Install pypdf or check OCR)")
            return 1
    else:
        # It's a text file
        assignment_text = safe_read_text_file(args.file)

    # HANDLER FOR NOTEBOOK
    if extract_ipynb and args.ipynb.lower().endswith(".ipynb"):
        try: code_text, outputs_text = extract_ipynb(args.ipynb)
        except: 
            code_text = safe_read_text_file("extracted/notebook_code.txt")
            outputs_text = safe_read_text_file("extracted/notebook_outputs.txt")
    else:
        code_text = ""
        outputs_text = ""

    rag_summary = ""
    if RAG:
        try:
            rag_obj = RAG(assignment_text)
            rag_summary = rag_obj.query("Summarize assignment and equations.")
        except: pass

    # --- 2. Initialization ---
    generator = SectionGenerator(verbosity=args.verbosity)
    validator = SectionValidator()
    assembler = LatexAssembler()
    stylist = LatexStylist(preamble_path=os.path.join("note2tex", "preamble.tex"), model_id=args.stylist_model)

    SECTIONS = [
        "title_abstract", "problem", "theory", "method", "code",
        "experiments", "results", "figures", "limitations", "future", "conclusion"
    ]
    sections_out = {}

    # --- 3. Generation Loop (Gen -> Val -> Refine) ---
    print("   [2/5] Generating Sections...")
    for sec in SECTIONS:
        print(f"\n   >>> Processing: {sec}")
        
        # A. Generator
        sec_draft = generator.generate(sec, assignment_text, code_text, outputs_text, rag_summary)
        time.sleep(args.wait_between_calls)

        # B. Validator
        ok, issues = validator.validate(sec, sec_draft)
        
        # C. Refiner (Conditional)
        attempt = 0
        while not ok and attempt < args.max_refines:
            attempt += 1
            print(f"       ⚠️ Issues: {issues} -> Refining (Attempt {attempt})...")
            try:
                sec_draft = refine_section(sec, sec_draft, issues, assignment_text, code_text, outputs_text, rag_summary, model_id=args.stylist_model)
            except Exception as e:
                print(f"       ❌ Refiner crashed: {e}")
                break
            
            time.sleep(args.wait_between_calls)
            ok, issues = validator.validate(sec, sec_draft)

        if ok: print("       ✅ Validated.")
        else: print(f"       ⚠️ Remaining Issues: {issues}")
        
        sections_out[sec] = sec_draft

    # --- 4. Assembly ---
    print("\n   [3/5] Assembling Body...")
    raw_body = assembler.assemble_body(sections_out)
    
    (OUTDIR / f"{args.name}_raw.tex").write_text(raw_body, encoding="utf-8")

    # --- 5. Final Styling (70B Model) ---
    print("\n   [4/5] Running Final Stylist Agent (70B)...")
    try:
        final_tex = stylist.style(raw_body)
    except Exception as e:
        print(f"⚠️ Stylist failed ({e}). Saving raw version.")
        final_tex = raw_body

    final_path = OUTDIR / f"{args.name}.tex"
    final_path.write_text(final_tex, encoding="utf-8")
    
    print(f"\n🎉 Done! Output saved to: {final_path}")
    return 0

if __name__ == "__main__":
    main()