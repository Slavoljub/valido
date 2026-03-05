from flask import Flask, request, jsonify, render_template
from models.openai_models import predict_validoai_explanation, predict_time_series_analysis

# Kreiraj Flask aplikaciju
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# Ruta za objašnjenje funkcionalnosti
@app.route('/api/explanation', methods=['POST'])
def explanation():
    user_message = request.json.get('message', '')
    response = predict_validoai_explanation(user_message)
    return jsonify({'response': response})

# Ruta za vremenske serije
@app.route('/api/time-series', methods=['POST'])
def time_series():
    user_message = request.json.get('message', '')
    response = predict_time_series_analysis(user_message)
    return jsonify({'response': response})

# Ruta za chat funkcionalnost
@app.route('/api/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')  # Dobij poruku od korisnika
    response = predict_validoai_explanation(user_message)  # Koristi funkciju modela
    return jsonify({'response': response})  # Vraćanje rezultata

# Pokreni aplikaciju
if __name__ == '__main__':
    app.run(debug=True)
