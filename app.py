import streamlit as st
import os
import io
import zipfile
from PIL import Image
from converter import advanced_pdf_processor
import pypdf
from pdfmd import pdf_to_markdown, Options 


logo_image = Image.open("PDFLOGO.jpeg")
st.set_page_config(
    page_title="Token Hero",  # 👈 Updated to Token Hero
    page_icon=logo_image,     # 👈 Ensures your custom logo is used
    layout="wide"
)
# 3. Inject custom CSS to hide ONLY the developer toolbar items without breaking the footer
st.markdown("""
    <style>
        /* Hides the pencil icon, github icon, and manage app button inside the top toolbar */
        .viewerBadge_container__1QSob, 
        button[title="Edit in GitHub"],
        footer,
        [data-testid="stDecoration"] {
            display: none !important;
        }
        
        /* Targets the top toolbar header specifically to hide the GitHub link up there */
        header a[href*="github.com"] {
            display: none !important;
        }
        
        /* Hides the bottom-right manage app button */
        iframe[title="Manage app"], 
        div[data-testid="manage-app-button"],
        button:has(span:contains("Manage app")) {
            display: none !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("Token Hero - PDF to Markdown Converter")
st.write("Tokens cost money now, who knew?")

# 1. Multi-file upload configuration (capped at 5)
uploaded_files = st.file_uploader(
    "Drag & Drop your PDFs here", 
    type=["pdf"], 
    accept_multiple_files=True
)

# Updated to a single-line horizontal radio button selector
selected_profile = st.radio(
    "Conversion Profile",
    options=["Default", "Academic article", "Slides / handouts", "Scan-heavy / OCR-first"],
    horizontal=True,
    help="Matches the official pdfmd configurations for handling columns, layouts, and formatting."
)

if uploaded_files:
    if len(uploaded_files) > 5:
        st.error("Please limit your batch upload to 5 files at a time.")
        st.stop()

    # Dictionary to store compiled conversion assets for mass zip downloads
    converted_manifest = {}
    
    st.subheader("Files")

    # Process each individual file down the sequence stack
    for uploaded_file in uploaded_files:
        file_bytes = uploaded_file.read()
        
        # Temporary file write sequence for backend ingestion
        temp_filename = f"temp_{uploaded_file.name}"
        with open(temp_filename, "wb") as f:
            f.write(file_bytes)
        
        try:
            # Page extraction execution loop for baseline calculations
            pdf_reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            page_count = len(pdf_reader.pages)
            
            # Execute MarkItDown parsing
            md_text = advanced_pdf_processor(temp_filename, profile_name=selected_profile)            
            # Token Math Computations
            # Formula targets 2 visual tiles per page base layout structure plus standard lexical layers
            est_direct_pdf_tokens = (page_count * (258 * 2)) + (page_count * 500)
            est_markdown_tokens = int(len(md_text) / 4)
            
            # Avoid dividing by zero margins
            if est_direct_pdf_tokens == 0: est_direct_pdf_tokens = 1
            token_savings_pct = int(((est_direct_pdf_tokens - est_markdown_tokens) / est_direct_pdf_tokens) * 100)
            
            # Append target files into state dictionary cache for processing loops
            md_filename = uploaded_file.name.replace(".pdf", ".md")
            converted_manifest[md_filename] = md_text

            # Build an isolated visual box wrapper card layout for every target object file
            with st.container(border=True):
                col1, col2 = st.columns([2, 3])
                
                with col1:
                    st.markdown(f"### 📕 {uploaded_file.name}")
                    st.caption(f"Total Pages: {page_count} | Raw Size: {len(file_bytes)/1024:.1f} KB")
                    
                    # Render separate explicit single click local file downloads
                    st.download_button(
                        label=f"⬇️ Save individual .md",
                        data=md_text,
                        file_name=md_filename,
                        mime="text/markdown",
                        key=f"dl_{uploaded_file.name}"
                    )
                    
                with col2:
                    st.markdown("**Token Footprint Comparison**")
                    
                    # Layout tracking metric metrics columns grid block
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Direct PDF (Vision)", f"~{est_direct_pdf_tokens:,}")
                    m2.metric("Markdown Text", f"~{est_markdown_tokens:,}")
                    m3.metric("Tokens Saved", f"{token_savings_pct}%", delta=f"-{est_direct_pdf_tokens - est_markdown_tokens:,}")

        except Exception as e:
            st.error(f"Failed to process target structure {uploaded_file.name}: {str(e)}")
        finally:
            # Clean up local dynamic cache instances securely
            if os.path.exists(temp_filename):
                os.remove(temp_filename)

    # 2. Bulk Processing Zip compilation sector block
    if len(converted_manifest) > 1:
      
        # Construct compilation directory completely in memory buffer storage blocks
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for filename, text_content in converted_manifest.items():
                zip_file.writestr(filename, text_content)
        
        st.download_button(
            label="⬇️ Download All Results (.ZIP)",
            data=zip_buffer.getvalue(),
            file_name="markdown_batch_outputs.zip",
            mime="application/zip",
            use_container_width=True
        )
## --- CUSTOM FOOTER ---
st.markdown("---")  # Adds a subtle horizontal separator line

# Inject your custom text and credit link at the very bottom
st.markdown("""
    <div style='text-align: left; color: #888888; font-size: 14px; padding: 20px 0;'>
        By <a href='https://github.com/AdamUniG/PDF_To_MD' target='_blank' style='color: #a855f7; text-decoration: none; font-weight: bold;'>Adam Vogel</a>, I like to build things <br>
        Thanks to <a href='https://github.com/M1ck4/pdfmd' target='_blank' style='color: #a855f7; text-decoration: none; font-weight: bold;'>M1ck4</a> the GOAT
    </div>
""", unsafe_allow_html=True)