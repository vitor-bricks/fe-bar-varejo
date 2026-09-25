# LojaBR Varejo — Torre de Controle de Disponibilidade
### Da ruptura reativa à reposição preditiva

**Para:** VP de Operações / Supply Chain (patrocinador) e Head de Reposição / Operações de Loja (dono do domínio)
**Apresentado por:** Field Engineering · Databricks
*(Dados 100% sintéticos — demonstração)*

---

## 1. O problema de negócio

**Produto fora da gôndola = venda perdida — e cliente que migra para o concorrente.**

- Disponibilidade em gôndola (OSA) no varejo físico tem gap de **5–10% dos SKUs** a qualquer momento.
- Na LojaBR isso representa **R$ 3,26M perdidos em 120 dias** → **≈ R$ 9,9M por ano**.
- A dor operacional: o time de reposição reage **depois** que a gôndola já esvaziou, com relatórios defasados.

> A pergunta do executivo: *"Quanto de venda estou perdendo agora e o que faço hoje para recuperar?"*

---

## 2. O resultado que entregamos

| KPI | Hoje | Com a Torre de Controle |
|-----|------|-------------------------|
| Taxa de ruptura (SKU×loja) | ~5,5% | **< 4%** |
| Receita perdida / ano | ~R$ 9,9M | **Recuperar ~R$ 5M** (metade do gap) |
| Reação da reposição | após gôndola vazia | **horas de antecedência** (risco previsto) |
| Priorização | por intuição | **por R$ em risco** (modelo + IA) |

**Tese de valor:** transformar reposição reativa em **preditiva**, priorizada por receita em risco — recuperando vendas que hoje simplesmente evaporam.

---

## 3. O que construímos — uma tela, uma decisão

Uma **Torre de Controle** que o time de operação abre de manhã e sabe **exatamente onde agir**:

- **KPIs executivos:** taxa de ruptura, receita perdida (dia / período / anualizada), itens em risco agora.
- **Worklist de reposição** priorizado por **receita esperada em risco (7 dias)** — não por intuição.
- **Recomendação em linguagem natural (IA)** por item: por que está em risco e qual pedido disparar.
- **Pergunte ao Genie:** qualquer gestor pergunta em português e recebe o número na hora.

---

## 4. Como funciona — uma jornada de dados integrada na plataforma

```
Dados brutos ─▶ Lakeflow ─▶ Unity Catalog ─▶ ML + GenAI ─▶ Lakebase ─▶ App (Torre)
 (POS, estoque,  (ingestão +   (governança:    (risco de     (serving    (+ Genie
  auditorias)     medallion)    catálogo/         ruptura +     operacional  embutido)
                                lineage/qualidade) justificativa) baixa latência)
                                       │
                                       └─▶ Genie (perguntas em linguagem natural)
```

Tudo **governado no Unity Catalog**, do dado bruto à decisão — sem silos, sem exportar planilha.

---

## 5. A inteligência — risco de ruptura priorizado por dinheiro

- Modelo prevê a **probabilidade de ruptura nos próximos 7 dias** por SKU×loja.
- **AUC 0,86** · **precisão nos 100 de maior risco = 100%** → o time age numa lista curta, sem desperdício.
- Cada item vem com **pedido de reposição sugerido** e **receita esperada em risco** — a fila é ordenada por R$, não por alarme genérico.
- Modelo registrado e versionado no **Unity Catalog** (governança e reprodutibilidade).

---

## 6. Da previsão à ação — IA que explica e recomenda

> *"O SKU10029 está com estoque zerado na loja L119, mas vende 87 un/dia — ruptura confirmada (100%). Ação: acelerar o pedido pendente e priorizar o abastecimento."*

- A **Foundation Model API (Claude)** transforma o score em uma justificativa que o gerente de loja entende e executa.
- Fecha o ciclo: **prever → explicar → agir**, na mesma tela.

---

## 7. Autoatendimento — Genie em linguagem natural

- *"Quais lojas perderam mais receita?"* · *"Qual a taxa de ruptura por região?"* · *"Quantos itens em risco agora?"*
- Genie gera o **SQL governado** e responde em segundos — o dono do domínio não depende de um analista.
- Democratiza o dado sem abrir mão do controle (Unity Catalog).

---

## 8. Business case

- **Perda atual:** ~R$ 9,9M/ano em vendas por ruptura (medido nos dados).
- **Alvo:** reduzir ruptura de ~5,5% para <4% → **recuperar ~R$ 5M/ano**.
- **Concentração:** Nordeste e Sudeste concentram a maior perda → priorização regional imediata.
- **Custo x valor:** plataforma serverless, sem infra dedicada; o ganho de um único mês paga o esforço.

---

## 9. Por que Databricks

- **Uma plataforma, do bruto à decisão** — Lakeflow, Unity Catalog, ML/GenAI, Lakebase, Genie e Apps integrados.
- **Governança nativa** (UC): lineage, qualidade, permissões — sem cópias e silos.
- **Serving operacional (Lakebase)** e **analítico** na mesma base governada.
- **Time to value:** protótipo end-to-end funcionando — não slideware.

---

## 10. Roadmap — a mesma jornada, mais valor

- 📈 **Previsão de demanda** alimentando o pedido de reposição.
- 🏷️ **Markdown/preço** para queimar excesso protegendo margem.
- 🎯 **Next-best-offer** sobre o comportamento do cliente.

Um único produto que cresce em cima da **mesma base de dados governada**.

---

## Apêndice — evidência técnica (para o stakeholder técnico)

- **Lakeflow Declarative Pipeline:** Auto Loader → bronze → silver (expectativas de qualidade) → gold; 600K linhas/camada.
- **Unity Catalog:** catálogo/schemas `fe_bar_varejo_*`, comments, lineage automática.
- **ML:** HistGradientBoosting, AUC 0,856, precision@top100 = 1,0, registrado no UC.
- **GenAI:** Foundation Model API (Claude Sonnet) para justificativa de reposição.
- **Lakebase:** Postgres autoscaling servindo worklist/KPIs em baixa latência.
- **Genie:** Space governado sobre as tabelas gold, respostas em PT-BR com SQL.
- **App:** Databricks App (FastAPI + React), service principal com acesso mínimo necessário.
- **Repo (evidência de execução em texto):** github.com/vitor-bricks/fe-bar-varejo
