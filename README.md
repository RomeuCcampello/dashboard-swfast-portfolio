# Dashboard Swfast

Sistema de análise de vendas e cancelamentos para restaurantes. O pipeline coleta registros da API Swfast, organiza os dados no PostgreSQL e abastece um painel no Metabase. Assumi o projeto em sua fase inicial e concluí o dashboard. A base é creditada a George-Gabryel na [licença MIT](LICENSE).

## Uma pergunta de operação

**Em qual loja vale investigar os cancelamentos primeiro?** Na demonstração, Mercado Norte passou de **4 para 10 cancelamentos em 100 pedidos** entre as duas semanas. Praça Sul passou de 2 para 1 no mesmo volume. Isso direciona a investigação para Mercado Norte. Para explicar o motivo, precisaríamos de dados sobre cada cancelamento.

[**Abrir a demonstração no GitHub**](demonstracao.ipynb) · [Ver os dados fictícios](foodops_demo.csv) · [Consultar os testes](tests/test_foodops.py)

## O que foi acrescentado

O assistente é uma extensão independente do painel. Recebe perguntas em português e usa um classificador Naive Bayes treinado localmente com 21 frases rotuladas para escolher entre cancelamentos, ticket médio e faturamento. O Python calcula os valores a partir de um CSV com duas lojas e duas semanas. O modelo tem vocabulário limitado e solicita outra pergunta quando há pouca evidência para escolher a métrica.

## Executar em um minuto

Na raiz do projeto, com Python 3.10 ou superior:

```sh
python foodops.py "Onde os cancelamentos pioraram?"
python foodops.py "Qual foi o ticket médio?"
python -m unittest discover -s tests -p test_foodops.py
```

A demo usa apenas a biblioteca padrão. A taxa de cancelamento divide cancelamentos pelo total de tentativas. O ticket médio divide a receita pelas vendas concluídas. Há também um adaptador opcional para um modelo instalado no Ollama, selecionado com `--modelo-local NOME_DO_MODELO`. Os testes desse adaptador usam respostas simuladas.

## Código do dashboard

- [Pipeline de extração e carga](swfast/pipeline.py) — coordena a coleta e o processamento.
- [Transformação dos registros](swfast/transformacao.py) — prepara os dados de vendas e cancelamentos.
- [Consultas do painel](swfast/visoes.py) — organiza os indicadores consultados pelo Metabase.
- [Assistente em Python](foodops.py) — classifica a pergunta e calcula a métrica da demonstração.
