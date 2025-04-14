import threading
import msgpack_numpy
from kafka import KafkaConsumer


class KafkaDataRegister():
    
    def __init__(self, kafka_uri, kafka_topic):
        self.kafka_topic = kafka_topic
        self.kafka_uri = kafka_uri
        self.data = []
        consumer = KafkaConsumer(
            self.kafka_topic,
            bootstrap_servers=[f'{self.kafka_uri}:60612'])
        if consumer.bootstrap_connected():
            kafka_thread = threading.Thread(target=self.monitor, args=(consumer, ))
            kafka_thread.start()

    def monitor(self, consumer):
        for message in consumer:
            kafka_msg = msgpack_numpy.unpackb(message.value)
            if kafka_msg[0] == "start":
                self.data.append(kafka_msg[1])
            if kafka_msg[0] == "event":
                self.data.append(kafka_msg[1])

    def clear_data(self):
        self.data = []

    def get_data(self):
        return self.data