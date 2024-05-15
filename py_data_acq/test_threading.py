import asyncio
import threading
import queue

class Producer1:
    def __init__(self, output_queue):
        self.output_queue = output_queue

    async def produce(self):
        for i in range(5):
            await asyncio.sleep(0.2)  # Simulate some async work
            data = f"Data from producer 1: {i}"
            self.output_queue.put(data)

class Producer2:
    def __init__(self, output_queue):
        self.output_queue = output_queue

    async def produce(self):
        for i in range(5):
            await asyncio.sleep(1)  # Simulate some async work
            data = f"Data from producer 2: {i}"
            self.output_queue.put(data)

class ProducerManager(threading.Thread):
    def __init__(self):
        super().__init__()
        self.output_queue = queue.Queue()
        self.producer1 = Producer1(self.output_queue)
        self.producer2 = Producer2(self.output_queue)

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tasks = [
            asyncio.ensure_future(self.producer1.produce()),
            asyncio.ensure_future(self.producer2.produce())
        ]
        loop.run_until_complete(asyncio.wait(tasks))
        loop.close()

class Consumer:
    def __init__(self, output_queue):
        self.output_queue = output_queue

    def consume(self):
        while True:
            item = self.output_queue.get()
            if item is None:
                break
            print("Consumed:", item)
            self.output_queue.task_done()

def main():
    producer_manager = ProducerManager()
    consumer_queue = producer_manager.output_queue

    # Start producer manager
    producer_manager.start()

    # Start consumer in another thread
    consumer = Consumer(consumer_queue)
    consumer_thread = threading.Thread(target=consumer.consume)
    consumer_thread.start()

    producer_manager.join()
    consumer_queue.put(None)  # Signal consumer to stop
    consumer_thread.join()

if __name__ == "__main__":
    main()
