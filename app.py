import eventlet
eventlet.monkey_patch()
from flask import Flask, render_template
from flask_socketio import SocketIO
import pika
import json

RABBITMQ_URL = 'amqps://wpfgnbuw:gWdKRlS4mcfrAdlls4AQ5PY4X46TRd-v@possum.lmq.cloudamqp.com/wpfgnbuw'
QUEUE = 'temperatura'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'uma-chave-secreta-muito-forte!'

socketio = SocketIO(app, async_mode='eventlet')

@app.route('/')
def index():
    return render_template('index.html')

def start_rabbitmq_consumer():
    print(' [APP] Consumidor RabbitMQ iniciando (Modo POLLING)...')
    channel = None
    
    while True:
        try:
            params = pika.URLParameters(RABBITMQ_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE, durable=True)
            print(' [APP] Conectado e lendo fila do RabbitMQ...')

            while True:
                method, properties, body = channel.basic_get(queue=QUEUE, auto_ack=False)

                if method: 
                    print(f" [APP] Recebido do RabbitMQ: {body.decode()}")
                    try:
                        data = json.loads(body)
                        socketio.emit('nova_leitura', data)
                        channel.basic_ack(method.delivery_tag)
                        
                    except Exception as e:
                        print(f" [APP] Erro ao processar/emitir mensagem: {e}")
                socketio.sleep(0.1) 
                
        except pika.exceptions.AMQPConnectionError as e:
            print(f" [APP] Erro de conexão com RabbitMQ: {e}. Tentando reconectar em 5s...")
            if channel and channel.is_open:
                channel.close()
            if 'connection' in locals() and connection.is_open:
                connection.close()
            socketio.sleep(5) 
        except Exception as e:
            print(f" [APP] Erro fatal no consumidor: {e}")
            socketio.sleep(5)

def test_emitter():
    """Envia um evento de teste a cada 3 segundos."""
    print(" [TEST] Emissor de teste iniciado...")
    counter = 0
    while True:
        counter += 1
        test_data = {'contagem': counter}
        print(f" [TEST] Enviando ping: {test_data}")
        
        socketio.emit('teste_evento', test_data)
        socketio.sleep(3) 
@socketio.on('connect')
def on_connect():
    print(' [APP] Cliente web conectou!')

if __name__ == '__main__':
    print(' [APP] Iniciando servidor Flask/SocketIO...')
    socketio.start_background_task(target=start_rabbitmq_consumer)
    socketio.start_background_task(target=test_emitter)
    socketio.run(app, debug=True, port=8080)