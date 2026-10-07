# Client.py
import socket
import sys
from urllib.parse import quote

def main():
    if len(sys.argv) != 3:
        print("Usage: python Client.py <Addr> <Port>")
        return

    host = sys.argv[1]
    port = int(sys.argv[2])

    token = None
    
    # keep prompting the user for entering a command until quit. 
    # keep a HTTP formatted variable request_line, send it to the server and get a response
    while True:
        
        command = input("Enter command \n * login [USER_NAME] [PASSWORD]\n * show_list\n * show_day [DAY_NAME]\n * show_my_res\n"
            " * make_res [DAY_NAME] [SLOT_BEGINNING_TIME]\n * cancel_res [DAY_NAME]\n * quit\n> ").strip()

        if not command:
            continue
        if command.lower() == "quit":
            break
        
        encoded = quote(command) 

        request_lines = [
            f"GET /{encoded} HTTP/1.1",  
            f"Host: {host}"
        ]
        
        if token:
            request_lines.append(f"X-Auth-Token: {token}")
        request_lines.append("")  # end headers
        request_lines.append("")
        request = "\r\n".join(request_lines)

        # TCP connection
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(request.encode())

            # get server response
            response = s.recv(65536).decode()

        print("\n--- Server Response ---")
        print(response)
        print("-----------------------")

        head, _, body = response.partition("\r\n\r\n")
        for line in head.split("\r\n"):
            if line.lower().startswith("set-auth-token:"):
                token = line.split(":", 1)[1].strip()
                print(f"(session token saved)")

if __name__ == "__main__":
    main()