from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from openai import OpenAI
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeReviewRequest(BaseModel):
    code: str
    language: str = "python"
    review_type: str = "comprehensive"  # comprehensive, security, performance, style

class CodeReviewResponse(BaseModel):
    review: dict
    score: int
    suggestions: list
    issues: list

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "code-review-service"}

@app.post("/review")
async def review_code(request: CodeReviewRequest):
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        if not client.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        # Create a comprehensive code review prompt
        system_prompt = f"""You are an expert code reviewer and software engineer. Analyze the provided {request.language} code and provide a comprehensive review.

Review Criteria:
1. **Code Quality**: Readability, maintainability, and best practices
2. **Security**: Potential vulnerabilities and security issues
3. **Performance**: Efficiency and optimization opportunities
4. **Style**: Code style, naming conventions, and formatting
5. **Architecture**: Design patterns and structure

Provide your response in the following JSON format:
{{
    "overall_score": 85,
    "summary": "Brief overall assessment",
    "detailed_review": {{
        "code_quality": {{
            "score": 80,
            "assessment": "Detailed assessment",
            "suggestions": ["Suggestion 1", "Suggestion 2"]
        }},
        "security": {{
            "score": 90,
            "assessment": "Security assessment",
            "suggestions": ["Security suggestion 1"]
        }},
        "performance": {{
            "score": 85,
            "assessment": "Performance assessment",
            "suggestions": ["Performance suggestion 1"]
        }},
        "style": {{
            "score": 88,
            "assessment": "Style assessment",
            "suggestions": ["Style suggestion 1"]
        }},
        "architecture": {{
            "score": 82,
            "assessment": "Architecture assessment",
            "suggestions": ["Architecture suggestion 1"]
        }}
    }},
    "critical_issues": [
        {{
            "severity": "high/medium/low",
            "description": "Issue description",
            "line": "Line number or section",
            "fix": "Suggested fix"
        }}
    ],
    "positive_aspects": ["Good practice 1", "Good practice 2"],
    "improvement_areas": ["Area 1", "Area 2"]
}}"""

        user_prompt = f"""Please review this {request.language} code:

```{request.language}
{request.code}
```

Focus on {request.review_type} review. Be thorough but constructive. Highlight both issues and good practices."""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )
        
        # Parse the response
        review_text = response.choices[0].message.content
        
        # Try to extract JSON from the response
        try:
            # Find JSON in the response (in case there's extra text)
            start_idx = review_text.find('{')
            end_idx = review_text.rfind('}') + 1
            json_str = review_text[start_idx:end_idx]
            review_data = json.loads(json_str)
        except:
            # If JSON parsing fails, create a structured response
            review_data = {
                "overall_score": 75,
                "summary": "Code review completed",
                "detailed_review": {
                    "code_quality": {"score": 75, "assessment": review_text, "suggestions": []},
                    "security": {"score": 75, "assessment": "Security review included", "suggestions": []},
                    "performance": {"score": 75, "assessment": "Performance review included", "suggestions": []},
                    "style": {"score": 75, "assessment": "Style review included", "suggestions": []},
                    "architecture": {"score": 75, "assessment": "Architecture review included", "suggestions": []}
                },
                "critical_issues": [],
                "positive_aspects": [],
                "improvement_areas": []
            }
        
        return review_data
        
    except Exception as e:
        print(f"Error in code review: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Code review failed: {str(e)}")

@app.post("/quick-review")
async def quick_review(request: CodeReviewRequest):
    """Quick review for simple feedback"""
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        if not client.api_key:
            raise HTTPException(status_code=500, detail="OpenAI API key not configured")
        
        prompt = f"""Quickly review this {request.language} code and provide:
1. Overall score (1-100)
2. 3 main issues to fix
3. 2 positive aspects
4. Brief summary

Code:
```{request.language}
{request.code}
```

Respond in JSON format:
{{
    "score": 85,
    "issues": ["Issue 1", "Issue 2", "Issue 3"],
    "positives": ["Positive 1", "Positive 2"],
    "summary": "Brief summary"
}}"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        review_text = response.choices[0].message.content
        
        try:
            start_idx = review_text.find('{')
            end_idx = review_text.rfind('}') + 1
            json_str = review_text[start_idx:end_idx]
            return json.loads(json_str)
        except:
            return {
                "score": 75,
                "issues": ["Unable to parse review"],
                "positives": ["Review completed"],
                "summary": "Quick review completed"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quick review failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004) 