# CS421 – Computer Networks (Bilkent University, Fall 2025)

My coursework for CS421. Everything is written in Python using only the standard library (`socket`, `threading`), as the assignments required.

| Folder | What it is |
|---|---|
| [`pa1-tennis-court-reservation`](pa1-tennis-court-reservation) | HTTP-based client/server reservation system over raw TCP sockets |
| [`pa2-go-back-n-over-udp`](pa2-go-back-n-over-udp) | Reliable file transfer with a Go-Back-N sender over UDP |
| [`written`](written) | Wireshark lab report and written Homework 2 (PDF) |

## PA1 – Tennis Court Reservation (HTTP over TCP)

A server manages one tennis court (7 days × 14 hourly slots) for 10 predefined users. The client and server talk with hand-built HTTP/1.1 messages; after `login` the server returns a session token (`Set-Auth-Token`) that the client sends with every later request.

- `Server.py` – parses HTTP requests, handles sessions and returns proper status codes (`200`, `400`, `401`, `404`, `409`, `500`)
- `BookingManager.py` – users, authentication and booking rules
- `Day.py` – slots of a single day (one booking per user per day)
- `Client.py` – interactive command-line client
- `report.pdf` – design report

```bash
python Server.py 127.0.0.1 8080
python Client.py 127.0.0.1 8080
```

Commands: `login <user> <password>`, `show_list`, `show_day <DAY>`, `show_my_res`, `make_res <DAY> <HOUR>`, `cancel_res <DAY>` (users are `user1`…`user10`, password = the number).

## PA2 – Go-Back-N over UDP

`sender.py` splits a file into 1022-byte chunks with a 2-byte sequence-number header and sends them with a sliding window. A separate thread listens for cumulative ACKs and slides the window; on timeout the whole window is retransmitted. A packet with sequence number 0 ends the transfer.

```bash
python sender.py <file_path> <receiver_port> <window_size_N> <timeout_ms>
```

The receiver (which simulates ACK loss and delay) was provided by the course and is not included here. `report.pdf` measures throughput against loss rate, window size and timeout.

---
Author: Irmak İmdat
