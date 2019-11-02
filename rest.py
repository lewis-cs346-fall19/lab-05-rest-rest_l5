#!/usr/bin/python3

import re
import cgi
import cgitb
import os
import simplejson as json
import MySQLdb
import passwords

#cgitb.enable()

conn = MySQLdb.connect(host   = passwords.SQL_HOST,
                       user   = passwords.SQL_USER,
                       passwd = passwords.SQL_PASSWD,
                       db     = "restlab")

url = "ec2-3-83-252-90.compute-1.amazonaws.com/cgi-bin/rest.py/ff/"
pattern = re.compile("/ff/\d+")

form = cgi.FieldStorage()

if 'PATH_INFO' in os.environ:
    path_info = os.environ['PATH_INFO']
else:
    path_info = ""


def index():
    print("Content-type: text/html")
    print("Status: 200 OK")
    print("""
    <html>
    <body>
    <b><font size=+3> Fantasy Football (REST) Website </font></b>
    <p>
    <a href="rest.py/ff">Players</a> (GET)
    <br>
    <a href="rest.py/new_player">Add Player</a> (POST to Players)
    <hr>
    </body></html>
    """)


def newPlayer():
    print("Content-type: text/html")
    print("Status: 200 OK")
    print("""
    <html>
    <body>
    <form action = "add_player" method = POST>
    <p> Name: <br><input type="text" name="name" maxlength="30"> <br>
    <p> Position: <br><input type="text" name="pos" maxlength="2"> <br>
    <p> Week: <br><input type="number" name="week" min="0" max="17"> <br>
    <p> Points: <br><input type="number" name="pts" min="-50" max = "200" step="0.1"> <br><br>
    <input type="submit" value="Submit">
    </form>
    </body></html>
    """)


def addPlayer():
    main = "http://ec2-3-83-252-90.compute-1.amazonaws.com/cgi-bin/rest.py"

    name = form.getvalue("name")
    pos  = form.getvalue("pos")
    week = form.getvalue("week")
    pts  = form.getvalue("pts")

    if (name is None or pos is None or week is None or pts is None):
        print("Content-type: text/html")
        print("Status: 200 OK")
        print("""
        <html>
        <body>
        <p>Error: <a href="%s"> Return to main page</a> </p>
        </body>
        </html>
        """ % main)
    else:
        query = ("insert into fantasyplayers (name, position, week, points) \
                values (\"%s\", \"%s\", %s, %s)" % (name, pos, week, pts))
        cursor = conn.cursor()
        cursor.execute(query)
        new_id = cursor.lastrowid
        cursor.close()
        conn.commit()
        conn.close()
        reurl = "ff/" + str(new_id)
        print("Status: 302 Redirect")
        print("Location: %s" % reurl)
        print()


def gets():
    json_id = path_info.strip('/').split('/')[-1]

    if json_id.isdigit():
        cursor = conn.cursor()
        cursor.execute("select * from fantasyplayers where id = %s" % json_id)
        result = [dict((cursor.description[i][0], value) \
                  for i, value in enumerate(row)) for row in cursor.fetchall()]
        cursor.close()
        result[0]["url"] = url + str(result[0]["id"])
        print("Content-type: application/json")
        print("Status: 200 OK\n")
        print(json.dumps(result, indent=2))
    else:
        cursor = conn.cursor()
        cursor.execute("select * from fantasyplayers")
        results = [dict((cursor.description[i][0], value) \
                   for i, value in enumerate(row)) for row in cursor.fetchall()]
        cursor.close()
        for item in results:
            item["url"] = url + str(item["id"])
        results_json = json.dumps(results, indent=2)
        print("Content-type: application/json")
        print("Status: 200 OK\n")
        print(results_json)


def test():
    print("Content-type: text/html")
    print("Status: 200 OK")
    print("""
    <html>
    <head><title> REST lab </title></head>
    """)
    print("<p> %s\n </p>" % path_info.strip("/"))
    print("</body>")
    print("</hmtl>")


def test_json():
    x = [1,2,3]
    x_json = json.dumps(x, indent=2)
    print("Content-type: application/json")
    print("Status: 200 OK\n")
    print(x_json)


if path_info.strip("/") == "test":
    test()
elif path_info.strip("/") == "json_test":
    test_json()
elif path_info.strip("/") == "ff":
    gets()
elif pattern.match(path_info) != None:
    gets()
elif path_info == "":
    index()
elif path_info.strip("/") == "new_player":
    newPlayer()
elif path_info.strip("/") == "add_player":
    addPlayer()
else:
    print("Status: 302 Redirect")
    print("Location: redirect.py\n")
