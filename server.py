import tornado.websocket
import tornado.httpserver
import tornado.ioloop
import tornado.web
import os
import csv

CSV_FILE = "cards.csv"
PORT = 80
Listeners = []

HTML = """
<!DOCTYPE>
<html>
<head>
    <title>Credentials Scanned</title>
    <style>
        #credentials {
            font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
            border-collapse: collapse;
            width: 100%%;
        }

        #credentials td, #credentials th {
            border: 1px solid #ddd;
            padding: 8px;
        }

        #credentials tr:nth-child(even){background-color: #f2f2f2;}

        #credentials tr:hover {background-color: #ddd;}

        #credentials th {
            padding-top: 12px;
            padding-bottom: 12px;
            text-align: left;
            background-color: #4CAF50;
            color: white;
        }
    </style>
    </head>
<body>
<div id="links">
    <a href="./cards.csv">Download CSV</a>&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="#" onclick="confirm('Are you sure you want to clear cards.csv?')?document.location.href='./clearcsv':null;">Clear CSV</a>&nbsp;&nbsp;&nbsp;&nbsp;
</div>
<div id="file">
    <table id=credentials>
        <tr>
            <th>ID</th>
            <th>Bit Length</th>
            <th>Wiegand Binary</th>
            <th>Wiegand Hex Data</th>
            <th>iCLASS Standard Encrypted Hex Data</th>
            <th>Facility Code</th>
            <th>Card Number</th>
            <th>Card Number without Facility Code</th>
        </tr>
    </table>
</div>

    <script type="text/javascript" charset="utf-8">
        var credential;
        function parseCredential(line) {
            credential = line.split(",");
            write_data(credential)
        }

        function write_data(credential) {
            var id = credential[0];
            var bits = credential[1];
            var wiegand_binary = credential[2];
            var wiegand_hex = credential[3];
            var iclass_std_enc_hex = credential[4];
            var fac_code = credential[5];
            var card_num = credential[6];
            var card_num_no_fac = credential[7];
            var table = document.getElementById("credentials");
            var row = table.insertRow(1);
            var cell01 = row.insertCell(-1);
            var cell02 = row.insertCell(-1);
            var cell03 = row.insertCell(-1);
            var cell04 = row.insertCell(-1);
            var cell05 = row.insertCell(-1);
            var cell06 = row.insertCell(-1);
            var cell07 = row.insertCell(-1);
            var cell08 = row.insertCell(-1);
            cell01.innerHTML = id;
            cell02.innerHTML = bits;
            cell03.innerHTML = wiegand_binary;
            cell04.innerHTML = wiegand_hex;
            cell05.innerHTML = iclass_std_enc_hex;
            cell06.innerHTML = fac_code;
            cell07.innerHTML = card_num;
            cell08.innerHTML = card_num_no_fac;
        }
        if ("MozWebSocket" in window) {
            WebSocket = MozWebSocket;
        }
        if (WebSocket) {
            var ws = new WebSocket("ws://%s/ws");
            ws.onopen = function() {};
            ws.onmessage = function (evt) {
                parseCredential(evt.data);
            };
            ws.onclose = function() {};
        } else {
            alert("WebSocket not supported");
        }
    </script>
    </table>
</body>
</html>
"""

cards_file = open(CSV_FILE)
cards_file.seek(os.path.getsize(CSV_FILE))

def check_file():
    position = cards_file.tell()
    line = cards_file.readline()
    if not line:
        cards_file.seek(position)
    else:
        print "File changed detected!"
        for l in Listeners:
            l.write_message(line)

class CredentialHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        print 'new connection'
        Listeners.append(self)
        #self.write_message("Connected!")
        # Initially print out contents of file
        with open(CSV_FILE) as cards_file:
            next(cards_file)
            for line in cards_file:
                print "Sending message!"
                self.write_message(line)

    def on_message(self, message):
        pass

    def on_close(self):
        print 'connection closed'
        Listeners.remove(self)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(HTML % (self.request.host))

class CSVDownloadHandler(tornado.web.RequestHandler):
    def get(self):
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=' + CSV_FILE)
        # Print out contents of file
        with open(CSV_FILE) as cards_file:
            for line in cards_file:
                self.write(line)
        self.finish()

class ClearCSV(tornado.web.RequestHandler):
    def get(self):
        with open(CSV_FILE, 'w') as csv_file:
            fieldnames = ['id', 'bit_length', 'wiegand_binary', 'wiegand_hex', 'iclass_std_enc_hex', 'fac_code', 'card_num',
                          'card_num_no_fac']
            csvwriter = csv.DictWriter(csv_file, lineterminator='\n', fieldnames=fieldnames)
            csvwriter.writeheader()
        cards_file.seek(os.path.getsize(CSV_FILE))
        self.redirect('/')

application = tornado.web.Application([
    (r'/ws', CredentialHandler),
    (r'/', IndexHandler),
    (r'/clearcsv', ClearCSV),
    (r'/cards.csv', CSVDownloadHandler)
])

http_server = tornado.httpserver.HTTPServer(application)
http_server.listen(PORT)
tornado.ioloop.PeriodicCallback(check_file, 500).start()
tornado.ioloop.IOLoop.instance().start()
