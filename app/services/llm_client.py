import logging
import os

from dotenv import load_dotenv
from langchain.schema import HumanMessage
from langchain_openai import AzureChatOpenAI

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_API_KEY")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")

if not all([azure_endpoint, api_key, deployment_name, api_version]):
    raise ValueError("One or more Azure OpenAI environment variables are missing.")

llm = AzureChatOpenAI(
    azure_endpoint=azure_endpoint,
    openai_api_key=api_key,
    deployment_name=deployment_name,
    openai_api_version=api_version,
    openai_api_type="azure",
    temperature=0
)


def generate_prompt(user_input: str) -> str:
    return (
        f"Extract structured preferences from the following statement in valid JSON format: "
        f"'{user_input}'. Ensure the JSON keys are descriptive and match the context of the input. "
        f"Example structure: {{ 'name': <string>, 'shift_preference': <string>, 'days_off': <string>, 'location': <string>, 'other_preferences': <string> }}."
    )




def parse_response_to_json(response_text: str) -> dict:
    preferences = {}

    name_match = re.search(r"([A-Z][a-z]+ [A-Z][a-z]+)", response_text)
    if name_match:
        preferences["name"] = name_match.group(1).strip()

    shift_match = re.search(r"(morning|evening|night|early morning|continuous 3-day streaks)", response_text, re.IGNORECASE)
    if shift_match:
        preferences["shift_preference"] = shift_match.group(1).strip()

    days_off_match = re.search(r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|weekend|Fridays off|Sundays off|at least one weekend off)", response_text, re.IGNORECASE)
    if days_off_match:
        preferences["days_off"] = days_off_match.group(1).strip()

    location_match = re.search(r"located in ([A-Za-z]+)", response_text, re.IGNORECASE)
    if location_match:
        preferences["location"] = location_match.group(1).strip()

    other_preferences_match = re.search(r"(avoid night shifts|avoid back-to-back shifts|long-haul flights)", response_text, re.IGNORECASE)
    if other_preferences_match:
        preferences["other_preferences"] = other_preferences_match.group(1).strip()

    return preferences



import json
import re


def call_llm(user_input: str) -> dict:
    try:
        # Generate the dynamic prompt
        prompt = generate_prompt(user_input)
        logger.info(f"LLM Prompt: {prompt}")

        # Call the LLM
        response = llm([HumanMessage(content=prompt)])
        response_text = response.content.strip()
        logger.info(f"LLM Response: {response_text}")
        logger.info(f"Type of LLM Response: {type(response_text)}")

        # Remove triple backticks if present
        if response_text.startswith("```") and response_text.endswith("```"):
            response_text = re.sub(r"^```[a-zA-Z]*", "", response_text)  # Remove opening backticks and language specifier
            response_text = response_text.rstrip("```")  # Remove closing backticks

        logger.info(f"Cleaned Response: {response_text}")

        # Attempt to parse the response as JSON
        try:
            response_json = json.loads(response_text)  # Parse the cleaned JSON string
            return response_json
        except json.JSONDecodeError:
            logger.warning("Response is not valid JSON. Attempting to parse manually.")
            return parse_response_to_json(response_text)

    except Exception as e:
        logger.error(f"Error during LLM call: {e}")
        raise


