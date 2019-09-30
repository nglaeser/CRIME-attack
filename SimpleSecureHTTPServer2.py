import socket, ssl

HOST, PORT, CERT, KEY = 'localhost', 443, '/Users/noemi/Documents/UMD/fall19/CMSC818O-Security/attack/cert.pem', '/Users/noemi/Documents/UMD/fall19/CMSC818O-Security/attack/key.pem'

def handle(conn):
  print(conn.recv())
  conn.write(b'HTTP/1.1 200 OK\n\n%s' % conn.getpeername()[0].encode())

def main():
  sock = socket.socket()
  sock.bind((HOST, PORT))
  sock.listen(5)
  context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
  context.load_cert_chain(keyfile=KEY, certfile=CERT)  # 1. key, 2. cert, 3. intermediates
  #print("context options: {} {}".format(context.options, bin(context.options)))
  #context.options |= ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1  # optional
  #print("context options: {} {}".format(context.options, bin(context.options)))
  context.options &= ~ssl.OP_NO_COMPRESSION
  print("context options: {} {}".format(context.options, bin(context.options)))
  context.set_ciphers('EECDH+AESGCM:EDH+AESGCM:AES256+EECDH:AES256+EDH')
  while True:
    conn = None
    ssock, addr = sock.accept()
    try:
      conn = context.wrap_socket(ssock, server_side=True)
      handle(conn)
    except ssl.SSLError as e:
      print(e)
    finally:
      if conn:
        conn.close()
if __name__ == '__main__':
  main()
