import logging
import queue
from flask import Flask, request, render_template
from flask_cors import CORS
from py_data_acq.common.common_types import QueueData, MCAPServerStatusQueueData, DataInputType
from typing import Any
from hypercorn.config import Config
from hypercorn.asyncio import serve
from hytech_eth_np_proto_py import ht_eth_pb2
from datetime import datetime

class WebApp:
    def __init__(self, 
                 writer_status_queue: queue.Queue[MCAPServerStatusQueueData],
                 writer_command_queue: queue.Queue[QueueData], # the writer command queue will contain protobuf data just like all the rest but the writer will look to see if the messages
                 init_writing= True, 
                 init_filename = '.',
                 host='localhost', 
                 port=20000):
        self.recordings = []
        self.host = host
        self.port = port
        self.is_writing = init_writing
        self.cmd_queue = writer_command_queue # mcap writer output queue
        self.status_queue = writer_status_queue # queue that contains the mcap writer status (is writing / filenames, etc.)
        self.attempting_start_stop = False
        # self.getting_params = False
        if(init_writing):
            self.is_writing = True
            self.mcap_status_message = f"An MCAP file is being written: {init_filename}"
        else:
            self.is_writing = False
            self.mcap_status_message = "No MCAP file is being written."
        self.errors = []
        self.parameters = self._get_new_params()
   
    def _get_new_params(self, config_msg: ht_eth_pb2.config = None):
        message_proto = ht_eth_pb2.config()
        use_defaults = True
        if config_msg is not None:
            message_proto = config_msg 
            use_defaults = False
        parameters = {}
        for field_desc in message_proto.DESCRIPTOR.fields:
            parameters[field_desc.name]= {}
            if config_msg is not None:
                value = getattr(message_proto, field_desc.name)
            if field_desc.type == field_desc.TYPE_BOOL:
                parameters[field_desc.name]['type'] = 'bool'
                parameters[field_desc.name]['value'] = False if use_defaults else value
            else:
                parameters[field_desc.name]['type'] = 'number'
                parameters[field_desc.name]['value'] = 0 if use_defaults else value
        return parameters

    def _send_new_params(self, params_dict):
        config_msg = ht_eth_pb2.config()
        for field_desc in config_msg.DESCRIPTOR.fields:
            if field_desc.type == field_desc.TYPE_FLOAT:
                setattr(config_msg, field_desc.name, float(params_dict[field_desc.name]['value']))
            elif field_desc.type == field_desc.TYPE_INT32:
                setattr(config_msg, field_desc.name,int(params_dict[field_desc.name]['value']))
            else: 
                setattr(config_msg, field_desc.name,params_dict[field_desc.name]['value'])
        union_msg = ht_eth_pb2.HT_ETH_Union()
        union_msg.config_.CopyFrom(config_msg)
        self.general_command_queue.put(QueueData(union_msg.DESCRIPTOR.name, union_msg))
        
    def handle_interface_command(self, out_queue: queue.Queue[QueueData], proto_msg):
        msg = QueueData(proto_msg.DESCRIPTOR.name, proto_msg)
        out_queue.put(msg)

    def start_stop_mcap_generation(self, input_cmd: bool, cmd_queue, status_queue):
        self.attempting_start_stop = True
        web_app_command = ht_eth_pb2.web_app_command()
        # input the command into the command queue
        cmd_queue.put(QueueData(web_app_command.DESCRIPTOR.name, web_app_command, data_type=DataInputType.WEB_APP_DATA))
        # get the response from the status queue
        message = status_queue.get()
        print("got feedback!", message)
        if message.is_writing:
            self.is_writing = True
        else:
            self.is_writing = False
        self.attempting_start_stop = False 
        return message.writing_file
    
    def create_app(self):
        print("App Created")
        app = Flask(__name__)
        CORS(app)

        @app.route('/', methods=['GET', 'POST'])
        def index():
            # print("form: ", request.form)
            if request.method == 'POST':
                if 'action' in request.form and not self.attempting_start_stop:
                    action = request.form['action']
                    if action == 'start':
                        file_name = self.start_stop_mcap_generation(input_cmd=True, cmd_queue=self.cmd_queue, status_queue=self.status_queue)
                        self.recordings.append({'status': 'started', 'filename': file_name})
                    elif action == 'stop':
                        file_name = self.start_stop_mcap_generation(input_cmd=True, cmd_queue=self.cmd_queue, status_queue=self.status_queue)
                        self.recordings.append({'status': 'stopped', 'filename': file_name})
                    elif action =='get_params':
                        if self.queue_manager.param_queue_has_data():
                            param_msg = self.queue_manager.get_param_msg()
                            self._get_new_params(param_msg.pb_msg)
                            print("yoooo updating website boi")
                else:
                    # Update parameters dynamically
                    for key in self.parameters:
                        if self.parameters[key]['type'] == 'number':
                            self.parameters[key]['value'] = float(request.form.get(key, 0.0))
                        elif self.parameters[key]['type'] == 'bool':
                            self.parameters[key]['value'] = request.form.get(key) == 'on'
                    self._send_new_params(self.parameters)
            return render_template('index.html', recordings=self.recordings, parameters=self.parameters, errors=self.errors)
        return app
    
    def start_server(self):
        print("Starting webserver")
        app = self.create_app()
        app.run(host='0.0.0.0', port=8888)