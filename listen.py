import socket

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while 1:
    try:
        client_socket.connect(("localhost", 1599))
        data = raw_input ( "Enter text to be upper-cased, q to quit\n" )
        client_socket.send(data)
        if ( data == 'q' or data == 'Q'):
            client_socket.close()
            break;
        else:        
            data = client_socket.recv(5000)
            print "Your upper cased text:  " , data
        client_socket.close()
    except:
        pass