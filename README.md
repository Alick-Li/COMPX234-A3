# Client/Server System

## 1. Project Overview
This project constructs a client/server network system based on TCP sockets to manage the "tuple space". Clients can send PUT, READ, and GET requests. The server can handle multiple client requests simultaneously.

## 2. Function Introduction

### 2.1 Client
1. Obtain the server hostname, port number, and request file name from the command line.
2. Check the request format.
3. Construct request messages according to the protocol, send them to the server, and output the response results.

### 2.2 Server
1. Receive the port number to start, listen for client connections, and create a new thread for each client.
2. Operate on the tuple space according to the requests, return responses in accordance with the protocol, and record various statistical information.
3. Print a summary of the tuple space every 10 seconds.

## 3. Usage Guide

### 3.1 Start the Server
Execute in the terminal:
```bash
python Server.py
```

### 3.2 Start the Client
Execute in another terminal:
```bash
python Client.py
```

## 4. Code Structure

### 4.1 `Client.py`
1. `client_task` function: Handle requests from a single client, including connection, request processing, and exception handling.
2. `main` function: Create and manage multiple client threads.

### 4.2 `Server.py`
1. Global variables: Record information such as the tuple space, number of connections, and number of operations.
2. `handle_client` function: Process client requests and update statistical information.
3. `display_summary` function: Print the summary of the tuple space at regular intervals.
4. `start_server` function: Start the server, listen for and handle client connections. 
