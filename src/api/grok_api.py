from langchain_xai import ChatXAI
from dotenv import load_dotenv
import os
import base64
from src.parsing.parse_setup import string_to_json

# Load environment variables
load_dotenv()
XAI_API_KEY = os.getenv("XAI_API_KEY")

# If not found, try loading from project root
if not XAI_API_KEY:
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    env_path = os.path.join(project_root, '.env')
    load_dotenv(env_path)
    XAI_API_KEY = os.getenv("XAI_API_KEY")

# Few-shot examples - stored as data structure for efficiency
FEW_SHOT_EXAMPLES = [
    {
        "image_path": "C:/Users/Daniel/Pictures/Screenshots/Screenshot 2025-07-15 120650.png",
        "output": {
            "1": "['4', 'B', '4', '10', '4', '6', '2', '8', '5', '3']",
            "2": "['6', '2', '7', '2', '7', '2', '2', '1', '9', '6']",
            "3": "['8', '2', '5', 'B', '3', 'B', '4', '7', '2', '2']",
            "4": "['3', '3', 'B', 'F', 'B', 'B', '5', '5', '3', '6']"
        }
    },
    {
        "image_path": "C:/Users/Daniel/Pictures/Screenshots/Screenshot 2025-07-15 120950.png",
        "output": {
            "1": "['2', '6', '4', '2', '2', '5', '7', '2', '6', '2']",
            "2": "['8', '2', '4', 'B', '2', '9', '1', '3', '10', '7']",
            "3": "['5', '2', '7', 'B', '3', '8', 'B', '6', '4', 'B']",
            "4": "['3', '5', '3', '4', '6', '3', 'B', '5', 'B', 'F']"
        }
    },
    {
        "image_path": "C:/Users/Daniel/Pictures/Screenshots/Screenshot 2025-07-15 151053.png",
        "output": {
            "1": "['6', '2', '4', '8', '2', '5', '2', '4', '2', 'B']",
            "2": "['2', '9', '2', '1', '7', '2', '4', '5', '6', '5']",
            "3": "['4', 'B', 'B', '7', '3', '10', '6', '8', '3', '7']",
            "4": "['B', 'F', 'B', '3', 'B', '5', '3', '6', '3', '2']"
        }
    },
    {
        "image_path": "C:/Users/Daniel/Pictures/Screenshots/Screenshot 2025-07-15 150646.png",
        "output": {
            "1": "['5', '2', '2', '6', '5', '2', '6', '4', '5', '2']",
            "2": "['8', '6', '9', '3', '7', '2', '10', '2', '8', '2']",
            "3": "['6', '1', '3', 'B', '4', '4', '7', '3', 'B', '5']",
            "4": "['7', '4', 'B', 'F', 'B', 'B', '3', 'B', '3', '2']"
        }
    }
]

# Cache for encoded images to avoid re-encoding
_image_cache = {}

def encode_image(image_path):
    """Encode image to base64 with caching"""
    if image_path in _image_cache:
        return _image_cache[image_path]
    
    with open(image_path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode('utf-8')
        _image_cache[image_path] = encoded
        return encoded

def format_json_output(output_dict):
    """Format output dictionary as JSON string matching the original format"""
    lines = ["{"]
    for i, (key, value) in enumerate(output_dict.items()):
        comma = "," if i < len(output_dict) - 1 else ""
        lines.append(f'  "{key}": "{value}"{comma}')
    lines.append("}")
    return "\n".join(lines)

def build_few_shot_messages(examples, task_prompt):
    """Build few-shot messages efficiently"""
    messages = []
    
    for example in examples:
        # User message with image
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": task_prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{encode_image(example['image_path'])}",
                        "detail": "high"
                    }
                }
            ]
        })
        
        # Assistant response
        messages.append({
            "role": "assistant",
            "content": format_json_output(example['output'])
        })
    
    return messages


def transcribe_setup(path, use_few_shot=True, max_examples=4):
    """
    Transcribe a Stratego setup image to JSON format.
    
    Args:
        path: Path to the user's input image
        use_few_shot: Whether to use few-shot examples (default: True)
        max_examples: Maximum number of few-shot examples to use (default: 3)
    """
    # Define the task prompt
    task_prompt = """
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
        temperature=0.25
    )


    # Build messages
    messages = [
        {
            "role": "system",
            "content": [
                {
                    "type": "text",
                    "text": """
            Ensure the transcription is precise and follows the grid structure.
            Use numbers (1-10) for piece ranks, 'B' for bombs, and 'F' for the flag.
            Make sure to double-check your results, as mismatches can happen. Here are some examples of mismatches: 
            - A piece doesnt get detected and the next pieces in the row all get shifted one space to the left. The row is filled out with a hallucinated piece. For example '3', '3', '3', '7', '4', 'B', 'F', 'B' is detected as '3', '3', '7', '4', 'B', 'F', 'B', 'B'.
            - One piece gets detected wrong when pieces are repeated multiple times in a row. For example ‘2’, ‘2’, ‘2’, ‘2’ is detected as ‘2’, ‘2’, ‘2’, ‘5’.
            - 2 seen as 4
            - 4 seen as 2 
            - 5 seen as 3 (especially on the 5th position of the first row)
            - 5 seen as 4
            - 5 seen as 7
            - 6 seen as 5
            - 6 seen as 8
            - B seen as 8
            - F seen as 8
            """
                }
            ]
        }
    ]

    # Add few-shot examples if enabled
    if use_few_shot:
        examples_to_use = FEW_SHOT_EXAMPLES[:max_examples]
        few_shot_messages = build_few_shot_messages(examples_to_use, task_prompt)
        messages.extend(few_shot_messages)

    # Add user's input image
    messages.append({
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": task_prompt
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{encode_image(path)}",
                    "detail": "high"
                }
            }
        ]
    })

    # Invoke the chat model and get the response
    response = chat.invoke(messages)

    setup = string_to_json(response.content)
    return setup

