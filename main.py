# --- Custom modules for the project --- #
from llm import llm # for LLM calls
from structured_output.output_models import FinancialInstitutionOutput, BradescoOutput # for output data structure
from pdf_parsing.checkbox_detector import CheckboxDetector # for checkbox detection
from pdf_parsing.ocr_pipeline import OcrPipeline # for OCR and checkbox detection
from document_processor.document_processor import process_document # for document processing orchestration

# --- Python modules --- #
import logfire # for logging, debugging and tracing
import toml # for prompts
from pydantic_ai import Agent, RunContext # AI models and Agents
import logging
from pathlib import Path
import numpy as np
import pandas as pd

# --- Load the prompts --- #
prompts = toml.load("prompt/prompts.toml")

# --- Configure logfire --- #
logfire.configure(token='nYw2vt8FDf9w036fjxqKYdwXFzT7YMJ2KXDMBlXmrQjb')

# --- Building agents --- #
# Este agente faz a detecção de instituição financeira no documento
financial_institution_detector_agent = Agent(
    model = llm.gpt_4o_mini,
    result_type = str,
    model_settings = {
        "temperature": 0
    },
    system_prompt = prompts["system"]["financial_institution_detector"]
)

# Este agente realiza a extração de dados, considerando o template de documento do Bradesco.
bradesco_agent = Agent(
    model = llm.gpt_4o,
    result_type = BradescoOutput,
    model_settings = {
        "temperature": 0.05,
        "max_result_retries": 3  # Increase retries to see more attempts
    },
    system_prompt = prompts["system"]["bradesco_data_extractor"]
)

def to_dataframe(output: BradescoOutput) -> 'pd.DataFrame':
    """
    Convert BradescoOutput to a pandas DataFrame with 'campo' and 'preenchimento' columns.
    
    Args:
        output: BradescoOutput instance
        
    Returns:
        pd.DataFrame with columns ['campo', 'preenchimento']
    """
    from pydantic import BaseModel
    
    # Initialize lists to store flattened data
    campos = []
    preenchimentos = []
    
    def process_model(prefix: str, model: BaseModel):
        """Recursively process nested Pydantic models"""
        for field_name, value in model:
            if isinstance(value, BaseModel):
                # Recursively process nested models
                process_model(f"{prefix}{field_name}.", value)
            else:
                # Add leaf node to lists
                campos.append(f"{prefix}{field_name}")
                preenchimentos.append(str(value))
    
    # Process the root model
    process_model("", output)
    
    # Create DataFrame
    df = pd.DataFrame({
        'campo': campos,
        'preenchimento': preenchimentos
    })
    
    return df

# --- Load and Process the PDF file --- #
INPUT_FILE = "./data/BRADESCO_FORMULARIO_1.pdf"
TESSERACT_PATH = r'D:\Arquivos de Programas\Tesseract\tesseract.exe'

# Process document and get markdown content
success, markdown_content, error = process_document(INPUT_FILE, TESSERACT_PATH)
if not success:
    logging.error(f"Document processing failed: {error}")
    exit(1)

# Log the markdown content for debugging
logging.info("Markdown Content:")
logging.info("-" * 50)
logging.info(markdown_content)
logging.info("-" * 50)

# --- Run the Agents --- #
try:
    # Add the template to the user prompt
    user_prompt = prompts["user"]["bradesco_data_extractor"].format(input=markdown_content)

    bradesco_extraction = bradesco_agent.run_sync(
        user_prompt=user_prompt,
        deps={"content": markdown_content}
    )

    # --- Logging the results --- #
    logfire.notice(
        "Bradesco Extraction: {bradesco_extraction}",
        bradesco_extraction=bradesco_extraction.data
    )

    # Print the response for debugging
    print("\nAgent Response:")
    print("=" * 50)
    print(f"Response Type: {type(bradesco_extraction)}")
    print(f"Data Type: {type(bradesco_extraction.data)}")
    print("\nResponse Data:")
    print("-" * 50)
    print(bradesco_extraction.data)
    print("=" * 50)

    # Convert to DataFrame
    df = to_dataframe(bradesco_extraction.data)

    # Save to CSV
    output_file = 'bradesco_extraction.csv'
    df.to_csv(output_file, index=False, encoding='utf-8')
    logging.info(f"Extraction saved to {output_file}")

except Exception as e:
    logging.error("Error during extraction:")
    logging.error(str(e))
    raise
