import os
import sys
from urllib.parse import parse_qsl, urlencode, urlsplit

# Adiciona o diretório raiz ao Python path para permitir importações relativas e absolutas do backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.app import app as flask_app


class VercelPathFixMiddleware:
    """Restaura o PATH_INFO original enviado via ?__path=/$1 pelo rewrite da Vercel."""
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        qs = environ.get("QUERY_STRING", "") or ""
        if "__path=" in qs:
            pairs = parse_qsl(qs, keep_blank_values=True)
            restored_path = None
            remaining_pairs = []
            for k, v in pairs:
                if k == "__path" and restored_path is None:
                    restored_path = v
                else:
                    remaining_pairs.append((k, v))
            if restored_path is not None:
                if not restored_path.startswith("/"):
                    restored_path = "/" + restored_path
                # Normaliza barras duplicadas no início (ex: "//" -> "/")
                while restored_path.startswith("//"):
                    restored_path = restored_path[1:]
                environ["PATH_INFO"] = restored_path or "/"
                environ["QUERY_STRING"] = urlencode(remaining_pairs, doseq=True)
                return self.wsgi_app(environ, start_response)

        path = environ.get("PATH_INFO", "") or "/"
        if path in ("/api/index", "/api/index.py"):
            orig = (
                environ.get("HTTP_X_VERCEL_ORIGINAL_URL")
                or environ.get("HTTP_X_FORWARDED_URI")
                or environ.get("HTTP_X_INVOKE_PATH")
                or ""
            )
            if orig:
                path = urlsplit(orig).path or "/"
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
