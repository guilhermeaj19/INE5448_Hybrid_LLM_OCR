# Sistema Híbrido LLM+OCR para Paleografia Brasileira

Este repositório contém os componentes para um protótipo de sistema de software capaz de transcrever imagens digitalizadas de documentos manuscritos do Registro Civil Brasileiro. A arquitetura implementa um pipeline de pós-correção de OCR utilizando uma LLM, orquestrado pela plataforma de automação n8n.

## N8N - Orquestração do Workflow

O n8n é utilizado como o orquestrador central do fluxo de trabalho, conectando os diferentes serviços (OCR, LLM) e gerenciando o fluxo de dados.

### Pré-requisitos

Docker instalado e em execução no sistema.

### Execução

Para iniciar a instância do n8n, utilize o seguinte comando no seu terminal. Ele irá iniciar o n8n na porta 5678 e persistir seus dados na pasta **~/.n8n**.

```bash

    sudo docker run -it --rm \
    --name n8n \
    -p 5678:5678 \
    -u $(id -u):$(id -g) \
    -v ~/.n8n:/home/node/.n8n:z \
    n8nio/n8n
```

Nota de Permissão: Em alguns sistemas Linux, a pasta **~/.n8n** pode ser criada com permissões incorretas. Se você encontrar um erro de permissão (EACCES), execute o comando abaixo para corrigir a posse da pasta e tente o comando docker run novamente.
```bash
    sudo chown -R $(whoami):$(whoami) ~/.n8n
```

### Importando o Workflow

Após iniciar o n8n e acessá-lo em http://localhost:5678:

Crie um novo workflow em branco.

No menu superior, vá em **File > Import from File**.

Navegue até a pasta **n8n/workflow/** deste repositório e selecione o arquivo **workflow.json**.

O fluxo de trabalho completo será carregado na sua tela.

## OCR Server - Transcrição Base

Este componente é um serviço de API customizado, construído com Python e Flask, que executa a transcrição inicial das imagens.

### Visão Geral

O servidor utiliza a biblioteca PaddleOCR para realizar o Reconhecimento Óptico de Caracteres.

Tecnologia Base: PaddleOCR (https://github.com/PaddlePaddle/PaddleOCR)

Licença: O projeto PaddleOCR é distribuído sob a licença Apache 2.0. Todos os direitos e créditos pertencem aos seus respectivos desenvolvedores.

### Build e Execução

Para construir e iniciar o servidor de OCR, siga os passos abaixo a partir da pasta **ocr_server**.

Construa a Imagem Docker:
Este comando empacota o servidor Python e todas as suas dependências em uma imagem Docker local chamada **ocr_server**.
Bash

```bash 
    sudo docker build -t ocr_server .
```

Inicie o Container:
Este comando inicia o servidor a partir da imagem que você acabou de construir. O serviço de OCR estará disponível na porta 8868.

```bash
    sudo docker run --rm --name paddleocr -it -p 8868:8868 ocr_server
```

## LLM - Pós-Correção

Nesta fase do projeto, o componente de pós-correção com um modelo de linguagem grande (LLM) especializado através de fine-tuning ainda não foi implementado. Para fins de demonstração e validação da arquitetura do fluxo de trabalho, o workflow utiliza uma conexão com um modelo de linguagem genérico (Google Gemini) como substituto. A integração final com o modelo treinado para paleografia é um próximo passo planejado no desenvolvimento do sistema.