import os
import sys
import uuid
import urllib.parse
import http.server
import socketserver
from http import cookies

# ==============================================================================
# CONFIGURATION
# ==============================================================================
PORT = 8080
USERNAME = "admin"
PASSWORD = "durianx2026"  # Change your password here

# Directory to serve (Services/Reports folder)
SERVE_DIR = os.path.dirname(os.path.abspath(__file__))

# Active session tokens (in-memory)
ACTIVE_SESSIONS = set()
# Default persistent token for convenience across server restarts
DEFAULT_TOKEN = "durianx_auth_token_secret_998877"
ACTIVE_SESSIONS.add(DEFAULT_TOKEN)


# ==============================================================================
# HTML LOGIN PAGE TEMPLATE (Glassmorphism & Rich Aesthetics)
# ==============================================================================
LOGIN_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DurianX Portal - Secure Sign In</title>
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: #090d16;
        }}
        .font-outfit {{
            font-family: 'Outfit', sans-serif;
        }}
        .glass-panel {{
            background: rgba(15, 23, 42, 0.65);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 40px rgba(99, 102, 241, 0.1);
        }}
        .glow-bg {{
            position: absolute;
            width: 500px;
            height: 500px;
            border-radius: 50%;
            filter: blur(120px);
            pointer-events: none;
            opacity: 0.4;
        }}
        .glow-1 {{
            top: -100px;
            left: -100px;
            background: radial-gradient(circle, #6366f1 0%, transparent 70%);
        }}
        .glow-2 {{
            bottom: -150px;
            right: -100px;
            background: radial-gradient(circle, #10b981 0%, transparent 70%);
        }}
        .btn-gradient {{
            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        .btn-gradient:hover {{
            background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
            box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.5);
            transform: translateY(-1px);
        }}
        .input-glow:focus {{
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25);
            border-color: #6366f1;
        }}
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4 relative overflow-hidden text-slate-100">
    <!-- Ambient Background Glows -->
    <div class="glow-bg glow-1"></div>
    <div class="glow-bg glow-2"></div>

    <div class="w-full max-w-md relative z-10">
        <!-- Logo & Branding Header -->
        <div class="text-center mb-8">
            <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 mb-4 shadow-lg shadow-indigo-500/10">
                <span class="text-3xl">🍈</span>
            </div>
            <h1 class="text-3xl font-extrabold font-outfit text-white tracking-tight">DurianX Analytics</h1>
            <p class="text-xs text-slate-400 mt-1 uppercase tracking-wider font-semibold">Protected Report Portal &bull; Enterprise Access</p>
        </div>

        <!-- Glassmorphic Login Card -->
        <div class="glass-panel rounded-3xl p-8 shadow-2xl">
            <div class="mb-6 text-center">
                <h2 class="text-xl font-bold font-outfit text-white">Sign In to Dashboard</h2>
                <p class="text-xs text-slate-400 mt-1">Enter your credentials to access merchant analytics reports.</p>
            </div>

            <!-- Error Banner -->
            {error_html}

            <form action="/login" method="POST" class="space-y-5" onsubmit="handleLoginSubmit(event)">
                <!-- Username Field -->
                <div>
                    <label class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Username</label>
                    <div class="relative">
                        <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                        </div>
                        <input type="text" name="username" required autocomplete="username" value="{input_username}" placeholder="Enter username" 
                            class="w-full pl-11 pr-4 py-3 bg-slate-900/80 border border-slate-700/80 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none input-glow transition duration-200">
                    </div>
                </div>

                <!-- Password Field -->
                <div>
                    <label class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Password</label>
                    <div class="relative">
                        <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
                        </div>
                        <input type="password" id="passwordInput" name="password" required autocomplete="current-password" placeholder="Enter password" 
                            class="w-full pl-11 pr-11 py-3 bg-slate-900/80 border border-slate-700/80 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none input-glow transition duration-200">
                        <button type="button" onclick="togglePasswordVisibility()" class="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-500 hover:text-slate-300 transition">
                            <svg id="eyeIcon" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                        </button>
                    </div>
                </div>

                <!-- Options Row -->
                <div class="flex items-center justify-between text-xs text-slate-400">
                    <label class="flex items-center space-x-2 cursor-pointer">
                        <input type="checkbox" name="remember" checked class="w-4 h-4 rounded bg-slate-900 border-slate-700 text-indigo-600 focus:ring-indigo-500/20">
                        <span>Remember session</span>
                    </label>
                    <span class="text-slate-500 hover:text-slate-400 cursor-pointer">Security Protocol TLS 1.3</span>
                </div>

                <!-- Submit Button -->
                <button type="submit" id="submitBtn" class="w-full py-3.5 px-4 btn-gradient text-white font-semibold rounded-xl text-sm shadow-lg flex items-center justify-center space-x-2">
                    <span id="btnText">Sign In to Reports</span>
                    <svg id="btnSpinner" class="hidden animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                </button>
            </form>

            <div class="mt-6 pt-5 border-t border-slate-800/80 text-center text-xs text-slate-500">
                Default Credentials: <span class="text-indigo-400 font-mono">admin</span> / <span class="text-indigo-400 font-mono">durianx2026</span>
            </div>
        </div>

        <!-- Footer Notice -->
        <p class="text-center text-xs text-slate-500 mt-6">&copy; 2026 DurianX Super App &bull; Authorized Operations Only</p>
    </div>

    <script>
        function togglePasswordVisibility() {{
            const input = document.getElementById('passwordInput');
            if (input.type === 'password') {{
                input.type = 'text';
            }} else {{
                input.type = 'password';
            }}
        }}

        function handleLoginSubmit(e) {{
            const btn = document.getElementById('submitBtn');
            const btnText = document.getElementById('btnText');
            const btnSpinner = document.getElementById('btnSpinner');
            btnText.textContent = 'Authenticating...';
            btnSpinner.classList.remove('hidden');
        }}
    </script>
</body>
</html>
"""


class SessionHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP Request Handler supporting Cookie Authentication and Custom UI Login."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=SERVE_DIR, **kwargs)

    def is_authenticated(self):
        """Check if request contains a valid auth session cookie."""
        cookie_header = self.headers.get('Cookie')
        if not cookie_header:
            return False
        
        C = cookies.SimpleCookie()
        try:
            C.load(cookie_header)
            if 'durianx_session' in C:
                token = C['durianx_session'].value
                if token in ACTIVE_SESSIONS:
                    return True
        except Exception:
            pass
        return False

    def render_login_page(self, error_msg="", input_username=""):
        """Render the custom glassmorphism login UI."""
        if error_msg:
            error_html = f"""
            <div class="mb-5 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-medium flex items-center space-x-2">
                <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                <span>{error_msg}</span>
            </div>
            """
        else:
            error_html = ""

        content = LOGIN_HTML_TEMPLATE.format(
            error_html=error_html,
            input_username=input_username
        ).encode('utf-8')

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        """Handle GET requests."""
        # Handle logout endpoint
        if self.path == '/logout':
            self.send_response(302)
            self.send_header('Set-Cookie', 'durianx_session=deleted; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT')
            self.send_header('Location', '/login')
            self.end_headers()
            return

        # Handle login page request
        if self.path in ['/login']:
            if self.is_authenticated():
                self.redirect_to_dashboard()
            else:
                self.render_login_page()
            return

        # Check authentication for all other protected routes
        if not self.is_authenticated():
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
            return

        # Default root '/' redirect to store portal
        if self.path in ['/', '']:
            if os.path.exists(os.path.join(SERVE_DIR, 'stores', 'index.html')):
                self.path = '/stores/index.html'

        super().do_GET()

    def do_POST(self):
        """Handle POST login submission."""
        if self.path == '/login':
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            params = urllib.parse.parse_qs(body)

            username_input = params.get('username', [''])[0].strip()
            password_input = params.get('password', [''])[0].strip()

            if username_input == USERNAME and password_input == PASSWORD:
                # Create session token
                session_token = str(uuid.uuid4())
                ACTIVE_SESSIONS.add(session_token)

                self.send_response(302)
                self.send_header('Set-Cookie', f'durianx_session={session_token}; Path=/; HttpOnly; SameSite=Lax')
                self.send_header('Location', '/stores/index.html')
                self.end_headers()
            else:
                self.render_login_page(
                    error_msg="Invalid username or password. Please try again.",
                    input_username=username_input
                )
        else:
            self.send_error(404, "Not Found")

    def redirect_to_dashboard(self):
        self.send_response(302)
        self.send_header('Location', '/stores/index.html')
        self.end_headers()


def run_server(port=PORT):
    handler = SessionHTTPRequestHandler
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), handler) as httpd:
        print("==================================================")
        print("[DURIANX] Custom UI Login Report Server Running")
        print("==================================================")
        print(f" Directory:  {SERVE_DIR}")
        print(f" Local URL:  http://localhost:{port}")
        print(f" Login UI:   http://localhost:{port}/login")
        print(f" Username:   {USERNAME}")
        print(f" Password:   {PASSWORD}")
        print("==================================================")
        print("Server active... Press Ctrl+C to stop.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer gracefully stopped.")

if __name__ == "__main__":
    port_arg = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else PORT
    run_server(port_arg)
