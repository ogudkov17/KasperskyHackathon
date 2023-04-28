import multiprocessing
from flask import Flask, request, jsonify
from uuid import uuid4
from producer import proceed_to_deliver
import threading
import time
import json
import base64

host_name = "0.0.0.0"
port = 6011

app = Flask(__name__)             # create an app instance

APP_VERSION = "1.0.2"

_requests_queue: multiprocessing.Queue = None

@app.route("/data", methods=['POST'])
def update():
    content = request.json
    #auth = request.headers['auth']
    #if auth != 'very-secure-token':
    #    return "unauthorized", 401

    req_id = uuid4().__str__()
    try:
        target="CDataSign"
        valuetime = {}
        valuetime['value'] = content['value']
        valuetime['time'] = time.time()
        datastr =  json.dumps(valuetime)
        update_details = {
            "id": req_id,
            "data": json.dumps(valuetime), #json.dump({"value": content['value'], "time": time.time()}),
            "deliver_to": target,
            "operation": "sign_data",
            }
        #_requests_queue.put(update_details)
        print(f"update event: {update_details}")
        proceed_to_deliver(req_id, update_details)
    except:
        error_message = f"malformed request {request.data}"
        print(error_message)
        return error_message, 400


#    try:
#        target="CDataProc"
#        url="http://CDataInput:6011/data"
#        digest = 0
#        digest_alg = 0
#        update_details = {
#            "id": req_id,
#            "value": content['value'],
#            "hash": 0,
#            "sign": 0,
#            "id": req_id,
#            "operation": "proc_data",
#            "target": target,
#            "url": url,
#            "deliver_to": "CDataProc",
#            "digest": digest,
#            "digest_alg": digest_alg
#            }
#        #_requests_queue.put(update_details)
#        print(f"update event: {update_details}")
#        proceed_to_deliver(req_id, update_details)
#    except:
#        error_message = f"malformed request {request.data}"
#        print(error_message)
#        return error_message, 400

    return jsonify({"operation": "update requested", "value": content['value']})
#    return jsonify({"operation": "update requested", "id": req_id})

def start_rest(requests_queue):
    global _requests_queue 
    _requests_queue = requests_queue
    threading.Thread(target=lambda: app.run(host=host_name, port=port, debug=True, use_reloader=False)).start()

if __name__ == "__main__":        # on running python app.py
    start_rest()