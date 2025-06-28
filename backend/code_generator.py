from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()


class CodeGenerator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
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
                temperature=0.5
            )
            return self._clean_response(response.choices[0].message.content)
        except Exception as e:
            return f"# Error generating code:\n# {str(e)}"

    def _clean_response(self, code: str) -> str:
        """Remove markdown code blocks if present"""
        if code.startswith("```") and code.endswith("```"):
            return code[code.find('\n') + 1:-3]
        return code