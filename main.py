import socket
import sys
import select
import ssl
import os


if len(sys.argv) <= 1:
    print('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server')
    # sys.exit(2)
# Create a server socket, bind it to a port and start listening

tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Fill in start.
recv_buffer = 4096
TCP_IP = "localhost"
TCP_PORT = 8888
tcpSerSock.bind((TCP_IP, TCP_PORT))
tcpSerSock.listen(2)
print("Listening on port: ", TCP_PORT)

# Fill in end.


while 1:
    # Start receiving data from the client
    print ('\n\nReady to serve...')
    tcpCliSock, addr = tcpSerSock.accept()  # return address and tcp client socket
    print ('Received a connection from:', addr)
    # fill in start
    message = tcpCliSock.recv(4096)
    # fill in end
    if message == "":
        continue
    print (message)
    # Extract the filename from the given message
    file = message.split()[1]
    filename = file.split('/')[1]
    fileExist = "false"
    filetouse = file
    URL = file[1:]

    # check if file is blocked or not in the list of blocked urls of the server
    getout = 1
    with open('blockedfiles.txt') as f:
        for line in f:
            if URL in line:
                print("BLOCKED")
                getout = 0
                break
            else:
                getout = 1
    if getout == 0:
        break

    try:
        # Check whether the file exist in the cache
        f = open(filetouse[1:], "rb")
        outputdata = f.read()
        fileExist = "true"

        # ProxyServer finds a cache hit and generates a response message
        tcpCliSock.sendall("HTTP/1.0 200 OK\r\n".encode())
        tcpCliSock.sendall("Content-Type:text/html\r\n".encode())
        tcpCliSock.sendall("Content-Type: image/jpeg\r\n".encode())
        # Fill in start.
        tcpCliSock.sendall(outputdata)
        # Fill in end.
        f.close()
        print('Read from cache')

    # Error handling for file not found in cache
    except IOError:
        if fileExist == "false":
            print("hi")
            file = file[1:]
            #hostn = file
            # Create a socket on the proxyserver
            c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            hostname = file.replace("www.", "", 1)
            print(hostname + "=============================================================")
            try:
                # Connect to the socket to port 80
                # Fill in start.
                fileobj = c.makefile('rwb', 0)

                print("/////////////////////////////////////////////////////:")
                if not ("Referer" in message):
                    print("*Connecting to server"+ hostname)
                    # Connect to the socket to port 80
                    c.connect((hostname, 80))
                    print(hostname)
                    con = hostname
                    fileobj.write(b'GET / HTTP/1.0\r\n\r\n')
                else:
                    print("****Get path in referer: " + hostname)
                    c.connect((con, 80))
                    fileobj.write(b'GET /' + hostname + ' HTTP/1.0\r\n\r\n'.encode())
                # Read the response into buffer
                # Fill in start.
                print("done")
                buff = fileobj.read()

                print("done2")
                # Fill in end.

                # Create a new file in the cache for the requested file.
                # Also send the response in the buffer to client socket
                # and the corresponding file in the cache

                tmpFile = open("./" + filename, "wb")
                print(buff)
                for i in range(0, len(buff)):
                    tmpFile.write(buff[i])


                print("done3")
                tcpCliSock.sendall("HTTP/1.0 200 OK\r\n".encode())
                tcpCliSock.sendall("Content-Type:text/html\r\n".encode())
                tcpCliSock.sendall("Content-Type: image/jpeg\r\n".encode())
                print("done4")

                tcpCliSock.sendall(buff)
                #print(buff)
                # Fill in end.
                print('sent to client')
                tmpFile.close()
            except socket.timeout as ti:
                tcpCliSock.send(b'HTTP/1.0 522 Connection timed out\r\n')
                tcpCliSock.send(b'Content-Type:text/html\r\n')
                tcpCliSock.send(b'\r\n')
                tcpCliSock.send(b'<h1>Connection timed out</h1>')
                tcpCliSock.close()
                continue
            except socket.gaierror as e:
                tcpCliSock.send(b'HTTP/1.0 404 not found\r\n')
                tcpCliSock.send(b'Content-Type:text/html\r\n')
                tcpCliSock.send(b'\r\n')
                tcpCliSock.send(b'<h1>website not found</h1>')
                print("Illegal request", e)
                tcpCliSock.close()
                continue
            except IOError:
                print("Illegal request")
            else:
                # HTTP response message for file not found
                # Fill in start.
                tcpCliSock.send(b'HTTP/1.0 404 sendErrorErrorError\r\n')
                tcpCliSock.send(b'Content-Type:text/html\r\n')
                tcpCliSock.send(b'\r\n')


            # except socket.gaierror:
            #     open(error.txt)
            #     tcpCliSock.sendall(file.read)

        else:
            # HTTP response message for file not found
            # Fill in start.
            header = 'HTTP/1.0 404 Not Found\n\n'
            response = '<html>' \
                       '    <h1>' \
                       '        Error   ' \
                       '        404: File' \
                       '        not found  ' \
                       '     </h1>' \
                       '</html>'
            tcpCliSock.send(header.encode() + response.encode())
            # Fill in end.
            # Close the client and the server sockets

        tcpCliSock.close()

    # Fill in start.
tcpSerSock.close()