import asyncio
import ssl
from aioquic.asyncio import connect, serve
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import HandshakeCompleted, StreamDataReceived

class EchoServerProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def quic_event_received(self, event):
        if isinstance(event, HandshakeCompleted):
            print("Handshake completed!")
        elif isinstance(event, StreamDataReceived):
            # Echo the data back
            self._quic.send_stream_data(event.stream_id, event.data)
            self._quic.send_stream_data(event.stream_id, b"", end_stream=True)

async def main():
    # Create QUIC configuration
    configuration = QuicConfiguration(is_client=False)
    configuration.load_cert_chain(certfile="cert.pem", keyfile="key.pem")

    # Start the QUIC server
    await serve(
        host="localhost",
        port=4433,
        configuration=configuration,
        create_protocol=EchoServerProtocol
    )

    # Keep the server running
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
