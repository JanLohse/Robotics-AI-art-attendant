import json
import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Get your own API key from https://aistudio.google.com/app/apikey
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)


class LLMModule:

    # Function to send ingredients to the Gemini API and retrieve recipes
    def call_gemini(self, input_text):
        # Define the prompt to send to the API
        prompt = f"""You are an subservice for a little art robot that guides people around an art museum and analyzes paintings. You take inputs from users and need to determine if they want to go to the next painting, end the tour or if they have a question that needs to be answered regarding the current paintings. This is the voice input from the user: "{input_text}"
        ### Instructions:
        - From the voice input, determine if the user wants to continue the tour, end the tour or if they have a question regarding the current painting.
        - If it is clear that the user wants to continue to the next painting, userWant should be set to "continue".
        - If it is clear that the user wants end the tour or that they have seen enough, userWant should be set to "stop".
        - If the user asks a painting related question (or just a question in general), userWant should be set to "askQuestion".
        - If its unclear what the user has said or if what is said can not be mapped to the other outputs, userWant should be set to "unknown".
        - Do not include any text, explanations, or markdown formatting.
        - The JSON array must follow this structure exactly:
        {{  
            "userWant": "<continue/stop/askQuestion/unknown>",
        }}
        """

        # Send the request to the Gemini API
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            if response_text.startswith("```json") and response_text.endswith("```"):
                response_text = response_text[7:-3].strip()

            answer = json.loads(response_text)

            return answer
        except:
            return json.loads({{"userWant": "unknown"}})


if __name__ == "__main__":
    example = LLMModule()
    response = example.call_gemini("Please continue.")
    reason = response["userWant"]
    print(f"{reason}")
