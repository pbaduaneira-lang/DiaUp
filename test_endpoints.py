import unittest
import json
from backend.app.app import app
from backend.app.database import ensure_schema

class TestEndpoints(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.client = app.test_client()
        ensure_schema()

    def test_get_profile_default(self):
        res = self.client.get('/user/profile')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('name', data)
        self.assertIn('city', data)

    def test_update_and_get_profile(self):
        new_profile = {
            "name": "Mariana",
            "birth_date": "1994-08-20",
            "city": "Belo Horizonte",
            "state": "MG"
        }
        res_post = self.client.post('/user/profile', 
                                    data=json.dumps(new_profile), 
                                    content_type='application/json')
        self.assertEqual(res_post.status_code, 200)

        res_get = self.client.get('/user/profile')
        data = json.loads(res_get.data)
        self.assertEqual(data['name'], "Mariana")
        self.assertEqual(data['city'], "Belo Horizonte")
        self.assertEqual(data['state'], "MG")

    def test_get_message(self):
        profile = {
            "name": "Mariana",
            "birth_date": "1994-08-20",
            "city": "Belo Horizonte",
            "state": "MG"
        }
        self.client.post('/user/profile', data=json.dumps(profile), content_type='application/json')
        res = self.client.get('/user/get_message?category=Saúde')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('content', data)
        self.assertIn('Mariana', data['content'])
        self.assertTrue(data['content'].startswith('Mariana,'), f"Mensagem deve começar com o nome: {data['content']}")
        self.assertIn('Belo Horizonte', data['content'])
        print("\n--- Mensagem Gerada via Endpoint /user/get_message (Saúde) para Mariana ---")
        print(data['content'])
        print("---------------------------------------------------------------------------\n")

    def test_admin_saved_message(self):
        profile = {
            "name": "Carlos",
            "birth_date": "1990-05-10",
            "city": "Curitiba",
            "state": "PR"
        }
        self.client.post('/user/profile', data=json.dumps(profile), content_type='application/json')
        
        # Admin realiza login antes de adicionar mensagem
        self.client.post('/admin/login', data=json.dumps({"email": "diaup@gmail.com", "password": "diaedju1016"}), content_type='application/json')

        # Admin adiciona uma mensagem na biblioteca
        msg_data = {
            "content": "Acredite nos seus sonhos e nunca desista da sua caminhada.",
            "category": "Projetos"
        }
        res_post = self.client.post('/admin/add_message', data=json.dumps(msg_data), content_type='application/json')
        self.assertEqual(res_post.status_code, 201)

        # Chama o endpoint de mensagem algumas vezes para verificar se o nome vem sempre no início
        for _ in range(5):
            res = self.client.get('/user/get_message?category=Projetos')
            data = json.loads(res.data)
            self.assertTrue(data['content'].startswith('Carlos,'), f"Mensagem deve começar com 'Carlos,': {data['content']}")

        # Teste de atualização da mensagem adicionada (PUT)
        res_list = self.client.get('/admin/messages')
        data_list = json.loads(res_list.data)
        msg_id = data_list['messages'][0]['id']

        update_data = {
            "content": "Acredite com toda a força do coração, pois o sucesso em Amor e Finanças é uma realidade.",
            "category": "Amor"
        }
        res_put = self.client.put(f'/admin/messages/{msg_id}', data=json.dumps(update_data), content_type='application/json')
        self.assertEqual(res_put.status_code, 200)
        put_data = json.loads(res_put.data)
        self.assertEqual(put_data['item']['category'], "Amor")
        self.assertIn("Acredite com toda a força", put_data['item']['content'])

    def test_get_categories(self):
        res = self.client.get('/user/categories')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('categories', data)
        cat_names = [c['name'] for c in data['categories']]
        self.assertEqual(cat_names, ["Saúde", "Relacionamento", "Família", "Trabalho", "Projetos", "Amor", "Finanças"])

    def test_admin_stats(self):
        res_dl = self.client.post('/api/stats/download')
        self.assertEqual(res_dl.status_code, 200)

        # Admin realiza login antes de buscar estatísticas
        self.client.post('/admin/login', data=json.dumps({"email": "diaup@gmail.com", "password": "diaedju1016"}), content_type='application/json')

        res_stats = self.client.get('/admin/stats')
        self.assertEqual(res_stats.status_code, 200)
        data = json.loads(res_stats.data)
        self.assertIn('downloads', data)
        self.assertIn('registered', data)
        self.assertIn('recent_users', data)
        self.assertTrue(data['downloads'] >= 12)
        print(f"\n--- Estatísticas do Admin: {data['downloads']} downloads, {data['registered']} cadastrados ---")

    def test_admin_auth_flow(self):
        # 1. Tentar acessar sem login (deve retornar 401)
        res_unauth = self.client.get('/admin/stats')
        self.assertEqual(res_unauth.status_code, 401)
        
        # 2. Tentar login com senha incorreta (deve retornar 401)
        res_wrong = self.client.post('/admin/login', 
                                     data=json.dumps({"email": "diaup@gmail.com", "password": "senha_errada"}), 
                                     content_type='application/json')
        self.assertEqual(res_wrong.status_code, 401)
        
        # 3. Login com sucesso (deve retornar 200)
        res_login = self.client.post('/admin/login', 
                                     data=json.dumps({"email": "diaup@gmail.com", "password": "diaedju1016"}), 
                                     content_type='application/json')
        self.assertEqual(res_login.status_code, 200)
        
        # 4. Acessar rota protegida com a sessão logada (deve retornar 200)
        res_auth = self.client.get('/admin/stats')
        self.assertEqual(res_auth.status_code, 200)
        
        # 5. Logout (deve encerrar sessão e requisições posteriores voltam a 401)
        res_logout = self.client.post('/admin/logout')
        self.assertEqual(res_logout.status_code, 200)
        res_after_logout = self.client.get('/admin/stats')
        self.assertEqual(res_after_logout.status_code, 401)
        print("\n--- Teste de Fluxo de Autenticação Admin (Login, Logout e Acesso Negado) Concluído ---")

if __name__ == '__main__':
    unittest.main()
