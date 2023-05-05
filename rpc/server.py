import sqlite3
from concurrent.futures import ThreadPoolExecutor
import threading

import grpc

import schema_pb2 as stub
import schema_pb2_grpc as service

SERVER_ADDR = '0.0.0.0:1234'


class Database(service.DatabaseServicer):
    def __init__(self):
        self.conn = threading.local()
        self.cur = threading.local()

    def init(self):
        self.conn = sqlite3.connect('db.sqlite')
        self.cur = self.conn.cursor()
        self.cur.execute('CREATE TABLE IF NOT EXISTS Users (id INTEGER PRIMARY KEY, name VARCHAR(50))')

    def PutUser(self, request, context):
        self.conn = sqlite3.connect('db.sqlite')
        self.cur = self.conn.cursor()
        user_id = request.user_id
        user_name = request.user_name
        try:
            self.cur.execute('INSERT OR REPLACE INTO Users (id, name) VALUES (?, ?)', (user_id, user_name))
            self.conn.commit()

            print(f'PutUser: ({user_id}, {user_name})')
            return stub.StatusResponse(status=True)
        except:
            return stub.StatusResponse(status=False)
        finally:
            self.cur.close()
            self.conn.close()

    def DeleteUser(self, request, context):
        self.conn = sqlite3.connect('db.sqlite')
        self.cur = self.conn.cursor()
        user_id = request.user_id
        try:
            self.cur.execute('DELETE FROM Users WHERE id = ?', (user_id,))
            self.conn.commit()

            print(f'DeleteUser: ({user_id})')
            return stub.StatusResponse(status=True)
        except:
            return stub.StatusResponse(status=False)
        finally:
            self.cur.close()
            self.conn.close()

    def GetUsers(self, request, context):
        self.conn = sqlite3.connect('db.sqlite')
        self.cur = self.conn.cursor()
        try:
            self.cur.execute('SELECT * FROM Users')
            users = [stub.User(user_id=row[0], user_name=row[1]) for row in self.cur.fetchall()]

            print('GetUsers')
            return stub.UsersResponse(users=users)
        except:
            return stub.UsersResponse(users=[])
        finally:
            self.cur.close()
            self.conn.close()


if __name__ == '__main__':
    db = Database()
    db.init()

    server = grpc.server(ThreadPoolExecutor(max_workers=10))
    service.add_DatabaseServicer_to_server(db, server)
    server.add_insecure_port(SERVER_ADDR)
    server.start()

    print(f'Starting server on {SERVER_ADDR}')

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print('\nTerminating server')
        server.stop(0)

    # Close the database connection
    Database().conn.close()
