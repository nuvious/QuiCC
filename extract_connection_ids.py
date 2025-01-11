import pyshark

def get_unique_connection_ids(pcap_file):
    connection_ids = set()

    with pyshark.FileCapture(pcap_file, display_filter='quic') as capture:
        for packet in capture:
            if 'quic' in packet:
                quic_layer = packet['quic']
                
                if hasattr(quic_layer, 'dcid'):
                    connection_id = quic_layer.dcid
                    connection_ids.add(connection_id)
    return connection_ids

if __name__ == "__main__":
    import sys
    pcap_file = sys.argv[1]
    unique_connection_ids = get_unique_connection_ids(pcap_file)
    print(len(unique_connection_ids))
    sizes = set()
    for cid in unique_connection_ids:
        lcid = len(cid.replace(":",""))
        if lcid not in sizes:
            sizes.add(lcid)
    print(sizes)
