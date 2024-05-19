import queue
import os 
import json
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from py_data_acq.common.common_types import QueueData, MCAPServerStatusQueueData, DataInputType
from hytech_eth_np_proto_py import ht_eth_pb2


class WebApp:
    def __init__(self,
                 writer_status_queue: queue.Queue[MCAPServerStatusQueueData],
                 config_status_queue: queue.Queue[QueueData],
                 # queue directly from the data_writers that contains only received config_ msgs from the socket
                 writer_command_queue: queue.Queue[QueueData],
                 # the writer command queue will contain protobuf data just like all the rest but the writer will look to see if the messages
                 output_msg_queue: queue.Queue[QueueData],
                 # queue that contains the output messages that will be sent over the UDP interface (config changes at first)
                 init_writing=True,
                 init_filename='.',
                 host='localhost',
                 port=20000):
        self.recordings = []
        self.host = host
        self.port = port
        if init_writing:
            self.writing_file = init_filename
        else:
            self.writing_file = "N/A"
        self.is_writing = init_writing
        self.config_status_queue = config_status_queue
        self.webapp_output_msg_queue = output_msg_queue  # queue containing config updates for now (these msgs get sent directly over the UDP interface)
        self.cmd_queue = writer_command_queue  # mcap writer output queue
        self.status_queue = writer_status_queue  # queue that contains the mcap writer status (is writing / filenames, etc.)
        self.attempting_start_stop = False
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
            parameters[field_desc.name] = {}
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
                setattr(config_msg, field_desc.name, int(params_dict[field_desc.name]['value']))
            else:
                setattr(config_msg, field_desc.name, params_dict[field_desc.name]['value'])
        union_msg = ht_eth_pb2.HT_ETH_Union()
        union_msg.config_.CopyFrom(config_msg)
        self.webapp_output_msg_queue.put(
            QueueData(union_msg.DESCRIPTOR.name, union_msg, data_type=DataInputType.ETHERNET_DATA))

    def _request_current_params(self):
        output = ht_eth_pb2.get_config()
        output.update_frontend = True
        union_msg = ht_eth_pb2.HT_ETH_Union()
        union_msg.get_config_.CopyFrom(output)
        # clear the receiving queue to make sure the config we receive is the latest one
        while not self.config_status_queue.empty():
            trash_config = self.config_status_queue.get()
        print("attempting to output from web app")
        self.webapp_output_msg_queue.put(
            QueueData(union_msg.DESCRIPTOR.name, union_msg, data_type=DataInputType.ETHERNET_DATA))

    def _await_and_update_params(self):
        response = self.config_status_queue.get()
        self.parameters = self._get_new_params(response.pb_msg)

    def start_stop_mcap_generation(self, input_cmd: bool, cmd_queue, status_queue):
        self.attempting_start_stop = True
        web_app_command = ht_eth_pb2.web_app_command()
        web_app_command.writing = input_cmd
        # input the command into the command queue
        cmd_queue.put(QueueData(web_app_command.DESCRIPTOR.name, web_app_command, data_type=DataInputType.WEB_APP_DATA))
        # get the response from the status queue
        message = status_queue.get()
        print("got feedback!", message.is_writing, message.writing_file)
        if message.is_writing:
            self.is_writing = True
            self.writing_file = message.writing_file
        else:
            self.is_writing = False
            self.writing_file = "N/A"
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
                if 'action' in request.form:
                    action = request.form['action']
                    if action == 'start' and not self.attempting_start_stop and not self.is_writing:
                        file_name = self.start_stop_mcap_generation(input_cmd=True, cmd_queue=self.cmd_queue,
                                                                    status_queue=self.status_queue)
                        self.recordings.append({'status': 'started', 'filename': file_name})
                    elif action == 'start' and self.is_writing:
                        self.errors.append("WARNING: cannot start writing when already writing file")
                    elif action == 'stop' and not self.is_writing:
                        self.errors.append("WARNING: cannot stop writing when no file is being written")
                    elif action == 'stop' and not self.attempting_start_stop and self.is_writing:
                        file_name = self.start_stop_mcap_generation(input_cmd=False, cmd_queue=self.cmd_queue,
                                                                    status_queue=self.status_queue)
                        self.recordings.append({'status': 'stopped', 'filename': file_name})
                    elif action == 'get_params':
                        print("getting params")
                        self._request_current_params()
                        self._await_and_update_params()
                else:
                    # Update parameters dynamically
                    for key in self.parameters:
                        if self.parameters[key]['type'] == 'number':
                            self.parameters[key]['value'] = float(request.form.get(key, 0.0))
                        elif self.parameters[key]['type'] == 'bool':
                            self.parameters[key]['value'] = request.form.get(key) == 'on'
                    self._send_new_params(self.parameters)
            return render_template('index.html', recordings=self.recordings, parameters=self.parameters,
                                   errors=self.errors, writing_file=self.writing_file)

        @app.route('/start', methods=['POST'])
        def start_recording():
            if self.attempting_start_stop:
                return jsonify("Already attempting to start or stop recording"), 503
            if self.is_writing:
                return jsonify("Cannot start recording when already recording"), 400

            file_name = self.start_stop_mcap_generation(input_cmd=True, cmd_queue=self.cmd_queue,
                                                        status_queue=self.status_queue)
            self.recordings.append({'status': 'started', 'filename': file_name})

            return "Started Recording", 200

        @app.route('/stop', methods=['POST'])
        def stop_recording():
            if self.attempting_start_stop:
                return jsonify("Already attempting to start or stop recording"), 503
            if not self.is_writing:
                return jsonify("Cannot stop recording when not currently recording"), 400

            file_name = self.start_stop_mcap_generation(input_cmd=False, cmd_queue=self.cmd_queue,
                                                        status_queue=self.status_queue)

            self.recordings.append({'status': 'stopped', 'filename': file_name})

            return jsonify("Stopped Recording"), 200

        @app.route('/params', methods=['GET'])
        def get_params():
            self._request_current_params()
            self._await_and_update_params()

            return jsonify(self.parameters), 200

        @app.route('/params', methods=['POST'])
        def update_params():
            for key in self.parameters:
                if self.parameters[key]['type'] == 'number':
                    self.parameters[key]['value'] = float(request.form.get(key, 0.0))
                elif self.parameters[key]['type'] == 'bool':
                    self.parameters[key]['value'] = request.form.get(key) == 'on'
            self._send_new_params(self.parameters)

            return jsonify("Success"), 200

        @app.route('/recordings', methods=['GET'])
        def get_recordings():
            return jsonify(self.parameters), 200

        @app.route('/errors', methods=['GET'])
        def get_errors():
            return jsonify(self.errors), 200

        @app.route('/writing_file', methods=['GET'])
        def get_writing_file():
            return jsonify(self.writing_file), 200
        
        @app.route('/fields', methods=['GET'])
        def getJSON():
            try:
                if os.path.exists("/etc/nixos"):
                    with open (os.path.join(self.metadata_filepath, "metadata.json"), "r") as f:
                        data = json.load(f)
                    return jsonify(data)
                else:
                    with open (os.getcwd() +"/frontend_config/metadata.json", "r") as f:
                        data = json.load(f)
                    return jsonify(data)
            except FileNotFoundError:
                return jsonify({'error': 'File not found'}), 400

        @app.route('/saveFields', methods=['POST'])
        def saveFields():
            newFields = json.loads(request.data, strict = False)
            try:
                if os.path.exists("/etc/nixos"):
                    with open (os.path.join(self.metadata_filepath, "metadata.json"), "w") as f:
                        f.write(newFields)
                    return jsonify(message='success')
                else:
                    with open (os.getcwd() + "/frontend_config/metadata.json", "w") as f:
                        f.write(newFields)
                    return jsonify(message='success')
            except FileNotFoundError:
                return jsonify({'error': 'File not found'}), 400

        return app

    def start_server(self):
        print("Starting webserver")
        app = self.create_app()
        app.run(host='0.0.0.0', port=8888)
