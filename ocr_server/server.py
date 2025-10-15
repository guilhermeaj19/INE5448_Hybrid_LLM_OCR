from flask import Flask, request, jsonify, redirect, render_template, url_for
from paddleocr import PaddleOCR
import numpy as np
import base64
import os
import cv2
import requests
import uuid

app = Flask(__name__)


N8N_WEBHOOK_URL = "http://172.17.0.1:5678/webhook/1f9989e6-c4cb-490d-8adf-6bffc6e3c0a1"

# --- ARMAZENAMENTO TEMPORÁRIO EM MEMÓRIA ---
results_store = {}

# lang='pt' para português
ocr = PaddleOCR(use_textline_orientation=True, lang='pt') 

@app.route('/upload')
def upload_page():
    return render_template("send_image_page.html")

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/submit', methods=['POST'])
def handle_submit():
    if 'imageFile' not in request.files:
        return "Nenhum arquivo enviado", 400

    file = request.files['imageFile']
    task_id = str(uuid.uuid4())

    # Salva a imagem localmente
    filename = f"{task_id}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Envia para o n8n
    files = {'imageFile': (file.filename, open(filepath, 'rb'), file.content_type)}
    data = {'task_id': task_id}
    try:
        requests.post(N8N_WEBHOOK_URL, files=files, data=data)
    except requests.exceptions.RequestException as e:
        return f"Erro ao acionar o n8n: {e}", 500

    return redirect(url_for('aguardando_page', id=task_id))
# --- ROTA 3: PÁGINA DE ESPERA (polling) ---
@app.route('/aguardando')
def aguardando_page():
    task_id = request.args.get('id')
    return render_template('waiting_response.html', task_id=task_id)


@app.route('/reportar-resultado', methods=['POST'])
def reportar_resultado():
    data = request.json
    task_id = data.get('task_id')

    if not task_id:
        return jsonify({"error": "task_id não fornecido"}), 400

    # Busca a imagem salva localmente
    imagem_b64 = None
    mime_type = None
    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.startswith(task_id):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            with open(filepath, "rb") as f:
                imagem_b64 = base64.b64encode(f.read()).decode('utf-8')
            mime_type = "image/" + filename.split('.')[-1].lower()
            break

    # Injeta no resultado
    if imagem_b64 and mime_type:
        data['imagem_b64'] = imagem_b64
        data['mime_type'] = mime_type

    results_store[task_id] = data
    return jsonify({"status": "ok"}), 200
# --- ROTA 5: FORNECE O RESULTADO PARA A PÁGINA DE ESPERA ---
@app.route('/resultado')
def get_resultado():
    task_id = request.args.get('id')
    if task_id in results_store:
        result = results_store[task_id]
        # Limpa o resultado da memória após ser consultado
        del results_store[task_id] 
        return jsonify({"status": "completo", **result})
    else:
        return jsonify({"status": "processando"})


@app.route('/ocr', methods=['POST'])
def perform_ocr():
    if 'image' not in request.files:
        return jsonify({"error": "Nenhum arquivo de imagem enviado"}), 400

    file = request.files['image']
    
    img_bytes = file.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Verifica e redimensiona a imagem se ela for muito grande
    MAX_SIDE_LIMIT = 3700 
    height, width, _ = img.shape

    if height > MAX_SIDE_LIMIT or width > MAX_SIDE_LIMIT:
        scale = MAX_SIDE_LIMIT / max(height, width)
        new_width = int(width * scale)
        new_height = int(height * scale)
        # Redimensiona a imagem usando o OpenCV
        img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)

    # # Converte a imagem para escala de cinza
    # img_cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # # Aplica um limiar para binarizar a imagem
    # _, img_binarizada = cv2.threshold(img_cinza, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # # Aplica um filtro para remover ruído
    # img_sem_ruido = cv2.medianBlur(img_binarizada, 3)

    # Executa o OCR na imagem (que agora tem um tamanho seguro)
    result = ocr.predict(img)
    
    print("Result OCR: ", result)
    final_text = " ".join(result[0]['rec_texts'])
    
    return jsonify({"transcription": " ".join(final_text)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8868)