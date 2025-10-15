from flask import Flask, request, jsonify
from paddleocr import PaddleOCR
import numpy as np
import cv2

app = Flask(__name__)

# lang='pt' para português
ocr = PaddleOCR(use_textline_orientation=True, lang='pt') 

@app.route('/ocr', methods=['POST'])
def perform_ocr():
    if 'image' not in request.files:
        return jsonify({"error": "Nenhum arquivo de imagem enviado"}), 400

    file = request.files['image']
    
    img_bytes = file.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # --- INÍCIO DO NOVO BLOCO DE CÓDIGO ---
    # Verifica e redimensiona a imagem se ela for muito grande
    MAX_SIDE_LIMIT = 3700  # Usamos um limite seguro, um pouco abaixo do da biblioteca
    height, width, _ = img.shape

    if height > MAX_SIDE_LIMIT or width > MAX_SIDE_LIMIT:
        scale = MAX_SIDE_LIMIT / max(height, width)
        new_width = int(width * scale)
        new_height = int(height * scale)
        # Redimensiona a imagem usando o OpenCV
        img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
    # --- FIM DO NOVO BLOCO DE CÓDIGO ---

    # Executa o OCR na imagem (que agora tem um tamanho seguro)
    result = ocr.predict(img)
    
    print("Result OCR: ", result)
    final_text = " ".join(result[0]['rec_texts'])
    
    return jsonify({"transcription": " ".join(final_text)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8868)