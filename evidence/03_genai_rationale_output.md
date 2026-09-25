# S3 — GenAI Reorder Rationale — Execution Evidence

**Foundation Model:** `databricks-claude-sonnet-5` (Databricks Foundation Model API, `llm/v1/chat`)
**Called from:** notebook `03_ml_genai/03_stockout_model_and_genai.py` via `WorkspaceClient.serving_endpoints.query`
**Output table:** `serverless_stable_xpbmim_catalog.fe_bar_varejo_gold.gold_reorder_rationale`

For the top at-risk SKUs, the model turns the risk score + inventory context into a concise,
business-ready reorder rationale (PT-BR) a store manager can act on. **Real committed model
output below** (queried from the gold table):

```
[L119 / SKU10029 / Bebidas]  risk=100%  lost=R$8,512  order=0un
  -> O SKU10029 está com estoque zerado na loja L119, mas vende em média 87 un/dia — ou seja,
     a loja já perdeu vendas e a ruptura está confirmada (100% de probabilidade)...

[L108 / SKU10055 / Bebidas]  risk=100%  lost=R$6,247  order=133un
  -> **Justificativa – SKU10055 (Bebidas), Loja L108:** O estoque atual está **zerado**, muito
     abaixo do ponto de reposição (114 un), enquanto a venda média é de 50 un/dia — ou seja, a
     ruptura já está em curso e a probabilidade de falta em 7 dias é de **100%**. Isso deve gerar
     uma perda de receita estimada em **R$ 6.247** caso não haja ação imediata.
     **Ação recomendada:** disparar pedido de **133 unidades** hoje, priorizando o lead time de 2 dias...

[L105 / SKU10143 / Higiene]  risk=99%  lost=R$5,188  order=101un
  -> **Risco crítico de ruptura – SKU10143 (Higiene, Loja L105):** com estoque atual de 30 un e
     venda média de 19,9 un/dia, a cobertura é de apenas ~1,5 dia — muito abaixo do lead time de
     6 dias e do ponto de reposição (107 un), resultando em 99% de probabilidade de ruptura nos
     próximos 7 dias. Isso pode gerar perda de receita estimada em R$ 5.188...

[L108 / SKU10208 / Congelados]  risk=100%  lost=R$4,732  order=19un
  -> **Alerta de ruptura — SKU10208 (Congelados) — Loja L108** O estoque atual de 62 un cobre
     apenas ~3,5 dias de venda (média de 17,6 un/dia), enquanto o lead time de reposição é de 5
     dias — ou seja, a loja ficará sem produto antes que um novo pedido chegue, resultando em 100%
     de probabilidade de ruptura e perda estimada de R$ 4.732 em vendas...
```

The rationale grounds every claim in the SKU's own numbers (on-hand, reorder point, velocity,
lead time, risk %, R$ at stake) and ends with a concrete action — this is what surfaces in the
Control Tower app and what the Genie agent can summarize on demand.
