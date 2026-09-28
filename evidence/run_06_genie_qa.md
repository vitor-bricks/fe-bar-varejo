# Genie — natural-language Q&A (executed)

Space `LojaBR · Centro de Abastecimento (Genie)` (`01f1b906cf2d15b4b1c72c3b25ddb2f0`), configured by `05_genie/configure_genie_space.py`
(entity matching on store/product/supplier names, metric definitions, 5 certified example SQLs).
Driver: `05_genie/genie_qa.py` (Genie Conversation API). Q1–Q3 have certified SQL; **Q4–Q6 do not** — they test generalisation.

```text
==========================================================================================
Q1: Quantos itens estão na fila de ação agora?

Genie: Agora, há **188 itens** na fila de ação. Esses **188 itens** somam **R$ 16.174,77** em receita protegida potencial.

SQL gerado:
  SELECT count(*) AS `itens_na_fila`, round(sum(`revenue_protected`), 2) AS `rs_protegido` FROM `serverless_stable_xpbmim_catalog`.`fe_bar_varejo_gold`.`gold_replenishment_queue_final`

Resultado:
  itens_na_fila | rs_protegido
  188 | 16174.77
==========================================================================================
Q2: Qual foi a receita perdida por ruptura nos últimos 7 dias?

Genie: Nos últimos 7 dias, a **receita perdida por ruptura** foi de **R$ 60.330,37**. No mesmo período, a **taxa média de ruptura** foi de **6,5%**, o que ajuda a contextualizar o impacto dessa perda.

SQL gerado:
  SELECT round(sum(`lost_revenue`), 2) AS `receita_perdida_7d`, round(avg(`stockout_rate`), 4) AS `taxa_ruptura_media` FROM `serverless_stable_xpbmim_catalog`.`fe_bar_varejo_gold`.`gold_kpi_daily` WHERE `snapshot_date` > date_sub((SELECT max(`snapshot_date`) FROM `serverless_stable_xpbmim_catalog`.`fe_bar_varejo_gold`.`gold_kpi_daily`), 7)

Resultado:
  receita_perdida_7d | taxa_ruptura_media
  60330.37 | 0.0653
==========================================================================================
Q3: Quais fornecedores atrasam mais?

Genie: Os fornecedores que mais atrasam são os que têm a menor pontualidade de entrega entre os 9 fornecedores retornados. Alguns dos piores resultados são:
- **Limpa Mais Distribuidora** — pontualidade de **62,7%**, com **1.681** pedidos recebidos e atraso médio de **3,91 dias** quando há atraso
- **Higiene & Cia Distribuidora** — pontualidade de **68,1%**, com **1.761** pedidos recebidos e atraso médio de **3,49 dias**
- **Laticínios Serra Azul** — pontualidade de **70,6%**, com **2.311** pedidos recebidos e atraso médio de **1,99 dia**
- **Frios Paraná Logística** — pontualidade de **74,8%**, com **3.304** pedidos recebidos e atraso médio de **2,48 dias**
- **Distribuidora Tropical Bebidas** — pontualidade de **77,3%**, com **2.917** pedidos recebidos e atraso médio de **2,53 dias**

Entre os 9 fornecedores mostrados, a pontualidade varia de **62,7%** a **95,2%**, e o maior atraso médio quando há atraso também é da **Limpa Mais Distribuidora** (**3,91 dias**).

SQL gerado:
  SELECT `supplier_name`, `orders_received`, `on_time_rate`, `avg_delay_when_late`
  FROM `serverless_stable_xpbmim_catalog`.`fe_bar_varejo_gold`.`gold_supplier_otif`
  ORDER BY `on_time_rate` ASC

Resultado:
  supplier_name | orders_received | on_time_rate | avg_delay_when_late
  Limpa Mais Distribuidora | 1681 | 0.627 | 3.91
  Higiene & Cia Distribuidora | 1761 | 0.6814 | 3.49
  Laticínios Serra Azul | 2311 | 0.7062 | 1.99
  Frios Paraná Logística | 3304 | 0.7479 | 2.48
  Distribuidora Tropical Bebidas | 2917 | 0.7727 | 2.53
  Atacado Central Distribuidora | 3661 | 0.8296 | 2.04
  Hortifruti Vale Verde | 5561 | 0.8815 | 1.0
  CD LojaBR Cajamar (próprio) | 12940 | 0.9398 | 1.48
  Panificação LojaBR (própria) | 3746 | 0.9519 | 1.0
==========================================================================================
Q4: Quais ações estão recomendadas para a loja Asa Sul?

Genie: Para a **LojaBR Asa Sul**, há **9 ações recomendadas** no snapshot mais recente, e **todas são do tipo EXPEDITE** (antecipar pedidos já em trânsito). Exemplos incluem:
- **Feijão Carioca Camil 1kg** — **83 un**, prioridade **37**, risco de ruptura de **61,7%** e **R$ 115,28** protegidos
- **Sabão em Barra Ypê 5un** — **16 un**, prioridade **50**, risco de ruptura de **96,9%** e **R$ 101,20** protegidos
- **Leite Integral Piracanjuba 1L** — **97 un**, prioridade **52**, risco de ruptura de **68,8%** e **R$ 97,23** protegidos
- **Peito de Frango Congelado Sadia (kg)** — **22 un**, prioridade **53**, risco de ruptura de **64,3%** e **R$ 96,12** protegidos
- **Tira Manchas Vanish 450ml** — **10 un**, prioridade **109**, risco de ruptura de **75,1%** e **R$ 50,77** protegidos
As ações se concentram em antecipar pedidos para itens com cobertura muito baixa e risco relevante de ruptura, com valores protegidos entre **R$ 36,91** e **R$ 115,28**.

SQL gerado:
  SELECT action_type, severity, product_name, category, units, from_store_name, transfer_km, eta_days, risk_probability, revenue_at_risk, revenue_protected, priority, rationale
  FROM serverless_stable_xpbmim_catalog.fe_bar_varejo_gold.gold_replenishment_queue_final
  WHERE store_name = 'LojaBR Asa Sul'
    AND snapshot_date = (SELECT max(snapshot_date) FROM serverless_stable_xpbmim_catalog.fe_bar_varejo_gold.gold_replenishment_queue_final)
  ORDER BY priority ASC, revenue_protected DESC

Resultado:
  action_type | severity | product_name | category | units | from_store_name | transfer_km | eta_days | risk_probability | revenue_at_risk | revenue_protected | priority | rationale
  EXPEDITE | CRITICAL | Feijão Carioca Camil 1kg | Mercearia | 83 |  |  | 1 | 0.6168 | 115.28 | 115.28 | 37 | Feijão Carioca Camil 1kg em LojaBR Asa Sul: 0.1 dias de cobertura e 62% de risco de ruptura em 7 dias. O pedido de 83 un de CD LojaBR Cajamar (próprio) chega só em ~1 dias (pontualidade 94%) — cobrar antecipação para 1 dia(s).
  EXPEDITE | CRITICAL | Sabão em Barra Ypê 5un | Limpeza | 16 |  |  | 4 | 0.9694 | 101.2 | 101.2 | 50 | Sabão em Barra Ypê 5un em LojaBR Asa Sul: 0.8 dias de cobertura e 97% de risco de ruptura em 7 dias. O pedido de 16 un de CD LojaBR Cajamar (próprio) chega só em ~5 dias (pontualidade 94%) — cobrar antecipação para 4 dia(s).
  EXPEDITE | CRITICAL | Leite Integral Piracanjuba 1L | Laticínios | 97 |  |  | 1 | 0.6878 | 97.23 | 97.23 | 52 | Leite Integral Piracanjuba 1L em LojaBR Asa Sul: 0.6 dias de cobertura e 69% de risco de ruptura em 7 dias. O pedido de 97 un de CD LojaBR Cajamar (próprio) chega só em ~2 dias (pontualidade 94%) — cobrar antecipação para 1 dia(s).
  EXPEDITE | HIGH | Peito de Frango Congelado Sadia (kg) | Congelados | 22 |  |  | 2 | 0.6434 | 96.12 | 96.12 | 53 | Peito de Frango Congelado Sadia (kg) em LojaBR Asa Sul: 2.2 dias de cobertura e 64% de risco de ruptura em 7 dias. O pedido de 22 un de Frios Paraná Logística chega só em ~4 dias (pontualidade 75%) — cobrar antecipação para 2 dia(s).
  EXPEDITE | MEDIUM | Tira Manchas Vanish 450ml | Limpeza | 10 |  |  | 6 | 0.751 | 50.77 | 50.77 | 109 | Tira Manchas Vanish 450ml em LojaBR Asa Sul: 4.5 dias de cobertura e 75% de risco de ruptura em 7 dias. O pedido de 10 un de Limpa Mais Distribuidora chega só em ~8 dias (pontualidade 63%) — cobrar antecipação para 6 dia(s).
  EXPEDITE | HIGH | Batata Palito McCain 720g | Congelados | 13 |  |  | 2 | 0.6413 | 44.06 | 44.06 | 118 | Batata Palito McCain 720g em LojaBR Asa Sul: 2.3 dias de cobertura e 64% de risco de ruptura em 7 dias. O pedido de 13 un de Frios Paraná Logística chega só em ~4 dias (pontualidade 75%) — cobrar antecipação para 2 dia(s).
  EXPEDITE | CRITICAL | Atum em Óleo Gomes da Costa 170g | Mercearia | 45 |  |  | 1 | 0.5743 | 39.36 | 39.36 | 130 | Atum em Óleo Gomes da Costa 170g em LojaBR Asa Sul: 1.4 dias de cobertura e 57% de risco de ruptura em 7 dias. O pedido de 45 un de Atacado Central Distribuidora chega só em ~2 dias (pontualidade 83%) — cobrar antecipação para 1 dia(s).
  EXPEDITE | CRITICAL | Água com Gás São Lourenço 300ml | Bebidas | 46 |  |  | 1 | 0.8518 | 38.65 | 38.65 | 131 | Água com Gás São Lourenço 300ml em LojaBR Asa Sul: 0.3 dias de cobertura e 85% de risco de ruptura em 7 dias. O pedido de 46 un de CD LojaBR Cajamar (próprio) chega só em ~2 dias (pontualidade 94%) — cobrar antecipação para 1 dia(s).
  EXPEDITE | MEDIUM | Hidratante Nivea Milk 400ml | Higiene | 8 |  |  | 6 | 0.7412 | 36.91 | 36.91 | 137 | Hidratante Nivea Milk 400ml em LojaBR Asa Sul: 5.2 dias de cobertura e 74% de risco de ruptura em 7 dias. O pedido de 8 un de Higiene & Cia Distribuidora chega só em ~7 dias (pontualidade 68%) — cobrar antecipação para 6 dia(s).
==========================================================================================
Q5: Qual a taxa de ruptura por categoria no último mês?

Genie: No último mês, a maior taxa de ruptura foi em **Limpeza (12,5%)**, seguida por **Higiene (11,3%)** e **Congelados (10,1%)**; a menor foi em **Padaria (0,8%)**. Exemplos incluem:
- **Limpeza:** **12,5%**
- **Higiene:** **11,3%**
- **Congelados:** **10,1%**
- **Mercearia:** **6,2%**
- **Padaria:** **0,8%**

Entre as 8 categorias retornadas, a ruptura varia de **0,8%** a **12,5%**, com itens não alimentares liderando os maiores índices.

SQL gerado:
  SELECT `category`, 100 * AVG(`stockout_flag`) AS `taxa_ruptura_pct` FROM `serverless_stable_xpbmim_catalog`.`fe_bar_varejo_gold`.`gold_daily_store_sku` WHERE `snapshot_date` BETWEEN date_sub((SELECT max(`snapshot_date`) FROM `serverless_stable_xpbmim_catalog`.`fe_bar_varejo_gold`.`gold_kpi_daily`), 29) AND (SELECT max(`snapshot_date`) FROM `serverless_stable_xpbmim_catalog`.`fe_bar_varejo_gold`.`gold_kpi_daily`) AND `category` IS NOT NULL GROUP BY `category` ORDER BY `taxa_ruptura_pct` DESC

Resultado:
  category | taxa_ruptura_pct
  Limpeza | 12.461538461538462
  Higiene | 11.273809523809524
  Congelados | 10.055555555555555
  Mercearia | 6.166666666666667
  Laticínios | 5.377777777777778
  Bebidas | 5.166666666666667
  Hortifruti | 1.6018518518518519
  Padaria | 0.7777777777777778
==========================================================================================
Q6: Quanto de receita a fila protege por região?

Genie: A fila protege mais receita no **Sudeste**, com **R$ 10.003,19** em **109 itens**, e menos no **Norte**, com **R$ 1.161,29** em **17 itens**. Todas as 5 regiões retornadas foram:
- **Sudeste**: **R$ 10.003,19** protegidos em **109 itens**
- **Centro-Oeste**: **R$ 1.821,36** protegidos em **21 itens**
- **Nordeste**: **R$ 1.648,62** protegidos em **19 itens**
- **Sul**: **R$ 1.540,31** protegidos em **22 itens**
- **Norte**: **R$ 1.161,29** protegidos em **17 itens**

Pelos dados, o **Sudeste** concentra de longe a maior parcela da receita protegida e também o maior volume de itens na fila.

SQL gerado:
  SELECT `region`, COUNT(*) AS `itens_na_fila`, ROUND(SUM(`revenue_protected`), 2) AS `receita_protegida` FROM `serverless_stable_xpbmim_catalog`.`fe_bar_varejo_gold`.`gold_replenishment_queue_final` WHERE `snapshot_date` = (SELECT MAX(`snapshot_date`) FROM `serverless_stable_xpbmim_catalog`.`fe_bar_varejo_gold`.`gold_replenishment_queue_final`) AND `region` IS NOT NULL GROUP BY `region` ORDER BY `receita_protegida` DESC

Resultado:
  region | itens_na_fila | receita_protegida
  Sudeste | 109 | 10003.19
  Centro-Oeste | 21 | 1821.36
  Nordeste | 19 | 1648.62
  Sul | 22 | 1540.31
  Norte | 17 | 1161.29
==========================================================================================
```
