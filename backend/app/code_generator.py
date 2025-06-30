from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class CodeGenerator:
    def __init__(self):
        # Initialize client with configuration to prevent 'proxies' error
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            max_retries=3  # Adds automatic retries for failed requests
        )
        if not self.client.api_key:
            raise ValueError("Missing OpenAI API key in .env file")

    def generate_code(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert coding assistant. Generate clean, efficient code based on the user's request. "
                            "Respond ONLY with the code block (no explanations or markdown formatting). "
                            "Include all necessary imports and boilerplate."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                timeout=10  # Adds timeout to prevent hanging
            )
            return self._clean_response(response.choices[0].message.content)
        except Exception as e:
            # Enhanced error message with troubleshooting info
            return f"""# Error generating code:
# {str(e)}
# Possible fixes:
# 1. Check OPENAI_API_KEY in .env
# 2. Verify internet connection
# 3. Ensure OpenAI account has credits"""

    def _clean_response(self, code: str) -> str:
        # More robust code cleaning
        code = code.strip()
        if code.startswith("```") and code.endswith("```"):
            code = code[code.find('\n') + 1:-3].strip()
        return code