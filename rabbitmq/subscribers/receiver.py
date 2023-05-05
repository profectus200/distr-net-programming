import json

import pika

RMQ_HOST = 'localhost'
RMQ_USER = 'rabbit'
RMQ_PASS = '1234'
EXCHANGE_NAME = 'amq.topic'
ROUTING_KEY = 'co2.*'


def callback(channel, method, properties, body):
    data = json.loads(body)
    with open('receiver.log', 'a') as f:
        f.write(f"{data['time']}: {data['value']}\n")

    if data['value'] > 500:
        print('WARNING')
    else:
        print('OK')
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
        print('[*] Waiting for CO2 data. Press CTRL+C to exit')
        channel.basic_consume(queue=queue_name, on_message_callback=callback)
        channel.start_consuming()
    except KeyboardInterrupt:
        connection.close()
        exit('Receiver finished')

