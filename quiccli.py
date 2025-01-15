import asyncio
import json
import logging
import os
import re
import socket

from aioquic.quic.connection import RSA_BIT_STRENGTH, PEER_META, PEER_META_LOCK, resolve_hostname_from_url, create_peer_meta
from aioquic.quic.ccrypto import queue_message, get_compact_key

logger = logging.getLogger(__name__)

def json_serializer(obj):
    return str(obj)

class QuiCCli:
    def __init__(self,
            send_function = None,
            configuration = None,
            urls = None,
            data = None,
            include = None,
            output_dir = None,
            local_port = 0,
            zero_rtt = None,
            is_client=True
        ):
        self.is_client = is_client
        self.send_function = send_function
        self.configuration=configuration
        self.urls=urls
        self.data=data
        self.include=include
        self.output_dir=output_dir
        self.local_port=local_port
        self.zero_rtt=zero_rtt,
        if self.is_client:
            self.host, self.host_ip = resolve_hostname_from_url(self.urls[0])
            if self.host == 'localhost' or self.host_ip == "127.0.0.1":
                self.host_ip = "::1"
            else:
                self.host_ip = "::ffff:" + self.host_ip
            PEER_META_LOCK.acquire(timeout=5)
            peer_meta = create_peer_meta()
            key_bytes = get_compact_key(peer_meta['private_key'])
            open('client-public-key-client.bin', 'wb').write(key_bytes)
            queue_message(self.host_ip, key_bytes, peer_meta['cid_queue'], None, is_public_key=True)
            # We need one final connection to get the last chunk of the server's CID queue so add
            # an extra random CID at the end
            peer_meta['cid_queue'].put(os.urandom(20))
            PEER_META[self.host_ip] = peer_meta
            PEER_META_LOCK.release()
            self.send_message((RSA_BIT_STRENGTH // 128) + 1) # Receive the server public key
                
    
    def send_message(self, count):
        print(f"SENDING {count} REQUESTS")
        send_urls = [self.urls[i % len(self.urls)] for i in range(count)]
        for i, url in enumerate(send_urls):
            print(f"SENDING REQUEST {i+1}/{count}")
            asyncio.run(
                self.send_function(
                    configuration=self.configuration,
                    urls=[url],
                    data=self.data,
                    include=self.include,
                    output_dir=self.output_dir,
                    local_port=self.local_port,
                    zero_rtt=self.zero_rtt,
                )
            )

    def process_message(self, command_input):
        command = command_input[0]
        payload = command_input[1:]
        if self.is_client:
            peer_meta = PEER_META.get(self.host_ip)
        try:
            if command == 'm' or command == 'c':
                if payload and payload[0] == ':':
                    count = queue_message(self.host_ip, (command + payload[1:]).encode('utf8'), peer_meta['cid_queue'], peer_meta['public_key'])
                    if self.is_client:
                        self.send_message(count)
                else:
                    return False
            elif command == 'f':
                if payload and payload[0] == ':':
                    payload_bytes = open(payload[1:], 'rb').read()
                    count = queue_message(self.host_ip, b'f' + payload_bytes, peer_meta['cid_queue'], peer_meta['public_key'])
                    if self.is_client:
                        self.send_message(count)
                else:
                    return False
            elif command == 'k':
                payload = b'k'
                count = queue_message(self.host_ip, payload, peer_meta['cid_queue'], peer_meta['public_key'])
                if self.is_client:
                    self.send_message(count)
            elif command == 'q':
                os._exit(0)
            else:
                print(f"Unknown command '{command}'. Enter 'm', 'c', 'f', or 'q'.")
        except ValueError as e:
            logger.warning("Error queuing message for ip %s", self.host_ip)
            logger.warning("Peer meta dump:\n%s", json.dumps(PEER_META, default=json_serializer, indent=True))
        return True


    def run_cli(self):
        print("Welcome to the QuiCC console.")
        print("Enter 'm:[MESSAGE]' to send a message.")
        print("Enter 'c:[COMMAND]' to send a remote command.")
        print("Enter 'f:[FILE]' to send a file.")
        print("Enter 'k' to send a keepalive message to recieve responses.")
        print("Enter 'q' to quit.")
        
        while True:
            command_input = input("Enter your command: ").strip().lower()
            if len(command_input) >= 1:
                self.process_message(command_input)
            else:
                print("Invalid format. Use [COMMAND_CHAR]:[HOST]:[PAYLOAD]")
