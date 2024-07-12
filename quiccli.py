import asyncio
import os
import re
import socket

from aioquic.quic.connection import RSA_BIT_STRENGTH, PEER_META, PEER_META_LOCK, resolve_hostname_from_url, create_peer_meta
from aioquic.quic.ccrypto import queue_message, get_compact_key


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
                self.host_ip = "::ffff:" + self.host_ip
            PEER_META_LOCK.acquire(timeout=5)
            peer_meta = create_peer_meta()
            key_bytes = get_compact_key(peer_meta['private_key'])
            open('client-public-key-client.bin', 'wb').write(key_bytes)
            queue_message(self.host_ip, key_bytes, peer_meta['cid_queue'], None, is_public_key=True)
            peer_meta['cid_queue'].put(os.urandom(8))
            PEER_META[self.host_ip] = peer_meta
            PEER_META_LOCK.release()
            self.send_message((RSA_BIT_STRENGTH // (8*8)) + 1) # Receive the server public key
                
    
    def send_message(self, count):
        print(f"SENDING {count} REQUESTS")
        send_urls = [self.urls[i % len(self.urls)] for i in range(count)]
        for i, url in enumerate(send_urls):
            print(f"SENDING REQUEST {i}/{count}")
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

    def process_message(self, command, payload):
        peer_meta = PEER_META.get(self.host_ip)
        if command == 'm' or command == 'c':
            count = queue_message(self.host_ip, (command + payload).encode('utf8'), peer_meta['cid_queue'], peer_meta['public_key'])
            if self.is_client:
                self.send_message(count)
        elif command == 'f':
            payload_bytes = open(payload, 'rb').read()
            count = queue_message(self.host_ip, b'f' + payload_bytes, peer_meta['cid_queue'], peer_meta['public_key'])
            if self.is_client:
                self.send_message(count)
        elif command == 'k':
            payload = b'k'
            count = queue_message(self.host_ip, (command + payload).encode('utf8'), peer_meta['cid_queue'], peer_meta['public_key'])
            if self.is_client:
                self.send_message(count)
        else:
            print(f"Unknown command '{command}'. Enter 'm', 'c', 'f', or 'q'.")
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
            command_input.split(":")
            if len(command_input) < 2:
                if command_input == 'q':
                    os._exit(0)
                print("Invalid format. Use [COMMAND_CHAR]:[HOST]:[PAYLOAD]")
            command = command_input[0]
            payload = ':'.join(command_input[1:]) # Allows support for : in commands
            self.process_message(command, payload)
