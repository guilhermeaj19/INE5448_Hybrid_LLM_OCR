# Sistema Híbrido LLM+OCR com Fine-Tuning para Paleografia Brasileira

Este repositório contém os componentes de uma Prova de Conceito (PoC) para a transcrição e restauração semântica de documentos manuscritos históricos (Registros Civis do Séc. XIX/XX).

A solução substitui a abordagem tradicional de OCR local por uma arquitetura híbrida distribuída que utiliza **Google Cloud Vision** para extração visual robusta e um modelo **Llama-3-8B Fine-Tuned** para pós-correção e estruturação do texto.

## 🏗️ Arquitetura

O sistema opera em um modelo distribuído **Cliente-Servidor (Gateway + Processamento Remoto)** para viabilizar o uso de LLMs de ponta sem a necessidade de hardware local de alto custo.

* **Gateway Local (Frontend/BFF):** Interface Web leve em Python/Flask que gerencia o upload de imagens, fila de processamento e exibição dos resultados.
* **Nó de Processamento (Remoto):** Notebook Google Colab (GPU T4/L4) que executa o pipeline pesado (OCR via API + Inferência LLM Local) e expõe um endpoint público via Ngrok.

---

## 🚀 Componente 1: Nó de Processamento (Google Colab)

Este é o "cérebro" do sistema (Backend). Ele deve estar em execução antes de iniciar o gateway local.

### Pré-requisitos
* Conta Google (para acesso ao Colab).
* Conta no **Ngrok** (para tunelamento HTTP seguro).
* Projeto no **Google Cloud Platform** com a API **Cloud Vision** habilitada (necessário arquivo JSON da Service Account).

### Configuração do Ambiente (Colab)

1.  Abra o notebook de inferência no Google Colab.
2.  No menu lateral esquerdo **"Secrets" (Segredos)** do Colab (ícone de chave), adicione as seguintes variáveis:
    * `NGROK_TOKEN`: Seu Authtoken do painel do Ngrok.
    * `GOOGLE_JSON_KEY`: O conteúdo *inteiro* do arquivo `service_account.json` do Google Cloud.
3.  Execute todas as células do notebook. O script irá:
    * Instalar as dependências (`unsloth`, `google-cloud-vision`, `fastapi`, `uvicorn`, `pyngrok`).
    * Carregar o modelo Fine-tuned (Llama-3-8B) na GPU.
    * Iniciar o servidor API.
4.  Ao final da execução, copie a **URL pública** gerada pelo Ngrok (ex: `https://abcd-1234.ngrok-free.app`).

---

## 🐳 Componente 2: Gateway Local (Docker)

Interface cliente que roda na sua máquina sem necessidade de instalar Python ou bibliotecas manualmente.

### Pré-requisitos
* [Docker](https://docs.docker.com/get-docker/) instalado e rodando.

### 1. Configuração do Endpoint

Antes de subir o container, você precisa informar onde está o Colab.

1.  Entre na pasta do servidor:
    ```bash
    cd ocr_server
    ```
2.  Crie ou edite o arquivo **`endpoint.txt`** e cole a URL do Ngrok (passo anterior) seguida de `/transcrever`.

    **Exemplo do arquivo `endpoint.txt`:**
    ```text
    [https://seu-hash-ngrok.ngrok-free.app/transcrever](https://seu-hash-ngrok.ngrok-free.app/transcrever)
    ```

### 2. Build e Execução

Construa a imagem e inicie o container. O Docker cuidará de todas as dependências.

**Passo 1: Construir a Imagem**
```bash
# O ponto (.) no final é importante
sudo docker build -t ocr_server .
```

**Passo 2: Rodar o Container**
```bash
# O ponto (.) no final é importante
sudo docker run --rm --name ocr_gateway -it -p 8868:8868 ocr_server
```

### 3. Acesso

Abra seu navegador e acesse: 👉 http://localhost:8868/upload




