# --- Imports --- #
import os
from dotenv import load_dotenv

from openai import AsyncAzureOpenAI # in order to use Azure OpenAI API we must use the AsyncAzureOpenAI class
from pydantic_ai.models.openai import OpenAIModel

# --- Load Environment Variables --- #
load_dotenv()

# --- Azure OpenAI Config --- #
client = AsyncAzureOpenAI(
    api_key=os.getenv('AZURE_OPENAI_API_KEY'),
    api_version=os.getenv('AZURE_OPENAI_API_VERSION'),
    azure_endpoint=os.getenv('AZURE_ENDPOINT'),
)

# --- Models --- #
gpt_4o_mini = OpenAIModel(
    'gpt-4o-mini',
    openai_client=client
    )
gpt_4o = OpenAIModel(
    'gpt-4o',
    openai_client=client
    )