# implements Kafka topic consumer functionality

from email.mime import base
import threading
from confluent_kafka import Consumer, OFFSET_BEGINNING
import json
from producer import proceed_to_deliver
from urllib.request import urlopen
import requests
import base64

CONTENT_HEADER = {"Content-Type": "application/json"}
VALUE_THRESHOLD = 17

def handle_event(id: str, details: dict):    
    # print(f"[debug] handling event {id}, {details}")
    print(f"[info] handling event {id}, {details['source']}->{details['deliver_to']}: {details['operation']}")
    try:
        if details['operation'] == 'compare_data':
            print(f"[info] value {details['data']}, {details['sign']}")
            print(f"[info] details {details}")


            #data = response.read()
            #data_b64 = base64.b64encode(data).decode('ascii')
            #details['update_file'] = data_b64
            id = details['id']
            details['verified'] = None
            details['update_file_encoding'] = 'base64'            
            details['operation'] = 'verify_sign'
            details['deliver_to'] = 'CDataVerifySign'
            details['source'] = 'CDataComparator'
            # remove update url details as it will not be further used
            #del details['url']
            print(f"[debug] prepare to send details {details}")
            proceed_to_deliver(id, details)
        elif  details['operation'] == 'verified_sign':
            if details['verdict'] == True:
                status = 1
                d = json.loads(details['data'])
                if d['value'] <= VALUE_THRESHOLD:
                    status = 0
                data = {"status": status }
                try:    
                    response = requests.post(
                        "http://protection:6068/alarm",
                        data=json.dumps(data),
                        headers=CONTENT_HEADER,
                    )
                    print(f"[info] результат отправки данных: {response}")
                except Exception as e:
                    print(f"[error] ошибка отправки данных: {e}")
            else:
                print(f"[error] Wrong signature")


    except Exception as e:
        print(f"[error] failed to handle request: {e}")

def consumer_job(args, config):
    # Create Consumer instance
    downloader_consumer = Consumer(config)

    # Set up a callback to handle the '--reset' flag.
    def reset_offset(downloader_consumer, partitions):
        if args.reset:
            for p in partitions:
                p.offset = OFFSET_BEGINNING
            downloader_consumer.assign(partitions)

    # Subscribe to topic
    topic = "CDataComparator"
    downloader_consumer.subscribe([topic], on_assign=reset_offset)

    # Poll for new messages from Kafka and print them.
    try:
        while True:
            msg = downloader_consumer.poll(1.0)
            if msg is None:
                # Initial message consumption may take up to
                # `session.timeout.ms` for the consumer group to
                # rebalance and start consuming
                # print("Waiting...")
                pass
            elif msg.error():
                print(f"[error] {msg.error()}")
            else:
                # Extract the (optional) key and value, and print.
                try:
                    id = msg.key().decode('utf-8')
                    details_str = msg.value().decode('utf-8')
                    # print("[debug] consumed event from topic {topic}: key = {key:12} value = {value:12}".format(
                        # topic=msg.topic(), key=id, value=details_str))
                    handle_event(id, json.loads(details_str))
                except Exception as e:
                    print(
                        f"Malformed event received from topic {topic}: {msg.value()}. {e}")
    except KeyboardInterrupt:
        pass
    finally:
        # Leave group and commit final offsets
        downloader_consumer.close()


def start_consumer(args, config):
   threading.Thread(target=lambda: consumer_job(args, config)).start()


if __name__ == '__main__':

    start_consumer(None)
