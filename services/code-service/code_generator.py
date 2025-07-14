from openai import OpenAI
import os
from dotenv import load_dotenv
import structlog

load_dotenv()

logger = structlog.get_logger()

class CodeGenerator:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        if not self.client.api_key:
            raise ValueError("Missing OpenAI API key in .env file")

    def generate_code(self, prompt: str, language: str = "python") -> str:
        try:
            language_prompts = {
                "python": "You are an expert Python developer. Generate clean, efficient, and well-documented Python code. Follow PEP 8 style guidelines. Include type hints where appropriate. Respond ONLY with the code block (no explanations or markdown formatting).",
                "javascript": "You are an expert JavaScript developer. Generate clean, efficient, and well-documented JavaScript code. Use modern ES6+ syntax. Include JSDoc comments for functions. Respond ONLY with the code block (no explanations or markdown formatting).",
                "typescript": "You are an expert TypeScript developer. Generate clean, efficient, and well-documented TypeScript code. Use proper type annotations. Follow TypeScript best practices. Respond ONLY with the code block (no explanations or markdown formatting).",
                "java": "You are an expert Java developer. Generate clean, efficient, and well-documented Java code. Follow Java naming conventions. Include proper documentation comments. Respond ONLY with the code block (no explanations or markdown formatting).",
                "cpp": "You are an expert C++ developer. Generate clean, efficient, and well-documented C++ code. Use modern C++ features (C++11 and later). Include proper header guards and namespaces. Respond ONLY with the code block (no explanations or markdown formatting).",
                "csharp": "You are an expert C# developer. Generate clean, efficient, and well-documented C# code. Use modern C# features. Follow C# naming conventions. Respond ONLY with the code block (no explanations or markdown formatting).",
                "go": "You are an expert Go developer. Generate clean, efficient, and well-documented Go code. Follow Go conventions and best practices. Include proper error handling. Respond ONLY with the code block (no explanations or markdown formatting).",
                "rust": "You are an expert Rust developer. Generate clean, efficient, and well-documented Rust code. Use proper ownership and borrowing. Include proper error handling with Result types. Respond ONLY with the code block (no explanations or markdown formatting).",
                "php": "You are an expert PHP developer. Generate clean, efficient, and well-documented PHP code. Use modern PHP features (PHP 7.4+). Follow PSR standards. Respond ONLY with the code block (no explanations or markdown formatting).",
                "ruby": "You are an expert Ruby developer. Generate clean, efficient, and well-documented Ruby code. Follow Ruby conventions and best practices. Use idiomatic Ruby patterns. Respond ONLY with the code block (no explanations or markdown formatting).",
                "swift": "You are an expert Swift developer. Generate clean, efficient, and well-documented Swift code. Use modern Swift features. Follow Swift naming conventions. Respond ONLY with the code block (no explanations or markdown formatting).",
                "kotlin": "You are an expert Kotlin developer. Generate clean, efficient, and well-documented Kotlin code. Use modern Kotlin features. Follow Kotlin conventions. Respond ONLY with the code block (no explanations or markdown formatting)."
            }
            
            system_prompt = language_prompts.get(language, language_prompts["python"])
            
            enhanced_prompt = f"Generate {language} code for: {prompt}"
            
            logger.info("Generating code", language=language, prompt_length=len(prompt))
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {"role": "user", "content": enhanced_prompt}
                ],
                temperature=0.3
            )
            
            code = self._clean_response(response.choices[0].message.content)
            
            logger.info("Code generation successful", 
                       language=language, 
                       code_length=len(code),
                       tokens_used=response.usage.total_tokens if response.usage else 0)
            
            return code
            
        except Exception as e:
            logger.error("Code generation failed", error=str(e), language=language)
            return f"""# Error generating {language} code:
# {str(e)}
# Possible fixes:
# 1. Check OPENAI_API_KEY in .env
# 2. Verify internet connection
# 3. Ensure OpenAI account has credits
# 4. Try a different programming language"""

    def _clean_response(self, code: str) -> str:
        code = code.strip()
        if code.startswith("```") and code.endswith("```"):
            code = code[code.find('\n') + 1:-3].strip()
        return code 