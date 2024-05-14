import logging
import asyncio
from flask import Flask, request, render_template
from flask_cors import CORS
from py_data_acq.common.common_types import QueueData, MCAPServerStatusQueueData, MCAPFileWriterCommand, SharedQueueManager
from typing import Any
from hypercorn.config import Config
from hypercorn.asyncio import serve
from hytech_eth_np_proto_py import ht_eth_pb2
from datetime import datetime

class WebApp:
    def __await__(self):
        async def closure():
            return self
        return closure().__await__()
    def __enter__(self):
        return self
    def __exit__(self, exc_, exc_type_, tb_):
        pass
    def __aenter__(self):
        return self
    async def __aexit__(self, exc_type: Any, exc_val: Any, traceback: Any):
        print("Exit from the Context Manager...")
        _ = await self.start_stop_mcap_generation(input_cmd=False)
        

    def __init__(self, writer_command_queue: asyncio.Queue, 
                 writer_status_queue: asyncio.Queue, 
                 general_command_queue: asyncio.Queue[QueueData],
                 queue_manager: SharedQueueManager,
                 feedback_event: asyncio.Event,
                 init_writing= True, 
                 init_filename = '.',
                 host='localhost', 
                 port=20000):
        self.recordings = []
        self.host = host
        self.port = port
        self.queue_manager = queue_manager
        self.is_writing = init_writing
        self.general_command_queue = general_command_queue # output message queue for messages going directly to the socket
        self.cmd_queue = writer_command_queue # mcap writer output queue
        self.status_queue = writer_status_queue # queue that contains the mcap writer status (is writing / filenames, etc.)
        self.feedback_event = feedback_event # the event that handles syncing of the parameter feedback. tells the web app when there is something in the parameter msg queue
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

    async def _get_current_params(self):
        get_config_msg = ht_eth_pb2.get_config(update_frontend=True)
        union_msg = ht_eth_pb2.HT_ETH_Union()
        union_msg.get_config_.CopyFrom(get_config_msg)
        cmd_msg = QueueData(union_msg.DESCRIPTOR.name, union_msg)
        await self.general_command_queue.put(cmd_msg)
        print("waiting")
        params_msg = await self.queue_manager.get_param_msg()
        print("got msg???")
        self.parameters = self._get_new_params(params_msg.pb_msg)
    async def _send_new_params(self, params_dict):
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
        await self.general_command_queue.put(QueueData(union_msg.DESCRIPTOR.name, union_msg))
        
    async def handle_interface_command(self, out_queue: asyncio.Queue[QueueData], proto_msg):
        msg = QueueData(proto_msg.DESCRIPTOR.name, proto_msg)
        await out_queue.put(msg)

    async def start_stop_mcap_generation(self, input_cmd: bool, cmd_queue, status_queue):
        # logging.log("Starting/Stopping MCAP generation")
        self.attempting_start_stop = True
        await cmd_queue.put(MCAPFileWriterCommand(input_cmd))
        # logging.log("MCAP command put in queue")
            # message = await status_q.get()

        message = MCAPServerStatusQueueData(input_cmd, "yeet")
        if message.is_writing:
            self.is_writing = True
        else:
            # logging.log("Not Writing message to MCAP file")
            self.is_writing = False
            # self.mcap_status_message = f"No MCAP file is being written."
        self.attempting_start_stop = False 
        return message.writing_file
    
    async def create_app(self):
        print("App Created")
        app = Flask(__name__)
        CORS(app)

        @app.route('/', methods=['GET', 'POST'])
        async def index():

            # print("form: ", request.form)
            if request.method == 'POST':
                if 'action' in request.form and not self.attempting_start_stop:
                    action = request.form['action']
                    if action == 'start':
                        file_name = await self.start_stop_mcap_generation(input_cmd=True, cmd_queue=self.cmd_queue, status_queue=self.status_queue)
                        self.recordings.append({'status': 'started', 'filename': file_name})
                    elif action == 'stop':
                        file_name = await self.start_stop_mcap_generation(input_cmd=True, cmd_queue=self.cmd_queue, status_queue=self.status_queue)
                        self.recordings.append({'status': 'stopped', 'filename': file_name})
                    elif action =='get_params':
                        print("uh tryna get em")
                        await self._get_current_params()
                        # except asyncio.TimeoutError:
                        #     print('timed out getting params')
                        #     now = datetime.now()
                        #     error_str = str(now.strftime("%H:%M:%S"))
                        #     self.errors.append(("timed out getting params at "+ error_str))
                else:
                    # Update parameters dynamically
                    for key in self.parameters:
                        if self.parameters[key]['type'] == 'number':
                            self.parameters[key]['value'] = float(request.form.get(key, 0.0))
                        elif self.parameters[key]['type'] == 'bool':
                            self.parameters[key]['value'] = request.form.get(key) == 'on'
                    await self._send_new_params(self.parameters)
            return render_template('index.html', recordings=self.recordings, parameters=self.parameters, errors=self.errors)
        return app
    
    async def start_server(self):
        print("Starting webserver")
        app = await self.create_app()
        config = Config()
        config.bind = [f"{self.host}:{self.port}"]  # Set the bind address
        await serve(app, config, shutdown_trigger=lambda: asyncio.Future())
    