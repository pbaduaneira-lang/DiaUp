import os
import sys

# Adiciona o diretório raiz ao Python path para permitir importações relativas e absolutas do backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.app import app

# Exporta a instância 'app' do Flask como Serverless Function (WSGI app) para o Vercel
