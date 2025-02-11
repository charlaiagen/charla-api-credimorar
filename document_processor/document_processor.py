import logging
from pathlib import Path
import fitz
import numpy as np
import os
import sys

# Add project root to Python path for imports
project_root = str(Path(__file__).parent.parent.absolute())
if project_root not in sys.path:
    sys.path.append(project_root)

from pdf_parsing.checkbox_detector import CheckboxDetector
from pdf_parsing.ocr_pipeline import OcrPipeline

def process_document(input_file, tesseract_path):
    """
    Process a document with OCR and checkbox detection.

    Args:
        input_file (str): Path to the input PDF file
        tesseract_path (str): Path to the Tesseract executable

    Returns:
        tuple: (success, markdown_content, error)
            - success (bool): True if processing was successful
            - markdown_content (str): Markdown formatted string with results
            - error (str): Error message if processing failed
    """
    try:
        # Initialize components
        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        detector = CheckboxDetector()
        pipeline = OcrPipeline(tesseract_path)

        # Process checkboxes
        checkbox_results = []
        pdf_document = None

        try:
            pdf_document = fitz.open(str(input_path))

            for page_num in range(len(pdf_document)):
                logging.info(f"Processing page {page_num + 1}")
                page = pdf_document[page_num]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

                checkboxes = detector.detect_checkboxes(img_array)

                checkbox_results.append({
                    'page': page_num + 1,
                    'checkboxes': checkboxes
                })

        finally:
            if pdf_document:
                pdf_document.close()

        # Process OCR
        success, text_content, error = pipeline.process_document(input_path)
        if not success:
            return False, None, f"OCR processing failed: {error}"

        # Format results as markdown
        markdown_content = pipeline.format_results_as_markdown(
            text_content=text_content,
            checkbox_results=checkbox_results,
            input_file=input_path
        )

        # Print summary
        print("\nCheckbox Detection Summary:")
        total_checkboxes = sum(len(page['checkboxes']) for page in checkbox_results)
        print(f"Total checkboxes detected: {total_checkboxes}")
        for page_result in checkbox_results:
            checked_count = sum(1 for checkbox in page_result['checkboxes'] if checkbox['checked'])
            print(f"Page {page_result['page']}: {len(page_result['checkboxes'])} checkboxes "
                  f"({checked_count} checked)")

        return True, markdown_content, None

    except Exception as e:
        error_msg = f"Error processing document: {str(e)}"
        logging.error(error_msg)
        return False, None, error_msg


if __name__ == "__main__":
    success, markdown_content, error_msg = process_document("./data/BRADESCO_FORMULARIO_1.pdf", r'D:\Arquivos de Programas\Tesseract\tesseract.exe')
    if success:
        print(markdown_content)
    else:
        print(f"Error: {error_msg}")