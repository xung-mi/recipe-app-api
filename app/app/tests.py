from django.test import SimpleTestCase
from app import calc
from rest_framework.test import APIClient

class CalcTest(SimpleTestCase):
    def test_add_numbers(self):
        self.assertEqual(calc.add(10, 5), 15)
        
    def test_subtract_numbers(self):
        self.assertEqual(calc.subtract(10, 5), 5)
        
    def test_get_greetings(self):
        client = APIClient()
        response = client.get("/greetings/")
        self.assertEqual(response.status_code, 404)