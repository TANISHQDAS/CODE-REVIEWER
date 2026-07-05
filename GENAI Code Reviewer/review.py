import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(
    api_key=os.getenv('GEMINI_API_KEY')
)

def review_code(code):

    prompt = f"""
You are a Senior Software Engineer and Code Reviewer.

Review the code in the following format.

# Code Review

## Overall Score
Give a score out of 10.

## Summary
2-3 lines.

## Bugs
List all bugs.

## Syntax Errors
Mention syntax errors if any.

## Security Issues
Explain security problems.

## Performance
Suggest performance improvements.

## Time Complexity
State the time complexity.

## Space Complexity
State the space complexity.

## Best Practices
Mention best practices.

## Improved Code
Return ONLY the corrected code inside triple backticks.

Code:

{code}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text