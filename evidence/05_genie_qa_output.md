# S5 — Genie (Natural-Language Querying) — Execution Evidence

**Genie Space:** `LojaBR Varejo · Genie (Ruptura & Disponibilidade)` (id `01f1b906cf2d15b4b1c72c3b25ddb2f0`)
**Tables:** `gold_kpi_daily`, `gold_daily_store_sku`, `gold_current_availability`, `gold_stockout_predictions`
**Driver:** `05_genie/genie_qa.py` (Genie Conversation API, PT-BR questions)

Real committed Genie output below — for each question: the natural-language answer, the SQL
Genie generated, and the result rows. This is the queryable layer a business user talks to.

```
==========================================================================================
Q1: Qual foi a taxa de ruptura media dos ultimos 7 dias e a receita perdida total no periodo?

Genie: Nos últimos 7 dias, a **taxa média de ruptura** foi de **6,78%** e a **receita perdida total** no período foi de **R$ 209.032,70**. Como o resultado consolida 7 dias em 1 linha, isso indica uma perda relevante no período junto com uma ruptura média acima de **6%**.

SQL gerado:
  SELECT AVG(`stockout_rate`) AS `taxa_ruptura_media_7d`, SUM(`lost_revenue`) AS `receita_perdida_total_7d` FROM `serverless_stable_xpbmim_catalog`.`fe_bar_varejo_gold`.`gold_kpi_daily` WHERE `snapshot_date` BETWEEN date_sub(current_date(), 6) AND current_date()

Resultado:
  taxa_ruptura_media_7d | receita_perdida_total_7d
  0.06780000000000001 | 209032.69999999998
==========================================================================================
Q2: Quais as 5 lojas com maior receita perdida por ruptura no total do periodo?

Genie: As **5 lojas com maior receita perdida por ruptura** no total do período são:
- **L119**: **R$ 314.545,33**
- **L106**: **R$ 300.748,44**
- **L105**: **R$ 290.282,85**
- **L108**: **R$ 223.581,19**
- **L103**: **R$ 182.158,63**

Entre essas 5 lojas, a maior perda foi da **L119**, e a menor do grupo foi da **L103**.

SQL gerado:
  WITH `lojas_receita_perdida` AS (
    SELECT
      `store_id`,
      SUM(`lost_revenue`) AS `receita_perdida_total`
    FROM `serverless_stable_xpbmim_catalog`.`fe_bar_varejo_gold`.`gold_daily_store_sku`
    WHERE `store_id` IS NOT NULL
      AND `lost_revenue` IS NOT NULL
    GROUP BY `store_id`
  ), `ranking_lojas` AS (
    SELECT
      `store_id`,
      `receita_perdida_total`,
      RANK() OVER (ORDER BY `receita_perdida_total` DESC) AS `posicao`
    FROM `lojas_receita_perdida`
  )
  SELECT
    `store_id`,
    `receita_perdida_total` AS `receita_perdida_total_rs`,
    `posicao`
  FROM `ranking_lojas`
  WHERE `posicao` <= 5
  ORDER BY `receita_perdida_total` DESC, `store_id` ASC

Resultado:
  store_id | receita_perdida_total_rs | posicao
  L119 | 314545.3300000003 | 1
  L106 | 300748.4400000004 | 2
  L105 | 290282.84999999986 | 3
  L108 | 223581.18999999997 | 4
  L103 | 182158.63000000038 | 5
==========================================================================================
Q3: Quais categorias tem a maior taxa de ruptura?

Genie: A categoria com a **maior taxa de ruptura** é **Higiene**, com **7,58487654320988%**. No resultado retornado, **Higiene** aparece como a categoria líder em ruptura entre as categorias analisadas.

SQL gerado:
  WITH category_rates AS (
    SELECT
      `category`,
      try_divide(100.0 * SUM(CASE WHEN `stockout_flag` = 1 THEN 1 ELSE 0 END),COUNT(*)) AS `stockout_rate_pct`
    FROM `serverless_stable_xpbmim_catalog`.`fe_bar_varejo_gold`.`gold_daily_store_sku`
    WHERE `category` IS NOT NULL
    GROUP BY `category`
  ), ranked AS (
    SELECT
      `category`,
      `stockout_rate_pct`,
      RANK() OVER (ORDER BY `stockout_rate_pct` DESC) AS `rnk`
    FROM category_rates
  )
  SELECT
    `category`,
    `stockout_rate_pct`
  FROM ranked
  WHERE `rnk` = 1
  ORDER BY `category` ASC

Resultado:
  category | stockout_rate_pct
  Higiene | 7.58487654320988
==========================================================================================
Q4: Quantos itens estao atualmente em risco de ruptura (risk_flag = 1)?

Genie: Atualmente, há **2.393 itens** com **risk_flag = 1**, ou seja, marcados como em risco de ruptura. Com base no resultado retornado, o total de itens em risco neste momento é **2.393**.

SQL gerado:
  SELECT COUNT(*) AS `itens_em_risco`
  FROM `serverless_stable_xpbmim_catalog`.`fe_bar_varejo_gold`.`gold_current_availability`
  WHERE `risk_flag` = 1

Resultado:
  itens_em_risco
  2393
==========================================================================================
Q5: Liste os 5 itens com maior receita perdida esperada nos proximos 7 dias, com a loja e o pedido sugerido.

Genie: Os **5 itens com maior receita perdida esperada nos próximos 7 dias** são:
- **Loja L119** — **SKU10029** — pedido sugerido: **0** unidades — receita perdida esperada: **R$ 8.511,61**
- **Loja L108** — **SKU10055** — pedido sugerido: **133** unidades — receita perdida esperada: **R$ 6.246,88**
- **Loja L108** — **SKU10090** — pedido sugerido: **31** unidades — receita perdida esperada: **R$ 6.035,94**
- **Loja L105** — **SKU10143** — pedido sugerido: **101** unidades — receita perdida esperada: **R$ 5.188,13**
- **Loja L112** — **SKU10054** — pedido sugerido: **3** unidades — receita perdida esperada: **R$ 4.915,87**

Entre esses 5 itens, a maior perda esperada está na **Loja L119 / SKU10029**, e a **Loja L108** aparece duas vezes entre os maiores riscos financeiros.

SQL gerado:
  WITH ranked_items AS (
    SELECT
      `store_id`,
      `sku`,
      `suggested_order_units`,
      `expected_lost_revenue_7d`,
      RANK() OVER (ORDER BY `expected_lost_revenue_7d` DESC) AS `rnk`
    FROM `serverless_stable_xpbmim_catalog`.`fe_bar_varejo_gold`.`gold_stockout_predictions`
    WHERE `expected_lost_revenue_7d` IS NOT NULL
      AND `store_id` IS NOT NULL
      AND `sku` IS NOT NULL
      AND `suggested_order_units` IS NOT NULL
  )
  SELECT
    `store_id`,
    `sku`,
    `suggested_order_units`,
    `expected_lost_revenue_7d`
  FROM ranked_items
  WHERE `rnk` <= 5
  ORDER BY `expected_lost_revenue_7d` DESC, `store_id`, `sku`

Resultado:
  store_id | sku | suggested_order_units | expected_lost_revenue_7d
  L119 | SKU10029 | 0 | 8511.61
  L108 | SKU10055 | 133 | 6246.88
  L108 | SKU10090 | 31 | 6035.94
  L105 | SKU10143 | 101 | 5188.13
  L112 | SKU10054 | 3 | 4915.87
==========================================================================================
Q6: Qual a receita perdida por regiao no total do periodo?

Genie: A receita perdida total no período foi maior no **Nordeste** e menor no **Norte**. Exemplos incluem:
- **Nordeste**: **R$ 1.224.813,28**
- **Sudeste**: **R$ 771.791,52**
- **Centro-Oeste**: **R$ 546.468,57**
- **Sul**: **R$ 427.529,52**
- **Norte**: **R$ 290.282,85**

Entre as 5 regiões retornadas, o **Nordeste** concentra a maior perda de receita, bem acima das demais.

SQL gerado:
  SELECT `region`, SUM(COALESCE(`lost_revenue`, 0)) AS `total_lost_revenue` FROM `serverless_stable_xpbmim_catalog`.`fe_bar_varejo_gold`.`gold_daily_store_sku` WHERE `region` IS NOT NULL GROUP BY `region` ORDER BY `total_lost_revenue` DESC, `region` ASC

Resultado:
  region | total_lost_revenue
  Nordeste | 1224813.2799999975
  Sudeste | 771791.5200000007
  Centro-Oeste | 546468.5699999986
  Sul | 427529.51999999856
  Norte | 290282.84999999986
==========================================================================================
```
