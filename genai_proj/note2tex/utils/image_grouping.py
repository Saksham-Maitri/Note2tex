# note2tex/utils/image_grouping.py
import re

def group_images_smartly(latex_body: str) -> str:
    """
    Scans LaTeX for sequential \includegraphics commands and groups them.
    - 2 images -> Side by Side
    - 3 images -> 1 Row of 3
    - 4 images -> 2x2 Grid
    """
    
    # Regex to capture the whole figure environment or standalone includegraphics
    # For simplicity, we assume the generator outputs standalone \includegraphics or simple figure blocks
    # We will look for consecutive \includegraphics lines
    
    lines = latex_body.splitlines()
    new_lines = []
    image_buffer = []

    def flush_buffer():
        nonlocal image_buffer
        if not image_buffer:
            return []
        
        count = len(image_buffer)
        
        # If just 1 image, return it as is (but centered)
        if count == 1:
            return [r"\begin{figure}[H]", r"\centering"] + image_buffer + [r"\end{figure}"]

        # Logic for grouping
        out = [r"\begin{figure}[H]", r"\centering"]
        
        # 2x2 Grid Logic (For exactly 4 images)
        if count == 4:
            width = "0.45" # slightly less than 0.5 to fit gap
            for i, img_line in enumerate(image_buffer):
                # Extract filename from the line
                match = re.search(r"\{(.+?)\}", img_line)
                fname = match.group(1) if match else "placeholder"
                
                out.append(f"\\begin{{subfigure}}[b]{{{width}\\textwidth}}")
                out.append(r"\centering")
                out.append(f"\\includegraphics[width=\\linewidth]{{{fname}}}")
                out.append(r"\caption{}") # Empty caption for now
                out.append(r"\end{subfigure}")
                
                # Add a line break after the 2nd image to force grid
                if i == 1: 
                    out.append(r"\hfill") # spacing
                    out.append(r"") # newline in latex source
                elif i != 3:
                    out.append(r"\hfill")

        # Standard Row Logic (2 or 3 images)
        else:
            width = f"{0.95 / count:.2f}"
            for img_line in image_buffer:
                match = re.search(r"\{(.+?)\}", img_line)
                fname = match.group(1) if match else "placeholder"
                
                out.append(f"\\begin{{subfigure}}[b]{{{width}\\textwidth}}")
                out.append(r"\centering")
                out.append(f"\\includegraphics[width=\\linewidth]{{{fname}}}")
                out.append(r"\caption{}")
                out.append(r"\end{subfigure}")
                out.append(r"\hfill")

        out.append(r"\caption{Visual comparison of results.}")
        out.append(r"\end{figure}")
        return out

    # Iterate through lines
    for line in lines:
        stripped = line.strip()
        # Detect simple includegraphics
        if stripped.startswith(r"\includegraphics"):
            image_buffer.append(stripped)
        # Detect if we hit a blank line or text -> flush buffer
        elif stripped == "" or stripped.startswith("\\") or len(stripped) > 0:
            if image_buffer:
                new_lines.extend(flush_buffer())
                image_buffer = []
            new_lines.append(line)
            
    # Final flush
    if image_buffer:
        new_lines.extend(flush_buffer())

    return "\n".join(new_lines)