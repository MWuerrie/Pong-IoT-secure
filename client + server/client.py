import socket
import json
import pygame


# --------------------------------------------------
# Einstellungen
# --------------------------------------------------

SERVER_IP = input("Input server IP: ")
SERVER_PORT = 5000

WIDTH = 1000
HEIGHT = 600

FPS = 60


# --------------------------------------------------
# Pygame
# --------------------------------------------------

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong IoT Secure")

clock = pygame.time.Clock()


# --------------------------------------------------
# Farben
# --------------------------------------------------

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

RED = (255, 0, 0)
GREEN = (0, 255, 0)


# --------------------------------------------------
# Netzwerk
# --------------------------------------------------

client = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)

client.connect(
    (SERVER_IP, SERVER_PORT)
)

print("Mit Server verbunden.")


# --------------------------------------------------
# Server-Nachrichten
# --------------------------------------------------

buffer = ""

player_number = None

game_state = {
    "player1_y": 250,
    "player2_y": 250,

    "ball_x": 490,
    "ball_y": 290,

    "score1": 0,
    "score2": 0,

    "last_point": None,

    "serving_player": None,

    "ball_started": False,

    "game_state": "WAITING"
}


def receive_messages():

    global buffer
    global player_number
    global game_state

    client.setblocking(False)

    try:

        data = client.recv(4096)

        if not data:
            return

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

                print("Ungültiges JSON vom Server.")

                continue


            # --------------------------------------
            # PLAYER ASSIGNED
            # --------------------------------------

            if message.get("type") == "player_assigned":

                player_number = message["player"]

                print(
                    f"Du bist Spieler {player_number}"
                )


            # --------------------------------------
            # GAME STATE
            # --------------------------------------

            elif message.get("type") == "state":

                game_state = message

    except BlockingIOError:

        pass

    except ConnectionError:

        print("Verbindung zum Server verloren.")


def send_input(direction):

    message = {
        "type": "input",
        "direction": direction
    }

    data = json.dumps(message) + "\n"

    try:

        client.sendall(
            data.encode()
        )

    except ConnectionError:

        pass


# --------------------------------------------------
# Spiel
# --------------------------------------------------

running = True


while running:

    # ------------------------------------------------
    # Netzwerk
    # ------------------------------------------------

    receive_messages()


    # ------------------------------------------------
    # Events
    # ------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False


        # --------------------------------------------
        # SPACE
        # --------------------------------------------

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_SPACE:

                # Jeder Spieler darf SPACE drücken.
                #
                # Der Server entscheidet,
                # ob dieser Spieler gerade
                # aufschlagen darf.

                send_input("start")


    # ------------------------------------------------
    # Tastatur
    # ------------------------------------------------

    keys = pygame.key.get_pressed()

    direction = "none"


    # Spieler 1
    if player_number == 1:

        if keys[pygame.K_w]:

            direction = "up"

        elif keys[pygame.K_s]:

            direction = "down"


    # Spieler 2
    elif player_number == 2:

        if keys[pygame.K_UP]:

            direction = "up"

        elif keys[pygame.K_DOWN]:

            direction = "down"


    send_input(direction)


    # ------------------------------------------------
    # Bildschirm
    # ------------------------------------------------

    screen.fill(BLACK)


    # ------------------------------------------------
    # Mittellinie
    # ------------------------------------------------

    pygame.draw.line(
        screen,
        WHITE,
        (WIDTH // 2, 0),
        (WIDTH // 2, HEIGHT),
        2
    )


    # ------------------------------------------------
    # Spieler 1
    # ------------------------------------------------

    player1_y = game_state["player1_y"]

    pygame.draw.rect(
        screen,
        RED,
        (
            50,
            int(player1_y),
            20,
            100
        )
    )


    # ------------------------------------------------
    # Spieler 2
    # ------------------------------------------------

    player2_y = game_state["player2_y"]

    pygame.draw.rect(
        screen,
        GREEN,
        (
            WIDTH - 70,
            int(player2_y),
            20,
            100
        )
    )


    # ------------------------------------------------
    # Ball
    # ------------------------------------------------

    ball_x = game_state["ball_x"]
    ball_y = game_state["ball_y"]

    pygame.draw.rect(
        screen,
        WHITE,
        (
            int(ball_x),
            int(ball_y),
            20,
            20
        )
    )


    # ------------------------------------------------
    # Score
    # ------------------------------------------------

    font = pygame.font.Font(
        None,
        60
    )

    score1 = font.render(
        str(game_state["score1"]),
        True,
        WHITE
    )

    score2 = font.render(
        str(game_state["score2"]),
        True,
        WHITE
    )


    screen.blit(
        score1,
        (
            WIDTH // 2 - 80,
            30
        )
    )

    screen.blit(
        score2,
        (
            WIDTH // 2 + 50,
            30
        )
    )


    # ------------------------------------------------
    # Spieler-Anzeige
    # ------------------------------------------------

    small_font = pygame.font.Font(
        None,
        30
    )

    player_text = small_font.render(
        f"Spieler {player_number}",
        True,
        WHITE
    )

    screen.blit(
        player_text,
        (10, 10)
    )


    # ------------------------------------------------
    # Spielstatus
    # ------------------------------------------------

    current_game_state = game_state.get(
        "game_state"
    )

    serving_player = game_state.get(
        "serving_player"
    )

    ball_started = game_state.get(
        "ball_started",
        False
    )


    # ------------------------------------------------
    # WAITING
    # ------------------------------------------------

    if current_game_state == "WAITING":

        waiting_text = small_font.render(
            "Warte auf zweiten Spieler...",
            True,
            WHITE
        )

        screen.blit(
            waiting_text,
            (
                WIDTH // 2 - 160,
                HEIGHT // 2 - 20
            )
        )


    # ------------------------------------------------
    # BALL WAITING FOR SERVE
    # ------------------------------------------------

    elif (
        not ball_started
        and serving_player == player_number
    ):

        start_text = small_font.render(
            "SPACE = Ball starten",
            True,
            WHITE
        )

        screen.blit(
            start_text,
            (
                WIDTH // 2 - 120,
                HEIGHT - 40
            )
        )


    # ------------------------------------------------
    # WAITING FOR OTHER PLAYER
    # ------------------------------------------------

    elif not ball_started:

        waiting_text = small_font.render(
            f"Spieler {serving_player} "
            f"ist am Aufschlag",
            True,
            WHITE
        )

        screen.blit(
            waiting_text,
            (
                WIDTH // 2 - 140,
                HEIGHT - 40
            )
        )


    # ------------------------------------------------
    # DISPLAY
    # ------------------------------------------------

    pygame.display.flip()

    clock.tick(FPS)


# --------------------------------------------------
# Beenden
# --------------------------------------------------

client.close()

pygame.quit()