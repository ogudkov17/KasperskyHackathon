# implements Kafka topic consumer functionality

from email.mime import base
import threading
from confluent_kafka import Consumer, OFFSET_BEGINNING
import json
from producer import proceed_to_deliver
from urllib.request import urlopen
import base64

def handle_event(id: str, details: dict):    
    # print(f"[debug] handling event {id}, {details}")
    print(f"[info]+ handling event {id}, {details['source']}->{details['deliver_to']}: {details['operation']}")
    print(f"[info] value {details['data']}")
    print(f"[info] details {details}")
    try:
        d = {}
        if details['operation'] == 'proc_data':

            d['id'] = details['id']
            d['data'] = details['data']
            d['sign'] = details['sign']
            print(f"[info] event proc_data {id}, {details['source']}->{details['deliver_to']}: {details['operation']}")
            print(f"[alert] change data value to 1000")
            tmpdata = json.loads(details['data'])
            tmpdata['value'] = 1000
            details['data'] = json.dumps(tmpdata)

            details['verified'] = None
            #details['update_file_encoding'] = 'base64'            
            details['deliver_to'] = 'CDataComparator' #details['source']
            details['operation'] = 'compare_data'
            details['source'] = 'CDataProc'
            # remove update url details as it will not be further used
            #del details['url']
            proceed_to_deliver(id, details)


            d['data'] = details['data']
            d['deliver_to'] = 'CDataOutput'
            d['operation'] = 'put_data'
            d['source'] = 'CDataProc'
            d['verified'] = None
            proceed_to_deliver(id, d)
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
    topic = "CDataProc"
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
