# **CMPT 371 A3 Socket Programming `Connect Four`**

**Course:** CMPT 371 \- Data Communications & Networking  
**Instructor:** Mirza Zaeem Baig  
**Semester:** Spring 2026  
<span style="color: purple;"> ***NOTE:*** The sample README was used as a template for this project. Content has been modified to fit the specifics of our project but the formatting and structure is entirely based on the sample. </span>

## **Group Members**

| Name | Student ID | Email |
| :---- | :---- | :---- |
| Jessica Liu | 301581749 | jyl83@sfu.ca |
| Khaled Taseen | 301457597 | _____@sfu.ca |

## **1\. Project Overview & Description**

This project is a multiplayer connect four game made with python. It uses Python's Socket API to allow two players to connect over a network and play against each other through a terminal based interface. 

## **2\. Limitations and Known Issues**

### **Limitations**

* The size of the game board is fixed to be the default size of 7x6
* The client cannot choose who they want to play against, they are paired with the next client that connects to the server.

### **Known Issues**

* It is possible for the client who is waiting for the turn to enter their move before the other player has made their move. The server will not reject the move, unless it is invalid, but it is not processed until the server receives the move from the other player. This may cause confusion for the player waiting as it may look like their turn has been skipped. 


## **3\. Video Demo**

The demo which covers establishing a connection, simple gameplay, and client disconnects can be found [Here](https://www.youtube.com/watch?v=m9uqS08Ezl0)

## **4\. Prerequisites (Fresh Environment)**

To run this project, you need:

* **Python 3.10** or higher.  
* No external pip installations are required (uses standard socket, threading, json, sys libraries).  
* (Optional) VS Code or Terminal.

## **4\. Step-by-Step Run Guide**

### **Step 1: Start the Server**

Open your terminal and go to the folder that contains the project. The server binds to 127.0.0.1 on port 5050.  

```bash
py server.py  
# Console output: "Server started on 127.0.0.1:5050"
```

### **Step 2: Connect Player 1**

Open a **Second** terminal window. Run the client script to start the first client.  

```bash
py client.py  
# Console output: "Connected. Waiting for opponent..."
```

### **Step 3: Connect Player 2 (O)**

Open a **third** terminal window. Run the client script again to start the second client.  

```bash
python client.py  
# Console output: "Connected. Waiting for opponent..."
# Console output: "Match found! You are Player O."
```

### **Step 4: Gameplay**

1. A player is randomly selected to go first.
2. The player selected will be prompted to enter a column (from 0 to 6). The other player will be told they are waiting for the opponent to make a move.
3. After receiving a valid move, the server will update the game board for both players, the previous game board is cleared.
4. The other player will take their turn.
5. Steps 2 to 4 will repeat until a win or draw.
6. The players are told the results and the connection closes.

## **5\. Technical Protocol Details (JSON over TCP)**

The protocol details are as follows:

* **Message Format:** `{"type": <string>, "payload": <data>}`  
* **Handshake Phase:** \* Client sends: `{"type": "CONNECT"}`  
  * Server responds: `{"type": "WELCOME", "payload": "Player X"}`  
* **Gameplay Phase:**  
  * Client sends: `{"type": "MOVE", "payload": col}`  
  * Server broadcasts: `{"type": "UPDATE", "board": board, , "turn": turn, "status": "ongoing" / result}`


## **6\. Academic Integrity & References**

* **Code Origin:**  
  * The following pieces of code were taken from the TA guided tic tac toe tutorial and adjusted to fit our needs:
    * Board representation (printBoard)
    * Message formatting for JSON communication between server and clients (see message format above)
* **GenAI Usage:**  
  * ChatGPT was used to assist in finding potential issues and debugging
  * GitHub Copilot was used to write the code that handles client disconnects
* **References:**  
  * [Connect 4 Game Python](https://youtube.com/playlist?list=PLFCB5Dp81iNV_inzM-R9AKkZZlePCZdtV&si=K75-JoOdMu866gvS)  
  * [Socket Programming in Python](https://www.geeksforgeeks.org/python/socket-programming-python/)
  * [\[CMPT 371\] \[Assignment 3\] \[Socket Programming in Python\]](https://youtube.com/playlist?list=PL-8C2cUhmkO1yWLTCiqf4mFXId73phvdx&si=gomv_r-KvgDkF-3Z)
