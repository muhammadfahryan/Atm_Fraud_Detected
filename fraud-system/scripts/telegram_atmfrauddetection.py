import logging
import json
from confluent_kafka import Consumer, KafkaException, KafkaError
import requests

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Kafka Consumer configuration
consumer_config = {
    'bootstrap.servers': 'node1.alldataint.com:9094,node2.alldataint.com:9094,node3.alldataint.com:9094',
    'sasl.mechanism': 'PLAIN',
    'group.id': 'group-fraud',
    'security.protocol': 'SASL_SSL',
    'auto.offset.reset': 'latest',
    'sasl.username': 'dev',
    'sasl.password': 'P@ssw0rd',
    'ssl.ca.location': 'C:/Users/Sakuragi Hanamichi/Documents/FraudDetection_ATMACEH-main/fraud-system/data/ca.crt',
}

consumer = Consumer(consumer_config)
consumer.subscribe(['ATM_FRAUD_DETECTED'])

# Telegram bot configuration
bot_token = '6821890873:AAEfXwVTsubmnbAjlNDb2_V5Gs0HuJNM5B0'
chat_id = '-4553184184'

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {'chat_id': chat_id, 'text': message, 'parse_mode': 'Markdown'}
    response = requests.post(url, data=data)
    if response.status_code != 200:
        logging.error(f"Failed to send message: {response.text}")
    else:
        logging.info(f"Alert sent: {message}")

def process_message(raw_message):
    # Log the raw message
    logging.debug(f"Raw message before processing: {raw_message}")

    # Split the raw message by the delimiter
    parts = raw_message.split(b'\x02')  # assuming b'\x02' is the delimiter
    logging.debug(f"Split message parts: {parts}")

    try:
        # Check if the length of parts is as expected
        if len(parts) < 16:
            logging.error(f"Message parts length is less than expected: {len(parts)}")
            return None

        # Decode the relevant parts
        t2_account_id = parts[7].decode('utf-8').strip()  
        t1_atm = parts[12].decode('utf-8').strip()
        t2_atm = parts[13].decode('utf-8').strip()
        t1_location = parts[14].decode('utf-8').strip()
        t2_location = parts[15].decode('utf-8').strip()
        t1_transaction_id = parts[8].decode('utf-8').strip()
        t2_transaction_id = parts[9].decode('utf-8').strip()

        # Format the message for Telegram
        telegram_message = (
            f"*Fraud Alert!*\n\n"
            f"Akun ID: {t2_account_id}\n"
            f"ATM 1: {t1_atm} ({t1_location})\n"
            f"ATM 2: {t2_atm} ({t2_location})\n"
            f"ID Transaksi 1: {t1_transaction_id}\n"
            f"ID Transaksi 2: {t2_transaction_id}\n"
        )

        return telegram_message
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        return None

# Consume messages from Kafka and send to Telegram
try:
    while True:
        msg = consumer.poll(timeout=1.0)
        if msg is None:
            continue
        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                raise KafkaException(msg.error())

        # Ensure message is not empty
        if msg.value() and len(msg.value()) > 0:
            try:
                # Log raw message bytes
                raw_message = msg.value()
                logging.debug(f"Raw message bytes: {raw_message}")

                # Process the raw message
                telegram_message = process_message(raw_message)

                if telegram_message:
                    # Send the message to Telegram
                    send_telegram_message(telegram_message)

            except Exception as e:
                logging.error(f"Error processing message: {e}")
        else:
            logging.warning("Received empty or invalid message")

finally:
    consumer.close()
