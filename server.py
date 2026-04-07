import socket
import threading
import json
import random

HOST = '127.0.0.1' # Localhost
PORT = 5050

clientQueue = []
turnOptions = ['X', 'O']

ROWS = 6
COLUMNS = 7

# Server Loop: Listens for incoming connections and manages matchmaking.
# Portion of the code within this function is taken from TA guided tic-tac-toe tutorial
# Repo Link: https://github.com/mariam-bebawy/CMPT371_A3_Socket_Programming, original code found in server.py
def startServer():
    # Create an IPv4 TCP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server started on {HOST}:{PORT}")

    try:
        while True:
            # Block until a client connects
            con, addr = server.accept()
            data = con.recv(1024).decode('utf-8')

            # Look for initial connection message
            if "CONNECT" in data:
                # Notify that a client has connected and add them to the matchmaking queue
                print(f"Client {addr} connected and added to matchmaking queue.")
                clientQueue.append(con) # 

                # Start a new game when there are at least 2 clients in the queue
                if len(clientQueue) >= 2:
                    conn_x = clientQueue.pop(0)
                    conn_o = clientQueue.pop(0)

                    print(f"Match found! Starting game session for clients {conn_x.getpeername()} and {conn_o.getpeername()}.")
                    # Start a new thread to handle the game between the clients, marked as a daemon so it will close when the main thread closes
                    threading.Thread(target=startGame, args=(conn_x, conn_o), daemon=True).start()

    except KeyboardInterrupt:
        print(f"Shutting down server.")
    finally:
        server.close()

# Game Loop for a single game session between two clients. Handles game state, move validation, win/draw conditions, and disconnections
def startGame(conn_x, conn_o):
    board = [[' ' for _ in range(COLUMNS)] for _ in range(ROWS)] # Initial empty board

    # Send the welcome message to each client, tell them their roles
    conn_x.sendall((json.dumps({"type": "WELCOME", "payload": "Player X"}) + '\n').encode('utf-8'))
    conn_o.sendall((json.dumps({"type": "WELCOME", "payload": "Player O"}) + '\n').encode('utf-8'))

    # Randomly select a player to start
    turn = random.choice(turnOptions)

    # Send the initial board state and current turn to clients
    conn_x.sendall((json.dumps({"type": "UPDATE", "board": board, "turn": turn, "status": "ongoing"}) + '\n').encode('utf-8'))
    conn_o.sendall((json.dumps({"type": "UPDATE", "board": board, "turn": turn, "status": "ongoing"}) + '\n').encode('utf-8'))

    while True:
        current_conn = conn_x if turn == 'X' else conn_o # Determine whose turn it is

        # Handle opponent disconnects
        try:
            data = current_conn.recv(1024).decode('utf-8')
            if not data:  # client disconnected gracefully
                other_conn = conn_o if current_conn == conn_x else conn_x # Get the other client's connection 
                try:
                    # Notify the other client that their opponent has disconnected
                    other_conn.sendall((json.dumps({"type": "DISCONNECT"}) + '\n').encode('utf-8'))
                except: # Handle case where both clients have disconnected
                    pass 
                    break
        except (ConnectionResetError, ConnectionAbortedError): # Handle case where client disconnects ungracefully
            other_conn = conn_o if current_conn == conn_x else conn_x
            try:
                other_conn.sendall((json.dumps({"type": "DISCONNECT"}) + '\n').encode('utf-8'))
            except:
                pass
            break

        try:
            for chunk in data.strip().split('\n'):
                if not chunk:
                    continue

                msg = json.loads(chunk)

                # Validate that the message is a move before processing it
                if msg["type"] != "MOVE":
                    current_conn.sendall((json.dumps({"type": "INVALID_MOVE"}) + '\n').encode('utf-8'))
                    continue

                column = msg["payload"]

                # Validate the move before applying it to the board
                if not (isValidMove(board, column)):
                    current_conn.sendall((json.dumps({"type": "INVALID_MOVE"}) + '\n').encode('utf-8'))
                    continue
                
                # Place the piece in the lowest open row in selected column
                for r in range(ROWS -1, -1, -1):
                    if board[r][column] == ' ':
                        board[r][column] = turn
                        break
                
                # Check for win conditions
                if isWin(board, turn):
                    result = f"Player {turn} wins!"
                    msg_out = json.dumps({"type": "UPDATE", "board": board, "status": result}) + '\n'
                    conn_x.sendall(msg_out.encode('utf-8'))
                    conn_o.sendall(msg_out.encode('utf-8'))
                    return

                # Check for draw conditions (Board is full)
                elif all(board[0][c] != ' ' for c in range(COLUMNS)): # Check that top row is full for all columns
                    result = "It's a draw!"
                    msg_out = json.dumps({"type": "UPDATE", "board": board, "status": result}) + '\n'
                    conn_x.sendall(msg_out.encode('utf-8'))
                    conn_o.sendall(msg_out.encode('utf-8'))
                    return

                # Swap turns
                turn = 'O' if turn == 'X' else 'X'

                # Broadcast the updated board and turn to both clients
                msg_out = json.dumps({"type": "UPDATE","board": board,"turn": turn,"status": "ongoing"}) + '\n'

                conn_x.sendall(msg_out.encode('utf-8'))
                conn_o.sendall(msg_out.encode('utf-8'))

        except json.JSONDecodeError: # Handle malformed JSON packets by ignoring and waiting for valid one
            continue

# Checks if the player has won by checking for 4 in a row horizontally, vertically, and diagonally
def isWin(board, piece):
    # Horizontal check
    for col in range(COLUMNS - 3):
        for row in range(ROWS):
            if(board[row][col] == board[row][col + 1] == board[row][col + 2] == board[row][col + 3] == piece):
                return True

    # Vertical check
    for col in range(COLUMNS,):
        for row in range(ROWS - 3):
            if(board[row][col] == board[row + 1][col] == board[row + 2][col] == board[row + 3][col] == piece):
                return True
            
    # Diagonal checks
    # Upwards Diagonals
    for col in range(COLUMNS - 3):
        for row in range(3, ROWS):
            if (board[row][col] == board[row - 1][col + 1] == board[row - 2][col + 2] == board[row - 3][col + 3] == piece):
                return True
            
    # Downwards Diagonals
    for col in range(COLUMNS - 3):
        for row in range(ROWS - 3):
            if(board[row][col] == board[row + 1][col + 1] == board[row + 2][col + 2] == board[row + 3][col + 3] == piece):
                return True
    return False

# Determines if a move is valid by...
def isValidMove(board, column):
    # Checking if the column is in bounds of the board
    if(column < 0 or column >= 7):
        return False
    
    # Checking that the column is not full
    return board[0][column] == ' '

if __name__ == "__main__":
    startServer()