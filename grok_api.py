from openai import OpenAI
import base64


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


# Initialize the client
client = OpenAI(
    api_key="xai-g0OjcY9CJ5V01BYJYqUJt3gdT2Ip1h280lLeSxI9qTaxUh7FAPHraUkmWSHcnALJcyZu8Wd2GEyLdFJn",
    base_url="https://api.x.ai/v1"
)

# Path to your image
image_path = "C:/Users/Daniel/Pictures/Screenshots/Schermafbeelding 2025-04-28 200158.png"

# Encode the image
base64_image = encode_image(image_path)

# Your prompt about the image
prompt = "Can you transcribe this stratego setup like its done in the example provided below?  \
         {6, 2, 2, 7, 4, 2, 2, 7, 2, 6}, \
         {5, 2, 8, 5, 10, 6, 2, 9, 4, 5}, \
         {7, 1, 5, B, 3, 8, B, B, 6, 2}, \
         {3, 3, B, F, B, 3, 4, 3, B, 4}"

# Create the completion request
completion = client.chat.completions.create(
    model="grok-2-vision-1212",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ]
)

# Print the response
print(completion.choices[0].message.content)
