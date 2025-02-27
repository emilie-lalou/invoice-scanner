
#pages/01_Image_Upload.py
import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import io
import os
import uuid
from datetime import datetime

def ensure_dir(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        st.success(f"Created directory: {directory}")

def save_uploaded_image(uploaded_file, save_path):
    """Save the uploaded file to the specified path"""
    # Create a unique filename
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    filename = f"invoice_{timestamp}_{unique_id}{file_extension}"
    
    # Complete path
    file_path = os.path.join(save_path, filename)
    
    # Save the file
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return filename, file_path

def image_upload_page():
    st.set_page_config(
        page_title="Invoice Image Upload",
        page_icon="📄",
        layout="wide"
    )
    
    # Define the save directory
    SAVE_DIR = "invoice_images"
    ensure_dir(SAVE_DIR)
    
    st.title("Invoice Image Upload")
    st.subheader("Upload invoice images for processing")
    
    # Display current saved images
    st.sidebar.header("Saved Invoices")
    saved_images = []
    if os.path.exists(SAVE_DIR):
        saved_images = [f for f in os.listdir(SAVE_DIR) if f.endswith(('.png', '.jpg', '.jpeg'))]
        st.sidebar.write(f"Total saved invoices: {len(saved_images)}")
        if saved_images:
            st.sidebar.write("Recent uploads:")
            for img in sorted(saved_images, reverse=True)[:5]:
                st.sidebar.text(img)
    
    # File uploader
    uploaded_file = st.file_uploader("Choose an invoice image...", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(image, caption="Uploaded Invoice", use_column_width=True)
        
        with col2:
            st.subheader("Invoice Information")
            st.write(f"**File name:** {uploaded_file.name}")
            st.write(f"**File size:** {uploaded_file.size} bytes")
            st.write(f"**Image dimensions:** {image.size[0]} x {image.size[1]} pixels")
            
            # Save button
            if st.button("Save Invoice to Project Folder", type="primary"):
                filename, file_path = save_uploaded_image(uploaded_file, SAVE_DIR)
                st.success(f"Invoice saved successfully as '{filename}'")
                st.write(f"**Save location:** {file_path}")
                
                # Add refresh button
                if st.button("View All Saved Invoices"):
                    # This will refresh the page
                    st.experimental_rerun()
        
        # Image processing section
        st.subheader("Image Processing Options")
        
        tab1, tab2 = st.tabs(["Preview Adjustments", "OCR Preview"])
        
        with tab1:
            st.write("Adjust image before saving:")
            
            col1, col2 = st.columns(2)
            with col1:
                contrast = st.slider("Contrast", 0.5, 2.0, 1.0, 0.1)
                brightness = st.slider("Brightness", 0.5, 2.0, 1.0, 0.1)
            
            with col2:
                rotate = st.selectbox("Rotation", [0, 90, 180, 270])
                apply_bw = st.checkbox("Convert to Black & White for better OCR")
            
            # Apply adjustments
            adjusted_image = image.copy()
            
            # Apply rotation if selected
            if rotate != 0:
                adjusted_image = adjusted_image.rotate(rotate, expand=True)
            
            # Apply contrast/brightness
            if contrast != 1.0 or brightness != 1.0:
                from PIL import ImageEnhance
                if contrast != 1.0:
                    enhancer = ImageEnhance.Contrast(adjusted_image)
                    adjusted_image = enhancer.enhance(contrast)
                if brightness != 1.0:
                    enhancer = ImageEnhance.Brightness(adjusted_image)
                    adjusted_image = enhancer.enhance(brightness)
            
            # Apply B&W conversion
            if apply_bw:
                adjusted_image = adjusted_image.convert('L')
            
            # Display adjusted image
            st.image(adjusted_image, caption="Adjusted Invoice", use_column_width=True)
            
            # Add option to save the adjusted image
            if st.button("Save Adjusted Invoice"):
                # Convert to RGB if it's not already (PIL needs RGB for some formats)
                if adjusted_image.mode != 'RGB' and not apply_bw:
                    adjusted_image = adjusted_image.convert('RGB')
                
                # Save to memory first
                img_byte_arr = io.BytesIO()
                img_format = os.path.splitext(uploaded_file.name)[1][1:].upper()
                if img_format not in ['JPEG', 'JPG', 'PNG']:
                    img_format = 'PNG'
                adjusted_image.save(img_byte_arr, format=img_format)
                img_byte_arr.seek(0)
                
                # Create a simulated uploaded file
                from streamlit.uploaded_file_manager import UploadedFile
                adjusted_file = UploadedFile(
                    id=uploaded_file.id,
                    name=f"adjusted_{uploaded_file.name}",
                    type=uploaded_file.type,
                    size=len(img_byte_arr.getvalue()),
                    _file=img_byte_arr
                )
                
                # Save the adjusted file
                filename, file_path = save_uploaded_image(adjusted_file, SAVE_DIR)
                st.success(f"Adjusted invoice saved as '{filename}'")
        
        with tab2:
            st.write("OCR Preview (simulated):")
            st.info("In a full implementation, this would show extracted text from the invoice using OCR libraries like Tesseract, pytesseract, or cloud OCR services.")
            st.write("Common invoice data to extract:")
            sample_data = {
                "Invoice Number": "#INV-2023-42",
                "Date": "2024-02-21",
                "Vendor": "ABC Company Ltd.",
                "Total Amount": "$1,234.56",
                "Tax": "$123.45",
                "Due Date": "2024-03-21"
            }
            
            for key, value in sample_data.items():
                st.text(f"{key}: {value}")
            
            st.write("To implement actual OCR, you would need to:")
            st.code("""
# Install required libraries
# pip install pytesseract pillow

import pytesseract
from PIL import Image

# Extract text from image
def extract_text(image):
    return pytesseract.image_to_string(image)
            """)

if __name__ == "__main__":
    image_upload_page()