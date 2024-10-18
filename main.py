import socket

def client_hash(key_id, c_hash, name):
    key_dict = {
        0: 32037,
        1: 29295,
        2: 13603,
        3: 29533,
        4: 21952,
    }
    print("c_hash")
    print(c_hash)
    key = key_dict.get(int(key_id))

    ascii_sum = sum(ord(char) for char in name)

    r_hash = (ascii_sum * 1000) % 65536

    r = (r_hash + key) % 65536


    if not c_hash.isdigit():
        return False
    if r == int(c_hash):
        return True

    return False


def server_hash(key_id, name):
    key_dict = {
        0: 23019,
        1: 32037,
        2: 18789,
        3: 16443,
        4: 18189
    }
    key = key_dict.get(int(key_id))
    ascii_sum = sum(ord(char) for char in name)
    r_hash = (ascii_sum * 1000) % 65536

    r = (r_hash + key) % 65536

    return r


def get_coordinates(position):
    xy = str(position)[3:]
    split = xy.split()
    r = [int(split[0]), int(split[1])]
    return r

def get_kvadrant(xy):
    x = int(xy[0])
    y = int(xy[1])
    if (x >= 0) and (y >= 0):
        return 1
    if (x < 0) and (y > 0):
        return 2
    if (x > 0) and (y < 0):
        return 4
    if (x <= 0) and (y <= 0):
        return 3
#   if (x == 0) and (y > 0):
#       return 12
#   if (x == 0) and (y < 0):
#       return 34
#   if (x > 0) and (y == 0):
#       return 14
#   if (x < 0) and (y == 0):
#       return 23
#   if (x == 0) and (y == 0):
#       return 0

def get_direction(current, last):

    print(f"get dir{current} {last}")
    if current[0] > last[0]:
        return "right"
    if current[0] < last[0]:
        return "left"
    if current[1] > last[1]:
        return "up"
    if current[1] < last[1]:
        return "down"




sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(('', 6000))
sock.listen(25)

try:
    while 1:
        new_socket, address = sock.accept()
        print("Connected from", address)

        while 1:
            old_buffer = []
            class TimeoutException(Exception):
                pass

            def receive_data(length: int) -> str:
                if len(old_buffer) > 0:
                    return old_buffer.pop(0)
                received_buffer = ""
                new_socket.settimeout(1)
                try:
                    while not received_buffer.endswith("\a\b"):
                        received = new_socket.recv(128)
                        if not received:
                            continue
                        received_buffer += str(received.decode())
                except socket.timeout:
                    raise TimeoutException

                split_buffer = received_buffer.split("\a\b")
                to_push = split_buffer[1:-1]
                for i in to_push:
                    old_buffer.append(i)
                return split_buffer[0]


            def overeni():
                client_name = receive_data(128)

                send_data("107 KEY REQUEST")

                client_key_id = receive_data(128)

                if not client_key_id.isdigit():
                    send_data("301 SYNTAX ERROR")
                    raise ValueError
                if int(client_key_id) < 0 or int(client_key_id) > 4:
                    send_data("303 KEY OUT OF RANGE")
                    raise ValueError

                to_send = server_hash(client_key_id, client_name)

                send_data(str(to_send))

                c_hash = receive_data(128)

                if not client_hash(client_key_id, c_hash, client_name):
                    send_data("300 LOGIN FAILED")
                    raise ValueError
                send_data("200 OK")
            # prijem dat, vraci string

            def send_data(data: str) -> None:
                data += "\a\b"
                new_socket.send(bytes(data.encode()))


            def change_direction(kvadrant, dir):
                if kvadrant == 1:
                    if dir == "down":
                        send_data("104 TURN RIGHT")
                        dir = "left"
                        receive_data(128)
                        return dir
                    if dir == "left":
                        send_data("103 TURN LEFT")
                        dir = "down"
                        receive_data(128)
                        return dir
                    if dir == "right":
                        send_data("104 TURN RIGHT")
                        dir = "down"
                        receive_data(128)
                        return dir
                    if dir == "up":
                        send_data("103 TURN LEFT")
                        dir = "left"
                        receive_data(128)
                        return dir
                if kvadrant == 2:
                    if dir == "down":
                        send_data("103 TURN LEFT")
                        dir = "right"
                        receive_data(128)
                        return dir
                    if dir == "right":
                        send_data("104 TURN RIGHT")
                        dir = "down"
                        receive_data(128)
                        return dir
                    if dir == "up":
                        send_data("104 TURN RIGHT")
                        dir = "right"
                        receive_data(128)
                        return dir
                    if dir == "left":
                        send_data("103 TURN LEFT")
                        dir = "down"
                        receive_data(128)
                        return dir
                if kvadrant == 3:
                    if dir == "up":
                        send_data("104 TURN RIGHT")
                        dir = "right"
                        receive_data(128)
                        return dir
                    if dir == "right":
                        send_data("103 TURN LEFT")
                        dir = "up"
                        receive_data(128)
                        return dir
                    if dir == "down":
                        send_data("103 TURN LEFT")
                        dir = "right"
                        receive_data(128)
                        return dir
                    if dir == "left":
                        send_data("104 TURN RIGHT")
                        dir = "up"
                        receive_data(128)
                        return dir
                if kvadrant == 4:
                    if dir == "up":
                        send_data("103 TURN LEFT")
                        dir = "left"
                        receive_data(128)
                        return dir
                    if dir == "left":
                        send_data("104 TURN RIGHT")
                        dir = "up"
                        receive_data(128)
                        return dir
                    if dir == "right":
                        send_data("103 TURN LEFT")
                        dir = "up"
                        receive_data(128)
                        return dir
                    if dir == "down":
                        send_data("104 TURN RIGHT")
                        dir = "left"
                        receive_data(128)
                        return dir


            def dopredu(xy, last_pos):
                send_data("102 MOVE")
                position = receive_data(128)
                last_pos = xy
                xy = get_coordinates(position)
                return xy, last_pos

            def prvni_prekazka(xy, last_pos, kvadrant):
                send_data("104 TURN RIGHT")
                receive_data(128)
                xy, last_pos = dopredu(xy, last_pos)
                direction = get_direction(xy, last_pos)
                direction = change_direction(kvadrant, direction)
                return xy, last_pos, direction
            def na_ose(obstacle, xy, last_pos, kvadrant, direction):
                kvadrant = get_kvadrant(xy)
                direction = change_direction(kvadrant, direction)
                while not (xy[0] == 0 and xy[1] == 0):
                    print(f"current: {xy} last: {last_pos} direction: {direction} kvadrant: {kvadrant}")
                    if obstacle:
                        direction = change_direction(kvadrant, direction)
                        xy, last_pos = dopredu(xy, last_pos)                    #dolu
                        kvadrant = get_kvadrant(xy)
                        print(f"current: {xy} last: {last_pos} direction: {direction} kvadrant: {kvadrant}")
                        direction = change_direction(kvadrant, direction)
                        xy, last_pos = dopredu(xy, last_pos)                    #doleva
                        kvadrant = get_kvadrant(xy)
                        print(f"current: {xy} last: {last_pos} direction: {direction} kvadrant: {kvadrant}")

                        xy, last_pos = dopredu(xy, last_pos)                    #doleva
                        kvadrant = get_kvadrant(xy)
                        print(f"current: {xy} last: {last_pos} direction: {direction} kvadrant: {kvadrant}")
                        direction = change_direction(kvadrant, direction)
                        xy, last_pos = dopredu(xy, last_pos)                    #dup
                        kvadrant = get_kvadrant(xy)
                        print(f"current: {xy} last: {last_pos} direction: {direction} kvadrant: {kvadrant}")
                        direction = change_direction(kvadrant, direction)
                        kvadrant = get_kvadrant(xy)
                        obstacle = False
                        continue
                    xy, last_pos = dopredu(xy, last_pos)
                    if last_pos == xy:
                        obstacle = True


            def pohyb():

                send_data("102 MOVE")
                position = receive_data(128)
                xy = get_coordinates(position)
                last_pos = xy
                if xy == [0, 0]:
                    return
                xy, last_pos = dopredu(xy, last_pos)
                if (xy == [0, 0]):
                    return

                kvadrant = get_kvadrant(xy)
                if last_pos == xy:
                    xy, last_pos, direction = prvni_prekazka(xy, last_pos, kvadrant)
                    obstacle = False

                else:
                    obstacle = False
                    direction = get_direction(xy, last_pos)

                kvadrant = get_kvadrant(xy)

                while not (xy[0] == 0 and xy[1] == 0):
                    kvadrant = get_kvadrant(xy)

                    if (xy[0] == 0 or xy[1] == 0):
                        na_ose(obstacle, xy, last_pos, kvadrant, direction)
                        return
                    if obstacle == True:
                        direction = change_direction(kvadrant, direction)
                        obstacle = False
                    xy, last_pos = dopredu(xy, last_pos)
                    if last_pos == xy:
                        obstacle = True

            def package():
                send_data("105 GET MESSAGE")
                messege = receive_data(128)
                print(messege)
                send_data("106 LOGOUT")

            try:
                overeni()
                pohyb()
                package()
            except:
                break

        new_socket.close()
        print("Disconnected from", address)
finally:
    sock.close()
