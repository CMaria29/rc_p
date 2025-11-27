import os
import struct
import json
PAYLOAD_MARKER = 0xFF

def build_and_send_acknowledgement(sock, client_addr, msg_id, new_payload ,new_code = 69):
    """
    Trimite un mesaj CoAP de tip ACK (type = 2) către clientul care a trimis un CON.
    
    sock        -> socket-ul UDP deja deschis
    client_addr -> (ip, port) al clientului
    msg_id      -> Message ID al cererii originale (trebuie să fie același!)
    info        -> mesaj text/JSON trimis în payload (opțional)
    """

    # Header CoAP 
    version = 1
    msg_type = 2       # ACK
    tkl = 0
    code = new_code       
    first_byte = (version << 6) | (msg_type << 4) | tkl

    header = struct.pack("!BBH", first_byte, code, msg_id)

    # Payload JSON 
    payload = new_payload

    # Pachet final
    packet = header + bytes([PAYLOAD_MARKER]) + payload

    # Trimitem pachetul 
    sock.sendto(packet, client_addr)
    print(f"[<] Trimis ACK către {client_addr} (msg_id={msg_id}, code={code})")



    
def upload_request(payload,msg_type,msg_id,client_addr, sock):
    if(payload):
        file_path = payload.get("path")
        content = payload.get("content")

        if not file_path or content is None:
            print( "Trimit pachet eroare: payload incomplet")

        parts = file_path.split("/")

        if parts[0] != "storage":
            if msg_type==0:
                ack_payload=json.dumps({ "status": "error","message": "Unable to execute"}).encode("utf-8")
                build_and_send_acknowledgement(sock,client_addr,msg_id,ack_payload)  # am lasat codul de raspuns content pentru moment desi aici este vorba despre o eroare
            return
    
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        # scriu in fisier
        with open(file_path, "w") as f:
            f.write(content)
        ack_payload=json.dumps({ "status": "created","path": file_path,"size": os.path.getsize(file_path)}).encode("utf-8")
        build_and_send_acknowledgement(sock,client_addr,msg_id,ack_payload)
        print(f"Fișierul a fost creat în {file_path}")
    else:
        print("Trimit pachet eroare: la acest tip de request e necesar un payload!")