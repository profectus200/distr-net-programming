import random
import socket
import threading
from io import BytesIO

from PIL import Image

SERVER_IP = '127.0.0.1'
SERVER_PORT = 1234
MAX_CLIENTS = 10


def generate_random_image():
    img = Image.new('RGBA', (10, 10))
    pixels = img.load()
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            pixels[i, j] = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    return img


def handle_client(conn):
    img = generate_random_image()

    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes = img_bytes.getvalue()

    conn.send(img_bytes)
    conn.close()


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(MAX_CLIENTS)

    print(f'Server is listening on {SERVER_IP}:{SERVER_PORT}...')

    while True:
        try:
            conn, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(conn,))
            thread.start()
        except KeyboardInterrupt:
            print('Server shutting down...')
            server_socket.close()
            break


if __name__ == '__main__':
    start_server()
