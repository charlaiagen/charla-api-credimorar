import streamlit as st
import tempfile
import os
from pathlib import Path
import pandas as pd
import asyncio
import nest_asyncio
import logfire
from PIL import Image

# Import existing workflow components
from llm import llm
from structured_output.output_models import BradescoOutput
from document_processor.document_processor import process_document
from pydantic_ai import Agent
import toml

# Enable nested event loops
nest_asyncio.apply()

# Configure logfire
logfire.configure(token='nYw2vt8FDf9w036fjxqKYdwXFzT7YMJ2KXDMBlXmrQjb')

# Configure page
st.set_page_config(
    page_title="Extração de Dados - Credimorar",
    page_icon="🚀",
    layout="centered"
)

# Initialize session state
if 'uploader_key' not in st.session_state:
    st.session_state.uploader_key = 0
if 'download_ready' not in st.session_state:
    st.session_state.download_ready = False
if 'output_file' not in st.session_state:
    st.session_state.output_file = None

# =============================================================================================
# ======================== Stremlit Sidebar ===================================================
# =============================================================================================

image_path = "./static/credimorar.png"
image = Image.open(image_path)
st.markdown(
    """
    <style>
        [data-testid=stSidebar] [data-testid=stImage]{
            text-align: center;
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 100%;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
st.sidebar.image(image, width=200)
st.sidebar.divider()
st.sidebar.markdown("#### Powered by [Charla](https://charla.chat/)")
st.sidebar.markdown(
    "##### Esta aplicação pode cometer erros. Considere verificar todas as informações importantes."
)

# Load prompts
prompts = toml.load("prompt/prompts.toml")

# Configure agents
bradesco_agent = Agent(
    model=llm.gpt_4o,
    result_type=BradescoOutput,
    model_settings={
        "temperature": 0.05,
        "max_result_retries": 3
    },
    system_prompt=prompts["system"]["bradesco_data_extractor"]
)

def to_dataframe(output: BradescoOutput) -> 'pd.DataFrame':
    """Convert BradescoOutput to a pandas DataFrame"""
    campos = []
    preenchimentos = []

    def process_model(prefix: str, model):
        for field_name, value in model:
            if hasattr(value, '__fields__'):  # Check if it's a Pydantic model
                process_model(f"{prefix}{field_name}.", value)
            else:
                campos.append(f"{prefix}{field_name}")
                preenchimentos.append(str(value))

    process_model("", output)

    return pd.DataFrame({
        'campo': campos,
        'preenchimento': preenchimentos
    })

async def process_extraction(markdown_content: str):
    """Process the extraction asynchronously"""
    user_prompt = prompts["user"]["bradesco_data_extractor"].format(input=markdown_content)
    return await bradesco_agent.run(
        user_prompt=user_prompt,
        deps={"content": markdown_content}
    )

st.markdown('## Extração de Dados - Credimorar')
st.markdown('### Faça o upload do formulário de financiamento para extração')

uploaded_file = st.file_uploader("Escolha um arquivo PDF", type=['pdf'], key=f"uploader_{st.session_state.uploader_key}")

if uploaded_file:
    # Create temporary file
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = os.path.join(temp_dir, uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            # Process document
            with st.spinner('Processando documento...'):
                success, markdown_content, error = process_document(
                    temp_path,
                    os.getenv('TESSERACT_PATH', r'D:\Arquivos de Programas\Tesseract\tesseract.exe')
                )
                if not success:
                    st.error(f"Erro no processamento: {error}")


            # Run extraction
            with st.spinner('Gerando relatório...'):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(process_extraction(markdown_content))
                loop.close()

                # Save to Excel
                output_file = 'bradesco_extraction.xlsx'
                df = to_dataframe(result.data)
                df.to_excel(output_file, index=False, engine='openpyxl')

                st.session_state.download_ready = True
                st.session_state.output_file = output_file

        except Exception as e:
            st.error(f"Erro: {str(e)}")

if st.session_state.download_ready and st.session_state.output_file:
    with open(st.session_state.output_file, 'rb') as f:
        if st.download_button(
            "Baixar Relatório",
            data=f,
            file_name=st.session_state.output_file,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ):
            # Clean up after successful download
            os.remove(st.session_state.output_file)
            st.session_state.download_ready = False
            st.session_state.output_file = None
            # Increment uploader key to reset the file uploader
            st.session_state.uploader_key += 1
            # Force a rerun to clear the UI
            st.rerun()