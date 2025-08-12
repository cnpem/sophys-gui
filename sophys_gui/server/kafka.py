import threading
from queue import Queue
import msgpack_numpy
from kafka import KafkaConsumer


class KafkaDataRegister():
    
    def __init__(self, kafka_uri, kafka_topic):
        self.kafka_topic = kafka_topic
        self.kafka_uri = kafka_uri
        self.primary_uid = ""
        self.queue = Queue()
        consumer = KafkaConsumer(
            self.kafka_topic,
            bootstrap_servers=[self.kafka_uri])
        if consumer.bootstrap_connected():
            kafka_thread = threading.Thread(target=self.monitor, args=(consumer, ))
            kafka_thread.start()

    def monitor(self, consumer):
        for message in consumer:
            kafka_msg = msgpack_numpy.unpackb(message.value)
            if kafka_msg[0] == "start":
                self.queue.put(kafka_msg[1])
            elif kafka_msg[0] == "descriptor":
                if kafka_msg[1]["name"] == "primary":
                    self.primary_uid = kafka_msg[1]["uid"]
            elif kafka_msg[0] == "event":
                if "descriptor" in kafka_msg[1]:
                    if self.primary_uid == kafka_msg[1]["descriptor"]:
                        self.queue.put(kafka_msg[1])

    def get_data(self):
        kafka_data = []
        while not self.queue.empty():
            kafka_data.append(self.queue.get(block=False))
        return kafka_data