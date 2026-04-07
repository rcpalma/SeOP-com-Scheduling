Nesse projeto pessoal, utilizei Python e a biblioteca gurobipy para modelar e resolver o problema S&OP e Scheduling(sequenciamento) descrito em **SeOP.pdf**. Criei também algumas visualizações para melhor interpretabilidade da solução.

## Descrição
O problema S&OP consiste basicamente em atender a demanda de produtos em centros de destribuição num horizonte de tempo, portanto, dimensionar lotes de produtos p em linhas l num horizonte de tempo t levando em consideração custos de setup, tempo de setup, lead time
de frabricação, custos de estocagem na fábrica e nos CDs além de custos logísticos entre fábrica e CDs. Também adicionei o recurso escasso de mão de obra.
Após a solução ótima de produtos p a serem fabricados na linha l no tempo t, considerei também um outro problema de sequenciamento desses produtos a fim de determinar a solução de menor tempo de setup desses produtos.
## Instâncias
Os dados para gerar instâncias são sintéticos e construí utilizando ajuda de **IA** para facilitar a geração de dados mais realista.

## Estrutura do Projeto
```text
├── main.py        # main
├── solver.py      # Modelagem e otimização do S&OP
├── solver1.py      # Modelagem e otimização do Scheduling
├── data.py        # Geração de dados sintéticos utilizando **IA**
├── plot.py        # Visualizações da solução de ambos problemas
├── api.py         # API 
└── frontend/
    └── src/
        └── App.jsx

```
**A API e a interface web foram desenvolvidas com auxílio de IA como forma de tornar o modelo acessível e iterativo via browser, os dados sintéticos também foram criados com ajuda de IA. A concepção do problema juntamente com o arquivo pdf e as funçãos em solver, solver1 e main foram feitas exclusivamente pelo autor**

## Resultados e Gráficos

Dois gráficos são gerados ao executar main.py

**Primeiro - Produção ao longo do tempo:** Produção por produto ao longo do horizonte de planetamento t. 
<img width="1923" height=<img width="1000" height="600" alt="producao" src="https://github.com/user-attachments/assets/8a8dfc0f-7d93-4cc7-b3a0-a07de5438cdd" />



**Segundo - Estoque na fábrica:** Estoque de produtos p na única fabrica ao longo do horizonte de planejamento t.
<img width="1000" height="600" alt="estoque_fabrica" src="https://github.com/user-attachments/assets/e712fa91-9dcc-4cdf-b5aa-ea3999abf64b" />



**Terceiro - Fluxo dos produtos para os CDs:** Fluxo dos produtos p para os CDs ao longo do horizonte de planejamento t.
<img width="1000" height="600" alt="fluxo_cd" src="https://github.com/user-attachments/assets/c65c8544-796a-44a4-b141-4dfb223375c7" />


**Quarto - Sequenciamento dos produtos:** Sequenciamento dos produtos p nas linhas l ao longo do horizonte de planejamento t.
<img width="1200" height="440" alt="sequenciamento" src="https://github.com/user-attachments/assets/62fce943-2eb0-4bbb-a25c-6be045e6f062" />



## Como usar
Abra o arquivo main.py e escolha na função generate_data(P,L,m,T,42) os valores de P,L,m,T que são número de produtos, linhas, CDs e horizonte de tempo respectivamente. 
Salve e, no diretório do projeto execute o comando: "python main.py"

## Requirements

- Python 3.10+
- Gurobi (with valid license — academic license available at gurobi.com)
- **Python dependencies:**
  - `matplotlib`
  - `pandas`
  - `gurobipy`
  - `numpy`
```
pip install -r requirements.txt
```

## Demo - Interface Web
A API foi desenvolvida com **FastAPI** e **Uvicorn** (Python), com ajuda de **IA**.
A interface web foi construída com **JavaScript** e **React**, permitindo escolher os parâmetros e visualizar a solução de forma interativa 
no browser.
![SeOP](https://github.com/user-attachments/assets/62eb156f-d413-4aee-81c0-ed89dbc8ff53)




## References
*   **PDF Elaborado pelo autor**
