# Roleplay — roteiro de ensaio (LojaBR · Centro de Abastecimento)

20–30 min, dois personas na sala: **negócio** (VP de Operações, quem financia) e **técnico**
(arquiteto/data lead, quem vai conviver com a solução). Uma apresentação; depois, objeções.

> Regra de ouro: comece e termine no **R$**. Mostre só o que prova um ponto de negócio. Quando o
> técnico cavar fundo, responda o mecanismo e **suba de volta para o dinheiro numa frase**.

---

## 0 · Abertura (60–90 s, antes de qualquer tela) — *Demo setup*

> "Nosso cliente é a **LojaBR**, uma rede de 20 supermercados. O problema é ruptura: o produto
> some da gôndola e o cliente compra no concorrente. Nos dados deles, isso custa **4,1% da venda**,
> ou **R$ 2,4 milhões por ano** só nos 129 itens de maior giro, e o time descobre **depois** que a
> prateleira esvaziou. Vou mostrar três coisas: onde está o risco hoje, a lista de ação que o
> gerente aprova de manhã, e como a gente sabe que dá para confiar nela. No final, uma proposta de
> piloto de 30 dias."

---

## 1 · Tell–show–tell (7–8 min)

**A) Início**
- *Tell:* "Primeiro, o tamanho do problema e o que está em jogo esta semana."
- *Show:* os 4 KPIs: R$ 2,39 mi/ano perdidos, **R$ 16,8 mil em risco nos próximos 7 dias**,
  **Protegido hoje: R$ 0**, 3 de 20 lojas em alerta. Aponte a faixa da jornada: "cada caixinha é
  um estágio que rodou hoje às 6h, num único job".
- *Tell:* "Guardem esse **R$ 0**. Vamos mudar esse número daqui a pouco."

**B) Rede de lojas**
- *Tell:* "Onde agir primeiro."
- *Show:* o mapa. No zoom do Sudeste, as linhas tracejadas são **transferências sugeridas**.
  Clique em Tatuapé: os itens que vão acabar, com cobertura em dias e o que já está a caminho.
- *Tell:* "Estoque parado em Ribeirão Preto resolve a falta em Campinas em 2 dias, sem esperar
  o fornecedor."

**C) Fila de ação — o momento da demo**
- *Tell:* "É isto que o gerente abre às 7h."
- *Show:* um card. Produto, loja, risco, a ação mais barata (**transferir, antecipar ou pedido
  urgente**) e a justificativa. **Clique em Aprovar.** Volte à Início: "Protegido hoje" saiu de
  R$ 0. Mostre na aba **Lakebase** a escrita que acabou de acontecer, com o seu nome.
- *Tell:* "Isso é uma decisão, não um relatório. Fica registrada, com autor, e vira resultado medido."

**D) Agente + Genie (1 min)**
- *Show:* a Sala do agente, com as ferramentas que ele consultou antes de decidir. Abra o botão
  âmbar e pergunte: *"Quais fornecedores atrasam mais?"*
- *Tell:* "O gerente pergunta em português e decide sem abrir chamado para o time de dados."

**Fechamento (30 s)**
> "Saímos do reativo para o preditivo, com a ação na mão de quem decide. A meta é recuperar um
> terço da venda perdida por ruptura, **~R$ 1,4 mi a cada R$ 100 mi de venda**. A proposta é
> provar isso em 30 dias, em 4 lojas, com grupo de controle."

---

## 2 · Objeções

### 🟠 Negócio — custo, risco, tempo até o valor
| Pergunta | Resposta |
|---|---|
| *Quanto custa?* | "Serverless: paga pelo uso, sem infraestrutura dedicada. O piloto mede R$ recuperado por loja contra o custo antes de qualquer escala." |
| *E se o modelo errar?* | "Ele acerta **84% da lista diária, contra 38% da regra usada hoje**. E ele não decide sozinho: prioriza por R$, e o gerente aprova." |
| *Quanto tempo até ver resultado?* | "O protótipo já roda ponta a ponta. O piloto leva 30 dias, e a ruptura é medida desde a primeira semana." |
| *Esses R$ 16 mil são garantidos?* | "É valor esperado, ponderado pelo risco, e está declarado assim. É exatamente o que o grupo de controle do piloto vai confirmar ou corrigir." |
| *Meu time vai usar?* | "É um clique dentro da rotina da manhã, e a lista tem 8% dos itens, não o sortimento inteiro." |

### 🔵 Técnico — arquitetura, qualidade, segurança, integração
| Pergunta | Resposta (e a subida para o negócio) |
|---|---|
| *Como os dados entram?* | "**Lakeflow** com Auto Loader em 7 feeds brutos, medallion declarativo no **Unity Catalog**. Na LojaBR real, é plugar o POS e o ERP no mesmo ponto." |
| *Qualidade de dados?* | "7 expectativas no silver (preço válido, estoque não negativo, chegada depois do pedido…). **0 falhas no último run**, com linhagem automática. Número errado não chega ao gerente." |
| *O modelo não está vazando futuro?* | "Não. Só pontua itens **ainda na gôndola**, e usa o pedido em aberto naquele dia com a chegada **prevista**, não a real. Validação temporal em datas futuras. Por isso o número é crível." |
| *Por que um agente? LLM alucina.* | "O agente é obrigado a consultar ferramentas antes de decidir; se decidir antes, o loop rejeita. Ele cita só números devolvidos pelas ferramentas. Os demais itens usam regra, e a tela mostra qual é qual." |
| *Por que Lakebase e não o warehouse?* | "A fila e as aprovações são OLTP: leitura em **~3 ms** e escrita transacional. O analítico continua no warehouse e no Genie, tudo governado no mesmo lugar." |
| *Segurança?* | "O app roda com service principal de acesso mínimo: leitura no serving, escrita só nas tabelas de estado. A aprovação grava o usuário real que o gateway identifica." |
| *Orquestração?* | "Um job diário às 6h: dado bruto → pipeline → modelo → agente → Lakebase. Um run id de ponta a ponta." |

---

## 3 · Trocar de altitude (o que mais pontua)
> **Técnico:** "Como o pedido sugerido é calculado?"
> **Você:** "Demanda média de 28 dias × a janela até a reposição, menos o que já está em casa e a
> caminho; transferência só se a doadora mantiver 10 dias de cobertura e estiver a até 450 km.
> **Na prática, é o que evita perder os R$ 430 do Café Pilão em Campinas nesta semana.**"

## 4 · Profissionalismo
- Uma ideia por frase. Objeção não é ataque: "boa pergunta", resposta direta, volta ao valor.
- Antes de começar: confira que o "Protegido hoje" está em **R$ 0** (para o clique ao vivo ter efeito).
- Ensaie cronometrando: ~8 min de demo e o resto para perguntas.
