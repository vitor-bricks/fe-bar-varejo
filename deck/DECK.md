# LojaBR · Centro de Abastecimento — deck de negócio (versão em texto)

> PDF: `LojaBR_Centro_de_Abastecimento.pdf` · English: `DECK_EN.md` / `LojaBR_Replenishment_Center_EN.pdf`
> Público: **VP de Operações & Supply Chain** (patrocinador) e **Gerente de Reposição** (dono do domínio).
> Dados 100% sintéticos. Todos os números vêm do run de evidência de 28/09/2026 (`evidence/`).

---

## 1. Recuperar até R$ 0,8 mi por ano em vendas que hoje somem da gôndola

O Centro de Abastecimento avisa **2,9 dias antes** que um item vai faltar. A ação mais barata para cada caso chega pronta, e o gerente de reposição aprova **em um clique**.

- **Hoje:** 4,1% da venda se perde por ruptura, ou R$ 2,39 mi/ano na amostra.
- **Na rede:** ~R$ 1,4 mi recuperáveis a cada R$ 100 mi de venda (⅓ da perda).
- **O pedido:** piloto de 30 dias em 4 lojas, com 4 lojas de controle.

## 2. Resumo executivo

| | |
|---|---|
| **O problema** | 4,1% da venda some por ruptura: R$ 2,39 mi por ano só em 129 itens de alto giro, nas 20 lojas. O time descobre **depois** que a gôndola esvaziou. |
| **A solução** | Um modelo aponta quais itens vão faltar nos próximos 7 dias. Um agente de IA confere os fatos e propõe a ação mais barata: transferir, antecipar ou pedido urgente. O gerente aprova em um clique. Tudo numa única plataforma, a Databricks. |
| **O valor** | Até ⅓ da perda recuperada: R$ 0,4 a 0,8 mi por ano na amostra, conforme a execução. Na rede inteira, R$ 0,7 a 1,4 mi a cada R$ 100 mi de venda. |
| **O pedido** | Piloto de 30 dias em 4 lojas, com 4 lojas de controle. A decisão de escalar sai dos números da própria LojaBR, não de uma projeção. |

## 3. O problema, em reais

- **4,1%** da venda perdida por ruptura, ou **R$ 2,39 mi/ano** em 129 itens × 20 lojas.
- Disponibilidade em gôndola de **93,5%** nos últimos 7 dias (ruptura de 6,5%, por loja × item × dia).
- A perda é concentrada. Por categoria (120 dias; média da rede de 5,3%): Limpeza 11,3%, Higiene 9,2%, Congelados 8,1%, Mercearia 5,2%, Bebidas 4,5%, Laticínios 4,2%, Hortifruti 1,2% e Padaria 0,6%.
- Os fornecedores de Limpeza e Higiene entregam no prazo só **63% e 68%** das vezes.

## 4. Os KPIs do comprador

| KPI | Hoje | Com o Centro de Abastecimento | Quem acompanha |
|---|---|---|---|
| Disponibilidade em gôndola | 93,5% | ≥ 95,5% | VP de Operações |
| Taxa de ruptura (loja × item × dia) | 6,5% | < 4,5% | VP e gerente |
| Venda perdida por ruptura | 4,1% · R$ 2,39 mi/ano | até −⅓ · ≈ R$ 0,8 mi/ano de volta | VP e financeiro |
| Aviso antes de a gôndola esvaziar | nenhum (reativo) | ~2,9 dias · 75% com ≥ 2 dias | Gerente de reposição |
| Itens para revisar por dia | 29% do sortimento · 38% de acerto | 8% · 84% de acerto | Gerente de reposição |

Regra de bolso: a cada R$ 100 mi de venda, ~R$ 4 mi se perdem em ruptura. Recuperar um terço vale ~R$ 1,4 mi.

## 5. O que muda para cada um

**Patrocinador: VP de Operações & Supply Chain**
- **Venda de volta no P&L:** ≈ R$ 0,8 mi/ano na amostra, ou ~R$ 1,4 mi a cada R$ 100 mi de venda.
- **Estoque parado vira venda:** 39 transferências num único dia usaram o excesso de outra loja, sem compra nova.
- **Risco sob controle:** quem decide é o gerente, e cada decisão fica registrada com autor e horário.
- **Escala sem projeto novo:** a mesma plataforma cobre a rede toda e novas categorias.

**Dono do domínio: Gerente de Reposição**
- **Uma lista curta:** 8% dos itens, 3,6× menos que a regra atual, ordenada por R$ ou por criticidade.
- **2,9 dias de aviso:** tempo de transferir ou antecipar o pedido, em vez de apagar incêndio.
- **A justificativa pronta:** estoque, loja doadora e pontualidade do fornecedor no próprio card.
- **Um clique aprova,** e as perguntas sobre os dados vão ao Genie, em português, sem abrir chamado.

## 6. Uma fila de ação, não um relatório

1. **Abre a fila às 7h.** Todas as ações do dia, ordenadas por R$ protegido ou pelo que esvazia primeiro.
2. **Lê o card.** Produto, loja, a ação mais barata, a justificativa do agente e o R$ em jogo.
3. **Aprova com um clique.** A decisão vai para o banco com o nome dele, e o "R$ protegido hoje" sobe na tela.

As ações são três: **transferir** de uma loja próxima com excesso, **antecipar** o pedido que já está a caminho, ou fazer um **pedido urgente** quando não há alternativa. *(Captura do app: `img/card.png`.)*

## 7. Estoque parado numa loja resolve a falta na outra

- **39 transferências** sugeridas num único dia, com o excesso de outras lojas.
- Só a até **450 km** e sem deixar a doadora com menos de **10 dias** de estoque.
- Chegam em **1 a 2 dias**, antes do pedido do fornecedor.
- O mapa mostra a ruptura por loja e as rotas. Um clique abre a loja e as ações dela. *(Captura do app: `img/map.png`.)*

## 8. O modelo acerta mais que o dobro da regra atual

- **84%** de acerto na lista diária, contra **38%** da regra "cobertura < prazo de entrega".
- **2,9 dias** de antecedência, com 75% dos alertas chegando 2 dias antes ou mais.
- **AUC 0,85**, validado em datas que o modelo não viu.
- A lista tem **8%** dos itens em gôndola; a regra marcaria 29%.
- O agente consulta a posição do item, as lojas vizinhas e o histórico do fornecedor antes de recomendar. Se tentar decidir antes, o sistema rejeita a decisão.

> "A LojaBR Campinas tem apenas 9 unidades em estoque (cobertura de 0,6 dia) e o pedido de reposição só chega em 2 dias. A LojaBR Ribeirão Preto, a 207 km, possui excedente de 61 unidades, permitindo transferir 46 unidades sem comprometer seu próprio estoque."
> — Café Pilão 500g, run de evidência de 28/09/2026

## 9. Quanto vale, conforme a execução

| Ações aprovadas e executadas no prazo | 50% | 75% | 100% |
|---|---|---|---|
| Venda protegida por semana · amostra | R$ 8,1 mil | R$ 12,1 mil | R$ 16,2 mil |
| Por ano · amostra (129 itens × 20 lojas) | R$ 0,42 mi | R$ 0,63 mi | R$ 0,84 mi |
| Parcela da perda anual recuperada | 18% | 26% | 35% |
| **A cada R$ 100 mi de venda na rede** | **R$ 0,7 mi** | **R$ 1,1 mi** | **R$ 1,4 mi** |

- **Base:** a fila de um dia (run de 28/09) protege R$ 16,2 mil nos 7 dias seguintes, ≈ 27% da perda da semana anterior.
- **Premissas:** é valor **esperado** (ponderado pelo risco), não garantido; a amostra é de itens de alto giro; o custo da plataforma (serverless, pago pelo uso) é medido no piloto.

## 10. Do dado bruto à decisão, num único job diário

```
Ingestão → Medallion → Governança → Modelo → Agente → Serving → Linguagem natural → Decisão
Auto Loader  bronze→gold  Unity Catalog  MLflow·UC  FMAPI·tools  Lakebase  Genie     este app
```

- **Um job, todo dia às 06:00.** Ingestão, qualidade, modelo, agente e publicação para o app rodam juntos, com um único registro de execução.
- **Governado no Unity Catalog.** Linhagem de cada número, 7 regras de qualidade (0 falhas no último run) e acesso mínimo para o app.
- **Sem cópia, sem planilha.** O mesmo dado alimenta o app, o Genie e o modelo. Cada estágio abre no workspace direto do app.

## 11. Por que Databricks: o que a plataforma muda no resultado

| | Com ferramentas separadas | Com Databricks |
|---|---|---|
| **Integração** | ETL, data warehouse, ML, banco operacional, LLM, BI e hospedagem do app: 7 peças para integrar e manter | Uma plataforma: Lakeflow, Unity Catalog, MLflow, Foundation Model API, Lakebase, Genie e Apps |
| **O número** | Cópias entre sistemas; o R$ do app nem sempre bate com o do relatório | Um dado governado: o app, o Genie e o modelo leem o mesmo número, com linhagem |
| **Tempo até o piloto** | Meses de integração e uma revisão de segurança por ferramenta | O protótipo já roda ponta a ponta; o piloto leva 30 dias |
| **Segurança** | Permissões e auditoria espalhadas em cada ferramenta | Um lugar só: quem vê o quê, e quem aprovou cada ação |
| **Custo** | Licenças e infraestrutura fixas, rodando ou não | Serverless: a jornada inteira roda em **8,4 min por dia** e só esse tempo é cobrado |

Os mesmos dados já servem os próximos casos: **previsão de demanda**, **markdown do excesso de estoque** e **sortimento por loja**.

## 12. Piloto de 30 dias: risco controlado, resultado medido

| Quando | O que acontece | Como medimos |
|---|---|---|
| Semana 1 | Conectar vendas, estoque e pedidos das 4 lojas-piloto | dados chegando todo dia, qualidade ≥ 99% |
| Semanas 2–4 | Fila de ação nas 4 lojas; 4 lojas parecidas como controle | ruptura e venda perdida, piloto contra controle |
| Fim | Decisão de escalar | R$ recuperado por loja, comparado ao custo |

- **Critério de sucesso:** ruptura nas lojas-piloto ≥ 1,5 p.p. abaixo do controle, e R$ recuperado maior que o custo da plataforma.
- **Riscos e mitigação:**
  - *Modelo errar:* a lista é priorizada por R$ e o gerente decide.
  - *Adoção:* um clique, dentro da rotina da manhã.
  - *Dado de fornecedor incompleto:* o agente declara a confiança e a regra cobre o resto.

## 13. O pedido

**Patrocinar um piloto de 30 dias em 4 lojas, com grupo de controle.** Medir ruptura e venda recuperada com os números da própria LojaBR, e decidir a escala com base neles.

- **Semana 0 (patrocinador):** escolher as 4 lojas-piloto e as 4 de controle.
- **Semana 1 (TI LojaBR + Databricks):** liberar os feeds de vendas, estoque e pedidos.
- **Semana 4 (comitê):** decidir a escala com o resultado medido na mão.

---

### Apêndice: para o time técnico
- **Lakeflow Declarative Pipelines:** Auto Loader em 7 feeds brutos; medallion com 7 expectativas de qualidade e 0 falhas no último run.
- **Modelo:** gradient boosting com features *point-in-time* (pedido em aberto com a chegada **prevista**, não a real); AUC 0,85; registrado no Unity Catalog via MLflow.
- **Agente:** tool-calling na Foundation Model API. Consulta 3 ferramentas, e o sistema rejeita qualquer decisão tomada antes da consulta.
- **Lakebase:** schema `serving` publicado de forma atômica e schema `app` com aprovações e log do Genie; leitura em ~3 ms.
- **Genie:** entity matching, definições de métrica e 5 SQL certificados.
- **App:** React + TypeScript / FastAPI, service principal com acesso mínimo.
- **Evidência em texto:** github.com/vitor-bricks/fe-bar-varejo → `evidence/`
