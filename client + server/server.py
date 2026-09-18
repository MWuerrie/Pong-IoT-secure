# import socket
# import json
# import threading
# import time

# from game.game import Game


# HOST = "0.0.0.0"
# PORT = 5000

# game = Game()

# game_state = "WAITING"

# # Spieler, der den nächsten Aufschlag bekommt
# serving_player = None

# # True = Ball ist im Spiel
# # False = Ball hängt an einem Paddle
# ball_started = False

# clients = {}

# player_inputs = {
#     1: "none",
#     2: "none"
# }

# lock = threading.Lock()


# # --------------------------------------------------
# # SEND MESSAGE
# # --------------------------------------------------

# def send_message(client, message):

#     data = json.dumps(message) + "\n"

#     try:
#         client.sendall(data.encode())
#     except ConnectionError:
#         pass


# # --------------------------------------------------
# # BROADCAST
# # --------------------------------------------------

# def broadcast(message):

#     data = json.dumps(message) + "\n"
#     encoded_message = data.encode()

#     with lock:
#         current_clients = list(clients.items())

#     for player_number, client in current_clients:

#         try:
#             client.sendall(encoded_message)

#         except ConnectionError:

#             print(
#                 f"Player {player_number} disconnected"
#             )

#             with lock:

#                 if player_number in clients:
#                     del clients[player_number]

#                 player_inputs[player_number] = "none"


# # --------------------------------------------------
# # SEND GAME STATE
# # --------------------------------------------------

# def send_state():

#     with lock:

#         state = {
#             "type": "state",

#             "game_state": game_state,

#             "player1_y":
#                 game.player1.paddle.y,

#             "player2_y":
#                 game.player2.paddle.y,

#             "ball_x":
#                 game.ball.x,

#             "ball_y":
#                 game.ball.y,

#             "score1":
#                 game.player1.score,

#             "score2":
#                 game.player2.score,

#             "last_point":
#                 game.last_point,

#             "serving_player":
#                 serving_player,

#             "ball_started":
#                 ball_started
#         }

#         current_clients = list(
#             clients.items()
#         )

#     message = json.dumps(state) + "\n"
#     encoded_message = message.encode()

#     for player_number, client in current_clients:

#         try:

#             client.sendall(encoded_message)

#         except ConnectionError:

#             print(
#                 f"Player {player_number} disconnected"
#             )

#             with lock:

#                 if player_number in clients:
#                     del clients[player_number]

#                 player_inputs[player_number] = "none"


# # --------------------------------------------------
# # CLIENT HANDLER
# # --------------------------------------------------

# def handle_client(client, player_number):

#     global game_state
#     global serving_player
#     global ball_started

#     print(
#         f"Player {player_number} connected"
#     )

#     # Tell client which player it is
#     send_message(
#         client,
#         {
#             "type": "player_assigned",
#             "player": player_number
#         }
#     )

#     buffer = ""

#     try:

#         while True:

#             data = client.recv(1024)

#             if not data:
#                 break

#             buffer += data.decode(
#                 errors="replace"
#             )

#             # One TCP packet can contain multiple messages.
#             # Therefore we split at newline.
#             while "\n" in buffer:

#                 line, buffer = buffer.split(
#                     "\n",
#                     1
#                 )

#                 if not line:
#                     continue

#                 # Security: prevent oversized messages
#                 if len(line) > 4096:

#                     print(
#                         f"Player {player_number}: "
#                         f"message too large"
#                     )

#                     continue

#                 try:

#                     message = json.loads(line)

#                 except json.JSONDecodeError:

#                     print(
#                         f"Player {player_number}: "
#                         f"invalid JSON"
#                     )

#                     continue

#                 message_type = message.get(
#                     "type"
#                 )

#                 # --------------------------------
#                 # INPUT
#                 # --------------------------------

#                 if message_type == "input":

#                     direction = message.get(
#                         "direction"
#                     )

#                     # Movement
#                     if direction in (
#                         "up",
#                         "down",
#                         "none"
#                     ):

#                         with lock:

#                             player_inputs[
#                                 player_number
#                             ] = direction

#                     # --------------------------------
#                     # START BALL
#                     # --------------------------------

#                     elif direction == "start":

#                         with lock:

#                             # Only the player whose turn it is
#                             # may start the ball.
#                             if (
#                                 game_state == "PLAYING"
#                                 and
#                                 serving_player
#                                 == player_number
#                                 and
#                                 not ball_started
#                             ):

#                                 game.ball.launch()

#                                 ball_started = True

#                                 print(
#                                     f"Player "
#                                     f"{player_number} "
#                                     f"started the ball"
#                                 )

#     except ConnectionError:

#         pass

#     finally:

#         with lock:

#             if player_number in clients:

#                 del clients[player_number]

#             player_inputs[player_number] = "none"

#             # If somebody leaves, stop the game.
#             game_state = "WAITING"

#             serving_player = None

#             ball_started = False

#         client.close()

#         print(
#             f"Player {player_number} disconnected"
#         )


# # --------------------------------------------------
# # SERVER SOCKET
# # --------------------------------------------------

# server = socket.socket(
#     socket.AF_INET,
#     socket.SOCK_STREAM
# )

# server.setsockopt(
#     socket.SOL_SOCKET,
#     socket.SO_REUSEADDR,
#     1
# )

# server.bind(
#     (HOST, PORT)
# )

# server.listen(2)

# print(
#     f"Server listening on "
#     f"{HOST}:{PORT}"
# )


# # --------------------------------------------------
# # MAIN GAME LOOP
# # --------------------------------------------------

# last_time = time.perf_counter()


# while True:

#     # ------------------------------------------------
#     # ACCEPT CONNECTIONS
#     # ------------------------------------------------

#     server.settimeout(0.001)

#     try:

#         client, address = server.accept()

#     except socket.timeout:

#         client = None


#     if client is not None:

#         with lock:

#             if 1 not in clients:

#                 player_number = 1

#             elif 2 not in clients:

#                 player_number = 2

#             else:

#                 player_number = None


#             if player_number is not None:

#                 clients[player_number] = client


#         # Game already full
#         if player_number is None:

#             send_message(
#                 client,
#                 {
#                     "type": "error",
#                     "message": "Game is full"
#                 }
#             )

#             client.close()

#         else:

#             print(
#                 f"Player {player_number} "
#                 f"connected from {address}"
#             )

#             thread = threading.Thread(
#                 target=handle_client,
#                 args=(client, player_number),
#                 daemon=True
#             )

#             thread.start()


#     # ------------------------------------------------
#     # CHECK PLAYER COUNT
#     # ------------------------------------------------

#     with lock:

#         player_count = len(clients)


#     # ------------------------------------------------
#     # START GAME WHEN TWO PLAYERS CONNECT
#     # ------------------------------------------------

#     if (
#         player_count == 2
#         and
#         game_state == "WAITING"
#     ):

#         print(
#             "Both players connected."
#         )

#         print(
#             "Player 1 gets the first serve."
#         )

#         game_state = "PLAYING"

#         serving_player = 1

#         ball_started = False

#         # Put ball on Player 1 paddle
#         game.ball.attach_to_paddle(
#             game.player1.paddle
#         )

#         game.last_point = None


#     # ------------------------------------------------
#     # GAME TIME
#     # ------------------------------------------------

#     current_time = time.perf_counter()

#     dt = current_time - last_time

#     last_time = current_time


#     # Prevent huge time steps
#     if dt > 0.1:

#         dt = 0.1


#     # ------------------------------------------------
#     # GAME UPDATE
#     # ------------------------------------------------

#     if game_state == "PLAYING":

#         with lock:

#             direction1 = player_inputs[1]

#             direction2 = player_inputs[2]


#         # --------------------------------------------
#         # PLAYER 1 MOVEMENT
#         # --------------------------------------------

#         if direction1 == "up":

#             game.player1.paddle.move_up(dt)

#         elif direction1 == "down":

#             game.player1.paddle.move_down(
#                 game.screen_height,
#                 dt
#             )


#         # --------------------------------------------
#         # PLAYER 2 MOVEMENT
#         # --------------------------------------------

#         if direction2 == "up":

#             game.player2.paddle.move_up(dt)

#         elif direction2 == "down":

#             game.player2.paddle.move_down(
#                 game.screen_height,
#                 dt
#             )


#         # --------------------------------------------
#         # BALL UPDATE
#         # --------------------------------------------

#         if ball_started:

#             game.update(dt)


#         # --------------------------------------------
#         # POINT DETECTED
#         # --------------------------------------------

#         if game.last_point is not None:

#             scored_by = game.last_point


#             # ----------------------------------------
#             # Player 1 scored
#             # ----------------------------------------

#             if scored_by == 1:

#                 print(
#                     "Player 1 scored!"
#                 )

#                 # Player 2 gets next serve
#                 serving_player = 2

#                 game.ball.attach_to_paddle(
#                     game.player2.paddle
#                 )


#             # ----------------------------------------
#             # Player 2 scored
#             # ----------------------------------------

#             elif scored_by == 2:

#                 print(
#                     "Player 2 scored!"
#                 )

#                 # Player 1 gets next serve
#                 serving_player = 1

#                 game.ball.attach_to_paddle(
#                     game.player1.paddle
#                 )


#             # Ball is waiting for SPACE
#             ball_started = False


#             # Important:
#             # last_point should only be sent once
#             # as the point event.
#             #
#             # The client can display the point
#             # based on this value.
#             #
#             # We clear it after the state has
#             # been sent below.


#         # --------------------------------------------
#         # SEND CURRENT STATE
#         # --------------------------------------------

#         send_state()


#         # --------------------------------------------
#         # CLEAR POINT EVENT
#         # --------------------------------------------

#         if game.last_point is not None:

#             game.last_point = None


#     # ------------------------------------------------
#     # SERVER LOOP SPEED
#     # ------------------------------------------------

#     time.sleep(1 / 60)



















import socket
import json
import threading
import time

from game.game import Game


# ==================================================
# SERVER SETTINGS
# ==================================================

HOST = "0.0.0.0"
PORT = 5000

MAX_MESSAGE_SIZE = 1024
MAX_BUFFER_SIZE = 8192

# Minimaler Abstand zwischen zwei Client-Nachrichten
# desselben Clients.
MIN_MESSAGE_INTERVAL = 0.01


# ==================================================
# GAME
# ==================================================

game = Game()

game_state = "WAITING"

serving_player = None

ball_started = False


# ==================================================
# CLIENTS
# ==================================================

clients = {}

player_inputs = {
    1: "none",
    2: "none"
}


# Zeitpunkt der letzten gültigen Nachricht
last_message_time = {
    1: 0,
    2: 0
}


lock = threading.Lock()


# ==================================================
# SEND MESSAGE
# ==================================================

def send_message(client, message):

    data = json.dumps(message) + "\n"

    try:

        client.sendall(data.encode())

    except ConnectionError:

        pass


# ==================================================
# SEND GAME STATE
# ==================================================

def send_state():

    with lock:

        state = {
            "type": "state",

            "game_state": game_state,

            "player1_y":
                game.player1.paddle.y,

            "player2_y":
                game.player2.paddle.y,

            "ball_x":
                game.ball.x,

            "ball_y":
                game.ball.y,

            "score1":
                game.player1.score,

            "score2":
                game.player2.score,

            "last_point":
                game.last_point,

            "serving_player":
                serving_player,

            "ball_started":
                ball_started
        }

        current_clients = list(
            clients.items()
        )


    message = json.dumps(state) + "\n"

    encoded_message = message.encode()


    for player_number, client in current_clients:

        try:

            client.sendall(encoded_message)

        except ConnectionError:

            print(
                f"Player {player_number} "
                f"disconnected"
            )

            with lock:

                if player_number in clients:

                    del clients[player_number]

                player_inputs[
                    player_number
                ] = "none"


# ==================================================
# CLIENT HANDLER
# ==================================================

def handle_client(client, player_number):

    global game_state
    global serving_player
    global ball_started


    print(
        f"Player {player_number} connected"
    )


    # ------------------------------------------------
    # Tell client which player it is
    # ------------------------------------------------

    send_message(
        client,
        {
            "type": "player_assigned",
            "player": player_number
        }
    )


    buffer = ""


    try:

        while True:

            # ----------------------------------------
            # RECEIVE DATA
            # ----------------------------------------

            data = client.recv(4096)


            if not data:

                break


            # ----------------------------------------
            # BUFFER SIZE PROTECTION
            # ----------------------------------------

            if len(buffer) + len(data) > MAX_BUFFER_SIZE:

                print(
                    f"Player {player_number}: "
                    f"buffer too large"
                )

                break


            buffer += data.decode(
                errors="replace"
            )


            # ----------------------------------------
            # PROCESS COMPLETE MESSAGES
            # ----------------------------------------

            while "\n" in buffer:

                line, buffer = buffer.split(
                    "\n",
                    1
                )


                # Empty line
                if not line:

                    continue


                # ------------------------------------
                # MESSAGE SIZE CHECK
                # ------------------------------------

                if len(line) > MAX_MESSAGE_SIZE:

                    print(
                        f"Player {player_number}: "
                        f"message too large"
                    )

                    continue


                # ------------------------------------
                # RATE LIMIT
                # ------------------------------------

                current_time = time.perf_counter()


                with lock:

                    previous_time = (
                        last_message_time[
                            player_number
                        ]
                    )


                    if (
                        current_time
                        - previous_time
                        < MIN_MESSAGE_INTERVAL
                    ):

                        continue


                    last_message_time[
                        player_number
                    ] = current_time


                # ------------------------------------
                # JSON PARSING
                # ------------------------------------

                try:

                    message = json.loads(line)

                except json.JSONDecodeError:

                    print(
                        f"Player {player_number}: "
                        f"invalid JSON"
                    )

                    continue


                # ------------------------------------
                # JSON MUST BE AN OBJECT
                # ------------------------------------

                if not isinstance(
                    message,
                    dict
                ):

                    print(
                        f"Player {player_number}: "
                        f"message is not an object"
                    )

                    continue


                # ------------------------------------
                # TYPE FIELD
                # ------------------------------------

                message_type = message.get(
                    "type"
                )


                if not isinstance(
                    message_type,
                    str
                ):

                    print(
                        f"Player {player_number}: "
                        f"invalid message type"
                    )

                    continue


                # ------------------------------------
                # ONLY INPUT MESSAGES
                # ------------------------------------

                if message_type != "input":

                    print(
                        f"Player {player_number}: "
                        f"unknown message type"
                    )

                    continue


                # ------------------------------------
                # DIRECTION
                # ------------------------------------

                direction = message.get(
                    "direction"
                )


                if not isinstance(
                    direction,
                    str
                ):

                    print(
                        f"Player {player_number}: "
                        f"invalid direction type"
                    )

                    continue


                # ------------------------------------
                # WHITELIST
                # ------------------------------------

                allowed_directions = {
                    "up",
                    "down",
                    "none",
                    "start"
                }


                if direction not in allowed_directions:

                    print(
                        f"Player {player_number}: "
                        f"invalid direction: "
                        f"{direction}"
                    )

                    continue


                # ====================================
                # MOVEMENT
                # ====================================

                if direction in {
                    "up",
                    "down",
                    "none"
                }:

                    with lock:

                        player_inputs[
                            player_number
                        ] = direction


                # ====================================
                # START BALL
                # ====================================

                elif direction == "start":

                    with lock:

                        # Only the player whose turn it is
                        # may start the ball.

                        if (
                            game_state
                            == "PLAYING"

                            and

                            serving_player
                            == player_number

                            and

                            not ball_started
                        ):

                            game.ball.launch()

                            ball_started = True

                            print(
                                f"Player "
                                f"{player_number} "
                                f"started the ball"
                            )


    except ConnectionError:

        pass


    finally:

        with lock:

            if player_number in clients:

                del clients[player_number]


            player_inputs[
                player_number
            ] = "none"


            last_message_time[
                player_number
            ] = 0


            # Stop game when a player leaves

            game_state = "WAITING"

            serving_player = None

            ball_started = False


        client.close()


        print(
            f"Player {player_number} "
            f"disconnected"
        )


# ==================================================
# SERVER SOCKET
# ==================================================

server = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)


server.setsockopt(
    socket.SOL_SOCKET,
    socket.SO_REUSEADDR,
    1
)


server.bind(
    (HOST, PORT)
)


server.listen(2)


print(
    f"Server listening on "
    f"{HOST}:{PORT}"
)


# ==================================================
# GAME LOOP
# ==================================================

last_time = time.perf_counter()


while True:

    # ------------------------------------------------
    # ACCEPT CONNECTIONS
    # ------------------------------------------------

    server.settimeout(0.001)


    try:

        client, address = server.accept()

    except socket.timeout:

        client = None


    if client is not None:

        with lock:

            if 1 not in clients:

                player_number = 1

            elif 2 not in clients:

                player_number = 2

            else:

                player_number = None


            if player_number is not None:

                clients[player_number] = client


        # --------------------------------------------
        # GAME FULL
        # --------------------------------------------

        if player_number is None:

            send_message(
                client,
                {
                    "type": "error",
                    "message": "Game is full"
                }
            )

            client.close()


        # --------------------------------------------
        # NEW PLAYER
        # --------------------------------------------

        else:

            print(
                f"Player {player_number} "
                f"connected from {address}"
            )


            thread = threading.Thread(
                target=handle_client,
                args=(
                    client,
                    player_number
                ),
                daemon=True
            )


            thread.start()


    # ------------------------------------------------
    # PLAYER COUNT
    # ------------------------------------------------

    with lock:

        player_count = len(clients)


    # ------------------------------------------------
    # START GAME
    # ------------------------------------------------

    if (
        player_count == 2
        and
        game_state == "WAITING"
    ):

        print(
            "Both players connected."
        )

        print(
            "Player 1 gets the first serve."
        )


        game_state = "PLAYING"


        serving_player = 1


        ball_started = False


        # Attach ball to Player 1

        game.ball.attach_to_paddle(
            game.player1.paddle
        )


        game.last_point = None


    # ------------------------------------------------
    # CALCULATE DT
    # ------------------------------------------------

    current_time = time.perf_counter()


    dt = (
        current_time
        - last_time
    )


    last_time = current_time


    # Prevent huge time steps

    if dt > 0.1:

        dt = 0.1


    # ------------------------------------------------
    # GAME UPDATE
    # ------------------------------------------------

    if game_state == "PLAYING":

        with lock:

            direction1 = player_inputs[1]

            direction2 = player_inputs[2]


        # --------------------------------------------
        # PLAYER 1
        # --------------------------------------------

        if direction1 == "up":

            game.player1.paddle.move_up(
                dt
            )

        elif direction1 == "down":

            game.player1.paddle.move_down(
                game.screen_height,
                dt
            )


        # --------------------------------------------
        # PLAYER 2
        # --------------------------------------------

        if direction2 == "up":

            game.player2.paddle.move_up(
                dt
            )

        elif direction2 == "down":

            game.player2.paddle.move_down(
                game.screen_height,
                dt
            )


        # --------------------------------------------
        # BALL
        # --------------------------------------------

        if ball_started:

            game.update(dt)


        # --------------------------------------------
        # POINT DETECTED
        # --------------------------------------------

        if game.last_point is not None:

            scored_by = game.last_point


            # Player 1 scored
            if scored_by == 1:

                print(
                    "Player 1 scored!"
                )


                # Player 2 serves next

                serving_player = 2


                game.ball.attach_to_paddle(
                    game.player2.paddle
                )


            # Player 2 scored
            elif scored_by == 2:

                print(
                    "Player 2 scored!"
                )


                # Player 1 serves next

                serving_player = 1


                game.ball.attach_to_paddle(
                    game.player1.paddle
                )


            # Ball is now waiting

            ball_started = False


        # ------------------------------------------------
        # SEND STATE
        # ------------------------------------------------

        send_state()


        # ------------------------------------------------
        # CLEAR POINT EVENT
        # ------------------------------------------------

        if game.last_point is not None:

            game.last_point = None


    # ------------------------------------------------
    # SERVER LOOP
    # ------------------------------------------------

    time.sleep(
        1 / 60
    )