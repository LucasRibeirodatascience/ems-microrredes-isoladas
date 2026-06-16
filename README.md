# EMS para Microrredes Isoladas PV/BESS/Diesel

Repositório público e sanitizado para organização da metodologia de um Sistema de Gerenciamento de Energia (EMS) aplicado a microrredes isoladas híbridas com geração fotovoltaica, sistema de baterias e gerador diesel.

Este projeto representa uma versão aberta da estrutura técnica utilizada para estudo, simulação e comparação de estratégias EMS. Não inclui dados proprietários, parâmetros confidenciais, modelos treinados privados ou código industrial fechado.

## Objetivo

Simular e avaliar estratégias de gerenciamento energético para microrredes isoladas, considerando:

- atendimento prioritário da carga pela geração fotovoltaica;
- uso estratégico do sistema de baterias (BESS);
- acionamento do gerador diesel quando PV e BESS não atendem a demanda;
- comparação entre estratégias de controle;
- cálculo de métricas operacionais relevantes para tomada de decisão.

## Contexto técnico

O projeto foi desenvolvido no contexto de P&D em Energia Inteligente, com foco em microrredes isoladas híbridas PV/BESS/Diesel e avaliação de estratégias EMS em horizonte anual.

Destaques metodológicos:

- simulação horária anual com 8760 amostras;
- integração entre PV, BESS e gerador diesel;
- comparação entre M1, M2 e M3;
- uso de previsão solar para antecipação operacional;
- interface para política baseada em aprendizado por reforço;
- métricas de consumo de diesel, partidas, horas de operação, curtailment e operação em faixa ótima.

## Estratégias modeladas

### M1 - Estratégia base

Estratégia determinística que utiliza a geração fotovoltaica como fonte prioritária, carrega a bateria com excedentes e aciona o gerador diesel quando PV e BESS não conseguem atender a carga.

### M2 - Estratégia orientada por previsão

Extensão do M1 com uso de previsão solar para preservar energia no BESS em períodos de baixa disponibilidade renovável esperada.

### M3 - Estratégia com aprendizado por reforço

Interface pública para integração de uma política de aprendizado por reforço. A versão aberta não inclui agente treinado, pesos de modelo ou lógica confidencial. O objetivo é documentar a arquitetura esperada para acoplamento de políticas como PPO/Stable Baselines3.

## Estrutura

```text
ems-microrredes-isoladas/
|-- data/
|   `-- README.md
|-- examples/
|   `-- sample_timeseries.csv
|-- src/
|   `-- ems_microgrid/
|       |-- __init__.py
|       |-- components.py
|       |-- main.py
|       |-- metrics.py
|       |-- simulator.py
|       `-- strategies.py
|-- pyproject.toml
`-- README.md
```

## Como executar

Instale o projeto em modo editável:

```bash
pip install -e .
```

Execute uma simulação com a estratégia M1:

```bash
python -m ems_microgrid.main \
  --data examples/sample_timeseries.csv \
  --strategy m1 \
  --output reports/m1_results.csv
```

Execute a estratégia orientada por previsão:

```bash
python -m ems_microgrid.main \
  --data examples/sample_timeseries.csv \
  --strategy m2 \
  --output reports/m2_results.csv
```

## Formato dos dados

O arquivo de entrada deve conter resolução horária e, no mínimo, as colunas:

- `timestamp`: data e hora da amostra;
- `load_kw`: demanda elétrica da microrrede;
- `pv_kw`: potência fotovoltaica disponível.

Para o M2, recomenda-se incluir:

- `pv_forecast_kw`: previsão de potência fotovoltaica para suporte à decisão.

## Métricas calculadas

- consumo estimado de diesel;
- número de partidas do gerador;
- horas de operação do gerador;
- energia fotovoltaica não aproveitada;
- energia não atendida;
- operação do gerador dentro da faixa ótima;
- SOC médio, mínimo e máximo do BESS.

## Limitações da versão pública

Esta versão tem finalidade de portfólio técnico, documentação metodológica e demonstração de estrutura de código. Ela não substitui o simulador industrial completo e não contém:

- dados reais de operação;
- parâmetros proprietários da PS Soluções;
- modelos treinados;
- detalhes confidenciais de otimização;
- regras industriais fechadas de despacho.

## Autor

Lucas Ribeiro Alves Costa  
Cientista de Dados | Aprendizado de Máquina | Previsão e Otimização  
Portfólio: https://lucasribeirodatascience.github.io/portfolio-lucas-ribeiro/  
LinkedIn: https://www.linkedin.com/in/lucas-ribeiro-datascientist/
