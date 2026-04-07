import socket
import json
import os
import time

HOST = '127.0.0.1'
PORT = 5050

# Board representation code taken from TA guided tic-tac-toe tutorial, modified for 7x6 connect four board
# Repo Link: https://github.com/mariam-bebawy/CMPT371_A3_Socket_Programming, original code found in client.py
def printBoard(board):
    # Print headers
    print("\n    0   1   2   3   4   5   6")
    print("  ┌───┬───┬───┬───┬───┬───┬───┐")

    for i, row in enumerate(board):
        # Print row 
        print(f"  │ {row[0]} │ {row[1]} │ {row[2]} │ {row[3]} │ {row[4]} │ {row[5]} │ {row[6]} │")
        
        # Row separators or the bottom border
        if i < 5:
            print("  ├───┼───┼───┼───┼───┼───┼───┤")
        else:
            print("  └───┴───┴───┴───┴───┴───┴───┘\n")

# Clears the console for better readability after each move
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# Determines if a move is valid by...
def isValidMove(board, column):
    # Checking if the column is in bounds of the board
    if(column < 0 or column >= 7):
        return False
    
    # Checking that the column is not full
    return board[0][column] == ' '

# Portion of the code within this fuction is taken from TA guided tic-tac-toe tutorial, modified for connect four game logic
# Repo Link: https://github.com/mariam-bebawy/CMPT371_A3_Socket_Programming, original code found in client.py
def startClient():
    # Create a IPv4 TCP socket and connect to the server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    
    # Send initial connection message to be placed in matchmaking queue 
    client.sendall(json.dumps({"type": "CONNECT"}).encode('utf-8'))
    print("Connected. Waiting for opponent...")
    
    role = None
    try: 
        while True:
            # Wait for data from server
            data = client.recv(1024).decode('utf-8')
                
            # Handle case where multiple JSON packets are received at once by splitting on newline characters
            # Allows us to handle multiple messages without data loss
            for chunk in data.strip().split('\n'):
                if not chunk: continue
                # Deserialize the JSON packet
                msg = json.loads(chunk)
                
                
                if msg["type"] == "WELCOME": # Handle initial message
                    # Assign the client a role base on message from server
                    role = msg["payload"][-1]
                    print(f"Match found, You are Player {role}.")
                    time.sleep(1)  # Brief pause before the first board update
                
                elif msg["type"] == "UPDATE": # Handle board updates and game status
                    # Clear the console then print the current board state
                    clear() 
                    printBoard(msg["board"])

                    if msg["status"] == "ongoing": # Game has not ended
                        if msg["turn"] == role: # Check that it's this client's turn
                            print(f"Your turn! You are player {role}. Enter a column (0-6):")
                            while True: # Loop until client enters a valid move
                                try:
                                    col = int(input())
                                    isValid = isValidMove(msg["board"], col)

                                    # Make sure the move is valid before sending it to the server
                                    if isValid:
                                        break
                                    else:
                                        print("Invalid move. Please try again.")
                                except ValueError: # Handle non-integer input
                                    print("Please enter a valid integer between 0 and 6.")

                            # Send the move to the server
                            client.sendall(json.dumps({"type": "MOVE", "payload": col}).encode('utf-8'))
                        else: # Wait for opponent to make a move
                            print("Waiting for opponent's move...")
                    else: # Game has ended, print the result and exit
                        print(f"Game over! {msg['status']}")
                        if(msg['status'] == f"Player {role} wins!"):
                            print("Congratulations, you won!")
                        elif(msg['status'] == "It's a draw!"):
                            print("Well played.")
                        else:
                            print("Better luck next time!")
                        return
                elif msg["type"] == "DISCONNECT": # Handle opponent disconnect
                    # Tell client opponent has disconnected and close the connection
                    print("Opponent disconnected. Exiting game.")
                    client.close()
                    return

    except KeyboardInterrupt: # Handle Ctrl+C gracefully by notifying the server and closing the connection
        exitMsg = (json.dumps({"type": "DISCONNECT"}) + '\n').encode('utf-8')
        client.sendall(exitMsg) # Send the disconnect message to the server
        print("Exiting game.") # Notify the client that they are exiting
        client.close() 
    finally:
        client.close()
        
if __name__ == "__main__":
    startClient()