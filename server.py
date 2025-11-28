from handle_requests import upload_request
import socket
import json
import struct

# Setări server
SERVER_IP = "0.0.0.0"
SERVER_PORT = 5683  # Port standard CoAP
PAYLOAD_MARKER = 0xFF

def parse_coap_header(data):
    """Parsează primii 4 bytes ai headerului CoAP"""
    if len(data) < 4:
        raise ValueError("Pachet prea scurt pentru header CoAP")

    # Despachetăm primii 4 bytes: (Version/Type/TKL, Code, Message ID)
    first_byte, code, msg_id = struct.unpack("!BBH", data[:4])

    version = (first_byte >> 6) & 0x03
    msg_type = (first_byte >> 4) & 0x03
    tkl = first_byte & 0x0F

    header = {
        "version": version,
        "type": msg_type,
        "tkl": tkl,
        "code": code,
        "message_id": msg_id
    }

    return header

def parse_packet(data):
    if PAYLOAD_MARKER in data:
        header_part, payload_part = data.split(bytes([PAYLOAD_MARKER]), 1)
    else:
        header_part, payload_part = data, b""

    header = parse_coap_header(header_part)

    payload = {}
    if payload_part:
        try:
            payload = json.loads(payload_part.decode('utf-8'))
        except json.JSONDecodeError:
            print("[!] Eroare parsare JSON payload")

    return header, payload


def handle_request(header, payload, client_addr, sock):
    """Procesează cererea primită în funcție de codul CoAP"""
    code = header.get("code")
    msg_type=header.get("type")
    msg_id=header.get("message_id")
    
    if code == 1:
        print("download fisier")
    elif code == 2:
        print("upload fisier")
        upload_request(payload,msg_type,msg_id,client_addr, sock)
    elif code == 4:
        print("delete fisier")
    else:
        print("cod necunoscut!")




if __name__ == "__main__":
    nr_cereri=0
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((SERVER_IP, SERVER_PORT))
    print(f"[+] Server ascultă pe {SERVER_IP}:{SERVER_PORT}")

    while nr_cereri<4: #primim un nr de pachete p
        data, client_addr = sock.recvfrom(65535)
        print(f"[>] Pachet primit de la {client_addr}")
        nr_cereri+=1
        header, payload = parse_packet(data)
        if header:
            handle_request(header, payload, client_addr, sock)
