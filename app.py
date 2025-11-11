# ==========================================================
# 1. FORÇAR O EVENTLET - Estas linhas devem ser
# AS PRIMEIRAS LINHAS ABSOLUTAS do seu arquivo.
import eventlet
eventlet.monkey_patch()
# ==========================================================

from flask import Flask, render_template
from flask_socketio import SocketIO
import pika
import json
import time # Esta linha será usada corretamente agora

# ========= CONFIGURAÇÃO =========
RABBITMQ_URL = 'amqps://wpfgnbuw:gWdKRlS4mcfrAdlls4AQ5PY4X46TRd-v@possum.lmq.cloudamqp.com/wpfgnbuw'
QUEUE = 'temperatura'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-forte!'

# 2. Diga explicitamente ao SocketIO que estamos usando eventlet
socketio = SocketIO(app, async_mode='eventlet')

# ========= ROTA WEB =========
@app.route('/')
def index():
    return render_template('index.html')

# ========= CONSUMIDOR RABBITMQ =========
def start_rabbitmq_consumer():
    print(' [APP] Consumidor RabbitMQ iniciando...')
    try:
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE, durable=True)
        print(' [APP] Aguardando mensagens do RabbitMQ...')

        def callback(ch, method, properties, body):
            print(f" [APP] Recebido do RabbitMQ: {body.decode()}")
            try:
                data = json.loads(body)
                # 3. Emite os dados
                # O monkey_patch deve corrigir o problema de contexto
                socketio.emit('nova_leitura', data)
                
            except Exception as e:
                print(f" [APP] Erro ao processar/emitir mensagem: {e}")
            
            ch.basic_ack(delivery_tag=method.delivery_tag)

        channel.basic_consume(queue=QUEUE, on_message_callback=callback)
        channel.start_consuming()

    except pika.exceptions.AMQPConnectionError as e:
        print(f" [APP] Erro ao conectar com RabbitMQ: {e}")
    except Exception as e:
        print(f" [APP] Erro fatal no consumidor: {e}")
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()
            print(" [APP] Conexão RabbitMQ fechada.")

# ========= EMISSOR DE TESTE =========
def test_emitter():
    """Envia um evento de teste a cada 3 segundos."""
    print(" [TEST] Emissor de teste iniciado...")
    counter = 0
    while True:
        counter += 1
        test_data = {'contagem': counter}
        print(f" [TEST] Enviando ping: {test_data}")
        
        # Emite o evento de teste
        socketio.emit('teste_evento', test_data)
        
        # 4. Use socketio.sleep() para cooperar com o eventlet
        socketio.sleep(3) 

@socketio.on('connect')
def on_connect():
    print(' [APP] Cliente web conectou!')

if __name__ == '__main__':
    print(' [APP] Iniciando servidor Flask/SocketIO...')

    socketio.start_background_task(target=start_rabbitmq_consumer)
    socketio.start_background_task(target=test_emitter)
    socketio.run(app, debug=True, port=8080)