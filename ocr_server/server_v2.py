from flask import Flask, request, jsonify, redirect, render_template, url_for
import base64
import os
import requests
import uuid
import threading

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

results_store = {}

def get_colab_endpoint():
    try:
        with open("endpoint.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

# --- FUNÇÃO DE BACKGROUND (O TRABALHO PESADO) ---
def process_image_background(task_id, filepath, endpoint):
    """Esta função roda em paralelo sem travar o usuário"""
    try:
        # Prepara o arquivo. É importante abrir aqui dentro da thread.
        with open(filepath, 'rb') as f:
            files = {'image': (os.path.basename(filepath), f, 'image/jpeg')} # Ajuste o mime type se precisar
            data = {'task_id': task_id}
            
            print(f"🚀 [Task {task_id}] Enviando para Colab...")
            response = requests.post(endpoint, files=files, data=data)
            
            if response.status_code == 200:
                # Sucesso! Salva no dicionário
                print(f"✅ [Task {task_id}] Sucesso!")
                results_store[task_id] = response.json()
            else:
                print(f"❌ [Task {task_id}] Erro Colab: {response.status_code}")
                results_store[task_id] = {"error": "Erro no processamento remoto"}
                
    except Exception as e:
        print(f"❌ [Task {task_id}] Erro de conexão: {e}")
        results_store[task_id] = {"error": str(e)}

# ------------------------------------------------

@app.route('/upload')
def upload_page():
    return render_template("send_image_page.html")

@app.route('/submit', methods=['POST'])
def handle_submit():
    if 'imageFile' not in request.files:
        return "Nenhum arquivo enviado", 400

    file = request.files['imageFile']
    task_id = str(uuid.uuid4())

    # 1. Salva localmente
    filename = f"{task_id}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    endpoint = get_colab_endpoint()
    if not endpoint:
        return "Endpoint não configurado", 500

    thread = threading.Thread(target=process_image_background, args=(task_id, filepath, endpoint))
    thread.start()

    return redirect(url_for('aguardando_page', id=task_id))

@app.route('/aguardando')
def aguardando_page():
    task_id = request.args.get('id')
    return render_template('waiting_response.html', task_id=task_id)

@app.route('/resultado')
def get_resultado():
    task_id = request.args.get('id')
    
    # Verifica se já existe resultado no dicionário
    if task_id in results_store:
        result = results_store[task_id]
        
        # Se tiver erro no processamento
        if "error" in result:
             del results_store[task_id]
             return jsonify({"status": "erro", "message": result["error"]})

        # Sucesso: Monta a imagem e retorna
        imagem_b64 = None
        mime_type = None
        
        try:
            for fname in os.listdir(UPLOAD_FOLDER):
                if fname.startswith(task_id):
                    fpath = os.path.join(UPLOAD_FOLDER, fname)
                    with open(fpath, "rb") as f:
                        imagem_b64 = base64.b64encode(f.read()).decode('utf-8')
                   
                    ext = fname.split('.')[-1].lower()
                    mime_type = f"image/{'jpeg' if ext in ['jpg', 'jpeg'] else ext}"
                    break
        except Exception as e:
            print(f"Erro imagem local: {e}")

        if imagem_b64:
            result['imagem_b64'] = imagem_b64
            result['mime_type'] = mime_type

        del results_store[task_id]
        return jsonify({"status": "completo", **result})
    
    else:
        # Se não está no store, ainda está processando na thread
        return jsonify({"status": "processando"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8868)