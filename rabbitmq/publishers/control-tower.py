import pika

RMQ_HOST = 'localhost'
RMQ_USER = 'rabbit'
RMQ_PASS = '1234'
EXCHANGE_NAME = 'amq.topic'
ROUTING_KEY_CURRENT = 'rep.current'
ROUTING_KEY_AVERAGE = 'rep.average'

if __name__ == '__main__':
    credentials = pika.PlainCredentials(RMQ_USER, RMQ_PASS)
    parameters = pika.ConnectionParameters(RMQ_HOST, credentials=credentials)
    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue

    try:
        while True:
            query = input('Enter Query: ')
            if query == 'current':
                channel.basic_publish(exchange=EXCHANGE_NAME, routing_key=ROUTING_KEY_CURRENT, body=b'')
            elif query == 'average':
                channel.basic_publish(exchange=EXCHANGE_NAME, routing_key=ROUTING_KEY_AVERAGE, body=b'')
            else:
                print('Unknown Query')
    except KeyboardInterrupt:
        connection.close()
        exit('Control tower finished')
