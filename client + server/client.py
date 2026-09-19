import socket
import json
import threading

import pygame


HOST = input("Server-IP: ")
PORT = XXXX  # Port number

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
    "player1_y": HEIGHT / 2 - 50,
    "player2_y": HEIGHT / 2 - 50,
    "ball_x": WIDTH / 2,
    "ball_y": HEIGHT / 2,
    "score1": 0,
    "score2": 0,
    "last_point": None
}

state_lock = threading.Lock()

my_player = None
rps_active = False

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


                # ------------------------------
                # WELCOME
                # ------------------------------

                if message.get(
                    "type"
                ) == "welcome":

                    my_player = message.get(
                        "player"
                    )

                    print(
                        f"Du bist Player "
                        f"{my_player}"
                    )


                # ------------------------------
                # GAME STATE
                # ------------------------------

                elif message.get(
                    "type"
                ) == "state":

                    with state_lock:

                        state.update(
                            message
                        )


                # ------------------------------
                # ERROR
                # ------------------------------

                elif message.get(
                    "type"
                ) == "error":

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


# --------------------------------------------------
# MAIN CLIENT LOOP
# --------------------------------------------------

while running:

    # ----------------------------------------------
    # EVENTS
    # ----------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False


    # ----------------------------------------------
    # KEYBOARD
    # ----------------------------------------------

    keys = pygame.key.get_pressed()

    input_direction = "none"


    if keys[pygame.K_w]:

        input_direction = "up"

    elif keys[pygame.K_s]:

        input_direction = "down"


    # ----------------------------------------------
    # SEND INPUT
    # ----------------------------------------------

    message = {
        "type": "input",
        "direction": input_direction
    }

    try:

        data = json.dumps(message) + "\n"

        client.sendall(
            data.encode()
        )

    except ConnectionError:

        running = False

        break


    # ----------------------------------------------
    # COPY STATE
    # ----------------------------------------------

    with state_lock:

        current_state = state.copy()

    # ----------------------------------------------
    # DRAW
    # ----------------------------------------------

    screen.fill(
        "black"
    )


    # Player 1 paddle - RED

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


    # Player 2 paddle - GREEN

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


    # Ball

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


    # ----------------------------------------------
    # SCORE
    # ----------------------------------------------

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


    # ----------------------------------------------
    # PLAYER INDICATOR
    # ----------------------------------------------

    if my_player == 1:

        player_text = font.render(
            "PLAYER 1",
            True,
            "red"
        )

    elif my_player == 2:

        player_text = font.render(
            "PLAYER 2",
            True,
            "green"
        )

    else:

        player_text = font.render(
            "CONNECTING...",
            True,
            "white"
        )


    player_rect = player_text.get_rect(
        center=(
            WIDTH // 2,
            HEIGHT - 30
        )
    )

    # kleine Schrift wäre schöner,
    # deshalb skalieren wir die Anzeige nicht weiter;
    # für den Prototyp reicht das.

    screen.blit(
        player_text,
        player_rect
    )


    pygame.display.flip()


    clock.tick(
        60
    )


# --------------------------------------------------
# CLEANUP
# --------------------------------------------------

running = False

try:

    client.close()

except:

    pass

pygame.quit()