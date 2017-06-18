import socket
import threading
import util
import main

host, port = '127.0.0.1', 10000

global players
players = None

global owned_player
owned_player = None

global sock
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((host, port))

def mainloop():
    while True:
        data = sock.recv(1024)

        if not data:
            break

        data_buffer = util.DataBuffer(data)

        while len(data_buffer.remaining):
            handle_packet(data_buffer.readByte(), data_buffer)

def handle_packet(packet_id, data_buffer):
    if packet_id == util.PACKET_SPAWN:
        try:
            player_id = data_buffer.readSByte()
            owned = data_buffer.readByte()
            x = data_buffer.readShort()
            y = data_buffer.readShort()

            # clear the buffer
            data_buffer.clear()
        except:
            return

        if owned:
            # create a new player instance as an owned object
            player = main.Player(player_id, True)

            #player_group.add(player)
            #player_group.center(player.rect.center)
        else:
            player = main.Player(player_id, False)

        player.x = x
        player.y = y

        players[player_id] = player

    elif packet_id == util.PACKET_DESPAWN:
        try:
            player_id = data_buffer.readSByte()

            # clear the buffer
            data_buffer.clear()
        except:
            return

        if player_id not in players:
            return

        del players[player_id]

    elif packet_id == util.PACKET_POSITION_UPDATE:
        try:
            player_id = data_buffer.readSByte()
            x = data_buffer.readShort()
            y = data_buffer.readShort()

            # clear the buffer
            data_buffer.clear()
        except:
            return

        if player_id not in players:
            return

        player = players[player_id]
        player.x = x
        player.y = y

def handle_send_request_spawn():
    data_buffer = util.DataBuffer()
    data_buffer.writeByte(util.PACKET_REQUEST_SPAWN)

    sock.send(data_buffer.data)

def handle_send_position_update(player):
    data_buffer = util.DataBuffer()
    data_buffer.writeByte(util.PACKET_POSITION_UPDATE)
    data_buffer.writeSByte(player.id)
    data_buffer.writeShort(player.x)
    data_buffer.writeShort(player.y)

    sock.send(data_buffer.data)

def run_mainloop():
    t = threading.Thread(target=mainloop)
    t.daemon = True
    t.start()
