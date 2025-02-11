# --- Custom modules for the project --- #
from llm import llm # for LLM calls
from structure import FinancialInstitutionOutput, BradescoOutput # for output data structure
from checkbox_detector import CheckboxDetector # for checkbox detection
from ocr_pipeline import OcrPipeline # for OCR and checkbox detection
from document_processor import document_processor

# --- Python modules --- #
import logfire # for logging, debugging and tracing
import toml # for prompts
from pydantic_ai import Agent, RunContext # AI models and Agents
import logging
from pathlib import Path
import numpy as np


# --- Load the prompts --- #
prompts = toml.load("prompt/prompts.toml")

# --- Configure logfire --- #
logfire.configure()

# --- Building agents --- #
# Este agente faz a detecção de instituição financeira no documento
financial_institution_detector_agent = Agent(
    model = llm.gpt_4o_mini,
    result_type = FinancialInstitutionOutput,
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
        "temperature": 0.1
    },
    system_prompt = prompts["system"]["bradesco_data_extractor"]
)


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Configuration
    INPUT_FILE = "./data/BRADESCO_FORMULARIO_1.pdf"
    TESSERACT_PATH = r'D:\Arquivos de Programas\Tesseract\tesseract.exe'

    # Process the document
    process_document(INPUT_FILE, TESSERACT_PATH)
