import threading
import time
import queue
from flask import Flask, render_template, request

app = Flask(__name__)

class Consumer(threading.Thread):
    def __init__(self):
        super().__init__()
        self.keep_running = True
        self.consume_mode = "normal"  # default mode
        self.command_queue = queue.Queue()
        self.data_queue = queue.Queue()
        self.data_event = threading.Event()

    def run(self):
        while self.keep_running:
            if self.data_event.wait():
                self.process_queues()
                # self.command_event.clear()
                self.data_event.clear()

    def stop(self):
        self.keep_running = False

    def process_queues(self):
        while not self.command_queue.empty() or not self.data_queue.empty():
            if not self.command_queue.empty():
                cmd = self.command_queue.get()
                self.process_command(cmd)
                self.command_queue.task_done()
            if not self.data_queue.empty():
                data = self.data_queue.get()
                if self.consume_mode == "normal":
                    self.process_normal(data)
                elif self.consume_mode == "reverse":
                    self.process_reverse(data)
                # Add more modes as needed
                self.data_queue.task_done()

    def process_normal(self, item):
        # Normal processing logic
        print("Normal processing:", item)

    def process_reverse(self, item):
        # Reverse processing logic
        reversed_item = item[::-1]
        print("Reverse processing:", reversed_item)

    def set_consume_mode(self, mode):
        self.consume_mode = mode

    def process_command(self, cmd):
        # Process command
        print("Received command:", cmd)

    def add_command(self, cmd):
        # Add command to the command queue
        self.command_queue.put(cmd)
        self.data_event.set()

    def add_data(self, data):
        # Add data to the data queue
        print("adding data to queue")
        self.data_queue.put(data)
        self.data_event.set()

class ConsumerController(threading.Thread):
    def __init__(self, consumer):
        super().__init__()
        self.consumer = consumer

    def run(self):
        app.run()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/change_mode', methods=['POST'])
def change_mode():
    mode = request.form['mode']
    consumer.set_consume_mode(mode)
    return '', 204

@app.route('/send_command', methods=['POST'])
def send_command():
    cmd = request.form['cmd']
    consumer.add_command(cmd)
    return '', 204

# Example usage
if __name__ == "__main__":
    consumer = Consumer()
    consumer_controller = ConsumerController(consumer)

    # Start consumer and controller in separate threads
    consumer.start()
    consumer_controller.start()

    # Add items to the data queue
    i=0
    while True:
        time.sleep(0.3)
        i = i+1
        consumer.add_data(str(i))

    # Wait for consumer and controller threads to finish
    consumer.join()
    consumer_controller.join()
