from flask import Flask, render_template, request, jsonify
from sympy import symbols, Eq, solve, sympify, parse_expr, SympifyError
import requests
import json
import re
import time

# Copyright © 2023 Chetan Sharma. All rights reserved.
# This source code is protected by copyright law and international treaties.
# Unauthorized reproduction or distribution of this source code, or any portion of it,
# may result in severe civil and criminal penalties, and will be prosecuted to the
# maximum extent possible under the law.

app = Flask(__name__)

# 🔐 OpenRouter API key and endpoint
API_KEY = "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"
API_URL = "https://openrouter.ai/api/v1/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 🛠️ Auto-fix equations like 5x to 5*x
def format_equation(equation):
    equation = equation.replace("^", "**")  # Handle power symbol
    equation = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', equation)  # 5x → 5*x
    equation = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', equation)  # x2 → x*2 (optional)
    return equation

# 🧮 Enhanced equation solver that can handle more complex equations
def solve_equation(equation_str):
    try:
        if "=" in equation_str:
            left, right = equation_str.split("=")
            x = symbols("x")
            formatted_left = format_equation(left)
            formatted_right = format_equation(right)
            eq = Eq(sympify(formatted_left), sympify(formatted_right))
            solution = solve(eq, x)
            
            if not solution:
                return "No solution found"
            elif len(solution) == 1:
                return f"x = {solution[0]}"
            else:
                return f"Solutions: {', '.join([f'x = {sol}' for sol in solution])}"
        else:
            return "❌ Invalid equation format. Use '=' sign."
    except Exception as e:
        return f"❌ Error solving equation: {str(e)}"

@app.route("/", methods=["GET", "POST"])
def index():
    equation = ""
    equation_answer = ""
    riddle = ""
    riddle_answer = ""

    if request.method == "POST":
        equation = request.form.get("equation", "").strip()
        riddle = request.form.get("riddle", "").strip()

        # ✅ Solve math equation
        if equation:
            equation_answer = solve_equation(equation)

        # ✅ Solve riddle using OpenRouter
        if riddle:
            try:
                payload = {
                    "model": "openai/gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are a riddle solver. Provide concise, accurate answers to riddles. If the riddle is common, give the standard answer. If it's ambiguous, provide the most likely solution."},
                        {"role": "user", "content": f"Answer this riddle: {riddle}"}
                    ]
                }

                response = requests.post(API_URL, headers=HEADERS, data=json.dumps(payload))

                if response.status_code == 200:
                    result = response.json()
                    riddle_answer = result['choices'][0]['message']['content'].strip()
                else:
                    riddle_answer = f"❌ API Error: {response.status_code} - {response.text}"
            except Exception as e:
                riddle_answer = f"❌ Error solving riddle: {str(e)}"

    return render_template(
        "index.html",
        equation=equation,
        equation_answer=equation_answer,
        riddle=riddle,
        riddle_answer=riddle_answer,
    )

# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy", "timestamp": time.time()})

if __name__ == "__main__":
    app.run(debug=True)
