"""Assistente de operação de restaurantes. A demo usa somente dados sintéticos."""
import argparse
import csv
import json
import math
import re
import unicodedata
from collections import Counter
from http.client import HTTPConnection, HTTPException
from pathlib import Path

BASE = Path(__file__).with_name("foodops_demo.csv")
EXEMPLOS = {
    "cancelamentos": (
        "pedidos cancelados", "taxa de cancelamentos", "quantas desistências",
        "onde os cancelamentos cresceram", "cancelamento de pedidos",
        "compras canceladas pelos clientes", "quantos desistiram",
    ),
    "ticket": (
        "ticket médio", "gasto médio por cliente", "média por compra",
        "quanto cada consumidor gastou", "qual foi o valor médio",
        "ticket por loja", "quanto gastam em média",
    ),
    "receita": (
        "quanto a loja faturou", "qual o faturamento", "total das vendas",
        "receita por loja", "qual unidade vendeu mais", "quanto arrecadou",
        "arrecadação da semana",
    ),
}
IGNORADAS = set("a o as os de da das do dos e em por para qual quais quanto quantas quantos foi cada onde loja lojas unidade semana mais".split())


def palavras(texto):
    simples = unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()
    return [p for p in re.findall(r"[a-z]+", simples) if p not in IGNORADAS]


def selecionar(pergunta):
    # Naive Bayes multinomial, com suavização de Laplace e exemplos locais.
    contagens = {
        classe: Counter(p for frase in frases for p in palavras(frase))
        for classe, frases in EXEMPLOS.items()
    }
    vocabulario = set().union(*contagens.values())
    termos = [p for p in palavras(pergunta) if p in vocabulario]
    if not termos:
        return "fora_do_escopo"
    escores = []
    for classe, contagem in contagens.items():
        total = sum(contagem.values()) + len(vocabulario)
        escore = sum(math.log((contagem[p] + 1) / total) for p in termos)
        escores.append((escore, classe))
    escores.sort(reverse=True)
    if escores[0][0] - escores[1][0] < math.log(1.5):
        return "fora_do_escopo"
    return escores[0][1]


def selecionar_com_modelo(pergunta, modelo):
    # O modelo só recebe a pergunta. Os dados e os cálculos permanecem no processo.
    escolhas = [*EXEMPLOS, "fora_do_escopo"]
    schema = {"type": "object", "properties": {"intencao": {"enum": escolhas}},
              "required": ["intencao"], "additionalProperties": False}
    corpo = {"model": modelo, "stream": False, "format": schema,
             "messages": [{"role": "system", "content": "Classifique a pergunta sobre o painel. "
                           "Use fora_do_escopo para assunto desconhecido ou ambíguo."},
                          {"role": "user", "content": pergunta}]}
    conn = HTTPConnection("127.0.0.1", 11434, timeout=30)
    try:
        conn.request("POST", "/api/chat", body=json.dumps(corpo),
                     headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        if resp.status != 200:
            raise ValueError(f"Ollama respondeu HTTP {resp.status}")
        texto = json.loads(resp.read())["message"]["content"]
        escolha = json.loads(texto)["intencao"]
        if escolha not in escolhas:
            raise ValueError("intenção desconhecida")
        return escolha
    finally:
        conn.close()


def dinheiro(centavos):
    return f"R$ {centavos / 100:.2f}".replace(".", ",")


def resumir(intencao, linhas):
    if intencao not in EXEMPLOS:
        return "Escolha uma métrica da demo: cancelamentos, ticket médio ou faturamento."
    grupos = {}
    for linha in linhas:
        chave = (linha["loja"], int(linha["semana"]))
        total = grupos.setdefault(chave, Counter())
        for coluna in ("pedidos", "receita_centavos", "cancelados"):
            total[coluna] += int(linha[coluna])
    saida = ["Dados fictícios | semana 1 -> semana 2"]
    for loja in sorted({loja for loja, _ in grupos}):
        valores = []
        for semana in (1, 2):
            item = grupos.get((loja, semana))
            if item is None:
                valores.append("sem dados")
                continue
            pedidos, cancelados = item["pedidos"], item["cancelados"]
            if intencao == "cancelamentos":
                total = pedidos + cancelados
                valor = (f"{100 * cancelados / total:.1f}% ({cancelados}/{total})"
                         if total else "sem pedidos")
            elif intencao == "ticket":
                valor = dinheiro(item["receita_centavos"] / pedidos) if pedidos else "sem vendas"
            else:
                valor = dinheiro(item["receita_centavos"])
            valores.append(valor)
        saida.append(f"{loja}: {' -> '.join(valores)}")
    return "\n".join(saida)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pergunta")
    parser.add_argument("--modelo-local", help="Nome de um modelo instalado no Ollama local")
    args = parser.parse_args()
    try:
        intencao = (selecionar_com_modelo(args.pergunta, args.modelo_local)
                    if args.modelo_local else selecionar(args.pergunta))
    except (OSError, HTTPException, ValueError, KeyError, TypeError) as erro:
        parser.exit(2, f"Modelo local indisponível ou resposta inválida ({erro}). "
                       "Execute sem --modelo-local para usar o roteador offline.\n")
    with BASE.open(encoding="utf-8", newline="") as arquivo:
        print(resumir(intencao, csv.DictReader(arquivo)))


if __name__ == "__main__":
    main()
