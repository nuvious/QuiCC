import asyncio
import ssl
import sys
from aioquic.asyncio import connect
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import HandshakeCompleted, StreamDataReceived

class EchoClientProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stream_id = None

    def quic_event_received(self, event):
        if isinstance(event, HandshakeCompleted):
            # Send initial data when handshake is complete
            self.stream_id = self._quic.get_next_available_stream_id()
            asyncio.ensure_future(self.send_input())
        elif isinstance(event, StreamDataReceived):
            # Print the received data
            print(event.data.decode(), end="")
            if event.end_stream:
                asyncio.get_event_loop().stop()

    async def send_input(self):
        loop = asyncio.get_event_loop()
        while True:
            line = await loop.run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            self._quic.send_stream_data(self.stream_id, line.encode())

async def main():
    # Create QUIC configuration
    configuration = QuicConfiguration(is_client=True)
    configuration.verify_mode = ssl.CERT_NONE  # Don't verify server certificate

    # Connect to the QUIC server
    async with connect(
        "localhost",
        4433,
        configuration=configuration,
        create_protocol=EchoClientProtocol
    ) as protocol:
        # Wait for the connection to close
        await protocol.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
