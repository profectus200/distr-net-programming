import multiprocessing
import os
import socket
import threading
import time

from PIL import Image

SERVER_URL = '127.0.0.1:1234'
FILE_NAME = 'VladimirRyabenko.gif'
CLIENT_BUFFER = 1024
FRAME_COUNT = 5000


def download_frames():
    t0 = time.time()
    if not os.path.exists('frames'):
        os.mkdir('frames')

    num_threads = 8
    frames_per_thread = FRAME_COUNT // num_threads
    threads = []
    for i in range(num_threads):
        start_index = i * frames_per_thread
        end_index = start_index + frames_per_thread if i < num_threads - 1 else FRAME_COUNT

        thread = threading.Thread(target=download_frame, args=(start_index, end_index))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return time.time() - t0


def download_frame(start_idx, end_idx):
    for i in range(start_idx, end_idx):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            ip, port = SERVER_URL.split(':')
            s.connect((ip, int(port)))
            image = b''
            while True:
                packet = s.recv(CLIENT_BUFFER)
                if not packet:
                    break
                image += packet
            with open(f'frames/{i}.png', 'wb') as f:
                f.write(image)


def create_gif():
    t0 = time.time()

    num_processes = os.cpu_count()
    with multiprocessing.Pool(processes=num_processes) as pool:
        frames = pool.map(load_frame, range(FRAME_COUNT))

    frames[0].save(FILE_NAME, format="GIF",
                   append_images=frames[1:], save_all=True, duration=500, loop=0)
    return time.time() - t0


def load_frame(frame_id):
    return Image.open(f"frames/{frame_id}.png").convert("RGBA")


if __name__ == '__main__':
    print(f"Frames download time: {download_frames()}")
    print(f"GIF creation time: {create_gif()}")
