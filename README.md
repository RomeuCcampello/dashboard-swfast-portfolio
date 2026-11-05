# Dashboard Swfast

O Dashboard Swfast reúne vendas e cancelamentos da API Swfast em PostgreSQL e apresenta os indicadores no Metabase. A licença MIT do projeto-base credita George-Gabryel.

## Assistente de análise de vendas e cancelamentos

Esta extensão de portfólio usa um CSV fictício de duas lojas para responder perguntas em português. Você pode executá-la separadamente do dashboard, usando apenas a biblioteca padrão do Python.

### Experimente

Na pasta do projeto, com Python 3.10 ou superior:

```sh
python foodops.py "Onde os cancelamentos pioraram?"
python foodops.py "Qual foi o ticket médio?"
python foodops.py "Quanto cada loja faturou?"
python -m unittest discover -s tests -p test_foodops.py
```

Em Mercado Norte, os cancelamentos passam de 4 em 100 pedidos para 10 em 100. Isso dá uma razão para investigar a operação dessa loja. Os dados permitem localizar a mudança; identificar sua causa exigiria registrar os motivos de cancelamento.

### Como o assistente funciona

Por padrão, um classificador Naive Bayes aprende com 21 frases rotuladas em português e escolhe entre três métricas. O treino e a inferência rodam no próprio Python sem rede, instalação adicional ou chave. Se faltam termos conhecidos ou os dois melhores resultados ficam próximos, ele pede uma pergunta mais específica. Para experimentar classificação por LLM, execute a mesma pergunta com `--modelo-local NOME_DO_MODELO` usando um modelo já instalado no Ollama na sua máquina. O programa envia somente a pergunta ao serviço de loopback, valida a intenção e calcula a resposta em Python. Perguntas fora do escopo recebem a lista de métricas. O modo básico trabalha com vocabulário limitado; as consultas sempre comparam as duas semanas da amostra, para todas as lojas.

O CSV sintético registra vendas concluídas, receita em centavos e pedidos cancelados por loja e semana. O ticket divide a receita pelas vendas concluídas. A taxa divide os cancelamentos pelo total de tentativas. A demo funciona sem Docker, banco, credencial ou serviço pago. O pipeline original tem suas próprias dependências e configuração.


## Origem e execução do projeto-base

O mantenedor desta versão assumiu uma versão inicial do projeto e concluído o dashboard. O código-base conserva a licença MIT e o aviso original em `LICENSE`. O assistente de métricas é uma extensão posterior.

O pipeline em `swfast/` extrai vendas da API Swfast, transforma registros e alimenta as tabelas consultadas pelo Metabase. Os arquivos Compose descrevem os serviços de banco, ETL e visualização. Para conhecer o assistente, basta executar os comandos acima sobre os dados fictícios incluídos.
