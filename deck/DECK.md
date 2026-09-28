# LojaBR · Centro de Abastecimento
### Ruptura: de reativo a preditivo — com a ação certa na mão de quem decide

**Para:** VP de Operações & Supply Chain (patrocinador) · Gerente de Reposição (dono do domínio)
**Por:** Field Engineering · Databricks — *dados 100% sintéticos*

---

## 1. O problema, em reais

- **4,1% da venda some por ruptura**: o cliente não acha o produto e compra no concorrente.
- Na amostra de 129 itens de alto giro × 20 lojas: **R$ 2,39 mi por ano**.
- Hoje o time descobre **depois** que a gôndola esvaziou.
- A causa está concentrada: **Limpeza e Higiene rompem 2–3× mais**, e dois fornecedores entregam no prazo só **63–67%** das vezes.

> *"Quanto estou perdendo agora, e o que eu faço hoje para não perder amanhã?"*

---

## 2. O resultado que buscamos

| KPI do comprador | Hoje | Meta |
|---|---|---|
| Taxa de ruptura (loja × item × dia) | 6,5% | **< 4,5%** |
| Venda perdida por ruptura | 4,1% da venda | **recuperar ~⅓** |
| Antecedência do alerta | nenhuma | **~2,9 dias** |
| Lista de trabalho | sortimento inteiro | **8% dos itens, ordenados por R$** |

**Regra de bolso:** a cada **R$ 100 mi de venda**, ~R$ 4 mi se perdem em ruptura; recuperar um terço = **~R$ 1,4 mi**.

---

## 3. O que o gerente vê de manhã

Uma **fila de ação** com o produto, a loja, o risco e o R$ em jogo, e a solução mais barata para cada item:

- **Transferir** de uma loja próxima com excesso (≤ 450 km, chega em 1–2 dias).
- **Antecipar** o pedido que já está a caminho, mas chegaria tarde.
- **Pedido urgente** quando não há alternativa.

**Um clique aprova.** A decisão fica registrada com o nome de quem aprovou, e o **"R$ protegido hoje"** sobe na tela.

---

## 4. Por que confiar no alerta

- O modelo só olha itens **ainda na gôndola**, porque prever o que já zerou não evita nada.
- **Acerta 84% da lista diária, contra 38% da regra "cobertura < lead time"** usada hoje.
- Avisa **~2,9 dias antes** (75% dos alertas com 2 dias ou mais).
- Validado em datas futuras, que o modelo não viu no treino.

---

## 5. Um agente que confere antes de recomendar

Para os itens de maior valor, um agente de IA **consulta os fatos** (estoque e venda, lojas vizinhas com excesso, histórico do fornecedor) e só então confirma ou muda a ação:

> *"A LojaBR Campinas tem apenas 9 unidades em estoque (cobertura de 0,6 dia) e o pedido de reposição só chega em 2 dias, insuficiente para evitar ruptura. A LojaBR Ribeirão Preto, a 207 km, possui excedente de 61 unidades e cobertura de 18,2 dias, permitindo transferir 46 unidades sem comprometer seu próprio estoque."*
> — justificativa real do agente, Café Pilão 500g, run de evidência de 28/09/2026

---

## 6. Business case — e as premissas

- **Fila do run de 28/09** (dados até 27/09): protege **R$ 16,2 mil nos próximos 7 dias** (valor esperado, ponderado pelo risco), ≈ 27% da perda da última semana.
- **Anualizado**, com as ações aprovadas: **≈ R$ 0,84 mi/ano** na amostra (≈ 35% da perda).
- **Premissas:** as ações aprovadas são executadas; o valor é esperado, não garantido; a amostra é de itens de alto giro. Tudo isso é medido no piloto (slide 8).

---

## 7. Como funciona — uma plataforma, uma execução por dia

```
dados brutos → Lakeflow → Unity Catalog → modelo → agente de IA → Lakebase → app
                                   └──────────→ Genie (perguntas em português)
```

Um único job roda tudo, todo dia às 06:00, governado no Unity Catalog: linhagem, qualidade e permissões mínimas. Não há planilha exportada nem cópia de dados.

---

## 8. Plano de piloto — 30 dias, risco controlado

| Semana | O que acontece | Como medimos |
|---|---|---|
| 1 | Conectar POS, estoque e pedidos das 4 lojas-piloto | dados fluindo, qualidade ≥ 99% |
| 2–4 | Fila de ação em 4 lojas; 4 lojas similares como **controle** | ruptura e venda perdida, piloto vs controle |
| Fim | Decisão de escalar | R$ recuperado por loja × custo |

**Riscos e mitigação:** o modelo errar → a fila é priorizada por R$ e o gerente decide; adoção → um clique, dentro da rotina da manhã; dados de fornecedor incompletos → o agente declara a confiança e a regra cobre a base.

---

## 9. Por que Databricks

- **Uma plataforma**, do dado bruto à decisão: ingestão, governança, ML, agente de IA, Postgres operacional, perguntas em linguagem natural e app.
- **Governança nativa**: quem vê o quê, de onde veio cada número.
- **Pronto para piloto hoje**: já roda ponta a ponta; não é slideware.

---

## 10. O pedido

**Patrocinar um piloto de 30 dias em 4 lojas**, com grupo de controle, para medir ruptura e venda recuperada, e decidir a escala com números da própria LojaBR.

---

### Apêndice técnico (stakeholder técnico)
- Lakeflow Declarative Pipeline: Auto Loader em 7 feeds brutos; medallion com 7 expectativas de qualidade (0 falhas no último run).
- ML: gradient boosting, features *point-in-time* (pedido em aberto com chegada **prevista**), AUC 0,85, registrado no UC.
- Agente: tool-calling na Foundation Model API; rejeita decisão sem consulta prévia.
- Lakebase: schema `serving` (publicação atômica) + `app` (aprovações, log do Genie); leitura em ms.
- Genie: entity matching, definições de métrica, SQL certificado.
- App: React + Vite + TypeScript + Tailwind / FastAPI, service principal com acesso mínimo.
- Evidência de execução em texto: github.com/vitor-bricks/fe-bar-varejo → `evidence/`
