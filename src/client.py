import socket
import threading
import pyaudio
import time
import tkinter
import queue
from src.emotions import EmotionDetection


class GuiPart:
    def __init__(self, master, message_queue):
        self.queue = message_queue
        # Set up the GUI
        self.emotion_label = tkinter.Label(master, text="NEUTRAL", foreground="white", font=("Courier", 44),
                                           background="black", width=300, height=100)
        self.emotion_label.pack()
        # Add more GUI stuff here depending on your specific needs

    def process_incoming(self):
        """Handle all messages currently in the queue, if any."""
        while self.queue.qsize():
            try:
                msg = self.queue.get(0)
                self.emotion_label.config(text=msg)
                self.emotion_label.update()
            except Exception as e:
                print(e)


class Client:
    def __init__(self, master, host, model):
        self.master = master
        self.queue = queue.Queue()
        self.gui = GuiPart(master, self.queue)
        print(model)
        self.emotion_detection = EmotionDetection(model=model)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s_text = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        while 1:
            try:
                self.target_ip = host
                self.target_port = 9999
                self.target_text_port = 9998

                self.s.connect((self.target_ip, self.target_port))
                self.s_text.connect((self.target_ip, self.target_text_port))

                break
            except:
                print("Couldn't connect to server")

        chunk_size = 1024  # 512
        audio_format = pyaudio.paInt16
        channels = 1
        rate = 20000

        # initialise microphone recording
        self.p = pyaudio.PyAudio()
        self.playing_stream = self.p.open(format=audio_format, channels=channels, rate=rate, output=True,
                                          frames_per_buffer=chunk_size)
        self.recording_stream = self.p.open(format=audio_format, channels=channels, rate=rate, input=True,
                                            frames_per_buffer=chunk_size)

        print("Connected to Server")

        # start threads
        self.emotion_thread = threading.Thread(target=self.emotion_detection.start_detection).start()
        self.receive_thread = threading.Thread(target=self.receive_server_data)
        self.receive_thread.start()
        self.receive_text_thread = threading.Thread(target=self.receive_server_text_data).start()
        self.send_thread = threading.Thread(target=self.send_data_to_server).start()
        self.send_text_thread = threading.Thread(target=self.send_text_data_to_server).start()

    def receive_server_data(self):
        while True:
            try:
                data = self.s.recv(1024)
                self.playing_stream.write(data)
            except Exception as e:
                print(e)

    def receive_server_text_data(self):
        while True:
            try:
                data = self.s_text.recv(1024)
                self.queue.put(data)
                self.gui.process_incoming()
            except Exception as e:
                print(e)

    def send_data_to_server(self):
        while True:
            try:
                data = self.recording_stream.read(1024)
                self.s.sendall(data)
            except Exception as e:
                print(e)

    def send_text_data_to_server(self):
        while True:
            try:
                z = self.emotion_detection.current_emotion
                z = bytes(z, 'utf-8')
                self.s_text.send(z)
                time.sleep(2)
            except Exception as e:
                print(e)


if __name__ == "__main__":
    root = tkinter.Tk()
    client = Client(root, "lucasjeske.de", "model_self_trained.h5")
    root.mainloop()
