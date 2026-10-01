# Pitch — LojaBR · Centro de Abastecimento (20–30 min)

> English: [`PITCH_EN.md`](PITCH_EN.md)

Roteiro falado do que construímos: deck v2, app ao vivo e workspace. Para cada bloco: **onde
estar**, **o que mostrar** e **o que dizer**. O tempo-alvo é **26 min** de apresentação. As versões
de 20 e de 30 min estão no fim. Todo "abra" ou "mostre" tem o link para abrir o que se pede.

- **Na sala:** 🟠 **negócio**, o VP de Operações & Supply Chain, que financia. 🔵 **técnico**, o
  arquiteto ou Head de Dados, que vai conviver com a solução.
- **Material:**
  - o deck [`LojaBR_Centro_de_Abastecimento_v2.pdf`][pdf], também em
    [texto](DECK_v2.md) e em [inglês][pdf-en];
  - o [app publicado][app];
  - o workspace, que também se abre pelo botão **arquitetura** do app.
- **O fio da história:** dinheiro → problema → ação → confiança → custo → plataforma → pedido.
  Começa e termina no **R$**.
- **Regra de ouro:** só mostre o que prova um ponto de negócio. Quando o técnico cavar fundo,
  responda o mecanismo e **suba de volta para o R$ numa frase**.

## Links rápidos

| O quê | Link |
|---|---|
| **Deck v2** (PDF, slide N = página N) | [PT][pdf] · [EN][pdf-en] · [texto PT](DECK_v2.md) |
| **App** | [Início][app-inicio] · [Rede de lojas][app-rede] · [Fila de ação][app-fila] · [Agente][app-agente] · [Lakebase][app-lakebase] |
| **Job diário** (o run de hoje é o primeiro da lista) | [`fe_bar_varejo_e2e`][ws-job] · [run de referência de 28/09][ws-run-ref] |
| **Pipeline Lakeflow** (grafo + qualidade) | [`fe_bar_varejo_pipeline`][ws-pipeline] |
| **Unity Catalog** | [schema gold][ws-gold] · [tabela da fila (aba Lineage)][ws-fila-tabela] · [modelo e versões][ws-modelo] |
| **Genie** (espaço no workspace) | [LojaBR · Centro de Abastecimento][ws-genie] |
| **Lakebase** (projeto) | [`fe-bar-varejo`][ws-lakebase] *(link ainda não conferido no workspace)* |
| **Notebooks** | [ingestão][ws-nb-ingest] · [pipeline][ws-nb-pipeline] · [modelo][ws-nb-modelo] · [agente][ws-nb-agente] · [sync Lakebase][ws-nb-sync] |
| **Evidência em texto** | [índice](../evidence/README.md) · [qualidade](../evidence/run_02_lakeflow_pipeline.md) · [modelo](../evidence/run_03_early_warning_model.md) · [agente](../evidence/run_04_replenishment_agent.md) · [Genie](../evidence/run_06_genie_qa.md) · [app](../evidence/run_07_app_checks.md) · [custo](../evidence/run_08_platform_cost.md) |
| **Preparação** | [`demo_prep.py`](demo_prep.py) (a cola do dia) · [`ROLEPLAY.md`](ROLEPLAY.md) (demo curta e objeções) |

---

## Antes de entrar (T − 30 min)

1. Rode [`python3 deck/demo_prep.py`](demo_prep.py) e deixe a **cola do dia** visível. Ela traz os
   números de hoje, a loja para clicar, a melhor transferência, o card para aprovar e a frase de
   fechamento.
2. Confira na cola: **"Protegido hoje: R$ 0"** e **"Jornada: todos os estágios OK"**.
3. **Aqueça o app** 5 min antes: abra [Início][app-inicio], [Rede][app-rede] e [Fila][app-fila]
   uma vez. A Lakebase escala até zero, e a primeira leitura depois de um tempo parada é mais lenta.
4. Deixe as abas prontas, nesta ordem:
   1. o [PDF v2][pdf] em tela cheia;
   2. o app em [Início][app-inicio];
   3. o [job][ws-job], com o run de hoje aberto;
   4. o [pipeline][ws-pipeline].

   Abrir as abas 3 e 4 agora resolve o SSO antes da demo.
5. Navegador com zoom de 110–125%, notificações desligadas e só essas abas abertas.
6. Plano B à mão: os slides [6](LojaBR_Centro_de_Abastecimento_v2.pdf#page=6),
   [7](LojaBR_Centro_de_Abastecimento_v2.pdf#page=7) e
   [10](LojaBR_Centro_de_Abastecimento_v2.pdf#page=10) têm as telas do app; o
   [`evidence/`](../evidence/README.md) tem tudo em texto.

> **Deck × app.** O deck é a fotografia do run de referência de 28/09. O app mostra a fila de hoje,
> que muda todo dia com o dado até ontem. Use o número do deck quando estiver no slide e o da cola
> quando estiver no app. Se notarem a diferença: *"o deck é a foto de um dia; o app é o filme. Muda
> o item, não muda a ordem de grandeza."*

---

## Mapa do tempo

| ⏱ | Bloco | Min | Onde |
|---|---|---|---|
| 00:00 | 1 · Abertura: o resultado e o pedido | 2 | slides [1](LojaBR_Centro_de_Abastecimento_v2.pdf#page=1)–[2](LojaBR_Centro_de_Abastecimento_v2.pdf#page=2) |
| 02:00 | 2 · O problema, em reais | 1,5 | slide [3](LojaBR_Centro_de_Abastecimento_v2.pdf#page=3) |
| 03:30 | 3 · Os KPIs e o valor para cada um | 2,5 | slides [4](LojaBR_Centro_de_Abastecimento_v2.pdf#page=4)–[5](LojaBR_Centro_de_Abastecimento_v2.pdf#page=5) |
| 06:00 | 4 · **Demo: a manhã do gerente** | 8 | app: [Início][app-inicio] → [Rede][app-rede] → [Fila][app-fila] → **Aprovar** → Início → [Lakebase][app-lakebase] |
| 14:00 | 5 · Por que confiar | 3,5 | slide [8](LojaBR_Centro_de_Abastecimento_v2.pdf#page=8) → app: [Agente][app-agente] → Genie |
| 17:30 | 6 · Quanto vale e quanto custa | 2 | slide [9](LojaBR_Centro_de_Abastecimento_v2.pdf#page=9) |
| 19:30 | 7 · Como funciona e por que Databricks | 4 | app: **arquitetura** → [run][ws-job] e [pipeline][ws-pipeline] → slide [11](LojaBR_Centro_de_Abastecimento_v2.pdf#page=11) |
| 23:30 | 8 · O piloto e o pedido | 2 | slides [12](LojaBR_Centro_de_Abastecimento_v2.pdf#page=12)–[13](LojaBR_Centro_de_Abastecimento_v2.pdf#page=13) |
| 25:30 | Fechamento e a pergunta de compromisso | 0,5 | slide [13](LojaBR_Centro_de_Abastecimento_v2.pdf#page=13) |
| 26:00 | Perguntas | — | ver "Perguntas prováveis" |

Os slides 6, 7 e 10 são as telas do app. Ao vivo, eles dão lugar à demo e ficam de reserva.

---

## 1 · Abertura: o resultado e o pedido · 00:00 → 02:00

**[Slide 1](LojaBR_Centro_de_Abastecimento_v2.pdf#page=1) (capa).** Fale olhando para o 🟠.
> "A LojaBR perde **4,1% da venda** porque o produto some da gôndola e o cliente compra no
> concorrente. Nos 129 itens de maior giro, são **R$ 2,39 milhões por ano**. Hoje o time descobre
> depois que a prateleira esvaziou.
> Construímos na Databricks o Centro de Abastecimento. Ele avisa **quase 3 dias antes**, já traz a
> ação mais barata, e o gerente aprova **com um clique**. A meta é recuperar até **R$ 0,8 milhão
> por ano** nesses itens. O que viemos pedir é um **piloto de 30 dias em 4 lojas**, com grupo de
> controle."

**[Slide 2](LojaBR_Centro_de_Abastecimento_v2.pdf#page=2) (resumo executivo).** Dê 30 s, sem ler
os quatro quadros.
> "Se vocês levarem uma página, é esta: problema, solução, valor e pedido."

**Agenda, numa frase, falando com os dois.**
> "Vou mostrar o problema em reais, o sistema rodando com os dados de hoje, por que dá para confiar
> no alerta, quanto custa, e o plano de piloto. [Nome do técnico], a arquitetura vem lá pelo minuto
> 20, e tudo que eu mostrar abre no workspace."

---

## 2 · O problema, em reais · 02:00 → 03:30

**[Slide 3](LojaBR_Centro_de_Abastecimento_v2.pdf#page=3).** Aponte primeiro os quatro números e
depois a barra de Limpeza.
> "São 120 dias de histórico das 20 lojas. A disponibilidade em gôndola está em 93,5%. O ponto
> importante é que **a perda é concentrada**: Limpeza e Higiene rompem duas vezes a média, e os
> fornecedores dessas categorias entregam no prazo só 63% e 68% das vezes. Não é um problema
> espalhado. Dá para atacar com uma **lista curta**, e é isso que vou mostrar."

---

## 3 · Os KPIs e o valor para cada um · 03:30 → 06:00

**[Slide 4](LojaBR_Centro_de_Abastecimento_v2.pdf#page=4) (KPIs do comprador).**
> "Não inventamos métrica nova. São os números que a LojaBR já acompanha. A faixa vai de metade das
> ações executadas até todas. Disponibilidade sobe de 93,5% para até 95,8%. Venda perdida cai de 18%
> a 35%. E o gerente passa a ter **2,9 dias de aviso**, que hoje é zero."

**[Slide 5](LojaBR_Centro_de_Abastecimento_v2.pdf#page=5) (o que muda para cada um).** Divida o
olhar.
- 🟠 *"Para você: venda de volta no P&L. E o valor sai barato, porque a maior parte vem de
  **antecipar pedidos que já estão a caminho**, sem compra nova nem frete."*
- 🟠/🔵 *"Para o time que opera: uma lista com 8% dos itens em vez de 29%, a justificativa
  pronta no card, e perguntas em português ao Genie, sem abrir chamado."*

**Transição para o app:**
> "Em vez de mostrar a tela num slide, vou abrir o sistema com a fila de hoje."

---

## 4 · Demo: a manhã do gerente · 06:00 → 14:00

Este é o centro do pitch. Cada passo prova um ponto de negócio.

### 4a · [Início][app-inicio] (1 min)
- **Mostrar:** os 4 KPIs. Use os números da cola: perda/ano, em risco nos próximos 7 dias,
  **Protegido hoje = R$ 0** e lojas em alerta.
- **Dizer:**
  > "Esses números são de hoje. O job rodou às 6h com os dados até ontem, então a fila fica pronta
  > antes de a loja abrir. Guardem este **R$ 0** do 'Protegido hoje'. Vamos mudá-lo daqui a pouco."

### 4b · [Rede de lojas][app-rede] (2 min)
- **Mostrar:**
  1. O mapa, com a ruptura por loja.
  2. Clique em **Sudeste**. As linhas tracejadas são **transferências sugeridas**.
  3. Passe o mouse numa loja para ver o tooltip com as métricas.
  4. Clique na **loja da cola**. Abrem o resumo, o ranking e o painel **"Ações para {loja}"**.
- **Dizer:** use a melhor transferência da cola.
  > "O estoque parado em {doadora} resolve a falta em {destino}: {item}, a {km} km, chegando em 1 a
  > 2 dias, sem esperar o fornecedor. A regra é simples: só a até 450 km, e a doadora nunca fica
  > com menos de 10 dias de estoque."

### 4c · [Fila de ação][app-fila]: o momento da demo (3 min)
- **Mostrar:**
  1. A fila ordenada por **impacto (R$)**. Troque para **criticidade** e volte:
     *"o gerente escolhe: o que vale mais, ou o que esvazia primeiro"*.
  2. Encontre o **card da cola**: produto, loja, risco, cobertura em dias, a ação, o **R$ em
     destaque** e a justificativa do agente.
  3. Leia **uma frase** da justificativa em voz alta, de preferência a que cita estoque e a
     pontualidade do fornecedor.
  4. **Clique em Aprovar.**
- **Dizer:**
  > "Isso é uma decisão, não um relatório. O agente conferiu o estoque das lojas vizinhas e o
  > histórico do fornecedor antes de sugerir. O gerente leu, concordou e aprovou com um clique."

### 4d · Volta ao [Início][app-inicio] (30 s)
- **Mostrar:** o "Protegido hoje" saiu de R$ 0.
- **Dizer:**
  > "Esse é o número que o piloto vai medir **contra o grupo de controle**. Cada clique vira
  > resultado contado."

### 4e · [Lakebase][app-lakebase], para o 🔵 (1 min)
- **Mostrar:** em "Escritas recentes · aprovações" aparece a decisão com **o seu nome e o horário**.
  Aponte a latência p50 em milissegundos.
- **Dizer:**
  > "A aprovação foi gravada num Postgres gerenciado da Databricks, a Lakebase, de forma
  > transacional e com autor. O app lê a fila daqui em poucos milissegundos. O analítico continua
  > no lakehouse, governado no mesmo lugar. Auditoria pronta: quem aprovou o quê e quando."

**Transição para o deck:**
> "Uma pergunta justa agora é: por que confiar nesse alerta?"

---

## 5 · Por que confiar · 14:00 → 17:30

**[Slide 8](LojaBR_Centro_de_Abastecimento_v2.pdf#page=8) (1,5 min).**
> "O modelo acerta **84%** da lista diária. A regra usada hoje, 'cobertura menor que o prazo de
> entrega', acerta 38%. E a lista dele tem 8% dos itens, não 29%. Validamos em quase 50 mil casos de
> 4 semanas que o modelo nunca viu.
> E quando ele erra? Um alerta errado não vira perda: a doadora continua com ao menos 10 dias, e o
> item vende no destino. O pior caso é o frete. Ele é re-treinado todo dia, no mesmo job."

Fonte, se pedirem: [`run_03_early_warning_model.md`](../evidence/run_03_early_warning_model.md).

**App · [Agente][app-agente] (1 min).**
- **Mostrar:** no topo, quantos itens de maior valor o agente revisou e quantas ações ele
  **alterou** depois de conferir os fatos. Embaixo, em "Como ele decide", as ferramentas que ele
  chamou nesta rodada (contagem real do loop).
- **Dizer** (para o 🔵):
  > "O agente é obrigado a consultar as ferramentas antes de decidir. Se tentar decidir sem
  > consultar, o sistema rejeita. Ele só cita números que as ferramentas devolveram."
- Se o 🔵 quiser o código: [notebook do agente][ws-nb-agente] ·
  [trace em texto](../evidence/run_04_replenishment_agent.md).

**App · Genie (1 min).**
- **Mostrar:** clique no **botão âmbar** do app e pergunte *"Quais fornecedores atrasam mais?"*.
  Se precisar, o mesmo espaço abre no [workspace][ws-genie].
- **Dizer**, enquanto ele responde (10–20 s):
  > "O gerente pergunta em português, sem abrir chamado para o time de dados. E cada pergunta fica
  > registrada, como a aprovação."
- **Gancho:** se o card aprovado citou um fornecedor, mostre que o Genie traz a mesma pontualidade.
  > "O app, o agente e o Genie leem o mesmo número."

---

## 6 · Quanto vale e quanto custa · 17:30 → 19:30

**[Slide 9](LojaBR_Centro_de_Abastecimento_v2.pdf#page=9).** Olhe para o 🟠.
> "No cenário conservador, com metade das ações executadas, são **R$ 0,42 milhão por ano**. Com
> todas, **R$ 0,84 milhão**. Para a rede, a regra de bolso é **R$ 1,4 milhão a cada R$ 100 milhões
> de venda**.
> O custo é medido, não estimado: **~US$ 440 por mês** a preço de lista, para rodar tudo. Ou seja,
> menos de US$ 500 por mês de plataforma contra ~R$ 35 mil por mês de venda de volta, no cenário
> mais conservador.
> E de onde vem o valor: no run de referência, 80% veio de **antecipar pedidos que já estão a
> caminho**."

Fonte do custo, se pedirem: [`run_08_platform_cost.md`](../evidence/run_08_platform_cost.md).

> ⚠️ O mix da barra muda todo dia. Cite os 80% como "no run de referência" e não compare com a fila
> de hoje.

---

## 7 · Como funciona e por que Databricks · 19:30 → 23:30

### 7a · Arquitetura ao vivo (2,5 min)
- **Mostrar:** no [app][app-inicio], clique no botão brilhante **arquitetura**. Aparecem os 8
  estágios: Ingestão → Medallion → Governança → Modelo → Agente → Serving → Linguagem natural →
  Decisão. Cada um traz o **status do run de hoje**.
- **Dizer:**
  > "É um job só, todo dia às 6h: do dado bruto à decisão em uns 8 minutos. E cada caixinha abre o
  > recurso real no workspace."
- **Abra até 2 links** (já aquecidos nas abas):
  1. **Run de hoje**: o [job][ws-job] com o primeiro run da lista, ou o link no topo da visão.
     Mostre as tarefas encadeadas: *"um run id de ponta a ponta"*.
  2. **[Pipeline][ws-pipeline]** (estágio Medallion): o grafo bronze → silver → gold e, ao clicar
     numa tabela silver, a qualidade com as **7 expectativas, 0 falhas**.
     > "Número errado não chega ao gerente."
- **Volte para o app** antes de abrir um terceiro link.

### 7b · [Slide 11](LojaBR_Centro_de_Abastecimento_v2.pdf#page=11), Por que Databricks (1,5 min)
> "Com ferramentas separadas, seriam 7 peças: ETL, warehouse, ML, banco operacional, LLM, BI e
> hospedagem do app. Aqui é uma plataforma. O que isso muda no resultado:
> - **O número bate.** O app, o Genie e o modelo leem o mesmo dado, com linhagem.
> - **O tempo até o piloto é de 30 dias**, porque a solução já executa ponta a ponta na Databricks.
> - **A segurança fica num lugar só.**
> - **O custo é medido.**"

Para o 🔵:
> "E a saída fica aberta: Delta, com Iceberg via UniForm, Postgres padrão, MLflow e código em Git."

Para fechar o slide:
> "Os mesmos dados já servem os próximos casos: previsão de demanda, markdown do excesso e
> sortimento por loja."

---

## 8 · O piloto e o pedido · 23:30 → 25:30

**[Slide 12](LojaBR_Centro_de_Abastecimento_v2.pdf#page=12).**
> "Semana 1: conectar vendas, estoque e pedidos das 4 lojas-piloto. Semanas 2 a 4: a fila rodando
> nas 4 lojas, com 4 lojas parecidas como controle. Mesmo mês, mesmo formato, mesma região, então
> sazonalidade e promoção se anulam. O critério de sucesso: ruptura pelo menos **1,5 ponto abaixo
> do controle**, e R$ recuperado maior que o custo."

**[Slide 13](LojaBR_Centro_de_Abastecimento_v2.pdf#page=13).**
> "O pedido é este: **patrocinar um piloto de 30 dias em 4 lojas, com grupo de controle**. Na
> semana 0 você escolhe as lojas. Na semana 1, o TI da LojaBR e a Databricks abrem os feeds. Na
> semana 4, o comitê decide a escala com o resultado medido na mão."

### Fechamento (30 s)
Use a frase da cola:
> "Na prática, é o que evita perder os R$ {valor} do {item} em {loja} nesta semana. Multipliquem
> isso por uma fila inteira, todo dia, em 20 lojas."

Depois, a **pergunta de compromisso**, e fique em silêncio:
> "Quais 4 lojas vocês colocariam no piloto?"

---

## Versão de 20 min

| Bloco | 26 min | 20 min | O que cortar |
|---|---|---|---|
| 1 · Abertura | 2 | 1,5 | a agenda vira meia frase |
| 2 · Problema | 1,5 | 1 | só a frase da concentração |
| 3 · KPIs e valor | 2,5 | 2 | o slide 5 em 30 s, só a linha do 🟠 |
| 4 · Demo | 8 | 6 | Rede em 1 min (só o clique na loja); Lakebase em 30 s |
| 5 · Confiar | 3,5 | 2,5 | pule a aba Agente; mantenha o Genie |
| 6 · Valor e custo | 2 | 1,5 | — |
| 7 · Plataforma | 4 | 3 | só o overlay e o link do run; slide 11 em 1 min |
| 8 · Piloto e pedido | 2 | 2 | não corte |

Nunca corte **o clique em Aprovar e a volta ao Início**, **o slide 9** nem **o pedido**.

## Versão de 30 min

Some estes itens ao roteiro de 26 min:
- **+1,5 min · Genie:** um follow-up, *"Quais ações estão recomendadas para a loja {loja da cola}?"*,
  e abra o SQL gerado para o 🔵.
- **+1,5 min · Unity Catalog:** abra a [tabela da fila][ws-fila-tabela], na aba **Lineage**, para
  mostrar de onde vem cada linha. Depois, o [modelo][ws-modelo], com uma versão por dia.
- **+1 min · [Apêndice A2](LojaBR_Centro_de_Abastecimento_v2.pdf#page=15):** a tabela de custo por
  componente. O app é 78% do custo e pode desligar fora do horário.
- **+1 min · Evidência no GitHub:** abra
  [`run_08_platform_cost.md`](../evidence/run_08_platform_cost.md).
  > "Todo número deste deck tem a consulta ao lado."

---

## Se algo der errado

| Sintoma | O que fazer |
|---|---|
| O app demora na primeira tela | A Lakebase está acordando. Fale do slide 5 enquanto carrega; se passar de 20 s, use os slides [6](LojaBR_Centro_de_Abastecimento_v2.pdf#page=6)–[7](LojaBR_Centro_de_Abastecimento_v2.pdf#page=7). |
| "Protegido hoje" não está em R$ 0 | *"Já temos R$ X aprovados hoje. Vejam subir."* O clique continua mostrando o efeito. |
| O card da cola sumiu da fila | Ordene por impacto e use o **primeiro card de transferência**. |
| O Genie demora mais de 30 s | Continue falando. Se não vier, mostre a Q3 em [`run_06_genie_qa.md`](../evidence/run_06_genie_qa.md). |
| O workspace pede login | Volte ao app e use o [slide 10](LojaBR_Centro_de_Abastecimento_v2.pdf#page=10) (a imagem da arquitetura). |
| Notam que o número do app difere do deck | *"O deck é a foto de 28/09; o app é a fila de hoje."* |

---

## Números na ponta da língua

| | |
|---|---|
| **Perda** | 4,1% da venda · R$ 2,39 mi/ano · 129 itens × 20 lojas · 120 dias de histórico |
| **Valor** | R$ 0,42–0,84 mi/ano · −18% a −35% de venda perdida · R$ 1,4 mi a cada R$ 100 mi de venda |
| **Alerta** | 2,9 dias de aviso · 75% com ≥ 2 dias · 84% de acerto contra 38% da regra · AUC 0,85 · 49.733 casos |
| **Lista** | 8% dos itens, contra 29% da regra (3,6× menor) |
| **Transferência** | ≤ 450 km · doadora mantém ≥ 10 dias · chega em 1–2 dias · protege ~R$ 74 em média |
| **Custo** | ~US$ 440/mês (US$ 14,58/dia) · lote diário US$ 0,52/dia · app = 78% do custo |
| **Operação** | job diário às 06:00 · ~8 min · 7 regras de qualidade, 0 falhas · leitura na Lakebase em ~3 ms |
| **Piloto** | 30 dias · 4 lojas + 4 de controle · sucesso = ≥ 1,5 p.p. abaixo do controle e R$ > custo |

---

## Perguntas prováveis (respostas de uma frase, e volta ao R$)

As objeções de base estão em [`ROLEPLAY.md`](ROLEPLAY.md) §2. Estas são as que as duas personas
levantaram na revisão do deck.

### 🟠 Negócio
| Pergunta | Resposta |
|---|---|
| *Quanto custa por mês?* | "Medido nas [tabelas de billing](../evidence/run_08_platform_cost.md): ~US$ 440 por mês a preço de lista, para tudo. O app é 78% disso e pode desligar fora do horário." |
| *Venda não é margem.* | "Certo. Com margem bruta de 20–25%, os ~R$ 35 mil de venda por mês do cenário conservador viram R$ 7–9 mil de margem, contra ~R$ 2,5 mil de plataforma." *(Conta de bolso: confira o câmbio do dia.)* |
| *Transferência errada custa quanto?* | "Cada transferência protege ~R$ 74. Por isso, no piloto, só transferimos em rota que já existe ou agrupando itens do mesmo par de lojas." |
| *30 dias provam alguma coisa? E a sazonalidade?* | "O controle vive o mesmo mês, então sazonalidade e promoção afetam os dois grupos. O piloto mede a diferença, não o nível." |
| *E para escalar depois?* | "A decisão sai na semana 4, com R$ recuperado por loja contra o custo. Aí sabemos quanto vale cada loja nova." |
| *Quem opera depois?* | "É um job agendado e serverless, sem cluster para manter. O gerente usa o app, e o time de dados acompanha o [run diário][ws-job]." |

### 🔵 Técnico
| Pergunta | Resposta |
|---|---|
| *O clique vira ordem no ERP?* | "A aprovação já é um registro transacional na Lakebase, com autor e horário. Levar ao ERP é escopo da semana 1 do piloto, por API ou arquivo, como a LojaBR preferir." |
| *O job é diário. O aviso não chega tarde?* | "O aviso é de 2,9 dias, então cabe num lote diário. Se precisar, o Auto Loader roda ao longo do dia sem mudar o pipeline." |
| *Como garantem que a doadora tem mesmo o estoque?* | "O agente consulta a posição do dia antes de recomendar, e o sistema rejeita decisão sem essa consulta. A justificativa cita o número que a ferramenta devolveu." ([trace](../evidence/run_04_replenishment_agent.md)) |
| *E o re-treino? Rejeições ensinam o modelo?* | "Ele é re-treinado todo dia, com versão no [Unity Catalog][ws-modelo]. Aprovações e rejeições ficam gravadas com autor e viram sinal de avaliação no piloto." |
| *Escala para o sortimento inteiro?* | "Tudo é serverless. No piloto, medimos tempo e custo com o sortimento completo das 4 lojas, antes de qualquer escala." |
| *Quem vê o quê?* | "As permissões ficam por papel no Unity Catalog. O app usa um service principal com acesso mínimo, e cada aprovação grava o usuário real." |
| *E se quisermos sair da Databricks?* | "Os formatos são abertos: Delta, com Iceberg via UniForm, Postgres padrão, MLflow e código em Git. Nada fica preso num formato fechado." |

[pdf]: LojaBR_Centro_de_Abastecimento_v2.pdf
[pdf-en]: LojaBR_Replenishment_Center_EN_v2.pdf
[app]: https://fe-bar-varejo-tower-7474654865387615.aws.databricksapps.com/
[app-inicio]: https://fe-bar-varejo-tower-7474654865387615.aws.databricksapps.com/
[app-rede]: https://fe-bar-varejo-tower-7474654865387615.aws.databricksapps.com/rede
[app-fila]: https://fe-bar-varejo-tower-7474654865387615.aws.databricksapps.com/fila
[app-agente]: https://fe-bar-varejo-tower-7474654865387615.aws.databricksapps.com/agente
[app-lakebase]: https://fe-bar-varejo-tower-7474654865387615.aws.databricksapps.com/lakebase
[ws-job]: https://fevm-serverless-stable-xpbmim.cloud.databricks.com/jobs/384370635751593
[ws-run-ref]: https://fevm-serverless-stable-xpbmim.cloud.databricks.com/jobs/384370635751593/runs/204235693781766
[ws-pipeline]: https://fevm-serverless-stable-xpbmim.cloud.databricks.com/pipelines/733e5172-5f51-404b-a790-b40cce95f015
[ws-gold]: https://fevm-serverless-stable-xpbmim.cloud.databricks.com/explore/data/serverless_stable_xpbmim_catalog/fe_bar_varejo_gold
[ws-fila-tabela]: https://fevm-serverless-stable-xpbmim.cloud.databricks.com/explore/data/serverless_stable_xpbmim_catalog/fe_bar_varejo_gold/gold_replenishment_queue_final
[ws-modelo]: https://fevm-serverless-stable-xpbmim.cloud.databricks.com/explore/data/models/serverless_stable_xpbmim_catalog/fe_bar_varejo_gold/stockout_early_warning
[ws-genie]: https://fevm-serverless-stable-xpbmim.cloud.databricks.com/genie/rooms/01f1b906cf2d15b4b1c72c3b25ddb2f0
[ws-lakebase]: https://fevm-serverless-stable-xpbmim.cloud.databricks.com/lakebase/projects/fe-bar-varejo
[ws-nb-ingest]: https://fevm-serverless-stable-xpbmim.cloud.databricks.com/editor/notebooks/561894903539841
[ws-nb-pipeline]: https://fevm-serverless-stable-xpbmim.cloud.databricks.com/editor/notebooks/561894903539842
[ws-nb-modelo]: https://fevm-serverless-stable-xpbmim.cloud.databricks.com/editor/notebooks/4068321213986550
[ws-nb-agente]: https://fevm-serverless-stable-xpbmim.cloud.databricks.com/editor/notebooks/4068321213986545
[ws-nb-sync]: https://fevm-serverless-stable-xpbmim.cloud.databricks.com/editor/notebooks/4068321213986551
