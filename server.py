import socket
import threading


class Server:
    def __init__(self):
        self.ip = "0.0.0.0"
        while True:
            try:
                self.port_audio = 9999
                self.port_text = 9998

                self.s_audio = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s_audio.bind((self.ip, self.port_audio))

                self.s_text = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s_text.bind((self.ip, self.port_text))
                break
            except Exception as e:
                print(e)
                print(f"Couldn't bind to {self.ip}:{self.port_audio}")
                print(f"Couldn't bind to {self.ip}:{self.port_text}")

        self.connections = []
        self.connections_text = []
        self.accept_connections()

    def accept_connections(self):
        self.s_audio.listen(2)
        self.s_text.listen(2)

        print(f"Running on IP: {self.ip}")
        print(f"Audio running on port: {self.port_audio}")
        print(f"Text running on port: {self.port_text}")

        while True:
            c, addr = self.s_audio.accept()
            c_text, addr_text = self.s_text.accept()

            self.connections.append(c)
            self.connections_text.append(c_text)

            threading.Thread(target=self.handle_client, args=(c, addr,)).start()
            threading.Thread(target=self.handle_text_client, args=(c_text, addr_text)).start()

    def broadcast(self, sock, data):
        for client in self.connections:
            if client != self.s_audio and client != sock:
                try:
                    client.send(data)
                except Exception as e:
                    self.connections.remove(client)
                    print(e)

    def broadcast_text(self, sock, data):
        for client in self.connections_text:
            if client != self.s_text and client != sock:
                try:
                    client.send(data)
                except Exception as e:
                    self.connections_text.remove(client)
                    print(e)

    def handle_text_client(self, c, addr):
        while 1:
            try:
                data = c.recv(1024)
                print(data)
                self.broadcast_text(c, data)
            except socket.error:
                c.close()

    def handle_client(self, c, addr):
        while 1:
            try:
                data = c.recv(1024)
                self.broadcast(c, data)
            except socket.error:
                c.close()


if __name__ == "__main__":
    server = Server()



