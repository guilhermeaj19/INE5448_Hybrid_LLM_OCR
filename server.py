# Importa as bibliotecas necessárias
from flask import Flask, request, jsonify
from paddleocr import PaddleOCR
import numpy as np
import cv2

# Inicializa o servidor Flask
app = Flask(__name__)

# Inicializa o PaddleOCR (isso pode levar alguns segundos na primeira vez)
# Use use_gpu=False se você não tiver uma GPU configurada
ocr = PaddleOCR(use_textline_orientation=True, lang='la')

@app.route('/ocr', methods=['POST'])
def perform_ocr():
    # Verifica se um arquivo de imagem foi enviado na requisição
    if 'image' not in request.files:
        return jsonify({"error": "Nenhum arquivo de imagem enviado"}), 400

    file = request.files['image']
    
    # Lê a imagem em um formato que o OpenCV/PaddleOCR entende
    img_bytes = file.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Executa o OCR
    result = ocr.ocr(img, cls=True)
    
    # Extrai apenas o texto detectado
    texts = [line[1][0] for line in result[0]]
    
    # Retorna o resultado como JSON
    return jsonify({"transcription": " ".join(texts)})

if __name__ == '__main__':
    # Roda o servidor, acessível por outros containers na mesma rede Docker
    app.run(host='0.0.0.0', port=8868)