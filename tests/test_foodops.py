import csv
import unittest
from unittest.mock import patch, MagicMock
import foodops


class TestFoodOps(unittest.TestCase):
    def test_perguntas(self):
        for pergunta, esperado in [
            ("Quanto cada loja faturou?", "receita"), ("O ticket médio mudou?", "ticket"),
            ("Onde os cancelamentos pioraram?", "cancelamentos"),
            ("Qual o clima?", "fora_do_escopo"), ("ticket e receita", "fora_do_escopo"),
        ]:
            with self.subTest(pergunta=pergunta):
                self.assertEqual(foodops.selecionar(pergunta), esperado)

    def test_inferencia_local(self):
        for pergunta, esperado in [
            ("Como ficou a arrecadação?", "receita"),
            ("Os clientes desistiram nesta semana?", "cancelamentos"),
            ("Comparar gasto por consumidor", "ticket"),
            ("Como está a previsão do tempo?", "fora_do_escopo"),
        ]:
            with self.subTest(pergunta=pergunta):
                self.assertEqual(foodops.selecionar(pergunta), esperado)

    def test_calculos(self):
        with foodops.BASE.open(encoding="utf-8") as arquivo:
            linhas = list(csv.DictReader(arquivo))
        self.assertIn("4.0% (4/100) -> 10.0% (10/100)", foodops.resumir("cancelamentos", linhas))
        self.assertIn("R$ 28,00 -> R$ 29,00", foodops.resumir("ticket", linhas))
        self.assertIn("R$ 2940,00 -> R$ 3069,00", foodops.resumir("receita", linhas))

    @patch("foodops.HTTPConnection")
    def test_contrato_modelo(self, conexao):
        resposta = MagicMock(status=200)
        conexao.return_value.getresponse.return_value = resposta
        for valor in ("ticket", "comando_arbitrario"):
            resposta.read.return_value = foodops.json.dumps({
                "message": {"content": foodops.json.dumps({"intencao": valor})}
            }).encode()
            if valor == "ticket":
                self.assertEqual(foodops.selecionar_com_modelo("Qual o ticket?", "demo"), valor)
            else:
                with self.assertRaises(ValueError):
                    foodops.selecionar_com_modelo("Qual o ticket?", "demo")
