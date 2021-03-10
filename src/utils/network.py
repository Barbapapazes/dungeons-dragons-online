"""Utils functions for network"""

import socket


def get_ip():
    """Get default ip used by the computer to establish a LAN Network

    Returns:
        `str` : Default IP or '127.0.0.1' if an error occurs
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # try to connect but no need to establish a connection (works in LAN)
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP


def enqueue_output(out, queue_line):
    """Queued the first line from stdout in the queue passed in parameter

    Args:
        out (int): file descriptor where the function will read
        queue_line (queue.Queue()): FIFO queue
    """
    for line in iter(out.readline, b""):
        queue_line.put(line)


def check_message(msg: str):
    msg = msg.split(" ")
    if len(msg) != 3:
        raise ValueError
    return 0
