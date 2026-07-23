import os
import mimetypes
from flask import Flask, request, Response, redirect, make_response, render_template_string

app = Flask(__name__)

# Configuration (Support Vercel Environment Variables)
USERNAME = os.environ.get("ADMIN_USER", "admin")
PASSWORD = os.environ.get("ADMIN_PASS", "durianx2026")
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "durianx_session_auth_token_9988")

# Directory containing report assets
REPORTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LOGIN_HTML = """<!DOCTYPE html>
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
        body { font-family: 'Plus Jakarta Sans', sans-serif; background: #090d16; }
        .font-outfit { font-family: 'Outfit', sans-serif; }
        .glass-panel {
            background: rgba(15, 23, 42, 0.65);
            backdrop-filter: blur(24px);
            -webkit-backdrop-filter: blur(24px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 40px rgba(99, 102, 241, 0.1);
        }
        .glow-bg {
            position: absolute; width: 500px; height: 500px; border-radius: 50%;
            filter: blur(120px); pointer-events: none; opacity: 0.4;
        }
        .glow-1 { top: -100px; left: -100px; background: radial-gradient(circle, #6366f1 0%, transparent 70%); }
        .glow-2 { bottom: -150px; right: -100px; background: radial-gradient(circle, #10b981 0%, transparent 70%); }
        .btn-gradient {
            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .btn-gradient:hover {
            background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%);
            box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.5);
            transform: translateY(-1px);
        }
        .input-glow:focus {
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25);
            border-color: #6366f1;
        }
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4 relative overflow-hidden text-slate-100">
    <div class="glow-bg glow-1"></div>
    <div class="glow-bg glow-2"></div>

    <div class="w-full max-w-md relative z-10">
        <div class="text-center mb-8">
            <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 mb-4 shadow-lg shadow-indigo-500/10">
                <span class="text-3xl">🍈</span>
            </div>
            <h1 class="text-3xl font-extrabold font-outfit text-white tracking-tight">DurianX Analytics</h1>
            <p class="text-xs text-slate-400 mt-1 uppercase tracking-wider font-semibold">Protected Report Portal &bull; Enterprise Access</p>
        </div>

        <div class="glass-panel rounded-3xl p-8 shadow-2xl">
            <div class="mb-6 text-center">
                <h2 class="text-xl font-bold font-outfit text-white">Sign In to Dashboard</h2>
                <p class="text-xs text-slate-400 mt-1">Enter your credentials to access merchant analytics reports.</p>
            </div>

            {% if error_msg %}
            <div class="mb-5 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-medium flex items-center space-x-2">
                <svg class="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                <span>{{ error_msg }}</span>
            </div>
            {% endif %}

            <form action="/login" method="POST" class="space-y-5" onsubmit="handleLoginSubmit(event)">
                <div>
                    <label class="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">Username</label>
                    <div class="relative">
                        <div class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                        </div>
                        <input type="text" name="username" required autocomplete="username" value="{{ input_username }}" placeholder="Enter username" 
                            class="w-full pl-11 pr-4 py-3 bg-slate-900/80 border border-slate-700/80 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none input-glow transition duration-200">
                    </div>
                </div>

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

                <div class="flex items-center justify-between text-xs text-slate-400">
                    <label class="flex items-center space-x-2 cursor-pointer">
                        <input type="checkbox" name="remember" checked class="w-4 h-4 rounded bg-slate-900 border-slate-700 text-indigo-600 focus:ring-indigo-500/20">
                        <span>Remember session</span>
                    </label>
                    <span class="text-slate-500">Security TLS 1.3</span>
                </div>

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

        <p class="text-center text-xs text-slate-500 mt-6">&copy; 2026 DurianX Super App &bull; Authorized Operations Only</p>
    </div>

    <script>
        function togglePasswordVisibility() {
            const input = document.getElementById('passwordInput');
            input.type = input.type === 'password' ? 'text' : 'password';
        }
        function handleLoginSubmit(e) {
            document.getElementById('btnText').textContent = 'Authenticating...';
            document.getElementById('btnSpinner').classList.remove('hidden');
        }
    </script>
</body>
</html>
"""

def is_authenticated():
    cookie = request.cookies.get('durianx_session')
    return cookie == AUTH_TOKEN

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_in = request.form.get('username', '').strip()
        pass_in = request.form.get('password', '').strip()
        if user_in == USERNAME and pass_in == PASSWORD:
            resp = make_response(redirect('/dark_order/Dark_Order_Chart.html'))
            resp.set_cookie('durianx_session', AUTH_TOKEN, max_age=60*60*24*7, httponly=True, samesite='Lax')
            return resp
        else:
            return render_template_string(LOGIN_HTML, error_msg="Invalid username or password. Please try again.", input_username=user_in)
    
    if is_authenticated():
        return redirect('/dark_order/Dark_Order_Chart.html')
    return render_template_string(LOGIN_HTML, error_msg="", input_username="")

@app.route('/logout')
def logout():
    resp = make_response(redirect('/login'))
    resp.set_cookie('durianx_session', '', expires=0)
    return resp

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    if not is_authenticated():
        return redirect('/login')

    if not path or path == '/':
        path = 'dark_order/Dark_Order_Chart.html'

    file_path = os.path.join(REPORTS_DIR, path)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        mime_type, _ = mimetypes.guess_type(file_path)
        with open(file_path, 'rb') as f:
            content = f.read()
        return Response(content, mimetype=mime_type or 'text/plain')

    # If missing, fallback to main chart
    chart_path = os.path.join(REPORTS_DIR, 'dark_order', 'Dark_Order_Chart.html')
    if os.path.exists(chart_path):
        with open(chart_path, 'rb') as f:
            return Response(f.read(), mimetype='text/html')
            
    return Response("File Not Found", status=404)

# Vercel WSGI Handler
app_wsgi = app
