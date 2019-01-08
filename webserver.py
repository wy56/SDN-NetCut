#!/usr/bin/python
import SimpleHTTPServer
import SocketServer
import logging
import cgi
import sys
import sqlite3
from database import database
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer


if len(sys.argv) > 2:
    PORT = int(sys.argv[2])
    I = sys.argv[1]
elif len(sys.argv) > 1:
    PORT = int(sys.argv[1])
    I = ""
else:
    PORT = 8080
    I = ""


class ServerHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

    def do_GET(self):
        try:
            logging.warning("======= GET STARTED =======")
            logging.warning(self.headers)
            #SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            data = open('./index.html', 'r').read()
            table = database().db_getHttptable()
            data = data.replace("##########", table)
            self.wfile.write(data)
        except Exception, e:
            print "Failed to read file ",str(e)
        
    def do_POST(self):
        logging.warning("======= POST STARTED =======")
        logging.warning(self.headers)
        form = cgi.FieldStorage(
        fp=self.rfile,
        headers=self.headers,
        environ={'REQUEST_METHOD':'POST','CONTENT_TYPE':self.headers['Content-Type'],})
        logging.warning("======= POST VALUES =======")
        address = ""
        access = ""
        for key in form.keys():
            variable = str(key)
            value = str(form.getvalue(variable))
            if variable == "address" :
                address = value
            if variable == "access" :
                access = value
        if address != "" :
            database().db_insert(address,access)
        self.do_GET()



Handler = ServerHandler
httpd = SocketServer.TCPServer(("", PORT), Handler)
print "serving at port", PORT
httpd.serve_forever()





