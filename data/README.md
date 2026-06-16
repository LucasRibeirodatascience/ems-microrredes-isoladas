# Dados

Os dados reais do projeto industrial não são publicados neste repositório.

Para executar o simulador, utilize um CSV horário com a seguinte estrutura:

```text
timestamp,load_kw,pv_kw,pv_forecast_kw
2025-01-01 00:00:00,180,0,0
2025-01-01 01:00:00,175,0,0
2025-01-01 12:00:00,220,310,290
```

Colunas obrigatórias:

- `timestamp`: data e hora;
- `load_kw`: carga elétrica;
- `pv_kw`: geração fotovoltaica disponível.

Coluna recomendada para o M2:

- `pv_forecast_kw`: previsão de geração fotovoltaica.

Para simulações anuais, o arquivo deve conter 8760 linhas em resolução horária.
