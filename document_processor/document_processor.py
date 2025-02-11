import logging
from pathlib import Path
import fitz
import numpy as np
from checkbox_detector import CheckboxDetector
from ocr_pipeline import OcrPipeline

def create_output_directories():
    """Create all necessary output directories."""
    directories = [
        "output/ocr_results",
        "output/debug_images"
    ]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logging.info(f"Created directory: {directory}")

def process_document(input_file, tesseract_path):
    """
    Process a document with OCR and checkbox detection.

    Args:
        input_file (str): Path to the input PDF file
        tesseract_path (str): Path to the Tesseract executable
    """
    try:
        # Initialize components
        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")

        create_output_directories()
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

                checkboxes, debug_path = detector.detect_checkboxes(
                    img_array,
                    output_dir=f"output/debug_images/page_{page_num + 1}"
                )

                checkbox_results.append({
                    'page': page_num + 1,
                    'checkboxes': checkboxes,
                    'debug_image': debug_path
                })

        finally:
            if pdf_document:
                pdf_document.close()

        # Process OCR
        success, text_content, error = pipeline.process_document(input_path)
        if not success:
            raise RuntimeError(f"OCR processing failed: {error}")

        # Save results
        output_file = pipeline.save_results_to_markdown(
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

        print(f"\nResults have been saved to: {output_file}")

    except Exception as e:
        logging.error(f"Error processing document: {str(e)}")
        raise
