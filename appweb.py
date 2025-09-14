import pytesseract
from PIL import Image
import cv2 # Import the OpenCV library
from pdf2image import convert_from_path

import os # To interact with the file system
 # For Windows users, you must set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def image_to_text(image_path, psm=6, debug_image_path=None):
    """
    Extracts text from an image file using Tesseract OCR.
    
    Args:
        image_path (str): The path to the image file.
        psm (int): The Tesseract Page Segmentation Mode to use (default is 6).
        debug_image_path (str, optional): Path to save the preprocessed image for debugging. Defaults to None.
        
    Returns:
        str: The extracted text from the image.
    """
    try:
        # Read the image using OpenCV
        # If image_path is an object (from PDF conversion), use it directly
        if isinstance(image_path, str):
            image = cv2.imread(image_path)
            # Add a check to ensure the image was loaded correctly
            if image is None:
                return f"Error: Could not read image file. It may be corrupt or an unsupported format: {os.path.basename(image_path)}"
        else: # It's an image object from memory
            image = image_path
        
        # --- Preprocessing Steps ---
        # 1. Convert the image to grayscale
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # 2. Apply noise reduction (median blur). This is effective against salt-and-pepper noise.
        #    The kernel size (e.g., 3) must be an odd number.
        denoised_image = cv2.medianBlur(gray_image, 3)
        # 3. Apply thresholding to get a binary image (pure black and white)
        #    Otsu's method automatically determines the best threshold value.
        _, binary_image = cv2.threshold(denoised_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Save the preprocessed image for debugging if a path is provided
        if debug_image_path:
            cv2.imwrite(debug_image_path, binary_image)
            
        # Define Tesseract configuration options
        custom_config = f'--psm {psm}'
        
        # Use pytesseract to extract text from the preprocessed image
        text = pytesseract.image_to_string(binary_image, config=custom_config)
        
        return text
        
    except FileNotFoundError:
        return "Error: Image file not found at the specified path."
    except Exception as e:
        return f"An error occurred: {e}"

# Example usage
if __name__ == "__main__":
    # --- Configuration ---
    # Directory containing the images you want to process
    # **Suggestion**: Create this folder and save your scanned images here.
    input_directory = r'C:\Users\rames\Documents\Scans'
    # Directory where the output .txt files will be saved
    output_directory = r'C:\Users\rames\OCRramesh\ocr_output'
    # Directory to save the black and white images for debugging
    preprocessed_dir = os.path.join(output_directory, 'preprocessed_images')
    # Path to the Poppler bin directory
    poppler_path = r'C:\poppler\poppler-25.07.0\bin'
    # --- End of Configuration ---

    # Create the output directory if it doesn't exist
    os.makedirs(input_directory, exist_ok=True)
    os.makedirs(output_directory, exist_ok=True)
    # Create the directory for preprocessed images
    os.makedirs(preprocessed_dir, exist_ok=True)

    print(f"Processing images from: {input_directory}")
    print(f"Saving text files to: {output_directory}\n")

    # Loop through all files in the input directory
    for filename in os.listdir(input_directory):
        base_filename, extension = os.path.splitext(filename)
        extension = extension.lower()
        
        # Check if the file is a supported image type
        if extension in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
            image_path = os.path.join(input_directory, filename)
            
            print(f"Processing '{filename}'...")
            
            # Define output paths
            debug_image_filepath = os.path.join(preprocessed_dir, f"{base_filename}_preprocessed.png")
            output_filepath = os.path.join(output_directory, f"{base_filename}.txt")
            
            # Process the image and get the text
            extracted_text = image_to_text(image_path, psm=6, debug_image_path=debug_image_filepath)
            
        # Check if the file is a PDF
        elif extension == '.pdf':
            pdf_path = os.path.join(input_directory, filename)
            print(f"Processing PDF '{filename}'...")
            
            try:
                # Convert PDF to a list of images
                pages = convert_from_path(pdf_path, poppler_path=poppler_path)
                full_text = ""
                
                # Process each page
                for i, page_image in enumerate(pages):
                    print(f"  - Processing page {i + 1}/{len(pages)}...")
                    # Convert PIL image to OpenCV format (numpy array)
                    page_cv_image = cv2.cvtColor(np.array(page_image), cv2.COLOR_RGB2BGR)
                    debug_image_filepath = os.path.join(preprocessed_dir, f"{base_filename}_page_{i+1}_preprocessed.png")
                    full_text += image_to_text(page_cv_image, psm=6, debug_image_path=debug_image_filepath) + "\n\n--- Page Break ---\n\n"
                
                extracted_text = full_text
            except Exception as e:
                extracted_text = f"An error occurred while processing the PDF: {e}"

        else:
            continue # Skip unsupported file types

        # Save the extracted text to the file
        output_filepath = os.path.join(output_directory, f"{base_filename}.txt")
        with open(output_filepath, 'w', encoding='utf-8') as f:
            f.write(extracted_text)
        print(f" -> Saved text to '{os.path.basename(output_filepath)}'")