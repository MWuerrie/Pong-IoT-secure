import socket
import json
import threading
import time

from game.game import Game


HOST = "X.X.X.X"   
PORT = XXXX

WINNING_SCORE = 20

game = Game()

game_state = "WAITING"

serving_player = None

rps_choices = {
    1: None,
    2: None
}

clients = {}

player_inputs = {
    1: "none",
    2: "none"
}

lock = threading.Lock()


# --------------------------------------------------
# SEND MESSAGE
# --------------------------------------------------

def send_message(client, message):
    """Sendet eine JSON-Nachricht mit Newline-Framing."""

    data = json.dumps(message) + "\n"

    client.sendall(
        data.encode()
    )


# --------------------------------------------------
# SEND TO ALL CLIENTS
# --------------------------------------------------

def broadcast(message):
    """Sendet eine Nachricht an alle verbundenen Clients."""

    data = json.dumps(message) + "\n"
    encoded_message = data.encode()

    with lock:
        current_clients = list(
            clients.items()
        )

    for player_number, client in current_clients:

        try:

            client.sendall(
                encoded_message
            )

        except ConnectionError:

            print(
                f"Player {player_number} disconnected"
            )

            with lock:

                if player_number in clients:
                    del clients[player_number]

                player_inputs[
                    player_number
                ] = "none"


# --------------------------------------------------
# SEND GAME STATE
# --------------------------------------------------

def send_state():
    """Sendet den aktuellen Game-State an alle Clients."""

    with lock:

        state = {
            "type": "state",

            "game_state":
                game_state,

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
                serving_player
        }

        current_clients = list(
            clients.items()
        )

    message = json.dumps(state) + "\n"
    encoded_message = message.encode()

    for player_number, client in current_clients:

        try:

            client.sendall(
                encoded_message
            )

        except ConnectionError:

            print(
                f"Player {player_number} disconnected"
            )

            with lock:

                if player_number in clients:
                    del clients[player_number]

                player_inputs[
                    player_number
                ] = "none"


# --------------------------------------------------
# RPS
# --------------------------------------------------

def determine_rps_winner():

    p1 = rps_choices[1]
    p2 = rps_choices[2]

    # Unentschieden

    if p1 == p2:

        return None

    # Player 1 gewinnt

    if (
        (p1 == "rock" and p2 == "scissors") or
        (p1 == "scissors" and p2 == "paper") or
        (p1 == "paper" and p2 == "rock")
    ):

        return 1

    # Sonst gewinnt Player 2

    return 2


# --------------------------------------------------
# CLIENT HANDLER
# --------------------------------------------------

def handle_client(client, player_number):

    global game_state
    global serving_player

    print(
        f"Player {player_number} connected"
    )

    # Spieler-Nummer mitteilen

    try:

        send_message(
            client,
            {
                "type": "welcome",
                "player": player_number
            }
        )

    except ConnectionError:

        client.close()
        return

    buffer = ""

    try:

        while True:

            data = client.recv(1024)

            if not data:
                break

            buffer += data.decode(
                errors="replace"
            )

            # TCP kann mehrere Nachrichten
            # gleichzeitig liefern

            while "\n" in buffer:

                line, buffer = buffer.split(
                    "\n",
                    1
                )

                if not line:
                    continue

                # Nachrichtenlimit

                if len(line) > 4096:

                    print(
                        f"Player {player_number}: "
                        "message too large"
                    )

                    continue

                # JSON lesen

                try:

                    message = json.loads(line)

                except json.JSONDecodeError:

                    print(
                        f"Player {player_number}: "
                        "invalid JSON"
                    )

                    continue


                # ------------------------------------------
                # RPS
                # ------------------------------------------

                if message.get("type") == "rps":

                    choice = message.get(
                        "choice"
                    )

                    # Nur erlaubte Werte

                    if choice not in (
                        "rock",
                        "paper",
                        "scissors"
                    ):

                        continue

                    with lock:

                        # Nur während RPS akzeptieren

                        if game_state == "RPS":

                            rps_choices[
                                player_number
                            ] = choice

                    continue


                # ------------------------------------------
                # NORMAL INPUT
                # ------------------------------------------

                if message.get("type") != "input":

                    continue

                direction = message.get(
                    "direction"
                )

                # Nur erlaubte Eingaben

                if direction not in (
                    "up",
                    "down",
                    "none"
                ):

                    continue

                with lock:

                    player_inputs[
                        player_number
                    ] = direction


    except ConnectionError:

        pass


    finally:

        
        with lock:

            if player_number in clients:

                del clients[
                    player_number
                ]

            player_inputs[
                player_number
            ] = "none"

            rps_choices[
                player_number
            ] = None

            # Wenn ein Spieler geht,
            # zurück in WAITING

            game_state = "WAITING"

            serving_player = None

        client.close()

        print(
            f"Player {player_number} disconnected"
        )


# --------------------------------------------------
# SERVER SOCKET
# --------------------------------------------------

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
    f"Server listening on 0.0.0.0:{PORT}"
)


last_time = time.perf_counter()


# --------------------------------------------------
# MAIN GAME LOOP
# --------------------------------------------------

while True:

    # Nicht dauerhaft in accept()
    # blockieren

    server.settimeout(
        0.001
    )

    try:

        client, address = server.accept()

    except socket.timeout:

        client = None


    # --------------------------------------------------
    # NEW CLIENT
    # --------------------------------------------------

    if client is not None:

        with lock:

            if 1 not in clients:

                player_number = 1

            elif 2 not in clients:

                player_number = 2

            else:

                player_number = None


            if player_number is not None:

                clients[
                    player_number
                ] = client


        # Kein Platz

        if player_number is None:

            try:

                send_message(
                    client,
                    {
                        "type": "error",
                        "message": "Game is full"
                    }
                )

            except ConnectionError:

                pass

            client.close()


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


    # --------------------------------------------------
    # CHECK PLAYER COUNT
    # --------------------------------------------------

    with lock:

        player_count = len(
            clients
        )


    # --------------------------------------------------
    # START RPS
    # --------------------------------------------------

    if (
        player_count == 2
        and game_state == "WAITING"
    ):

        game = Game()

        with lock:

            rps_choices[1] = None
            rps_choices[2] = None

            player_inputs[1] = "none"
            player_inputs[2] = "none"

        game_state = "RPS"

        print(
            "Both players connected!"
        )

        print(
            "Rock Paper Scissors!"
        )

        broadcast(
            {
                "type": "game_event",
                "event": "rps_start"
            }
        )


    # --------------------------------------------------
    # RPS CHECK
    # --------------------------------------------------

    if game_state == "RPS":

        with lock:

            p1_choice = rps_choices[1]
            p2_choice = rps_choices[2]


        # Beide haben gewählt

        if (
            p1_choice is not None
            and
            p2_choice is not None
        ):

            winner = determine_rps_winner()


            # ------------------------------------------
            # DRAW
            # ------------------------------------------

            if winner is None:

                print(
                    "RPS draw - try again"
                )

                broadcast(
                    {
                        "type": "game_event",
                        "event": "rps_draw"
                    }
                )

                with lock:

                    rps_choices[1] = None
                    rps_choices[2] = None


            # ------------------------------------------
            # WINNER
            # ------------------------------------------

            else:

                print(
                    f"Player {winner} "
                    "wins RPS"
                )

                serving_player = winner

                game_state = "READY"

                broadcast(
                    {
                        "type": "game_event",
                        "event": "rps_result",
                        "winner": winner
                    }
                )


    # --------------------------------------------------
    # DELTA TIME
    # --------------------------------------------------

    current_time = time.perf_counter()

    dt = (
        current_time
        - last_time
    )

    last_time = current_time

    if dt > 0.1:

        dt = 0.1


    # --------------------------------------------------
    # GAME
    # --------------------------------------------------

    if game_state == "PLAYING":

        # ----------------------------------------------
        # INPUT
        # ----------------------------------------------

        with lock:

            direction1 = player_inputs[1]
            direction2 = player_inputs[2]


        # Player 1

        if direction1 == "up":

            game.player1.paddle.move_up(
                dt
            )

        elif direction1 == "down":

            game.player1.paddle.move_down(
                game.screen_height,
                dt
            )


        # Player 2

        if direction2 == "up":

            game.player2.paddle.move_up(
                dt
            )

        elif direction2 == "down":

            game.player2.paddle.move_down(
                game.screen_height,
                dt
            )


        # ----------------------------------------------
        # GAME UPDATE
        # ----------------------------------------------

        game.update(
            dt
        )


        # ----------------------------------------------
        # SEND STATE
        # ----------------------------------------------

        send_state()


    # --------------------------------------------------
    # SERVER TICK
    # --------------------------------------------------

    time.sleep(
        1 / 60
    )