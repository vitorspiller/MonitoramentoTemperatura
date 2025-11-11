Monitoramento de Temperatura em Tempo Real 🌡️

Este projeto é um sistema completo para monitorar dados de sensores (neste caso, temperaturas simuladas) em tempo real feito como parte do projeto final da matéria de computação distribuida.

Ele utiliza o RabbitMQ como um message broker para desacoplar o produtor de dados (sensor) do consumidor (servidor web). O servidor web, construído com Flask-SocketIO, consome os dados da fila e os envia instantaneamente para qualquer cliente web conectado via WebSockets.

🏛️ Arquitetura

O fluxo de dados é o seguinte:

    producer.py: Um script Python simula um sensor, gerando dados aleatórios de temperatura.

    Envio: O produtor envia esses dados (como uma mensagem JSON) para uma fila (temperatura) em um servidor RabbitMQ (estamos usando CloudAMQP).

    Consumo: O servidor app.py (Flask) está conectado à mesma fila RabbitMQ. Ele consome as mensagens assim que chegam.

    Broadcast: Ao receber uma mensagem, o servidor Flask a retransmite imediatamente para todos os clientes conectados usando um evento SocketIO (nova_leitura).

    Visualização: O index.html (no navegador do cliente) está ouvindo esse evento SocketIO e, ao recebê-lo, atualiza a lista de temperaturas na tela em tempo real.

[producer.py] ----(JSON)----> [RabbitMQ (Fila)] ----(Pika)----> [app.py (Flask)] ----(SocketIO)----> [Navegador (index.html)]

🚀 Tecnologias Utilizadas

    Python 3

    Flask: Micro-framework web para servir o index.html.

    Flask-SocketIO: Habilita comunicação em tempo real (WebSockets) entre o servidor e o navegador.

    Pika: Biblioteca Python para comunicação com o RabbitMQ.

    Eventlet: Servidor assíncrono WSGI, necessário para o flask-socketio funcionar corretamente com tarefas de fundo.

    RabbitMQ: Message broker para gerenciar a fila de dados.

    HTML5 / JavaScript: Para o frontend.

🛠️ Instalação e Execução

Siga estes passos para rodar o projeto localmente.

1. Pré-requisitos

    Python 3.8+

    Conta no RabbitMQ: Você precisa da URL de conexão (ex: amqps://...). O projeto foi configurado com uma instância gratuita do CloudAMQP.

2. Configuração do Projeto

    Clone o repositório:
    Bash

git clone https://github.com/vitorspiller/MonitoramentoTemperatura.git
cd MonitoramentoTemperatura

Crie e Ative um Ambiente Virtual (Venv): No Windows (CMD):
Bash

python -m venv .venv
.\.venv\Scripts\activate.bat

No Windows (PowerShell):
PowerShell

python -m venv .venv
.\.venv\Scripts\Activate.ps1

(Se o PowerShell bloquear a ativação, rode Set-ExecutionPolicy RemoteSigned -Scope Process e tente novamente).

Crie os Arquivos de Configuração:

    Crie um arquivo chamado requirements.txt e cole o seguinte:
    Plaintext

flask
flask_socketio
pika
eventlet

Crie um arquivo chamado .gitignore para não enviar sua pasta .venv ao GitHub:
Plaintext

    # Ambiente Virtual
    .venv/
    __pycache__/

Instale as Dependências:
Bash

    pip install -r requirements.txt

3. Configure as Variáveis de Ambiente

Antes de rodar, você DEVE atualizar a URL do RabbitMQ em dois arquivos:

    producer.py: RABBITMQ_URL = 'amqps://wpfgnbuw:SUA_URL_AQUI@possum.lmq.cloudamqp.com/wpfgnbuw'

    app.py: RABBITMQ_URL = 'amqps://wpfgnbuw:SUA_URL_AQUI@possum.lmq.cloudamqp.com/wpfgnbuw'

Eles devem ser idênticos.

4. Executando a Aplicação

Você precisará de dois terminais abertos, ambos com o ambiente virtual (.venv) ativado.

    Terminal 1: Inicie o Servidor Web Este terminal irá rodar o servidor Flask e começar a ouvir a fila do RabbitMQ.
    Bash

python app.py

Terminal 2: Inicie o Produtor de Dados Este terminal irá simular o sensor, enviando dados para a fila.
Bash

    python producer.py

5. Veja a Mágica Acontecer

Abra seu navegador e acesse:

http://127.0.0.1:8080

(A porta 8080 está definida no final do app.py. Mude-a se necessário).

Você deverá ver as mensagens de temperatura aparecendo na tela em tempo real.Temperatura
