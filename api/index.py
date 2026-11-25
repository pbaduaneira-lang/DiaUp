import os
import sys
from urllib.parse import urlsplit

# Adiciona o diretório raiz ao Python path para permitir importações relativas e absolutas do backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.app import app as flask_app


class VercelPathFixMiddleware:
    """Garante que o PATH_INFO chegue limpo ao Flask mesmo quando a Vercel reescreve para /api/index(.py)."""
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        path = environ.get("PATH_INFO", "") or "/"
        if path in ("/api/index", "/api/index.py"):
            orig = (
                environ.get("HTTP_X_VERCEL_ORIGINAL_URL")
                or environ.get("HTTP_X_FORWARDED_URI")
                or environ.get("HTTP_X_INVOKE_PATH")
                or ""
            )
            if orig:
                parsed = urlsplit(orig)
                path = parsed.path or "/"
            else:
                path = "/"
            if path in ("/api/index", "/api/index.py"):
                path = "/"
            environ["PATH_INFO"] = path
        elif path.startswith("/api/index.py/"):
            environ["PATH_INFO"] = path[len("/api/index.py"):]
        elif path.startswith("/api/index/"):
            environ["PATH_INFO"] = path[len("/api/index"):]
        return self.wsgi_app(environ, start_response)


flask_app.wsgi_app = VercelPathFixMiddleware(flask_app.wsgi_app)
app = flask_app

# Exporta a instância 'app' do Flask como Serverless Function (WSGI app) para o Vercel
