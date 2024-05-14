import logging
import asyncio
from flask import Flask, request, render_template
from flask_cors import CORS
from py_data_acq.common.common_types import QueueData, MCAPServerStatusQueueData, MCAPFileWriterCommand
from typing import Any
from hypercorn.config import Config
from hypercorn.asyncio import serve
from hytech_eth_np_proto_py import ht_eth_pb2

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
        

    def __init__(self, writer_command_queue: asyncio.Queue, writer_status_queue: asyncio.Queue, general_command_queue: asyncio.Queue, init_writing= True, init_filename = '.',host='localhost', port=20000):
        self.recordings = []
        self.host = host
        self.port = port
    
        self.is_writing = init_writing
        self.general_command_queue = general_command_queue
        self.cmd_queue = writer_command_queue
        self.status_queue = writer_status_queue
        self.attempting_start_stop = False
        if(init_writing):
            self.is_writing = True
            self.mcap_status_message = f"An MCAP file is being written: {init_filename}"
        else:
            self.is_writing = False
            self.mcap_status_message = "No MCAP file is being written."
        message_proto = ht_eth_pb2.config()
        self.parameters = {}
        for field_desc in message_proto.DESCRIPTOR.fields:
            self.parameters[field_desc.name]= {}
            if field_desc.type == field_desc.TYPE_BOOL:
                
                self.parameters[field_desc.name]['type'] = 'bool'
                self.parameters[field_desc.name]['value'] = False
            else:
                self.parameters[field_desc.name]['type'] = 'number'
                self.parameters[field_desc.name]['value'] = 0
        
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
            if request.method == 'POST':
                if 'action' in request.form and not self.attempting_start_stop:
                    action = request.form['action']
                    if action == 'start':
                        file_name = await self.start_stop_mcap_generation(input_cmd=True, cmd_queue=self.cmd_queue, status_queue=self.status_queue)
                        self.recordings.append({'status': 'started', 'filename': file_name})
                    elif action == 'stop':
                        file_name = await self.start_stop_mcap_generation(input_cmd=True, cmd_queue=self.cmd_queue, status_queue=self.status_queue)
                        self.recordings.append({'status': 'stopped', 'filename': file_name})
                else:  
                    # Update parameters dynamically
                    for key in self.parameters:
                        if self.parameters[key]['type'] == 'number':
                            self.parameters[key]['value'] = float(request.form.get(key, 0.0))
                        elif self.parameters[key]['type'] == 'bool':
                            self.parameters[key]['value'] = request.form.get(key) == 'on'
            return render_template('index.html', recordings=self.recordings, parameters=self.parameters)
        return app
    
    async def start_server(self):
        print("Starting webserver")
        app = await self.create_app()
        config = Config()
        config.bind = [f"{self.host}:{self.port}"]  # Set the bind address
        await serve(app, config, shutdown_trigger=lambda: asyncio.Future())
    