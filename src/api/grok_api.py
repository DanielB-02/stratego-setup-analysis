from langchain_xai import ChatXAI
from dotenv import load_dotenv
import os
import base64
from src.parsing.parse_setup import string_to_json

# Load environment variables
load_dotenv()
XAI_API_KEY = os.getenv("XAI_API_KEY")


# Function to encode image to base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def transcribe_setup(path):
    # Define image paths
    user_input_image_path = path
    assistant_1_image_path = "C:/Users/Daniel/Pictures/Screenshots/Screenshot 2025-07-08 163819.png"
    assistant_2_image_path = "C:/Users/Daniel/Pictures/Screenshots/Screenshot 2025-07-08 123034.png"

    # Encode images
    user_input_base64_image = encode_image(user_input_image_path)
    assistant_1_base64_image = encode_image(assistant_1_image_path)
    assistant_2_base64_image = encode_image(assistant_2_image_path)

    # Define the prompt
    prompt = """
    Transcribe a Stratego setup and place it in a JSON object, like in the example below.
    
    Example:
    {
      "1": "['6', '6', '2', '2', '2', '7', '2', '2', '6', '6']"
      "2": "['4', '2', '9', '2', '5', '2', '10', '4', '3', '8']"
      "3": "['5', '4', 'B', 'B', '8', '1', '7', 'B', 'B', '5']"
      "4": "['7', '4', '3', '3', '3', '5', 'B', 'F', 'B', '3']"
    }
    """

    # Initialize ChatXAI
    chat = ChatXAI(
        api_key=XAI_API_KEY,
        model="grok-2-vision-1212",
        temperature=0.2
    )

    # Define messages
    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": """
                    Ensure the transcription is precise and follows the grid structure.
                    Ignore the color of the background, whether blue or red. It's not a relevant detail for the model. 
                    Use numbers (1-10) for piece ranks, 'B' for bombs, and 'F' for the flag.
                    Make sure to double-check your results, as mismatches can happen. 
                    """
                }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{assistant_1_base64_image}",
                        "detail": "high"
                    }
                }
            ]
        },
        {
            "role": "assistant",
            "content": """
    {
      "1": "['4', 'B', '4', '10', '4', '6', '2', '8', '5', '3']"
      "2": "['6', '2', '7', '2', '7', '2', '2', '1', '9', '6']"
      "3": "['8', '2', '5', 'B', '3', 'B', '4', '7', '2', '2']"
      "4": "['3', '3', 'B', 'F', 'B', 'B', '5', '5', '3', '6']"
    }
            """
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{assistant_2_base64_image}",
                        "detail": "high"
                    }
                }
            ]
        },
        {
            "role": "assistant",
            "content": """
    {
      "1": "['2', '6', '4', '2', '2', '5', '7', '2', '6', '2']"
      "2": "['8', '2', '4', 'B', '2', '9', '1', '3', '10', '7']"
      "3": "['5', '2', '7', 'B', '3', '8', 'B', '6', '4', 'B']"
      "4": "['3', '5', '3', '4', '6', '3', 'B', '5', 'B', 'F']"
    }
            """
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{user_input_base64_image}",
                        "detail": "high"
                    }
                }
            ]
        }
    ]

    # Invoke the chat model and get the response
    response = chat.invoke(messages)

    setup = string_to_json(response.content)
    return setup

