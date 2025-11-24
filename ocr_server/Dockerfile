# Use uma imagem base do Python
FROM python:3.9-slim

# ---- ADICIONE ESTAS DUAS LINHAS ----
# Atualiza a lista de pacotes e instala a dependência de sistema para o OpenCV
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 libgomp1
# ------------------------------------

# Defina a pasta de trabalho dentro do container
WORKDIR /app

# Copie o arquivo de dependências
COPY requirements.txt .

# Instale as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copie o resto dos seus arquivos (o server.py)
COPY . .

# Exponha a porta que o Flask vai usar
EXPOSE 8868

# O comando para iniciar seu servidor quando o container rodar
CMD ["python3", "server_v2.py"]