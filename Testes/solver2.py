from docplex.mp.model import Model

# =====================================================
# Parâmetros (dados do arquivo .dat)
# =====================================================
diasPorSemana   = 5
aulasPorDia     = 16
totalTurmas     = 43
totalProfessores = 82

# Definição dos conjuntos
Dias         = range(1, diasPorSemana + 1)
Horarios     = range(1, aulasPorDia + 1)
Turmas       = range(1, totalTurmas + 1)
Professores  = range(1, totalProfessores + 1)

# -----------------------------------------------------
# Parâmetros extraídos dos dados (arquivo .dat e Excel)
# Estes devem ser substituídos pelos dados reais.
# Por exemplo, a partir do pandas ou xlrd, conforme sua implementação.
# -----------------------------------------------------
# Exemplo de carregamento (substituir pelos dados reais):
# import pandas as pd
# df_G2 = pd.read_excel("Matrizes.xlsx", sheet_name="G2", header=None, skiprows=2, usecols="B:AR")
# ... (processar para obter um dicionário com chaves (p,t))
#
# Para este exemplo, utilizamos valores fictícios:
#ProfTurma = {(p, t): 1 for p in Professores for t in Turmas}  # Ex.: 1 aula por (p,t)
#G2       = {(p, t): 0 for p in Professores for t in Turmas}  # 0 ou 1
#G22      = {(p, t): 0 for p in Professores for t in Turmas}  # 0 ou 1
#G3       = {(p, t): 0 for p in Professores for t in Turmas}  # 0 ou 1

import pandas as pd

df_g2 = pd.read_excel("Matrizes.xlsx", sheet_name="G2", usecols="B:AR", skiprows=2, nrows=82, header=None)
G2 = {(i, j): df_g2.iat[i, j]
      for i in range(df_g2.shape[0])
      for j in range(df_g2.shape[1])}

df_g22 = pd.read_excel("Matrizes.xlsx", sheet_name="G22", usecols="B:AR", skiprows=2, nrows=82, header=None)
G22 = {(i, j): df_g2.iat[i, j]
      for i in range(df_g22.shape[0])
      for j in range(df_g22.shape[1])}

df_g3 = pd.read_excel("Matrizes.xlsx", sheet_name="G3", usecols="B:AR", skiprows=2, nrows=82, header=None)
G3 = {(i, j): df_g2.iat[i, j]
      for i in range(df_g3.shape[0])
      for j in range(df_g3.shape[1])}

df_prof_turma = pd.read_excel("Matrizes.xlsx", sheet_name="ProfTurma", usecols="B:AR", skiprows=2, nrows=82, header=None)
ProfTurma = {(i, j): df_prof_turma.iat[i, j]
      for i in range(df_prof_turma.shape[0])
      for j in range(df_prof_turma.shape[1])}

# =====================================================
# Criação do modelo
# =====================================================
mdl = Model("GradeHorarios")

# =====================================================
# Variáveis de decisão
# =====================================================
# Variável x[p,t,d,h]: 1 se o professor p leciona na turma t no dia d, horário h.
x = {(p, t, d, h): mdl.binary_var(name=f"x_{p}_{t}_{d}_{h}")
     for p in Professores for t in Turmas for d in Dias for h in Horarios}

# Variáveis para aulas geminadas:
y2   = {(p, t, d): mdl.binary_var(name=f"y2_{p}_{t}_{d}")
        for p in Professores for t in Turmas for d in Dias}
y3   = {(p, t, d): mdl.binary_var(name=f"y3_{p}_{t}_{d}")
        for p in Professores for t in Turmas for d in Dias}
y2a  = {(p, t, d): mdl.binary_var(name=f"y2a_{p}_{t}_{d}")
        for p in Professores for t in Turmas for d in Dias}
y2b  = {(p, t, d): mdl.binary_var(name=f"y2b_{p}_{t}_{d}")
        for p in Professores for t in Turmas for d in Dias}

# Variáveis de custo (não negativas, inteiras)
CustoCP1 = {(p, t, d): mdl.integer_var(lb=0, name=f"CustoCP1_{p}_{t}_{d}")
            for p in Professores for t in Turmas for d in Dias}
CustoCP2 = {(p, t, d): mdl.integer_var(lb=0, name=f"CustoCP2_{p}_{t}_{d}")
            for p in Professores for t in Turmas for d in Dias}
CustoCP3 = {(p, t, d): mdl.integer_var(lb=0, name=f"CustoCP3_{p}_{t}_{d}")
            for p in Professores for t in Turmas for d in Dias}
CustoCP4 = {(p, d): mdl.integer_var(lb=0, name=f"CustoCP4_{p}_{d}")
            for p in Professores for d in Dias}

CustoPD1 = {(p, t): mdl.integer_var(lb=0, name=f"CustoPD1_{p}_{t}")
            for p in Professores for t in Turmas}
CustoPD2 = {(p, t): mdl.integer_var(lb=0, name=f"CustoPD2_{p}_{t}")
            for p in Professores for t in Turmas}
CustoPD3 = {(p, t): mdl.integer_var(lb=0, name=f"CustoPD3_{p}_{t}")
            for p in Professores for t in Turmas}
CustoPD4 = {(p, t): mdl.integer_var(lb=0, name=f"CustoPD4_{p}_{t}")
            for p in Professores for t in Turmas}
CustoPD5 = {(p, t): mdl.integer_var(lb=0, name=f"CustoPD5_{p}_{t}")
            for p in Professores for t in Turmas}

# =====================================================
# Função objetivo: minimizar a soma dos custos
# =====================================================
mdl.minimize(
    mdl.sum(CustoCP1[p, t, d] for p in Professores for t in Turmas for d in Dias) +
    mdl.sum(CustoCP2[p, t, d] for p in Professores for t in Turmas for d in Dias) +
    mdl.sum(CustoCP3[p, t, d] for p in Professores for t in Turmas for d in Dias) +
    mdl.sum(CustoCP4[p, d]    for p in Professores for d in Dias) +
    mdl.sum(CustoPD1[p, t]    for p in Professores for t in Turmas) +
    mdl.sum(CustoPD2[p, t]    for p in Professores for t in Turmas) +
    mdl.sum(CustoPD3[p, t]    for p in Professores for t in Turmas) +
    mdl.sum(CustoPD4[p, t]    for p in Professores for t in Turmas) +
    mdl.sum(CustoPD5[p, t]    for p in Professores for t in Turmas)
)

# =====================================================
# Restrições do modelo
# =====================================================

# 1. Em cada horário de uma dada turma, no máximo um professor
for d in Dias:
    for h in Horarios:
        for t in Turmas:
            mdl.add_constraint(mdl.sum(x[p, t, d, h] for p in Professores) <= 1,
                               ctname=f"UnicoProf_t{t}_d{d}_h{h}")

# 2. Cada professor só pode estar em uma sala por vez
for d in Dias:
    for h in Horarios:
        for p in Professores:
            mdl.add_constraint(mdl.sum(x[p, t, d, h] for t in Turmas) <= 1,
                               ctname=f"ProfUnico_p{p}_d{d}_h{h}")

# 3. Alocação do número de aulas de cada professor em cada turma
for p in Professores:
    for t in Turmas:
        mdl.add_constraint(mdl.sum(x[p, t, d, h] for d in Dias for h in Horarios) == ProfTurma[(p-1, t-1)],
                           ctname=f"AulasProf_p{p}_t{t}")

# 4. Restrições de horários para turmas
# 4.a. Turmas 1 a 4: não podem ter aulas nos horários 7 a 16
for t in range(1, 5):
    for d in Dias:
        for h in range(7, 17):
            mdl.add_constraint(mdl.sum(x[p, t, d, h] for p in Professores) == 0,
                               ctname=f"EM_T{t}_d{d}_h{h}")

# 4.b. Turmas 5 a 8:
for t in range(5, 9):
    for d in Dias:
        # Manhã: horários 1 a 6 proibidos
        for h in range(1, 7):
            mdl.add_constraint(mdl.sum(x[p, t, d, h] for p in Professores) == 0,
                               ctname=f"EM_T{t}_Manha_d{d}_h{h}")
        # Noite: horários 13 a 16 proibidos
        for h in range(13, 17):
            mdl.add_constraint(mdl.sum(x[p, t, d, h] for p in Professores) == 0,
                               ctname=f"EM_T{t}_Noite_d{d}_h{h}")

# 4.c. Turmas 9 a 20: não podem ter aulas nos horários 1 a 12
for t in range(9, 21):
    for d in Dias:
        for h in range(1, 13):
            mdl.add_constraint(mdl.sum(x[p, t, d, h] for p in Professores) == 0,
                               ctname=f"Concom_T{t}_d{d}_h{h}")

# 4.d. Turmas do ensino superior e demais especificações
# Exemplos conforme o modelo original:
# Turmas 21 e 23: proibido horário 7 a 16
for t in [21, 23]:
    for d in Dias:
        for h in range(7, 17):
            mdl.add_constraint(mdl.sum(x[p, t, d, h] for p in Professores) == 0,
                               ctname=f"Sup1_T{t}_d{d}_h{h}")
# Turmas 22 e 24: proibido horários 1 a 6 e 13 a 16
for t in [22, 24]:
    for d in Dias:
        for h in list(range(1, 7)) + list(range(13, 17)):
            mdl.add_constraint(mdl.sum(x[p, t, d, h] for p in Professores) == 0,
                               ctname=f"Sup2_T{t}_d{d}_h{h}")
# Turmas 25 a 31: proibido horário 13 a 16
for t in range(25, 32):
    for d in Dias:
        for h in range(13, 17):
            mdl.add_constraint(mdl.sum(x[p, t, d, h] for p in Professores) == 0,
                               ctname=f"Eng_T{t}_d{d}_h{h}")
# Turmas 32 e 34: proibido horários 1 a 6 e 13 a 16
for t in [32, 34]:
    for d in Dias:
        for h in list(range(1, 7)) + list(range(13, 17)):
            mdl.add_constraint(mdl.sum(x[p, t, d, h] for p in Professores) == 0,
                               ctname=f"EMe_T{t}_d{d}_h{h}")
# Turma 33: proibido horário 7 a 16
for t in [33]:
    for d in Dias:
        for h in range(7, 17):
            mdl.add_constraint(mdl.sum(x[p, t, d, h] for p in Professores) == 0,
                               ctname=f"EMe2_T{t}_d{d}_h{h}")
# Turma 35: proibido horário 13 a 16
for t in [35]:
    for d in Dias:
        for h in range(13, 17):
            mdl.add_constraint(mdl.sum(x[p, t, d, h] for p in Professores) == 0,
                               ctname=f"EMe3_T{t}_d{d}_h{h}")
# Turmas 36 a 43: proibido horário 1 a 6
for t in range(36, 44):
    for d in Dias:
        for h in range(1, 7):
            mdl.add_constraint(mdl.sum(x[p, t, d, h] for p in Professores) == 0,
                               ctname=f"Lic_T{t}_d{d}_h{h}")

# 5. AULAS GEMINADAS
# Nota: Para representar as restrições de implicação com disjunção (exemplo para aula geminada de 2 tempos),
# introduzimos variáveis auxiliares para cada par consecutivo possível.
pairs_2 = [(h, h+1) for h in range(1, aulasPorDia) if h+1 <= aulasPorDia]

# Aulas geminadas de 2 tempos para (p,t) com G2[p,t]==1:
for p in Professores:
    for t in Turmas:
        if G2[(p-1, t-1)] == 1:
            # Deve ocorrer exatamente um dia com aula geminada
            mdl.add_constraint(mdl.sum(y2[p, t, d] for d in Dias) == 1,
                               ctname=f"G2_count_p{p}_t{t}")
            for d in Dias:
                # Variáveis auxiliares para cada par consecutivo
                z_vars = {(h1, h2): mdl.binary_var(name=f"z_{p}_{t}_{d}_{h1}")
                          for (h1, h2) in pairs_2}
                for (h1, h2), z in z_vars.items():
                    mdl.add_constraint(z <= x[p, t, d, h1],
                                       ctname=f"z_leq_x1_p{p}_t{t}_d{d}_h{h1}")
                    mdl.add_constraint(z <= x[p, t, d, h2],
                                       ctname=f"z_leq_x2_p{p}_t{t}_d{d}_h{h1}")
                    mdl.add_constraint(z >= x[p, t, d, h1] + x[p, t, d, h2] - 1,
                                       ctname=f"z_geq_p{p}_t{t}_d{d}_h{h1}")
                # Se y2[p,t,d] == 1, então pelo menos um par consecutivo deve ocorrer
                mdl.add_constraint(mdl.sum(z_vars[pair] for pair in z_vars) >= y2[p, t, d],
                                   ctname=f"G2_impl_p{p}_t{t}_d{d}")

# De forma similar, as restrições para aula geminada de 3 tempos (y3) e para as duplas geminadas (y2a, y2b)
# podem ser formuladas introduzindo conjuntos de três horários consecutivos e variáveis auxiliares.
pairs_3 = [(h, h+1, h+2) for h in range(1, aulasPorDia - 1) if h+2 <= aulasPorDia]

for p in Professores:
    for t in Turmas:
        if G3[(p-1, t-1)] == 1:
            mdl.add_constraint(mdl.sum(y3[p, t, d] for d in Dias) == 1,
                               ctname=f"G3_count_p{p}_t{t}")
            for d in Dias:
                z_vars_3 = {(h1, h2, h3): mdl.binary_var(name=f"z3_{p}_{t}_{d}_{h1}")
                            for (h1, h2, h3) in pairs_3}
                for (h1, h2, h3), z in z_vars_3.items():
                    mdl.add_constraint(z <= x[p, t, d, h1],
                                       ctname=f"z3_leq1_p{p}_t{t}_d{d}_h{h1}")
                    mdl.add_constraint(z <= x[p, t, d, h2],
                                       ctname=f"z3_leq2_p{p}_t{t}_d{d}_h{h1}")
                    mdl.add_constraint(z <= x[p, t, d, h3],
                                       ctname=f"z3_leq3_p{p}_t{t}_d{d}_h{h1}")
                    mdl.add_constraint(z >= x[p, t, d, h1] + x[p, t, d, h2] + x[p, t, d, h3] - 2,
                                       ctname=f"z3_geq_p{p}_t{t}_d{d}_h{h1}")
                mdl.add_constraint(mdl.sum(z_vars_3[pair] for pair in z_vars_3) >= y3[p, t, d],
                                   ctname=f"G3_impl_p{p}_t{t}_d{d}")

# Para turmas com duas aulas geminadas de dois tempos (G22 == 1)
for p in Professores:
    for t in Turmas:
        if G22[(p-1, t-1)] == 1:
            mdl.add_constraint(mdl.sum(y2a[p, t, d] for d in Dias) == 1,
                               ctname=f"G22a_count_p{p}_t{t}")
            mdl.add_constraint(mdl.sum(y2b[p, t, d] for d in Dias) == 1,
                               ctname=f"G22b_count_p{p}_t{t}")
            for d in Dias:
                mdl.add_constraint(y2a[p, t, d] + y2b[p, t, d] <= 1,
                                   ctname=f"G22_impl_p{p}_t{t}_d{d}")
                z_vars_22 = {(h1, h2): mdl.binary_var(name=f"z22_{p}_{t}_{d}_{h1}")
                             for (h1, h2) in pairs_2}
                for (h1, h2), z in z_vars_22.items():
                    mdl.add_constraint(z <= x[p, t, d, h1],
                                       ctname=f"z22_leq1_p{p}_t{t}_d{d}_h{h1}")
                    mdl.add_constraint(z <= x[p, t, d, h2],
                                       ctname=f"z22_leq2_p{p}_t{t}_d{d}_h{h1}")
                    mdl.add_constraint(z >= x[p, t, d, h1] + x[p, t, d, h2] - 1,
                                       ctname=f"z22_geq_p{p}_t{t}_d{d}_h{h1}")
                mdl.add_constraint(mdl.sum(z_vars_22[pair] for pair in z_vars_22) >= (y2a[p, t, d] + y2b[p, t, d]),
                                   ctname=f"G22_impl_p{p}_t{t}_d{d}")

# 6. Restrições Pedagógicas (Soft)
# Exemplo CP1:
for d in Dias:
    for t in Turmas:
        for p in Professores:
            total_aulas = mdl.sum(x[p, t, d, h] for h in Horarios)
            if G2[(p, t)] == 1 or G22[(p, t)] == 1:
                mdl.add_indicator(total_aulas >= 3, CustoCP1[p, t, d] == 10,
                                  name=f"CP1_p{p}_t{t}_d{d}")
            elif G3[(p, t)] == 1:
                mdl.add_indicator(total_aulas >= 4, CustoCP1[p, t, d] == 10,
                                  name=f"CP1_3_p{p}_t{t}_d{d}")
            else:
                mdl.add_indicator(total_aulas >= 2, CustoCP1[p, t, d] == 10,
                                  name=f"CP1_else_p{p}_t{t}_d{d}")

# CP2: Professor não pode dar aula na mesma turma em dias consecutivos
for d in range(2, diasPorSemana + 1):
    for t in Turmas:
        for p in Professores:
            prev = mdl.sum(x[p, t, d - 1, h] for h in Horarios)
            curr = mdl.sum(x[p, t, d, h] for h in Horarios)
            mdl.add_indicator((prev >= 1) & (curr >= 1), CustoCP2[p, t, d] == 3,
                              name=f"CP2_p{p}_t{t}_d{d}")

# CP3: Evitar determinados horários para alguns professores
for d in Dias:
    for t in Turmas:
        for p in [1, 4, 6, 7, 22, 24, 43, 54]:
            mdl.add_indicator(mdl.sum(x[p, t, d, h] for h in [5, 6]) >= 1,
                              CustoCP3[p, t, d] == 1,
                              name=f"CP3a_p{p}_t{t}_d{d}")
            mdl.add_indicator(mdl.sum(x[p, t, d, h] for h in [11, 12]) >= 1,
                              CustoCP3[p, t, d] == 1,
                              name=f"CP3b_p{p}_t{t}_d{d}")

# CP4: Evitar intervalos grandes entre aulas do mesmo professor
for p in Professores:
    for t in Turmas:
        for d in Dias:
            for h in range(1, aulasPorDia - 1):
                mdl.add_indicator(x[p, t, d, h] + x[p, t, d, h + 2] <= 1 + x[p, t, d, h + 1],
                                  CustoCP4[p, d] == 1,
                                  name=f"CP4_p{p}_t{t}_d{d}_h{h}")

# 7. Restrições Pessoais dos Professores (Soft)
# PD1: Professor não pode dar aula no último horário da noite e no primeiro da manhã do dia seguinte
for d in range(2, diasPorSemana + 1):
    for t in Turmas:
        for p in Professores:
            mdl.add_indicator(x[p, t, d - 1, 16] >= 1 and x[p, t, d, 1] >= 1,
                              CustoPD1[p, t] == 1,
                              name=f"PD1_p{p}_t{t}_d{d}")

# PD2: Para professores específicos, evitar aulas na última aula da manhã e primeira da tarde
for t in Turmas:
    for p in [15, 18, 23]:
        for d in Dias:
            mdl.add_indicator(mdl.sum(x[p, t, d, h] for h in [6]) >= 1 or
                              mdl.sum(x[p, t, d, h] for h in [7]) >= 1,
                              CustoPD2[p, t] == 1,
                              name=f"PD2_p{p}_t{t}_d{d}")

# PD3: Professor 1 não pode dar aula nos dois primeiros horários
for t in Turmas:
    for d in Dias:
        mdl.add_indicator(mdl.sum(x[1, t, d, h] for h in [1, 2]) >= 1,
                          CustoPD3[1, t] == 1,
                          name=f"PD3_t{t}_d{d}")

# PD4: Professores que não desejam aulas na sexta-feira (dia 5)
for t in Turmas:
    for p in [10, 14, 23, 18, 54]:
        mdl.add_indicator(mdl.sum(x[p, t, 5, h] for h in Horarios) >= 1,
                          CustoPD4[p, t] == 1,
                          name=f"PD4_p{p}_t{t}")

# PD4_: Professores que não desejam aulas na segunda-feira (dia 1)
for t in Turmas:
    for p in [8, 17, 32, 3, 44]:
        mdl.add_indicator(mdl.sum(x[p, t, 1, h] for h in Horarios) >= 1,
                          CustoPD4[p, t] == 1,
                          name=f"PD4_2_p{p}_t{t}")

# PD5: Priorização para professores substitutos na segunda (e na sexta)
for t in Turmas:
    for p in [33, 41, 42, 48]:
        mdl.add_indicator(mdl.sum(x[p, t, 1, h] for h in Horarios) >= 1,
                          CustoPD5[p, t] == 1,
                          name=f"PD5_1_p{p}_t{t}")
for t in Turmas:
    for p in [4, 28, 63, 76]:
        mdl.add_indicator(mdl.sum(x[p, t, 5, h] for h in Horarios) >= 1,
                          CustoPD5[p, t] == 1,
                          name=f"PD5_2_p{p}_t{t}")

# =====================================================
# Resolução do modelo
# =====================================================
solution = mdl.solve(log_output=True)

if solution:
    mdl.print_solution()
else:
    print("Nenhuma solução encontrada.")
