import socket
import struct
import secrets
import sys
import time
from typing import Optional


def eprint(s: str):
  print("stun_client:", s, file=sys.stderr)


def simple_stun(
    server,
    server_port,
    client_port=0,
    retries=3,
    timeout=2,
) -> Optional[tuple[str, int]]:
  msg_type = 0x0001
  msg_len = 0
  magic = 0x2112A442
  txn_id = secrets.token_bytes(12)
  request = struct.pack('!HHI12s', msg_type, msg_len, magic, txn_id)

  for attempt in range(1, retries + 1):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    if client_port != 0:
      try:
        sock.bind(("", client_port))
      except OSError as e:
        eprint(f"could not bind to port {client_port}: {e}")
        continue
    sock.settimeout(timeout)

    try:
      sock.sendto(request, (server, server_port))
      data, _ = sock.recvfrom(2048)
      sock.close()

      offset = 20
      while offset < len(data) - 4:
        attr_type, attr_len = struct.unpack('!HH', data[offset:offset+4])
        if attr_type == 0x0020 and attr_len >= 8:
          attr_data = data[offset+4:offset+4+attr_len]
          xor_port = struct.unpack('!H', attr_data[2:4])[0]
          xor_ip = struct.unpack('!I', attr_data[4:8])[0]

          port_resp = xor_port ^ (magic >> 16)
          ip_resp = socket.inet_ntoa(struct.pack('!I', xor_ip ^ magic))
          return ip_resp, port_resp

        offset += 4 + attr_len + ((4 - (attr_len % 4)) % 4)

      eprint("XOR-MAPPED-ADDRESS attribute not found in response")
      return None

    except socket.timeout:
      eprint(
          f"attempt {attempt} timed out on {server}:{server_port}, retrying...")
    except Exception as e:
      eprint(f"error on attempt {attempt} with {server}:{server_port}: {e}")
      break
    finally:
      sock.close()

    time.sleep(0.5)

  eprint("STUN request failed on all addresses after retries")
  return None


if __name__ == '__main__':
  import argparse

  parser = argparse.ArgumentParser()
  parser.add_argument("--server", action="extend", nargs=1)
  parser.add_argument("--port")
  args = parser.parse_args()

  default_servers = [("stun.cloudflare.com", 3478),
                     ('stun.l.google.com', 19302)]
  servers = default_servers if args.server is None else [(server, int(server_port_str)) for [server, server_port_str]
                                                         in map(lambda x: x.rsplit(":", 1), args.server)]
  port = 0 if args.port is None else int(args.port)

  for (server, server_port) in servers:
    eprint(f"trying {server}:{server_port}")
    result = simple_stun(server, server_port, client_port=port)
    if result is not None:
      ip, port = result
      print(f"{ip}:{port}")
      exit(0)
  exit(1)
