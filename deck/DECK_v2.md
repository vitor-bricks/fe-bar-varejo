# LojaBR · Centro de Abastecimento — deck de negócio v2 (versão em texto)

> PDF: `LojaBR_Centro_de_Abastecimento_v2.pdf` · English: `DECK_EN_v2.md` / `LojaBR_Replenishment_Center_EN_v2.pdf`
> Público: **VP de Operações & Supply Chain** (patrocinador) e **Gerente de Reposição** (dono do domínio).
> **De onde vêm os números:** um protótipo que já roda na Databricks, sobre o histórico de 120 dias das 20 lojas, nos 129 itens de maior giro. Valores do run de 28/09/2026; custo medido nas tabelas de billing (`evidence/run_08_platform_cost.md`). O piloto mede o resultado na operação das lojas.

---

## 1. Recuperar até R$ 0,8 mi por ano em vendas que hoje somem da gôndola

O Centro de Abastecimento avisa **2,9 dias antes** que um item vai faltar. A ação mais barata para cada caso chega pronta, e o gerente de reposição aprova **em um clique**.

- **Hoje:** 4,1% da venda se perde por ruptura, R$ 2,39 mi/ano nos itens de maior giro.
- **Na rede:** ~R$ 1,4 mi recuperáveis a cada R$ 100 mi de venda (⅓ da perda).
- **O pedido:** piloto de 30 dias em 4 lojas, com 4 lojas de controle.

## 2. Resumo executivo

| | |
|---|---|
| **O problema** | Nos 129 itens de maior giro das 20 lojas, 4,1% da venda some por ruptura: R$ 2,39 mi por ano, em linha com os ~4% do varejo. O time descobre depois que a gôndola esvaziou. |
| **A solução** | Um modelo aponta quais itens vão faltar nos próximos 7 dias. Um agente de IA confere os fatos e propõe a ação mais barata: transferir, antecipar ou pedido urgente. O gerente aprova em um clique. Tudo numa única plataforma, a Databricks. |
| **O valor** | Até ⅓ da perda recuperada: R$ 0,4 a 0,8 mi por ano nesses itens, conforme a execução; R$ 0,7 a 1,4 mi a cada R$ 100 mi de venda. Custo medido da plataforma: ~US$ 440 por mês, a preço de lista. |
| **O pedido** | Piloto de 30 dias em 4 lojas, com 4 lojas de controle. |

## 3. O problema, em reais (últimos 120 dias)

- 4,1% da venda perdida; R$ 2,39 mi/ano (20 lojas × 129 itens); disponibilidade de 93,5% nos últimos 7 dias; o pior fornecedor entrega no prazo 63% das vezes.
- Histórico de 120 dias de vendas, estoque e pedidos das 20 lojas, nos 129 itens de maior giro.
- A perda é concentrada. Por categoria (média de 5,3%): Limpeza 11,3%, Higiene 9,2%, Congelados 8,1%, Mercearia 5,2%, Bebidas 4,5%, Laticínios 4,2%, Hortifruti 1,2% e Padaria 0,6%. Os fornecedores de Limpeza e Higiene entregam no prazo 63% e 68% das vezes.

## 4. Os KPIs do comprador (faixa de 50% a 100% das ações executadas)

| KPI | Hoje | Com o Centro | Quem acompanha |
|---|---|---|---|
| Disponibilidade em gôndola | 93,5% | 94,7% a 95,8% | VP de Operações |
| Taxa de ruptura (loja × item × dia) | 6,5% | 5,3% a 4,2% | VP e gerente |
| Venda perdida por ruptura | 4,1% · R$ 2,39 mi/ano | −18% a −35% · R$ 0,42 a 0,84 mi/ano de volta | VP e financeiro |
| Aviso antes de a gôndola esvaziar | nenhum | ~2,9 dias · 75% com ≥ 2 dias | Gerente de reposição |
| Itens para revisar por dia | 29% · 38% de acerto | 8% · 84% de acerto | Gerente de reposição |

Premissa: a ruptura cai na mesma proporção da venda recuperada.

## 5. O que muda para cada um

**Patrocinador: VP de Operações & Supply Chain**
- **Venda de volta no P&L:** R$ 0,42 a 0,84 mi/ano nos itens de maior giro, ~R$ 1,4 mi a cada R$ 100 mi de venda.
- **O valor sai barato:** 80% dele vem de antecipar pedidos que já estão a caminho, sem compra nova nem frete.
- **Risco sob controle:** quem decide é o gerente, e cada decisão fica registrada com autor e horário.
- **Custo medido:** ~US$ 440 por mês para rodar tudo, a preço de lista.

**Dono do domínio: Gerente de Reposição**
- **Uma lista curta:** 8% dos itens, 3,6× menos que a regra atual, ordenada por R$ ou por criticidade.
- **2,9 dias de aviso:** tempo de transferir ou antecipar, em vez de apagar incêndio.
- **A justificativa pronta:** estoque, loja doadora e pontualidade do fornecedor no card.
- **Um clique aprova,** e as perguntas vão ao Genie, em português, sem abrir chamado.

## 6. Uma fila de ação, não um relatório

1. Abre a fila às 7h: todas as ações do dia, ordenadas por R$ protegido ou pelo que esvazia primeiro.
2. Lê o card: produto, loja, a ação mais barata, a justificativa do agente e o R$ em jogo.
3. Aprova com um clique, e o "R$ protegido hoje" sobe na tela.

**Depois do clique.** *No protótipo:* a decisão fica gravada na Lakebase com autor e horário. *No piloto:* a ordem segue para o ERP da LojaBR, por API ou arquivo de integração, e essa integração é o escopo da semana 1. *(Captura: `img/card.png`.)*

## 7. Estoque parado numa loja resolve a falta na outra

- 39 transferências sugeridas num único dia. Só a até 450 km, sem deixar a doadora com menos de 10 dias de estoque, e chegando em 1 a 2 dias.
- **Quando a transferência compensa:** cada uma protege, em média, **R$ 74**. Só compensa se o frete marginal custar menos que isso. Por isso, no piloto, transferimos só em rotas que já existem (como a entrega do CD) ou agrupando os itens do mesmo par de lojas.
- As transferências são 18% do valor. A maior parte, 80%, vem de antecipar pedidos que já estão a caminho. *(Captura: `img/map.png`.)*

## 8. O modelo acerta mais que o dobro da regra atual

- **84%** de acerto na lista diária, contra 38% da regra "cobertura < prazo de entrega".
- **2,9 dias** de antecedência: 3.691 alertas corretos no teste, 75% deles com 2 dias ou mais.
- **AUC 0,85**, validado em 49.733 casos de 4 semanas que o modelo não viu.
- A lista tem **8%** dos itens; a regra marcaria 29%.
- **E quando ele erra?** Um alerta errado não vira perda. A doadora continua com ao menos 10 dias de estoque, e o item transferido vende no destino. O prejuízo máximo é o frete.
- **Como ele se mantém bom:** o modelo é re-treinado todo dia no mesmo job, com uma nova versão no Unity Catalog. O agente consulta os fatos antes de recomendar, e o sistema rejeita decisões sem essa consulta.

## 9. Quanto vale, conforme a execução, e quanto custa

| Ações aprovadas e executadas no prazo | 50% | 75% | 100% |
|---|---|---|---|
| Venda protegida por semana | R$ 8,1 mil | R$ 12,1 mil | R$ 16,2 mil |
| Por ano · 20 lojas × 129 itens | R$ 0,42 mi | R$ 0,63 mi | R$ 0,84 mi |
| Parcela da perda anual recuperada | 18% | 26% | 35% |
| **A cada R$ 100 mi de venda na rede** | **R$ 0,7 mi** | **R$ 1,1 mi** | **R$ 1,4 mi** |
| Custo medido da plataforma (preço de lista) | ~US$ 440 por mês em qualquer cenário | | |

**De onde vem o valor da fila de um dia:**

| Ação | Quantidade | Valor | Participação |
|---|---|---|---|
| Antecipar | 142 | R$ 12,9 mil | 80% |
| Transferir | 39 | R$ 2,9 mil | 18% |
| Pedido urgente | 7 | R$ 0,4 mil | 2% |

**Premissas:**
- É valor esperado (ponderado pelo risco), não garantido.
- A base é a fila do run de 28/09.
- A conta cobre só os itens de maior giro.
- O frete das transferências fica fora da conta; por isso existe a regra de rota.

## 10. Do dado bruto à decisão, num único job diário

- Um job, todo dia às 06:00: com o dado até ontem, a fila fica pronta antes de a loja abrir. Tudo roda em 8,4 min.
- Governado no Unity Catalog: linhagem, 7 regras de qualidade (0 falhas) e acesso mínimo para o app.
- Sem cópia, sem planilha: o mesmo dado alimenta o app, o Genie e o modelo, e cada estágio abre no workspace direto do app.
- Todo número é rastreável: `evidence/`, incluindo as consultas de custo.

## 11. Por que Databricks: o que a plataforma muda no resultado

| | Com ferramentas separadas | Com Databricks |
|---|---|---|
| **Integração** | 7 peças para integrar e manter | Uma plataforma: Lakeflow, Unity Catalog, MLflow, Foundation Model API, Lakebase, Genie e Apps |
| **O número** | Cópias entre sistemas | Um dado governado, com linhagem |
| **Tempo até o piloto** | Meses de integração e revisões de segurança | O protótipo já roda; o piloto leva 30 dias |
| **Segurança** | Espalhada em cada ferramenta | Um lugar só: quem vê o quê, e quem aprovou cada ação |
| **Custo** | Licenças fixas | Medido: ~US$ 440/mês; a jornada em lote custa US$ 0,52/dia |
| **Saída** | Formatos fechados | Formatos abertos: Delta (e Iceberg via UniForm), Postgres padrão, MLflow e código em Git |

Próximos casos sobre os mesmos dados: previsão de demanda, markdown do excesso de estoque e sortimento por loja.

## 12. Piloto de 30 dias

| Quando | O que acontece | Como medimos |
|---|---|---|
| Semana 1 | Conectar vendas, estoque e pedidos das 4 lojas-piloto; integrar a aprovação ao ERP | dados chegando todo dia, qualidade ≥ 99% |
| Semanas 2–4 | Fila de ação nas 4 lojas; 4 lojas parecidas como controle | ruptura e venda perdida, piloto contra controle |
| Fim | Decisão de escalar | R$ recuperado por loja, comparado ao custo |

- **Critério de sucesso:** ruptura acumulada das semanas 2–4 pelo menos 1,5 p.p. abaixo do controle, e R$ recuperado maior que o custo.
- **Escolha das lojas:** 4 lojas com ruptura acima da média, em 2 regiões e 2 formatos. O controle é pareado por formato, região e ruptura e vive o mesmo mês, então sazonalidade e promoções se anulam.
- **Riscos e mitigação:**
  - *Modelo errar:* o gerente decide.
  - *Adoção:* um clique, na rotina da manhã.
  - *Frete:* só em rota existente.
  - *Dado de fornecedor incompleto:* a regra cobre.

## 13. O pedido

**Patrocinar um piloto de 30 dias em 4 lojas, com grupo de controle.** Medir nas lojas e decidir a escala com base nesses números. A plataforma custa ~US$ 440 por mês a preço de lista.

- **Semana 0 (patrocinador):** escolher as lojas.
- **Semana 1 (TI LojaBR + Databricks):** liberar os feeds e a integração da aprovação com o ERP.
- **Semana 4 (comitê):** decidir a escala.

---

### A1. Apêndice técnico
- **Lakeflow:** Auto Loader em 7 feeds; medallion com 7 expectativas e 0 falhas.
- **Modelo:** gradient boosting com features *point-in-time*; treino em 153 mil casos e teste em 49,7 mil de datas posteriores; AUC 0,85; re-treinado a cada run.
- **Agente:** tool-calling na Foundation Model API, com 3 ferramentas e rejeição de decisões sem consulta prévia.
- **Lakebase:** `serving` publicado de forma atômica e `app` com aprovações, rejeições e log do Genie; leitura em ~3 ms.
- **Genie:** entity matching, métricas e 5 SQL certificados.
- **App:** React + TypeScript / FastAPI, service principal com acesso mínimo e login via SSO do workspace.

### A2. Custo medido e operação (29/09/2026, só o run agendado, preço de lista)

| Componente | Consumo | US$/dia |
|---|---|---|
| Job serverless (4 tarefas) | 0,35 DBU | 0,16 |
| Pipeline Lakeflow | 0,39 DBU | 0,17 |
| Agente (LLM, 24 chamadas) | 2,72 DBU | 0,19 |
| Lakebase (escala até zero) | 5,11 DBU | 2,66 |
| App (sempre ligado) | 12 DBU | 11,40 |
| **Total** | ~US$ 440 / 30 dias | **14,58** |

**Operação:**
- **Latência:** lote diário às 06:00 com o dado até ontem. O Auto Loader pode rodar ao longo do dia se precisar.
- **Re-treino:** diário. Aprovações e rejeições ficam gravadas com o autor.
- **Escala:** serverless; tempo e custo são medidos no piloto com o sortimento completo das 4 lojas.
- **Segurança:** permissões por papel no Unity Catalog.
- **App:** é 78% do custo e pode ser desligado fora do horário.
