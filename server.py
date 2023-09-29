#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()

        #decode the data from bytes to string
        request_str=self.data.decode('utf-8')
        #split the request string into lines so it can be process parts by part
        request_lines=request_str.split('\n')

        # Extract the HTTP method and requested URL
        first_line=request_lines[0].strip().split()
        http_method=first_line[0] #this is the GET/POST
        requested_url=first_line[1] # path of the source

        if not self.check_http_method(http_method):
            return 
        #Append a trailing slash to the requested URL if it doesn't have one
        if not requested_url.endswith('/'):
            requested_url += '/'

            # Redirect to the new URL using a 301 status code
            self.request.sendall(
                bytearray(f"HTTP/1.1 301 Moved Permanently\r\nLocation: {requested_url}\r\n\r\n", 'utf-8')
            )
            return                       

        #create the path
        absolute_path = self.construct_absolute_path(requested_url)

        
        if absolute_path is None:
            # The requested URL contains "..", so we've already sent a 404 response
            return

        # Check if the requested resource exists
        if os.path.exists(absolute_path):
            # If it's a directory, look for an "index.html" file
            if os.path.isdir(absolute_path):
                index_file_path = os.path.join(absolute_path, "index.html")
                if os.path.exists(index_file_path):
                    # Serve the "index.html" file if it exists
                    self.serve_file(index_file_path)
                else:
                    # Set the response status code to 404 Not Found if "index.html" doesn't exist
                    self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\n\r\n", 'utf-8'))
            else:
                # If it's a file, serve it
                self.serve_file(absolute_path)
        else:
            # If the resource doesn't exist, send a 404 Not Found response
            self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\n\r\n", 'utf-8'))
 
    def serve_file(self, file_path):
        # Determine the content type based on the file extension
        content_type = "text/plain"
        if file_path.endswith(".html"):
            content_type = "text/html"
        elif file_path.endswith(".css"):
            content_type = "text/css"
        
        with open(file_path, 'rb') as file:
            file_content = file.read()
        
        # Create HTTP response headers with the appropriate fields
        headers = (
            f"HTTP/1.1 200 OK\r\n"
            f"Content-Length: {len(file_content)}\r\n"
            f"Content-Type: {content_type}\r\n"
            f"Connection: close\r\n\r\n"
        )
        response = headers.encode('utf-8') + file_content
        self.request.sendall(response)
    
    def construct_absolute_path(self, requested_url):
        # Define the base directory for your web server
        base_directory="www"
        # Check for ".." (parent directory references) in the requested URL
        if ".." in requested_url:
            # Respond with a 404 Not Found status code if ".." is detected
            self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\n\r\n", 'utf-8'))
            return None
        #create a path so OS can look up
        absolute_path = os.path.join(base_directory, requested_url.lstrip('/'))
        #Normalized the path 
        absolute_path = os.path.normpath(absolute_path)
        
        

        return absolute_path


    def check_http_method(self, http_method):
        # If the HTTP method is not GET, set the response status code to 405 Method Not Allowed
        if http_method!='GET':
            self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\r\n\r\n", 'utf-8'))
            return False
        return True

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
