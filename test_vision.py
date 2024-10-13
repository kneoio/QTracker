import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Set the OpenAI API key
openai.api_key = api_key

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",  # Change to "gpt-4" if you have access
    messages=[
        {
            "role": "user",
            "content": "Recognize the photo. Is it a petrol station counter or an odometer? Here is the image URL: https://images.wisegeek.com/vehicle-odometer.jpg."
        }
    ],
    max_tokens=300
)

print(response['choices'][0]['message']['content'])
