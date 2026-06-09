import os
import re
from bidi.algorithm import get_display
from pdfmd import pdf_to_markdown, Options 

def fix_rtl_hebrew(text):
    """Flips Hebrew text into the correct visual order without breaking Markdown structures."""
    lines = text.split('\n')
    fixed_lines = []
    for line in lines:
        if re.search(r'[\u0590-\u05FF]', line):
            fixed_lines.append(get_display(line))
        else:
            fixed_lines.append(line)
    return '\n'.join(fixed_lines)

def advanced_pdf_processor(temp_filename, profile_name="Default"):
    """
    Uses the native pdfmd Python API to cleanly extract layouts based on selected profiles,
    then post-processes text for correct Hebrew direction.
    """
    output_filename = temp_filename.replace(".pdf", ".md")
    
    # 1. Start with system baseline settings
    opts = Options(
        ocr_mode="auto",
        ocr_lang="heb+eng",
        remove_headers_footers=True,
        defragment_short=True,
        insert_page_breaks=True,
        heading_size_ratio=1.15,
        orphan_max_len=45,
        caps_to_headings=True
    )
    
    # 2. Adjust fields dynamically based on the requested profile selection
    if profile_name == "Academic article":
        opts.heading_size_ratio = 1.10
        opts.orphan_max_len = 60
        
    elif profile_name == "Slides / handouts":
        opts.remove_headers_footers = False  # Keep slide numbers/footers intact
        opts.insert_page_breaks = True       # Visually distinct slide separations
        
    elif profile_name == "Scan-heavy / OCR-first":
        opts.ocr_mode = "tesseract"          # Force page-by-page system engine OCR mapping
        opts.caps_to_headings = False        # Ignore case styling changes on low-res scans
        
    try:
        # Run the end-to-end processing pipeline using configuration
        pdf_to_markdown(
            input_pdf=temp_filename,
            output_md=output_filename,
            options=opts
        )
        
        if os.path.exists(output_filename):
            with open(output_filename, "r", encoding="utf-8") as f:
                raw_markdown = f.read()
            
            os.remove(output_filename)
            
            # Apply bidirectional adjustments for Hebrew characters
            final_markdown = fix_rtl_hebrew(raw_markdown)
            return final_markdown
        else:
            return "Error: Native conversion completed but output file was not found."
            
    except Exception as e:
        return f"Error during native pdfmd execution: {str(e)}"