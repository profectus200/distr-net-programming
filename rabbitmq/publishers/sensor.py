import json
from datetime import datetime

import pika

RMQ_HOST = 'localhost'
RMQ_USER = 'rabbit'
RMQ_PASS = '1234'
EXCHANGE_NAME = 'amq.topic'
ROUTING_KEY = 'co2.sensor'

if __name__ == '__main__':
    credentials = pika.PlainCredentials(RMQ_USER, RMQ_PASS)
    parameters = pika.ConnectionParameters(RMQ_HOST, credentials=credentials)
    connection = pika.BlockingConnection(parameters)

    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='topic', durable=True)

    try:
        while True:
            co2_level = int(input("Enter CO2 level: "))

            message = {
                "time": str(datetime.now()),
                "value": co2_level
            }

            channel.basic_publish(exchange=EXCHANGE_NAME, routing_key=ROUTING_KEY, body=json.dumps(message))
    except KeyboardInterrupt:
        connection.close()
        exit('Sensor stopped')
