from flask import Flask, render_template, request, jsonify
import ollama

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("prompt", "")
    model = request.json.get("model", "llama2:7b")  # Default to 7B if no model is selected

    try:
        # Generate response using Ollama
        response = ollama.generate(model=model, prompt=user_input)

        return jsonify({"response": response["response"]})  # Extract response text
    except Exception as e:
        return jsonify({"error": f"Error communicating with LLaMA 2: {str(e)}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

