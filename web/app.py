from flask import Flask, render_template, request, send_file, jsonify
from flask_cors import CORS
from io import BytesIO
from dplot import create_puzzle_gif
import time

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    holds_text = request.form['holds']
    
    try:
        # Aggiungi un piccolo delay per evitare troppe richieste simultanee
        time.sleep(0.1)
        
        gif_data = create_puzzle_gif(holds_text)
        return send_file(
            BytesIO(gif_data),
            mimetype='image/gif',
            as_attachment=False
        )
    except Exception as e:
        return str(e), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8099, debug=True)