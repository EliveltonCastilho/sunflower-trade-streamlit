# Sunflower Land - Visualizador de Preços

Um aplicativo Streamlit simples para visualizar os preços dos itens em Sunflower Land.

## Funcionalidades

- Seletor de itens para escolher qual item visualizar
- Gráfico de linhas mostrando os preços em Flower e USD (quando disponível)
- Controle deslizante para ajustar o período de visualização (1-90 dias)
- Exibição de dados brutos em formato tabular

## Configuração

1. Clone este repositório
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Configure o banco de dados:
   - Renomeie o arquivo `env_template.txt` para `.env`
   - Edite o arquivo `.env` com suas configurações de banco de dados

## Execução

```
streamlit run app.py
```

O aplicativo será iniciado e estará disponível em `http://localhost:8501`.

## Requisitos

- Python 3.8+
- Acesso ao banco de dados MySQL com a tabela `item_prices`

## Estrutura do Banco de Dados

O aplicativo espera uma tabela `item_prices` com pelo menos as seguintes colunas:
- `item_name`: Nome do item
- `p2p_price`: Preço em Flower
- `usd_price`: Preço em USD (pode ser nulo)
- `timestamp`: Data e hora do registro 