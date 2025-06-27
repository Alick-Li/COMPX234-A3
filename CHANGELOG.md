# Changelog

## 1st Commit
- `Server.py`: Initial implementation of a basic TCP server.
  - Added socket setup, bind, listen, and shutdown logic.
  - Placeholder for request handling.

---

## 2nd Commit
- `Server.py`:
  - Refactored server start logic to accept `hostname` and `port_number` as parameters.
  - Added `handle_client()` function with request parsing (command, key, value).
  - Set up a framework for handling multiple clients concurrently (preparing for threading).

---

## 3rd Commit
- `Server.py`:
  - Added global statistics and `tuple_space` storage.
  - Implemented counters for clients, operations, reads, gets, puts, and errors.
  - Skeleton logic for handling "R" (READ), "G" (GET), and "P" (PUT) commands with error/OK response placeholders.

---

## 4th Commit
- `Server.py`:
  - Implemented actual response message formats for READ, GET, PUT commands.
  - Added error handling for non-existent keys and duplicate keys.
  - Updated response message construction and sending.

---

## 5th Commit
- `Server.py`:
  - Added threading and time modules.
  - Calculated and tracked statistics: total tuples, average tuple size, key size, value size.
  - Added `display_summary()` function to print real-time summary statistics every 10 seconds.
  - Server now spawns a thread per client connection.

---

## 6th Commit
- `Client.py`: Initial client implementation.
  - Added `client_task` to connect to the server using TCP.
  - Set up argument passing and socket connection logic.
  - Added stub for a `main()` function.

---

## 7th Commit
- `Client.py`:
  - Implemented client to read commands from a file and send to the server.
  - Built and sent formatted request messages for READ, GET, PUT; received and printed server responses.
  - Added threading to allow multiple clients to run concurrently.

---

## 8th Commit
- `Client.py`:
  - Improved printed output: now displays which client file sent/received a response.
  - Enhanced error handling to specify file context.
  - Moved thread join logic to ensure all clients complete.

---

## 9th Commit
- `Server.py`:
  - Added missing global statistics initialization for tuple stats.
  - Ensured all relevant variables are declared as global in `handle_client`.

---

## 10th Commit
- `Client.py`:
  - Fixed file path formatting for client filenames in thread construction (`client_{i}.txt` instead of `client{i}.txt`).
- `Server.py`:
  - Improved `display_summary()` output formatting for better readability.

---

## 11th Commit
- `Server.py`:
  - Adjusted summary separator line in `display_summary()` for improved formatting.
