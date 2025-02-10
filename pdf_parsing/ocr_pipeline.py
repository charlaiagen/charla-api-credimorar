import logging
from pathlib import Path
import subprocess
from datetime import datetime
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    TesseractCliOcrOptions,
)
from docling.datamodel.base_models import InputFormat, ConversionStatus
from docling.document_converter import DocumentConverter, PdfFormatOption

class OcrPipeline:
    def __init__(self, tesseract_path):
        self.tesseract_path = tesseract_path
        self._verify_tesseract_languages()
        
    def _verify_tesseract_languages(self):
        """Verify that required Tesseract languages are installed."""
        try:
            result = subprocess.run(
                [self.tesseract_path, '--list-langs'],
                capture_output=True,
                text=True
            )
            available_langs = result.stdout.strip().split('\n')[1:]  # Skip header
            logging.info(f"Available Tesseract languages: {available_langs}")
            
            if 'por' not in available_langs:
                logging.error("Portuguese language pack is not installed for Tesseract!")
                logging.error("Please install it using: https://github.com/tesseract-ocr/tessdata/blob/main/por.traineddata")
                raise RuntimeError("Portuguese language pack not found")
                
        except Exception as e:
            logging.error(f"Error checking Tesseract languages: {str(e)}")
            raise
    
    def process_document(self, input_file):
        """
        Process a document through the OCR pipeline.
        
        Args:
            input_file (Path): Path to the input PDF file
            
        Returns:
            tuple: (success, document content, error message)
        """
        # Configure OCR
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = True
        pipeline_options.do_table_structure = True
        pipeline_options.table_structure_options.do_cell_matching = True

        tesseract_options = TesseractCliOcrOptions(
            tesseract_cmd=self.tesseract_path,
            force_full_page_ocr=True,
            lang='por'  # Use Portuguese language
        )
        pipeline_options.ocr_options = tesseract_options

        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options
                )
            }
        )

        try:
            result = converter.convert(input_file)
            if result.status != ConversionStatus.SUCCESS and result.status != ConversionStatus.PARTIAL_SUCCESS:
                return False, None, f"Conversion failed with status: {result.status}"
            
            return True, result.document.export_to_markdown(), None
            
        except Exception as e:
            error_msg = f"Error during conversion: {str(e)}"
            logging.error(error_msg)
            return False, None, error_msg

    def save_results_to_markdown(self, text_content, checkbox_results, input_file, output_dir="output/ocr_results"):
        """
        Save OCR and checkbox detection results to a markdown file.
        
        Args:
            text_content (str): The OCR text content
            checkbox_results (list): List of checkbox detection results
            input_file (Path): Path to the input PDF file
            output_dir (str): Directory to save the output file
            
        Returns:
            Path: Path to the output markdown file
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = output_path / f"ocr_results_{timestamp}.md"
        
        try:
            with output_file.open('w', encoding='utf-8') as f:
                # Write header with metadata
                f.write(f"# OCR Analysis Results\n\n")
                f.write(f"## Document Information\n")
                f.write(f"- **Source File:** {input_file.name}\n")
                f.write(f"- **Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Write OCR text content
                f.write(f"## OCR Text Content\n")
                f.write("```\n")
                f.write(text_content)
                f.write("\n```\n\n")
                
                # Write checkbox detection results
                f.write(f"## Checkbox Detection Results\n\n")
                for page_result in checkbox_results:
                    f.write(f"### Page {page_result['page']}\n\n")
                    
                    # Add debug image reference if available
                    if 'debug_image' in page_result:
                        debug_path = Path(page_result['debug_image'])
                        relative_path = debug_path.relative_to(output_path.parent)
                        f.write(f"![Debug Image Page {page_result['page']}]({relative_path})\n\n")
                    
                    if not page_result['checkboxes']:
                        f.write("No checkboxes detected on this page.\n\n")
                    else:
                        f.write("| Checkbox | Status | Position | Center | Confidence | Metrics |\n")
                        f.write("|----------|---------|-----------|---------|------------|----------|\n")
                        for i, checkbox in enumerate(page_result['checkboxes']):
                            status = "✓ CHECKED" if checkbox['checked'] else "☐ UNCHECKED"
                            pos = checkbox['position']
                            center = checkbox['center']
                            conf = checkbox.get('confidence', 0)
                            metrics = f"S:{checkbox.get('solidity', 0):.2f}, E:{checkbox.get('edge_uniformity', 0):.2f}, B:{checkbox.get('black_pixel_ratio', 0):.2f}"
                            f.write(f"| {i+1} | {status} | (x:{pos[0]}, y:{pos[1]}) | "
                                   f"(x:{center[0]}, y:{center[1]}) | {conf:.2f} | {metrics} |\n")
                        f.write("\n")
            
            logging.info(f"Results saved to: {output_file}")
            return output_file
            
        except Exception as e:
            logging.error(f"Error saving results to markdown: {str(e)}")
            raise
