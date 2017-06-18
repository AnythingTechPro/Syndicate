import socket
import threading

try:
    import socketserver
except ImportError:
    import SocketServer as socketserver

import util
import random

class Player(object):

    def __init__(self, id, owner, x, y):
        self.id = id
        self.owner = owner
        self.x = x
        self.y = y

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    player_id = None

    def handle_send(self, data):
        try:
            self.request.sendall(data)
        except socket.error:
            return

    def setup(self):
        self.server.add_handler(self)

        # send the initial creation for avatars that already exist
        for player in self.server.players.values():
            self.handle_send_player_spawn(player.id, player.x, player.y, False)

    def handle(self):
        while True:
            try:
                data = self.request.recv(1024)
            except socket.error:
                break

            if not data:
                break

            data_buffer = util.DataBuffer(data)

            while len(data_buffer.remaining):
                self.handle_packet(data_buffer.readByte(), data_buffer)

    def handle_packet(self, packet_id, data_buffer):
        if packet_id == util.PACKET_REQUEST_SPAWN:
            self.player_id = self.server.new_player_id

            # clear the buffer
            data_buffer.clear()

            # get a random spawn position
            x, y = random.choice(util.spawn_positions)

            player = Player(self.player_id, True, x, y)

            # add the player to the server's list of players
            self.server.players[self.player_id] = player

            # send player spawn as owner to the owner's client
            self.handle_send_player_spawn(player.id, player.x, player.y, False, True)

            # now broadcast to everyone else as a regular player
            self.handle_send_player_spawn(player.id, player.x, player.y, True, False)

        elif packet_id == util.PACKET_POSITION_UPDATE:
            try:
                player_id = data_buffer.readSByte()
                x = data_buffer.readShort()
                y = data_buffer.readShort()

                # clear the buffer
                data_buffer.clear()
            except:
                return self.request.close()

            if player_id not in self.server.players:
                return

            player = self.server.players[player_id]
            player.x = x
            player.y = y

            self.handle_send_player_position_update(player_id, x, y)

    def handle_send_player_spawn(self, player_id, x, y, broadcast=False, owner=False):
        data_buffer = util.DataBuffer()
        data_buffer.writeByte(util.PACKET_SPAWN)
        data_buffer.writeSByte(player_id)
        data_buffer.writeByte(owner)
        data_buffer.writeShort(x)
        data_buffer.writeShort(y)

        if broadcast:
            self.server.broadcast_data(self, data_buffer.data)
        else:
            self.handle_send(data_buffer.data)

    def handle_send_player_despawn(self, player_id):
        data_buffer = util.DataBuffer()
        data_buffer.writeByte(util.PACKET_DESPAWN)
        data_buffer.writeSByte(player_id)

        # send to everyone except us.
        self.server.broadcast_data(self, data_buffer.data)

        # remove the player from the server's list of players
        del self.server.players[player_id]

    def handle_send_player_position_update(self, player_id, x, y):
        data_buffer = util.DataBuffer()
        data_buffer.writeByte(util.PACKET_POSITION_UPDATE)
        data_buffer.writeSByte(player_id)
        data_buffer.writeShort(x)
        data_buffer.writeShort(y)

        self.server.broadcast_data(self, data_buffer.data)

    def finish(self):
        self.server.remove_handler(self)

        if not self.player_id:
            return

        self.handle_send_player_despawn(self.player_id)

class ThreadingMixIn:
    daemon_threads = True

    def process_request_thread(self, request, client_address):
        try:
            self.finish_request(request, client_address)
            self.shutdown_request(request)
        except:
            self.handle_error(request, client_address)
            self.shutdown_request(request)

    def process_request(self, request, client_address):
        t = threading.Thread(target=self.process_request_thread, args=(
            request, client_address,))

        t.setDaemon(self.daemon_threads)
        t.start()

class ThreadedTCPServer(ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True # allows address reuse
    request_queue_size = 100 # maximum allowed tcp connections at once

    handlers = []
    players = {}

    def add_handler(self, handler):
        if handler in self.handlers:
            return

        self.handlers.append(handler)

    def remove_handler(self, handler):
        if handler not in self.handlers:
            return

        self.handlers.remove(handler)

    def broadcast_data(self, sender_handler, data):
        for handler in self.handlers:
            if handler == sender_handler:
                continue

            handler.handle_send(data)

    @property
    def new_player_id(self):
        return len(self.players) + 1

if __name__ == '__main__':
    HOST, PORT = '0.0.0.0', 10000

    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    server.serve_forever(poll_interval=0.01)
