import json
import socket
from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer
import time
import os

# GET ENVIRONMENT VARIABLES
try:
    KAFKA_BROKERS = os.environ['KAFKA_BROKERS']
    SCHEMA_REGISTRY = os.environ['SCHEMA_REGISTRY']
    CLIENT_ID = os.environ['CLIENT_ID']
except KeyError as e:
    KAFKA_BROKERS = "node1.alldataint.com:9094,node2.alldataint.com:9094,node3.alldataint.com:9094"
    SCHEMA_REGISTRY = "https://node1.alldataint.com:8081"
    CLIENT_ID = "atm-transactions-producer"

conf = {
    'bootstrap.servers': 'node1.alldataint.com:9094,node2.alldataint.com:9094,node3.alldataint.com:9094',
    'client.id': CLIENT_ID,
    'sasl.mechanism': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': 'dev',
    'sasl.password': 'P@ssw0rd',
    'ssl.ca.location': 'C:/Users/Sakuragi Hanamichi/Documents/FraudDetection_ATMACEH-main/fraud-system/data/ca.crt',
    'schema.registry.url': 'https://node1.alldataint.com:8081',
    'schema.registry.basic.auth.credentials.source': 'USER_INFO',
    'schema.registry.basic.auth.user.info' : 'dev:P@ssw0rd',
    'schema.registry.ssl.ca.location' : 'C:/Users/Sakuragi Hanamichi/Documents/FraudDetection_ATMACEH-main/fraud-system/data/ca.crt',
}

value_schema_str = """
{
	"namespace": "ATM_TRANSACTION",
	"type": "record",
	"name": "value",
	"fields": [
		{"name": "account_id", "type": "string"},
		{"name": "atm",  "type": "string"},
		{"name": "amount", "type": "int"},
		{"name": "transaction_id",  "type": "string"},
		{"name": "location",  "type": {"type": "map", "values": "double"}},
		{"name": "timestamp",  "type": "string"},
		{"name": "address",  "type": "string"}
	]
}
"""

key_schema_str = """
{
   "namespace": "ATM_TRANSACTION",
   "name": "key",
   "type": "record",
   "fields" : [
     {
       "name" : "transaction_id",
       "type" : "string"
     }
   ]
}
"""

value_schema = avro.loads(value_schema_str)
key_schema = avro.loads(key_schema_str)

avroProducer = AvroProducer(conf, default_key_schema=key_schema, default_value_schema=value_schema)

# Create a UDP socket
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(('0.0.0.0', 6900))

while True:
    data, addr = udp_socket.recvfrom(1024)
    jsonString = data.decode('utf-8')
    print(jsonString)

    if jsonString != '':
        value = json.loads(jsonString)
        key = {"transaction_id": value['transaction_id']}

        try:
            avroProducer.produce(topic='ATM_TRANSACTION', value=value, key=key)
            print(f"Produced record to topic {value}")
        except Exception as e:
            print(f"Exception while producing record value - {value} to topic - 'ATM_TRANSACTION': {e}")
        else:
            print(f"key - {key}")

        avroProducer.flush()