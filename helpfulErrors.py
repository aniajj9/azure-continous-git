"""
The task:
    1. Login
    2. Go to the /ACCOUNT route, and notice that it displays user id
    3. Open the application tab in the browser inspector (or reach cookies in another way)
    4. Notice that there are 2 cookies present: uid and sid
    5. Notice that uid looks quite random, while the sid is short
    6. Try to change sid value to see what is displayed on the /ACCOUNT
    7. Iterate through sid values (up to 100?), and one of them will return the flag uid (meaningful error)
    8. Change the sid and uid cookies to the ones flag ones
    9. Go to account
    10. Flag is displayed, get the flag
"""

import socketserver
from http.server import *
from random import randint, choice
import string

flag_sid = "19"
flag_uid = "flag-user-754328273"
sessions = {flag_sid: flag_uid}  # TODO: maybe add some more permanent sessions


def generate_uid():
    characters = string.ascii_letters + string.digits
    uid = ''.join(choice(characters) for _ in range(15))
    return uid


def generate_sid():
    sid = str(randint(1, 100))
    while sid in sessions or sid == flag_sid:
        sid = str(randint(1, 100))
    return sid


def parse_cookies(cookie_list):
    return dict(((c.split("=")) for c in cookie_list.split(";"))) \
        if cookie_list else {}


class SessionHandler(BaseHTTPRequestHandler):
    def __init__(self, request: bytes, client_address: tuple[str, int], socket_server: socketserver.BaseServer):
        super().__init__(request, client_address, socket_server)
        self.user = None
        self.cookie = None

    def do_GET(self):
        routes = {
            "/login": self.login,
            "/logout": self.logout,
            "/": self.home,
            "/account": self.account
        }
        self.cookie = None
        sessions[flag_sid] = flag_uid
        try:
            response = 200
            cookies = parse_cookies(self.headers.get("Cookie", ""))
            cookies = {key.replace(" ", ""): value for key, value in cookies.items()}

            if "sid" in cookies and "uid" in cookies:
                if cookies["sid"] in sessions and sessions[cookies["sid"]] == cookies["uid"]:
                    self.user = cookies["uid"]
                else:
                    self.user = False
            else:
                self.user = False
            content = routes[self.path]()
        except:
            response = 404
            content = "Not Found"

        self.send_response(response)
        self.send_header('Content-type', 'text/html')
        if self.cookie:
            self.send_header('Set-Cookie', self.cookie.split(";")[0].strip())
            self.send_header('Set-Cookie', self.cookie.split(";")[1].strip())
        self.end_headers()
        self.wfile.write(bytes(content, "utf-8"))
        return

    def home(self):
        if self.user:
            return """
            Welcome User!<br><br>
            <a href="/login">Login</a> | <a href="/account">Account</a> | <a href="/logout">Logout</a>
            """
        else:
            return """
            Welcome Stranger!!!<br><br>
            <a href="/login">Login</a> | <a href="/account">Account</a> | <a href="/logout">Logout</a>
            """

    def account(self):
        if self.user:
            if self.user == flag_uid:
                return "Grab the flag: CTF{404_fl4g_n0t_fouNd}"
            else:
                return f"""
                            Your user id: {self.user}<br><br>
                            <a href="/login">Login</a> | <a href="/">Home</a> | <a href="/logout">Logout</a>
                            """
        else:
            sid_cookie = self.headers.get("Cookie", "").split("sid=")
            uid_cookie = self.headers.get("Cookie", "").split("uid=")
            if len(sid_cookie) > 1 and len(uid_cookie) > 1:
                sid = sid_cookie[1].split(";")[0].strip()
                uid = uid_cookie[1].split(";")[0].strip()
                if sid in sessions:
                    return f"""ERROR: User with uid: <b>{uid}</b> tried to access session with sid: <b>{sid}</b> belonging to user 
                    with uid <b>{sessions[sid]}</b><br><br>
                            <a href="/login">Login</a> | <a href="/">Home</a> | <a href="/logout">Logout</a>
                            """
                elif len(sid) > 0  and len(uid) > 0:
                    return f"""ERROR: User with uid: <b>{uid}</b> tried to access session with sid: <b>{sid}</b> currently not 
                    belonging to any user<br><br> <a href="/login">Login</a> | <a href="/">Home</a> | <a 
                    href="/logout">Logout</a>"""
                else:
                    return """Access only for logged in users<br><br>
                                        <a href="/login">Login</a> | <a href="/">Home</a> | <a href="/logout">Logout</a>
                                                """
            return """Access only for logged in users<br><br>
                    <a href="/login">Login</a> | <a href="/">Home</a> | <a href="/logout">Logout</a>
                            """

    def login(self):
        if self.user:
            return """Already Logged In <br><br>
                            <a href="/">Home</a> | <a href="/account">Account</a> | <a href="/logout">Logout</a>
                            """
        sid = generate_sid()
        uid = generate_uid()
        self.cookie = f"sid={sid};uid={uid}"
        sessions[sid] = uid
        return """Logged In <br><br>
                            <a href="/">Home</a> | <a href="/account">Account</a> | <a href="/logout">Logout</a>
                            """

    def logout(self):
        if not self.user:
            return """Can't Log Out: No User Logged In <br><br>
                            <a href="/">Home</a> | <a href="/account">Account</a> | <a href="/login">Login</a>
                            """
        self.cookie = "sid=;uid="
        keys_to_delete = []
        for key in sessions:
            if sessions.get(key) == self.user:
                keys_to_delete.append(key)
        for key in keys_to_delete:
            del sessions[key]
        return """Logged Out <br><br>
                            <a href="/">Home</a> | <a href="/account">Account</a> | <a href="/login">Login</a>
                            """


address = ('', 8000)
handler = SessionHandler
server = HTTPServer(address, handler)

server.serve_forever()
