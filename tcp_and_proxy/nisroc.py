#!/usr/bin/python -u

# $Id: sslclient.py 143 2010-08-20 09:15:53Z m.lukaszuk $

from fcntl import fcntl,F_SETFL
from OpenSSL import SSL
from os import O_NONBLOCK,fork
from select import select
import socket
import sys

def verifycallback(a1,a2,a3,a4,a5):
  return 1 

# main data exchnage function
def exchange(s):

  # input:
  # s - socket object
  # c - second socket object
  # return:
  # nothing :)
  
  # setting every descriptor to be non blocking
  #fcntl(s, F_SETFL, O_NONBLOCK)
  fcntl(0, F_SETFL, O_NONBLOCK)

  s_recv = s.recv
  s_send = s.send
  c_recv = sys.stdin.read
  c_send = sys.stdout.write

  while 1:
    toread,[],[] = select([0,s],[],[],30)
    [],towrite,[] = select([],[1,s],[],30)

    if 1 in towrite and s in toread:
      try:
        data = s_recv(4096)
      except SSL.WantReadError:
        data = ''
      except SSL.SysCallError:
        s.sock_shutdown(0)
        break

      if len(data) > 0:
        c_send(data)

    elif 0 in toread and s in towrite:

      data = c_recv(4096)

      if len(data) == 0:
        s.sock_shutdown(0)
        break
      else:
        s_send(data)


#### main stuff ####
if __name__ == '__main__':


  if len(sys.argv) >= 2:
    host = sys.argv[1]
    port = int(sys.argv[2])

    ctx = SSL.Context(SSL.SSLv3_METHOD)
    #ctx.set_verify(SSL.VERIFY_NONE,verifycallback)
   
    proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy.setsockopt(socket.IPPROTO_TCP, socket.TCP_CORK,1)  
   
    try:
      proxy.connect((host,port))
    except socket.error:
      sys.stderr.write("[-] problem connecting to "+str(host)+":"+str(port)+"\n")
      proxy.close()
      sys.exit()

    sys.stderr.write("[+] connecting to "+str(host)+":"+str(port)+"\n")
    ssl = SSL.Connection(ctx,proxy)
    ssl.setblocking(True)
    ssl.set_connect_state()
    ssl.do_handshake()
    ssl.setblocking(False)
    sys.stderr.write("[+] ssl handshake done\n")

    ssl.send('qwerty')

    try:
      exchange(ssl)
    except KeyboardInterrupt:
      pass

    proxy.close()

  else:
    sys.stderr.write("usage: "+sys.argv[0]+" ip_dest port_dest\n")


