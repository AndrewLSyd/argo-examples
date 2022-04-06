"""
COMP9331 Lab 3
z3330164
Andrew Lau

Usage:
python3 WebServer.py [Port number, defaults to 5000]

Note that I have used the below reference as a starting point:
https://bhch.github.io/posts/2017/11/writing-an-http-server-from-scratch/
"""
import socket
import os
import mimetypes
import datetime
import sys

class TCPServer:
    """
    Basic TCP server upon which HTTP servers will build upon via inheritence
    This basic TCP server just echoes back any received messages
    """
    def __init__(self, host='127.0.0.1', port=5000):  # default to localhost and port 5000
        self.host = host
        self.port = port

    def start(self):
        # initiating socket object
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # setting socket host and port
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.bind((self.host, self.port))
        my_socket.listen(5)

        print("*" * 50, "\nNow listening at host", my_socket.getsockname()[0], 'and port', my_socket.getsockname()[1])

        while True:
            connection, address = my_socket.accept()  # connection is a new socket object
            print("*" * 50, "\nTCP connection established")
            print("\ttime:", str(datetime.datetime.now()))
            print("\thost:", address[0])
            print("\tport:", address[1])

            data_received = connection.recv(4096)  # buffer size 4096

            # request handling here, subsequent classes will implement more sophisticated HTTP GET request handling
            response = self.handle_request(data_received)

            # send response back
            connection.sendall(response)

            # close connection once done
            connection.close()

    def handle_request(self, data_received):
        """
        basic request handling (echo)
        this method is overwritten in the HTTPServer class' handle_request
        """
        print("Sending the below message to client:")
        print(data_received.decode())
        return data_received

class HTTPRequest:
    """
    Need to be able to parse HTTP requests like
        GET /image.png HTTP/1.1
    """
    def __init__(self, data_received):

        self.HTTP_method = None  # eg GET
        self.URL = None  # eg /index.html
        self.HTTP_version = None # eg HTTP/1.1

        # immediately parse HTTP request upon instantiation
        self.parse(data_received)

    def parse(self, data_received):
        lines = data_received.split(b"\r\n")  # each line in the HTTP request is delimited by a carriage return/newline

        request_line = lines[0]

        words = request_line.split(b" ")

        self.HTTP_method = words[0].decode() # bytes to string

        # if a URI is provided (rather than implicit request for index.html)
        if len(words) > 1:
            self.uri = words[1].decode() # call decode to convert bytes to str

        elif len(words) > 2:
            self.HTTP_version = words[2]

class HTTPServer(TCPServer):
    """
    HTTP Server class built on top of TCP class
    """
    def __init__(self, host_HTTP='127.0.0.1', port_HTTP=5000):
        super(HTTPServer, self).__init__(host=host_HTTP, port=port_HTTP)  # inherit from super class
        self.headers = {'Server': 'COMP9331Server', 'Content-Type': 'text/html'}  # header info
        self.status_codes = {200: 'OK', 204:'No Content', 404: 'Not Found', 501: 'Not Implemented'}  # HTTP status codes

    def handle_request(self, data_received):
        request = HTTPRequest(data_received)

        print('Looking for request.HTTP_method', request.HTTP_method)

        try:
            handler = getattr(self, f'handle_{request.HTTP_method}')
        except AttributeError:  # we don't have a handler for that method
            print(request.HTTP_method, "not found, 501 error")
            handler = self.HTTP_501_handler

        print("Using handler", handler)
        response = handler(request)
        print("Sending response", response[:500])
        return response

    def HTTP_501_handler(self, request):
        """
        When the HTTP method hasn't been implemented
        """
        response_line = self.response_line(status_code=501)

        response_headers = self.response_headers()

        blank_line = b"\r\n"

        response_body = b"<marquee>501 Not Implemented</marquee>\nSorry, this HTTP method has not been implemented"

        return b"".join([response_line, response_headers, blank_line, response_body])

    def handle_GET(self, request):
        """
        HTTP GET request method
        """
        # strip forward slash to get the filename the client is trying to GET
        filename = request.uri.strip('/')

        response_headers = self.response_headers()
        response_body = b""
        blank_line = b"\r\n"

        # handle GET favicon.ico
        if filename.endswith('favicon.ico'):
            response_line = self.response_line(status_code=204)

        elif os.path.exists(filename):  # see if that file exists in our directory
            response_line = self.response_line(status_code=200)  # if we can find it, all good send back a 200

            # guess a file's MIME type
            content_type = mimetypes.guess_type(filename)[0]

            # if guess failed (returns none, then set to TEXT HTML)
            if not content_type:
                content_type = 'text/html'

            extra_headers = {'Content-Type': content_type}
            response_headers = self.response_headers(extra_headers)  # add context type as an extra header

            with open(filename, 'rb') as f:
                response_body = f.read()
        else:
            response_line = self.response_line(status_code=404)
            
            response_body = f"<marquee>404 Not Found</marquee>\nSorry, we couldn't find {filename} :("
            response_body = response_body.encode()

        # concat the bytes and return the response
        return b"".join([response_line, response_headers, blank_line, response_body])


    def response_line(self, status_code):
        """
        Response line with HTTP/1.1 and the mapped status code and reason"""
        reason = self.status_codes[status_code]
        line = "HTTP/1.1 %s %s\r\n" % (status_code, reason)

        return line.encode() # call encode to convert str to bytes

    def response_headers(self, extra_headers=None):
        """
        Generates header line of HTTP response
        """
        headers_copy = self.headers.copy() # make a local copy of headers

        if extra_headers:
            headers_copy.update(extra_headers)

        headers = ""

        for h in headers_copy:
            headers += "%s: %s\r\n" % (h, headers_copy[h])

        return headers.encode() # call encode to convert str to bytes
      
if __name__ == '__main__':
    # allow command line arguments, otherwise take default port as 5000
    if len(sys.argv) == 2:
        server_port = int(sys.argv[1])
    else:
        server_port = 5000  #change this port number if required

    server = HTTPServer(port_HTTP=server_port)
    # server = TCPServer()
    server.start()
