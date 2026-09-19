import socket
import json
import threading

import pygame


HOST = input("Server-IP: ")
PORT = 5000

WIDTH = 1000
HEIGHT = 600


# --------------------------------------------------
# SOCKET
# --------------------------------------------------

client = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

client.connect(
    (HOST, PORT)
)

print("Mit Server verbunden.")


# --------------------------------------------------
# GAME STATE
# --------------------------------------------------

state = {
    "game_state": "WAITING",

    "player1_y": HEIGHT / 2 - 50,
    "player2_y": HEIGHT / 2 - 50,

    "ball_x": WIDTH / 2,
    "ball_y": HEIGHT / 2,

    "score1": 0,
    "score2": 0,

    "last_point": None,

    "serving_player": None
}

state_lock = threading.Lock()

my_player = None

running = True


# --------------------------------------------------
# RECEIVE THREAD
# --------------------------------------------------

def receive_data():

    global running
    global my_player

    buffer = ""

    try:

        while running:

            data = client.recv(4096)

            if not data:

                print(
                    "Server hat die Verbindung beendet."
                )

                running = False

                break

            buffer += data.decode(
                errors="replace"
            )

            while "\n" in buffer:

                line, buffer = buffer.split(
                    "\n",
                    1
                )

                if not line:
                    continue

                try:

                    message = json.loads(line)

                except json.JSONDecodeError:

                    print(
                        "Ungültige Server-Nachricht."
                    )

                    continue


                # --------------------------------------------------
                # WELCOME
                # --------------------------------------------------

                if message.get("type") == "welcome":

                    my_player = message.get(
                        "player"
                    )

                    print(
                        f"Du bist Player {my_player}"
                    )


                # --------------------------------------------------
                # GAME STATE
                # --------------------------------------------------

                elif message.get("type") == "state":

                    with state_lock:

                        state.update(
                            message
                        )


                # --------------------------------------------------
                # GAME EVENT
                # --------------------------------------------------

                elif message.get("type") == "game_event":

                    event = message.get(
                        "event"
                    )

                    # ----------------------------------------------
                    # READY
                    # ----------------------------------------------

                    if event == "ready":

                        serving_player = message.get(
                            "serving_player"
                        )

                        with state_lock:

                            state["game_state"] = "READY"

                            state["serving_player"] = (
                                serving_player
                            )

                        print(
                            f"Player "
                            f"{serving_player} "
                            "ist dran."
                        )


                # --------------------------------------------------
                # ERROR
                # --------------------------------------------------

                elif message.get("type") == "error":

                    print(
                        message.get(
                            "message"
                        )
                    )

                    running = False

                    break


    except ConnectionError:

        running = False


# --------------------------------------------------
# RECEIVE THREAD START
# --------------------------------------------------

receive_thread = threading.Thread(
    target=receive_data,
    daemon=True
)

receive_thread.start()


# --------------------------------------------------
# PYGAME
# --------------------------------------------------

pygame.init()

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "Pong IoT Secure"
)

clock = pygame.time.Clock()

font = pygame.font.Font(
    None,
    60
)

small_font = pygame.font.Font(
    None,
    30
)


# --------------------------------------------------
# MAIN LOOP
# --------------------------------------------------

while running:

    # --------------------------------------------------
    # EVENTS
    # --------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False


        # --------------------------------------------------
        # SPACE = START
        # --------------------------------------------------

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:

                with state_lock:

                    current_game_state = state[
                        "game_state"
                    ]

                    current_serving_player = state[
                        "serving_player"
                    ]

                if (
                    current_game_state == "READY"
                    and
                    current_serving_player
                    == my_player
                ):

                    message = {
                        "type": "input",
                        "direction": "start"
                    }

                    try:

                        data = (
                            json.dumps(message)
                            + "\n"
                        )

                        client.sendall(
                            data.encode()
                        )

                    except ConnectionError:

                        running = False


    # --------------------------------------------------
    # KEYBOARD
    # --------------------------------------------------

    keys = pygame.key.get_pressed()

    input_direction = "none"


    # --------------------------------------------------
    # PLAYER 1
    # --------------------------------------------------

    if my_player == 1:

        if keys[pygame.K_w]:

            input_direction = "up"

        elif keys[pygame.K_s]:

            input_direction = "down"


    # --------------------------------------------------
    # PLAYER 2
    # --------------------------------------------------

    elif my_player == 2:

        if keys[pygame.K_UP]:

            input_direction = "up"

        elif keys[pygame.K_DOWN]:

            input_direction = "down"


    # --------------------------------------------------
    # SEND MOVEMENT
    # --------------------------------------------------

    message = {
        "type": "input",
        "direction": input_direction
    }

    try:

        data = (
            json.dumps(message)
            + "\n"
        )

        client.sendall(
            data.encode()
        )

    except ConnectionError:

        running = False

        break


    # --------------------------------------------------
    # COPY STATE
    # --------------------------------------------------

    with state_lock:

        current_state = state.copy()


    # --------------------------------------------------
    # DRAW
    # --------------------------------------------------

    screen.fill(
        "black"
    )


    # --------------------------------------------------
    # PLAYER 1
    # --------------------------------------------------

    pygame.draw.rect(
        screen,
        "red",
        (
            50,
            int(
                current_state[
                    "player1_y"
                ]
            ),
            20,
            100
        )
    )


    # --------------------------------------------------
    # PLAYER 2
    # --------------------------------------------------

    pygame.draw.rect(
        screen,
        "green",
        (
            WIDTH - 70,
            int(
                current_state[
                    "player2_y"
                ]
            ),
            20,
            100
        )
    )


    # --------------------------------------------------
    # BALL
    # --------------------------------------------------

    pygame.draw.rect(
        screen,
        "white",
        (
            int(
                current_state[
                    "ball_x"
                ]
            ),
            int(
                current_state[
                    "ball_y"
                ]
            ),
            20,
            20
        )
    )


    # --------------------------------------------------
    # SCORE
    # --------------------------------------------------

    score_text = font.render(
        f"{current_state['score1']}   "
        f"{current_state['score2']}",
        True,
        "white"
    )

    score_rect = score_text.get_rect(
        center=(
            WIDTH // 2,
            50
        )
    )

    screen.blit(
        score_text,
        score_rect
    )


    # --------------------------------------------------
    # STATUS
    # --------------------------------------------------

    game_state = current_state[
        "game_state"
    ]

    serving_player = current_state[
        "serving_player"
    ]


    if game_state == "WAITING":

        status = "WAITING FOR PLAYER"


    elif game_state == "READY":

        if serving_player == my_player:

            status = "PRESS SPACE TO START"

        else:

            status = (
                f"PLAYER "
                f"{serving_player} "
                "STARTS"
            )


    elif game_state == "PLAYING":

        status = "PLAYING"


    else:

        status = game_state


    status_text = small_font.render(
        status,
        True,
        "white"
    )

    status_rect = status_text.get_rect(
        center=(
            WIDTH // 2,
            HEIGHT - 60
        )
    )

    screen.blit(
        status_text,
        status_rect
    )


    # --------------------------------------------------
    # PLAYER INDICATOR
    # --------------------------------------------------

    if my_player == 1:

        player_text = small_font.render(
            "PLAYER 1",
            True,
            "red"
        )

    elif my_player == 2:

        player_text = small_font.render(
            "PLAYER 2",
            True,
            "green"
        )

    else:

        player_text = small_font.render(
            "CONNECTING...",
            True,
            "white"
        )


    player_rect = player_text.get_rect(
        center=(
            WIDTH // 2,
            HEIGHT - 25
        )
    )

    screen.blit(
        player_text,
        player_rect
    )


    pygame.display.flip()

    clock.tick(60)


# --------------------------------------------------
# CLEANUP
# --------------------------------------------------

running = False

try:

    client.close()

except:

    pass

pygame.quit()