from flask import Flask, request, jsonify
import google.generativeai as genai
import re
import os

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
genai.configure(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """You are an expert AI Investment Diversification Advisor created by Team AI Horizon for the INT428 project at LPU. Your team members are Kapil Gupta, Devansh Sharma, and Tejash Rai.

Your ONLY purpose is to analyze investment portfolios and suggest smart diversification strategies.

STRICT RULES:

1. Only respond to questions about: portfolio analysis, asset diversification, mutual funds, stocks, bonds, gold, real estate, ETFs, SIPs, fixed deposits, crypto allocation, risk management, and financial goal planning.

2. If the user asks ANYTHING outside of investment and portfolio topics, reply ONLY with:
I am not designed to answer this type of question. Please ask me about portfolio diversification, asset allocation, or investment strategies.

3. NEVER use markdown formatting. No hash symbols, asterisks, underscores, bullet dashes, or backticks.

4. Use plain numbered points and clear paragraphs only.

5. Be concise, professional, accurate, and factual.

6. When analyzing a portfolio provide: current risk assessment, diversification gaps, recommended asset classes, suggested percentage allocation, and short and long term strategy suggestions.

7. End every investment response with: This information is for educational purposes only and does not constitute financial advice.
"""

def clean_markdown(text):
    text = re.sub(r'#{1,6}\s*', '', text)
    text = re.sub(r'\*{1,3}(.*?)\*{1,3}', r'\1', text)
    text = re.sub(r'_{1,2}(.*?)_{1,2}', r'\1', text)
    text = re.sub(r'`{1,3}[^`]*`{1,3}', '', text)
    text = re.sub(r'^\s*[-•]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def handler(request_obj):
    if request_obj.method == 'POST':
        data = request_obj.get_json()
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({'response': 'Please enter a message.'})
        try:
            model = genai.GenerativeModel(
                model_name='gemini-1.5-flash',
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    top_p=0.85,
                    max_output_tokens=1024,
                ),
                system_instruction=SYSTEM_PROMPT
            )
            response = model.generate_content(user_message)
            reply = clean_markdown(response.text)
            return jsonify({'response': reply})
        except Exception as e:
            return jsonify({'response': f'Error: {str(e)}'}), 500
    return jsonify({'error': 'Method not allowed'}), 405
