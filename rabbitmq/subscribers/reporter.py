from statistics import mean

import pika

RMQ_HOST = 'localhost'
RMQ_USER = 'rabbit'
RMQ_PASS = '1234'
EXCHANGE_NAME = 'amq.topic'
ROUTING_KEY = 'rep.*'


def callback(channel, method, properties, body):
    query = method.routing_key.split('.')[1]
    with open('receiver.log', 'r') as f:
        data = f.readlines()
        time = data[-1].split(': ')[0]
        values = [int(line.split(': ')[1]) for line in data]

    if query == 'current':
        print(f"{time}: Latest CO2 level is {values[-1]}")
    elif query == 'average':
        print(f"{time}: Average CO2 level is {mean(values)}")
    channel.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    credentials = pika.PlainCredentials(RMQ_USER, RMQ_PASS)
    parameters = pika.ConnectionParameters(RMQ_HOST, credentials=credentials)
    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()

    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=EXCHANGE_NAME, queue=queue_name, routing_key=ROUTING_KEY)

    try:
        print('[*] Waiting for queries from the control tower. Press CTRL+C to exit')
        channel.basic_consume(queue=queue_name, on_message_callback=callback)
        channel.start_consuming()
    except KeyboardInterrupt:
        connection.close()
        exit('Reporter finished')
