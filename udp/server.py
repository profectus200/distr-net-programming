import os
import socket

BUF_SIZE = 20480

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int)
    args = parser.parse_args()

    port = args.port

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(('0.0.0.0', port))
        print(f"('0.0.0.0', {port}): Listening...")

        file_name, file_size = '', -1

        try:
            while True:
                # receive data from client
                data, addr = s.recvfrom(BUF_SIZE)
                decoded_data = data.decode('utf-8').split('|')
                message_type = decoded_data[0]
                seq_num = int(decoded_data[1])

                print(f'{addr}: {data.decode("utf-8")}')

                # check data type
                if message_type == 's':
                    # prepare to receive file from client
                    file_name, file_size = decoded_data[2:]
                    file_size = int(file_size)


                    if os.path.isfile(file_name):
                        print(f'Warning: "{file_name}" will be overwritten')
                    open(file_name, 'w').close()

                    ack_message = f'a|{(seq_num + 1) % 2}'
                    s.sendto(ack_message.encode('utf-8'), addr)

                elif message_type == 'd':
                    # write delivered chunk to file system
                    chunk = decoded_data[-1].encode('utf-8')

                    with open(file_name, 'ab') as f:
                        f.write(chunk)

                    ack_message = f'a|{(seq_num + 1) % 2}'
                    s.sendto(ack_message.encode('utf-8'), addr)
                else:
                    # terminate gracefully with error
                    ack_message = f'a|{(seq_num + 1) % 2}'
                    s.sendto(ack_message.encode('utf-8'), addr)
                    print('Error: invalid data type received')

                # check if file is complete

                if os.path.getsize(file_name) == file_size:
                    print(f'Received {file_name}')
                    print(f"('0.0.0.0', {port}): Listening...")
        except KeyboardInterrupt:
            print(f"('0.0.0.0', {port}):  Shutting down...")
            exit()
