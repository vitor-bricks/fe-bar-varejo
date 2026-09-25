# Roleplay — roteiro de ensaio (Torre de Controle · Varejo)

Sessão de 20–30 min, dois personas na sala ao mesmo tempo: **stakeholder de negócio** (o
executivo que financia) e **stakeholder técnico** (o arquiteto/data lead que vai conviver com
a solução). Você apresenta uma vez, faz o caso de valor e responde objeções dos dois.

> Regra de ouro: **lidere sempre com o outcome**, mostre, e feche traduzindo em R$. Troque de
> altitude conforme quem pergunta — número/decisão para o negócio, mecanismo/arquitetura para o
> técnico — sem perder o outro na sala.

---

## 0. Demo setup — enquadre antes de mergulhar (60–90s)
*(pontua "Demo setup")*

> "Antes de mostrar a tela, o contexto. Nosso cliente é a **LojaBR**, uma rede de supermercados
> com 20+ lojas no Brasil. O problema que atacamos é **ruptura de estoque — produto que falta na
> gôndola**. No varejo físico, produto fora da prateleira é venda perdida na hora e cliente que
> migra pro concorrente. Medimos isso nos dados da LojaBR: **R$ 3,26M perdidos em 120 dias, ~R$
> 9,9M por ano**. Hoje o time de reposição reage *depois* que a gôndola esvaziou, com relatório
> defasado. Vou mostrar como transformamos isso em reposição **preditiva**, priorizada por
> receita em risco. São três coisas: o painel executivo, a lista de ação priorizada, e as
> perguntas em linguagem natural. Começo pelo painel."

---

## 1. Tell-show-tell — o walkthrough (6–8 min)
*(pontua "Tell-show-tell" e "Value communication")*

Para **cada** tela: diga o que vai mostrar → mostre → aterrisse no que significa pro negócio.

**A) Painel executivo (KPIs + tendência + região)**
- *Tell:* "Primeiro, a foto do problema em dinheiro."
- *Show:* KPIs — taxa de ruptura 5%, **R$ 9,9M/ano** de perda, **2.393 itens em risco agora**;
  a curva de ruptura (picos no fim de semana); a perda por região.
- *Tell (aterrissa):* "O Nordeste concentra a maior perda — é onde um real de esforço rende
  mais. Isso já direciona a prioridade regional."

**B) Worklist de reposição (o coração — ML)**
- *Tell:* "A pergunta do gerente é 'o que eu faço hoje?'. Aqui está a lista de ação."
- *Show:* tabela ordenada por **receita esperada em risco (7 dias)**, com risco %, estoque e
  **pedido sugerido** por item. Filtro por loja.
- *Tell:* "Não é um alarme genérico: é uma fila priorizada por dinheiro. Dos 100 itens de maior
  risco, **100% de fato romperiam** — o time age numa lista curta, sem desperdício."

**C) Recomendação por IA + Pergunte ao Genie**
- *Tell:* "E para agir sem depender de analista…"
- *Show:* a justificativa em linguagem natural por item (*"estoque zerado, vende 87/dia →
  dispare o pedido"*); depois a aba **Genie**: pergunte *"qual a receita perdida por região?"* e
  o número aparece com o SQL gerado.
- *Tell:* "Qualquer gestor pergunta em português e decide na hora — o dado deixa de ser gargalo."

**Fechamento (30s):** "Resumindo: saímos de reposição reativa para preditiva, priorizada por R$.
A meta é ruptura de 5,5% para menos de 4% — **recuperar ~R$ 5M por ano**."

---

## 2. Banco de objeções

### 🟠 Stakeholder de NEGÓCIO — custo, risco, time-to-value
- **"Quanto custa rodar isso?"** → "Serverless, paga-se pelo uso; sem infra dedicada. O valor
  recuperado de **um único mês** paga o esforço de implantação. O caso é de retorno, não de custo."
- **"E se o modelo errar?"** → "Por isso a lista é ordenada por **R$ em risco** e não por um
  alarme cego — e a precisão no topo é 100%. O gerente decide; a IA prioriza. Começamos com um
  **piloto em poucas lojas** e medimos a ruptura antes/depois."
- **"Quanto tempo até ver resultado?"** → "O protótipo já roda end-to-end nos seus próprios
  dados. Piloto em **semanas**, não trimestres — e o KPI (taxa de ruptura, venda recuperada) é
  medível desde a primeira semana."
- **"Não bastaria contratar mais gente / melhorar o relatório?"** → "Relatório é retrovisor —
  reage depois que a venda já foi perdida. Isso é para-brisa: antecipa a ruptura e diz onde agir."

### 🔵 Stakeholder TÉCNICO — arquitetura, qualidade, segurança, integração
- **"Como isso se conecta?"** → "Uma plataforma só: **Lakeflow** ingere os feeds brutos (POS,
  estoque, auditorias) via Auto Loader; **Unity Catalog** governa; medallion bronze→silver→gold;
  **ML/GenAI** pontua e explica; **Lakebase** serve o operacional em baixa latência; **Genie** e
  o app consomem. Sem colar seis ferramentas."
- **"Qualidade de dados?"** → "Expectativas na camada silver (`@dlt.expect`), dedup por chave,
  tipagem — e **lineage automática** bronze→gold no Unity Catalog. Se o feed sujar, a regra pega."
- **"Segurança / quem vê o quê?"** → "Governança nativa no UC. O app roda com um **service
  principal de acesso mínimo**: SELECT nas tabelas de serving, CAN_USE no warehouse, CAN_RUN no
  Genie. Sem cópias de dado espalhadas."
- **"Como integra com nosso ERP/POS?"** → "Lakeflow Connect/Auto Loader ingere incremental dos
  seus feeds; o operacional sai por **Lakebase (Postgres)** — API e SQL padrão que seus sistemas
  já falam."
- **"Como versiona/retreina o modelo?"** → "Registrado no **Unity Catalog/MLflow**, versionado e
  reproduzível; retreino agendável num job. Dá pra monitorar drift na mesma plataforma."
- **"Por que Databricks e não construir na mão / Snowflake?"** → "Aqui ML, serving operacional,
  linguagem natural e app vivem **na mesma base governada**. Construir na mão vira integração e
  silo — exatamente o que faz esse tipo de projeto falhar."

---

## 3. Trocar de altitude (o que mais pontua em "reading the room")
Quando o técnico pergunta detalhe, responda o mecanismo **e** re-suba pro negócio numa frase:

> Técnico: *"Como garante que o pedido sugerido não é lixo?"*
> Você: *"O número vem de demanda média × (lead time + 7 dias) menos o que já está em casa e a
> caminho — regra explicável, auditável. **Na prática, é isso que evita a ruptura de R$ 8 mil
> naquele SKU.**"* ← fecha no dinheiro para o executivo não se perder.

## 4. Profissionalismo
- Fale devagar, uma ideia por frase. Comece e termine no **outcome**.
- Objeção não é ataque: "Ótima pergunta" + responda direto + volte ao valor.
- Não vire tour de feature. Cada clique existe para provar **um** ponto de negócio.
- Tenha o deck aberto; ensaie em voz alta cronometrando (~8 min de demo, resto pra objeção).
