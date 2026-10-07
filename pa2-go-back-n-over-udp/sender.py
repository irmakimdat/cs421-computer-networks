#sender.py
import threading
import socket
import sys
import time

HEADER_SIZE = 2
MAX_DATA_SIZE = 1022 #cause 1024-2 
TARGET_IP = "127.0.0.1"

#globals 
base = 1
next_seq_num = 1
timer_start = 0.0
done = False
total_packets = 0
lock = threading.Lock()

#create and return a packets list
# (send them as packets later) 
def read_file_packets(path):
    pkts = [b""]
    with open(path, "rb") as f:
        while True:
            chunk = f.read(MAX_DATA_SIZE)
            if not chunk:
                break
            pkts.append(chunk)
    return pkts

# works with a seperate thread and 
# waits and reads acks
def ack_listener(sock):
    global base, next_seq_num, timer_start, done, total_packets

    while True:
        try:
            data, addr = sock.recvfrom(1024)
        except socket.timeout:
            if done:
                break
            continue
        except OSError:
            break

        if len(data) >= HEADER_SIZE:
            ack = int.from_bytes(data[:HEADER_SIZE], "big")

            #move sender base when ack arrives
            with lock:
                if ack >= base:
                    base = ack + 1
                    if base == next_seq_num:
                        timer_start = 0.0
                    else:
                        timer_start = time.time()

# main sender logic that sends packets when 
#window is not full
def run_sender(path, port, window_size, timeout_msec):
    global base, next_seq_num, timer_start, done, total_packets
 
    timeout_sec = timeout_msec / 1000.0

    packets = read_file_packets(path)
    total_packets = len(packets) - 1  # -1 here cause packets[0] is not used

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.2)

    t = threading.Thread(target=ack_listener, args=(sock,), daemon=True)
    t.start()

    while True:
        with lock:
            if base > total_packets:
                break

        # send new packets while window allows
        while True:
            with lock:
                if (next_seq_num >= base + window_size) or (next_seq_num > total_packets):
                    break
                s = next_seq_num
                next_seq_num += 1
                if s == base:
                    timer_start = time.time()

            pkt = s.to_bytes(HEADER_SIZE, "big") + packets[s]
            sock.sendto(pkt, (TARGET_IP, port))

        # if timeout resend everything in the window
        with lock:
            b = base
            n = next_seq_num
            if (timer_start != 0.0) and ((time.time() - timer_start) > timeout_sec): 
                timer_start = time.time()

        if (timer_start != 0.0) and ((time.time() - timer_start) > timeout_sec): # timeout
            for s in range(b, n):
                pkt = s.to_bytes(HEADER_SIZE, "big") + packets[s]
                sock.sendto(pkt, (TARGET_IP, port))
        else:
            time.sleep(0.001)

    # termination segment
    sock.sendto((0).to_bytes(HEADER_SIZE, "big"), (TARGET_IP, port))

    done = True
    sock.close()
    t.join(timeout=1.0)

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("use: python3 sender.py <file_path> <receiver_port> <window_size_N> <retransmission_timeout>")
        sys.exit(1)

    run_sender(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
