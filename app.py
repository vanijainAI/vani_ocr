import os
from flask import Flask, request, render_template, redirect, url_for, flash
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
import cv2
import numpy as np
import pytesseract

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'pdf'}

# --- Path to External Dependencies (for local Windows development) ---
# This will be None on Render, which is what we want.
POPPLER_PATH = os.environ.get('POPPLER_PATH', None)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'supersecretkey' # Needed for flashing messages

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def image_to_text(image_source, psm=6):
    """
    Extracts text from an image source using Tesseract OCR.
    
    Args:
        image_source (str or numpy.ndarray): The path to the image file or an image object from memory.
        psm (int): The Tesseract Page Segmentation Mode to use (default is 6).
        
    Returns:
        str: The extracted text from the image.
    """
    try:
        if isinstance(image_source, str):
            image = cv2.imread(image_source)
            if image is None:
                return f"Error: Could not read image file: {os.path.basename(image_source)}"
        else: # It's an image object from memory
            image = image_source
        
        # --- Preprocessing Steps ---
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        denoised_image = cv2.medianBlur(gray_image, 3)
        _, binary_image = cv2.threshold(denoised_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Define Tesseract configuration options
        custom_config = f'--psm {psm}'
        
        # Use pytesseract to extract text from the preprocessed image
        text = pytesseract.image_to_string(binary_image, config=custom_config)
        
        return text
        
    except FileNotFoundError:
        return "Error: Image file not found at the specified path."
    except Exception as e:
        return f"An error occurred during OCR: {e}"

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # --- Perform OCR ---
            extracted_text = ""
            try:
                if filename.lower().endswith('.pdf'):
                    pages = convert_from_path(filepath, poppler_path=POPPLER_PATH)
                    for i, page_image in enumerate(pages):
                        page_cv_image = cv2.cvtColor(np.array(page_image), cv2.COLOR_RGB2BGR)
                        extracted_text += f"--- Page {i+1} ---\n"
                        extracted_text += image_to_text(page_cv_image, psm=6) + "\n\n"
                else:
                    # Use your existing image logic
                    extracted_text = image_to_text(filepath, psm=6)
            except Exception as e:
                extracted_text = f"An error occurred during OCR: {e}"
            
            return render_template('index.html', extracted_text=extracted_text, filename=filename)

    return render_template('index.html', extracted_text=None)

if __name__ == '__main__':
    # --- Local Windows Development Setup ---
    # Define paths for local external dependencies
    # On Windows, you might need to set the POPPLER_PATH environment variable
    # or define it here if the getenv call doesn't work for your setup.
    # Example: POPPLER_PATH = r'C:\poppler\poppler-25.07.0\bin'
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    # Ensure the upload folder exists when running locally
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Use Waitress for local production-like testing
    from waitress import serve
    print("Starting development server on http://127.0.0.1:5000")
    serve(app, host="127.0.0.1", port=5000)
