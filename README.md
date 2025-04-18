## 📂 Downloads

Aqui você encontra os arquivos de grade de horário utilizados neste projeto:

- 📘 [Grade de horário manual](Planilhas/grade_por_turma.xlsx)  
  Planilha construída manualmente, utilizada como referência.

- 📗 [Grade de horário gerada pelo CPLEX](Planilhas/grade_por_turma_CPLEX.xlsx)  
  Resultado da execução do modelo matemático desenvolvido com o solver CPLEX.

## Modelo matemático

**Tabela 1:** Estrutura básica do modelo proposto
| **Categoria**         | **Notações**       | **Descrição**                                                                 |
|-----------------------|--------------------|------------------------------------------------------------------------------|
| **Conjuntos**         | $P$              | Conjunto de professores, onde $p \in P = \{P1, P2, P3,...,P82\}$          |
|                       | $D$              | Conjunto de dias da semana, onde $d \in D = \{1, 2, 3, 4, 5\}$            |
|                       | $T$              | Conjunto de turmas onde os professores deverão ministrar aulas, com $t \in T = \{T1, T2, T3,..., T43\}$ |
|                       | $H$              | Conjunto de horários disponíveis em cada dia, onde $h \in H = \{1, 2, 3, 4,..., 16\}$ |
|                       | $PT[p,t]$        | Matriz com o número de aulas de cada professor em cada turma, com $p \in P$ e $t \in T$ |
| **Variáveis de decisão** | $x^{p,t}_{d,h}$  | Variável binária que indica se o professor $p$ está alocado na turma $t$ no dia $d$ no horário $h$ |
|                       | $CustoP^{p,t}_{d}$ | Variável inteira que define o **Custo Pedagógico** do professor $p$ estar alocado na turma $t$ no dia $d$ (a ser minimizado) |
|                       | $CustoD_{p,t}$   | Variável inteira que define o **Custo Docente** do professor $p$ estar alocado na turma $t$ (a ser minimizado) |


### Restrições básicas

$$
\sum_{p \in P} x^{p,t}_{d,h} \leq 1; \quad \forall d \in D, \forall h \in H, \forall t \in T.  
$$

---

$$
\sum_{t \in T} x^{p,t}_{d,h} \leq 1; \quad \forall d \in D, \forall h \in H, \forall p \in P.
$$

---

$$\sum_{d \in D, h \in H} x^{p,t}_{d,h} = PT[p,t]; \quad \forall p \in P, \forall t \in T.$$

---

$$\sum_{p \in P} x^{p,t}_{d,h} = 0; \quad \forall t \in \{1...4\}, \forall h \in \{7...16\}, \forall d \in D.$$

### Aulas geminadas


**Tabela 2:** Estrutura para o tratamento de aulas geminadas
| **Categoria**              | **Notações**          | **Descrição**                                                                 |
|----------------------------|-----------------------|-------------------------------------------------------------------------------|
| **Matrizes**               | `$G2[p,t]$`           | Matriz que indica se o professor `$p$` possui aula geminada de dois tempos na turma `$t$`. |
|                            | `$G22[p,t]$`          | Matriz que indica se o professor `$p$` possui duas aulas geminadas de dois tempos na turma `$t$`. |
|                            | `$G3[p,t]$`           | Matriz que indica se o professor `$p$` possui aula geminada de três tempos na turma `$t$`. |
| **Variáveis de Decisão**    | `$y2^{p,t}_{d}$`      | Variável binária que indica se o professor `$p$` tem aula geminada de dois tempos na turma `$t$` no dia `$d$`. |
|                            | `$y2a^{p,t}_{d}$`<br>`$y2b^{p,t}_{d}$` | Variáveis binárias que indicam se o professor `$p$` possui duas aulas geminadas de dois tempos (uma para cada aula) na turma `$t$` no dia `$d$`. |
|                            | `$y3^{p,t}_{d}$`      | Variável binária que indica se o professor `$p$` possui uma aula geminada de três tempos na turma `$t$` no dia `$d$`. |

### Restrições:

#### Uma aula geminada com dois tempos

$$\sum_{d \in D} y2^{p,t}_{d} = 1; \quad \forall p \in P, \forall t \in T: G2[p,t]=1.$$

---

$$
\textbf{Se } ( y2^{p,t}_{d} = 1 ) \textbf{ então } \big(( x^{p,t}_{d,1} = 1 \textbf{ e } x^{p,t}_{d,2} = 1 ) \textbf{ ou } \\ 
( x^{p,t}_{d,2} = 1 \textbf{ e } x^{p,t}_{d,3} = 1) \textbf{ ou } \dots \textbf{ ou } \\ 
( x^{p,t}_{d,15} = 1 \textbf{ e } x^{p,t}_{d,16} = 1)\big); \\ 
\forall d \in D, \forall p \in P, \forall t \in T: G2[p,t] = 1.
$$

#### Duas aulas geminadas com dois tempos

$$\sum_{d \in D} y2a^{p,t}_{d} = 1; \quad \forall p \in P, \forall t \in T : G22[p,t]=1.$$

---

$$\sum_{d \in D} y2b^{p,t}_{d} = 1; \quad \forall p \in P, \forall t \in T : G22[p,t]=1.$$

---

$$y2a^{p,t}_{d} + y2b^{p,t}_{d} \leq 1; \quad \forall p \in P, \forall t \in T: G22[p,t]=1.$$

---

$$
\textbf{Se } (y2a^{p,t}_{d} = 1) \textbf{ ou } (y2b^{p,t}_{d} = 1) \textbf{ então } 
\begin{aligned}
&\big((x^{p,t}_{d,1} = 1 \textbf{ e } x^{p,t}_{d,2} = 1) \textbf{ ou } \\
&(x^{p,t}_{d,2} = 1 \textbf{ e } x^{p,t}_{d,3} = 1) \textbf{ ou } \dots \textbf{ ou } \\
&(x^{p,t}_{d,15} = 1 \textbf{ e } x^{p,t}_{d,16} = 1)\big);
\end{aligned}
\\ \forall d \in D, \forall p \in P, \forall t \in T: G22[p,t] = 1.
$$

---

#### Uma Aula Geminada com Dois Tempos e uma Aula Geminada com Três Tempos

$$\sum_{d \in D} y3^{p,t}_{d} = 1; \quad \forall p \in P, \forall t \in T : G3[p,t]=1.$$

---

$$
\textbf{Se } (y3^{p,t}_{d} = 1) \textbf{ então }
\begin{aligned}
&\big((x^{p,t}_{d,1} = 1 \land x^{p,t}_{d,2} = 1 \land x^{p,t}_{d,3} = 1) \lor \\
&(x^{p,t}_{d,2} = 1 \land x^{p,t}_{d,3} = 1 \land x^{p,t}_{d,4} = 1) \lor \\
&\quad \vdots \\
&(x^{p,t}_{d,14} = 1 \land x^{p,t}_{d,15} = 1 \land x^{p,t}_{d,16} = 1)\big);
\end{aligned}
\\ \forall d \in D, \forall p \in P, \forall t \in T: G3[p,t] = 1.
$$

---

$$y2^{p,t}_{d} + y3^{p,t}_{d} \leq 1; \quad \forall p \in P, \forall t \in T, \forall d \in D: G2[p,t]=1 \land G3[p,t]=1.$$

### Restrições para o Custo Pedagígico (CP)





