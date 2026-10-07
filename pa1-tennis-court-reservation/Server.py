# Server.py
import socket
import sys
from BookingManager import BookingManager
import uuid
from urllib.parse import unquote 

## This server implementation handles user requests and sends back an appropriate 
## response from the server, and it does this using BookingManager.py file

# we will keep the authentication token inside this 
SESSIONS = {}

# build a http response to send to client
def build_http_response(body, status="200 OK", extra_headers=None):
    headers = {"Content-Type": "text/plain"}
    if extra_headers:
        headers.update(extra_headers)

    header_lines = []
    for key, value in headers.items():
        header_lines.append(f"{key}: {value}")
    header_string = "\r\n".join(header_lines)

    return f"HTTP/1.1 {status}\r\n{header_string}\r\n\r\n{body}"

# parse the http request you get from the client
def parse_http_request(request_text):
    if not request_text:
        return None, None, None, build_http_response("Empty request", "400 Bad Request")

    lines = request_text.split("\r\n")
    request_line = lines[0]
    parts = request_line.split()
    if len(parts) < 2:
        return None, None, None, build_http_response("Malformed request line", "400 Bad Request")

    method, target = parts[0], parts[1]
    path = target.lstrip("/")
    path = unquote(path)

    headers = {}
    line_index = 1
    while line_index < len(lines) and lines[line_index] != "":
        line = lines[line_index]
        if ":" in line:
            parts = line.split(":", 1)
            key = parts[0].strip().lower()
            value = parts[1].strip()
            headers[key] = value
        line_index += 1


    return method, path, headers, None

# handle user log in 
# (if user sends other commands before logging in, it will not work)
def handle_login(booking_manager, tokens):
    if len(tokens) != 3:
        body = "Usage: login [USER_NAME] [PASSWORD]"
        return build_http_response(body, "400 Bad Request")

    user, pw = tokens[1], tokens[2]
    if booking_manager.authenticate(user, pw):
        new_token = str(uuid.uuid4())
        SESSIONS[new_token] = user
        body = "Login successful"
        
        headers = {"Set-Auth-Token": new_token}
        return build_http_response(body, "200 OK", extra_headers=headers)
    else:
        body = "Authentication failed"
        return build_http_response(body, "401 Unauthorized")

# handles user commands other than log in
def handle_command(booking_manager, username, cmd, tokens):
    if cmd == "show_list":
        body = booking_manager.view_week_schedule()
        return build_http_response(body, "200 OK")

    if cmd == "show_day":
        if len(tokens) != 2:
            body = "Usage: show_day [DAY_NAME]"
            return build_http_response(body, "400 Bad Request")
        
        day = tokens[1].upper()
        ok, body = booking_manager.view_day_schedule(day)
        if ok:
            status = "200 OK"
        else:
            status = "400 Bad Request"

        return build_http_response(body, status)

    if cmd == "show_my_res":
        body = booking_manager.view_self_schedule(username)
        return build_http_response(body, "200 OK")

    if cmd == "make_res":
        if len(tokens) != 3:
            body = "Usage: make_res [DAY_NAME] [SLOT_BEGINNING_TIME]"
            return build_http_response(body, "400 Bad Request")
        
        day = tokens[1].upper()
        slot = tokens[2]
        ok, msg = booking_manager.make_booking(username, day, slot)
        
        if ok:
            status = "200 OK"
        else:
            status = "409 Conflict"

        return build_http_response(msg, status)

    if cmd == "cancel_res":
        if len(tokens) != 2:
            body = "Usage: cancel_res [DAY_NAME]"
            return build_http_response(body, "400 Bad Request")
        
        day = tokens[1].upper()
        ok, msg = booking_manager.cancel_booking(username, day)

        if ok:
            status = "200 OK"
        else: 
            status = "404 Not Found"

        return build_http_response(msg, status)

    # Default case for unknown authenticated command
    body = "Invalid command"
    return build_http_response(body, "400 Bad Request")

# handle user request (does not work if not logged in)
def handle_request(booking_manager, request_text):
    try:
        method, path, headers, error_response = parse_http_request(request_text)
        if error_response:
            return error_response

        token = headers.get("x-auth-token")
        username = SESSIONS.get(token)
    
        tokens = [t for t in path.split() if t]
        if not tokens:
            return build_http_response("No command", "400 Bad Request")

        cmd = tokens[0]

        if cmd == "login":
            return handle_login(booking_manager, tokens)
    
        if not username:
            body = "Please login first"
            return build_http_response(body, "401 Unauthorized")

        return handle_command(booking_manager, username, cmd, tokens)

    except Exception as e:
        return build_http_response(f"Server error: {e}", "500 Internal Server Error")

def main():
    if len(sys.argv) != 3:
        print("Usage: python Server.py <Addr> <Port>")
        return

    host = sys.argv[1]
    port = int(sys.argv[2])

    booking_manager = BookingManager()

    # create TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"Server running on {host}:{port}")

        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"Connected by {addr}")

                request = conn.recv(4096).decode()
                print("Received request:")
                print(request)

                response = handle_request(booking_manager, request)

                conn.sendall(response.encode())


if __name__ == "__main__":
    main()