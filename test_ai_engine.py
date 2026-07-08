import unittest
from backend.app.ai_engine import calculate_age, generate_fallback_message, generate_motivational_message

class TestAIEngine(unittest.TestCase):
    def test_calculate_age(self):
        age_full = calculate_age("1995-06-15")
        self.assertTrue(20 <= age_full <= 40)
        
        age_year = calculate_age("1990")
        self.assertTrue(25 <= age_year <= 50)
        
        age_invalid = calculate_age(None)
        self.assertEqual(age_invalid, 28)

    def test_fallback_message(self):
        msg = generate_fallback_message("Carlos", 30, "Curitiba", "PR", "Trabalho")
        self.assertIn("Carlos", msg)
        self.assertIn("Curitiba", msg)
        self.assertIn("30", msg)
        self.assertTrue(len(msg) > 20)

    def test_generate_motivational_message_fallback(self):
        profile = {
            "name": "Ana",
            "birth_date": "1992-05-10",
            "city": "Rio de Janeiro",
            "state": "RJ"
        }
        msg = generate_motivational_message(profile, "Projetos")
        self.assertIsInstance(msg, str)
        self.assertTrue(len(msg) > 20)
        print("\n--- Exemplo de Mensagem Gerada para Ana (Rio de Janeiro, Projetos) ---")
        print(msg)
        print("-----------------------------------------------------------------------\n")

if __name__ == '__main__':
    unittest.main()
