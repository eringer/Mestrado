import random
import math
import numpy as np

# Parâmetros do problema (extraídos do arquivo .dat)
diasPorSemana = 5
aulasPorDia = 16
totalTurmas = 43
totalProfessores = 82

# Parâmetros do Simulated Annealing
initial_temperature = 1000
cooling_rate = 0.995
min_temperature = 1
max_iterations = 1000

# Custos (extraídos do arquivo .dat)
CP1 = 8
CP2 = 6
CP3 = 1
CP4 = 1
PD1 = 1
PD2 = 1
PD3 = 1
PD4 = 1
PD5 = 1

matrizes = 'Matrizes.xlsx'

import pandas as pd

# ProfTurma: quantas aulas um professor deve dar em uma turma (valores típicos 0, 2 ou 3)
dfProfTurma = pd.read_excel(matrizes, sheet_name="ProfTurma", usecols="B:AR", skiprows=2, nrows=82, header=None)
ProfTurma = dfProfTurma.values

np.set_printoptions(threshold=np.inf)

# Matrizes binárias para aulas geminadas (G2, G22, G3)
dfG2 = pd.read_excel(matrizes, sheet_name="G2", usecols="B:AR", skiprows=2, nrows=82, header=None)
G2 = dfG2.values

dfG22 = pd.read_excel(matrizes, sheet_name="G22", usecols="B:AR", skiprows=2, nrows=82, header=None)
G22 = dfG22.values

dfG3 = pd.read_excel(matrizes, sheet_name="G3", usecols="B:AR", skiprows=2, nrows=82, header=None)
G3 = dfG3.values

# Função para calcular o custo total da solução
def calculate_cost(solution):
    cost = 0

    # Custo Pedagógico 1 (CP1)
    for p in range(totalProfessores):
        for t in range(totalTurmas):
            for d in range(diasPorSemana):
                aulas_no_dia = sum(solution[p][t][d][h] for h in range(aulasPorDia))
                if G2[p][t] == 1 or G22[p][t] == 1:
                    if aulas_no_dia >= 3:
                        cost += CP1
                elif G3[p][t] == 1:
                    if aulas_no_dia >= 4:
                        cost += CP1
                else:
                    if aulas_no_dia >= 2:
                        cost += CP1

    # Custo Pedagógico 2 (CP2) - Aulas em dias consecutivos
    for p in range(totalProfessores):
        for t in range(totalTurmas):
            for d in range(1, diasPorSemana):
                if sum(solution[p][t][d-1][h] for h in range(aulasPorDia)) >= 1 and \
                   sum(solution[p][t][d][h] for h in range(aulasPorDia)) >= 1:
                    cost += CP2

    # Custo Pedagógico 3 (CP3) - Professores específicos em horários específicos
    professores_exatas = {0, 3, 5, 6, 21, 23, 42, 53}  # IDs dos professores de exatas
    for p in professores_exatas:
        for t in range(totalTurmas):
            for d in range(diasPorSemana):
                if solution[p][t][d][4] == 1 or solution[p][t][d][5] == 1:  # Últimas aulas da manhã
                    cost += CP3
                if solution[p][t][d][10] == 1 or solution[p][t][d][11] == 1:  # Últimas aulas da tarde
                    cost += CP3

    # Custo Pedagógico 4 (CP4) - Aulas em turnos diferentes no mesmo dia
    for p in range(totalProfessores):
        for t in range(totalTurmas):
            for d in range(diasPorSemana):
                manha = sum(solution[p][t][d][h] for h in range(6))  # Horários 1-6 (manhã)
                tarde_noite = sum(solution[p][t][d][h] for h in range(6, aulasPorDia))  # Horários 7-16 (tarde/noite)
                if manha >= 1 and tarde_noite >= 1:
                    cost += CP4

    # Custo Pessoal 1 (PD1) - Aulas no último horário da noite e primeiro da manhã seguinte
    for p in range(totalProfessores):
        for t in range(totalTurmas):
            for d in range(1, diasPorSemana):
                if solution[p][t][d-1][15] == 1 and solution[p][t][d][0] == 1:
                    cost += PD1

    # Custo Pessoal 2 (PD2) - Professores específicos na última aula da manhã ou primeira da tarde
    professores_pd2 = {14, 17, 22}  # IDs dos professores com restrição PD2
    for p in professores_pd2:
        for t in range(totalTurmas):
            for d in range(diasPorSemana):
                if solution[p][t][d][5] == 1 or solution[p][t][d][6] == 1:
                    cost += PD2

    # Custo Pessoal 3 (PD3) - Professor 1 não pode dar aula nos dois primeiros horários
    for t in range(totalTurmas):
        for d in range(diasPorSemana):
            if solution[0][t][d][0] == 1 or solution[0][t][d][1] == 1:
                cost += PD3

    # Custo Pessoal 4 (PD4) - Professores que não querem dar aulas às sextas ou segundas
    professores_pd4_sexta = {9, 13, 22, 17, 53}  # IDs dos professores com restrição PD4 (sexta)
    professores_pd4_segunda = {7, 16, 31, 2, 43}  # IDs dos professores com restrição PD4 (segunda)
    for p in professores_pd4_sexta:
        for t in range(totalTurmas):
            if sum(solution[p][t][4][h] for h in range(aulasPorDia)) >= 1:  # Sexta-feira (dia 4)
                cost += PD4
    for p in professores_pd4_segunda:
        for t in range(totalTurmas):
            if sum(solution[p][t][0][h] for h in range(aulasPorDia)) >= 1:  # Segunda-feira (dia 0)
                cost += PD4

    # Verificação das aulas geminadas
    for p in range(totalProfessores):
        for t in range(totalTurmas):
            if G2[p][t] == 1:
                # Verifica se há uma aula geminada de 2 tempos
                geminada_valida = False
                for d in range(diasPorSemana):
                    for h in range(aulasPorDia - 1):
                        if solution[p][t][d][h] == 1 and solution[p][t][d][h+1] == 1:
                            geminada_valida = True
                            break
                    if geminada_valida:
                        break
                if not geminada_valida:
                    cost += 1000  # Penalidade alta para violação de restrição

            if G22[p][t] == 1:
                # Verifica se há duas aulas geminadas de 2 tempos em dias distintos
                dias_com_geminada = set()
                for d in range(diasPorSemana):
                    for h in range(aulasPorDia - 1):
                        if solution[p][t][d][h] == 1 and solution[p][t][d][h+1] == 1:
                            dias_com_geminada.add(d)
                            break
                if len(dias_com_geminada) < 2:
                    cost += 1000  # Penalidade alta para violação de restrição

            if G3[p][t] == 1:
                # Verifica se há uma aula geminada de 3 tempos
                geminada_valida = False
                for d in range(diasPorSemana):
                    for h in range(aulasPorDia - 2):
                        if solution[p][t][d][h] == 1 and solution[p][t][d][h+1] == 1 and solution[p][t][d][h+2] == 1:
                            geminada_valida = True
                            break
                    if geminada_valida:
                        break
                if not geminada_valida:
                    cost += 1000  # Penalidade alta para violação de restrição

    return cost

# Função para gerar uma solução inicial válida
def generate_initial_solution():
    solution = [[[[0 for _ in range(aulasPorDia)] for _ in range(diasPorSemana)] for _ in range(totalTurmas)] for _ in range(totalProfessores)]

    for p in range(totalProfessores):
        for t in range(totalTurmas):
            aulas_alocadas = 0
            while aulas_alocadas < ProfTurma[p][t]:
                d = random.randint(0, diasPorSemana - 1)
                h = random.randint(0, aulasPorDia - 1)
                if solution[p][t][d][h] == 0:
                    # Verifica se a alocação respeita as aulas geminadas
                    if G2[p][t] == 1:
                        if h < aulasPorDia - 1 and solution[p][t][d][h+1] == 0:
                            solution[p][t][d][h] = 1
                            solution[p][t][d][h+1] = 1
                            aulas_alocadas += 2
                    elif G22[p][t] == 1:
                        if h < aulasPorDia - 1 and solution[p][t][d][h+1] == 0:
                            solution[p][t][d][h] = 1
                            solution[p][t][d][h+1] = 1
                            aulas_alocadas += 2
                    elif G3[p][t] == 1:
                        if h < aulasPorDia - 2 and solution[p][t][d][h+1] == 0 and solution[p][t][d][h+2] == 0:
                            solution[p][t][d][h] = 1
                            solution[p][t][d][h+1] = 1
                            solution[p][t][d][h+2] = 1
                            aulas_alocadas += 3
                    else:
                        solution[p][t][d][h] = 1
                        aulas_alocadas += 1

    return solution

# Função para gerar uma solução vizinha
def generate_neighbor(solution):
    neighbor_solution = [[[[solution[p][t][d][h] for h in range(aulasPorDia)] for d in range(diasPorSemana)] for t in range(totalTurmas)] for p in range(totalProfessores)]

    # Escolhe um professor e uma turma aleatórios
    p = random.randint(0, totalProfessores - 1)
    t = random.randint(0, totalTurmas - 1)

    # Escolhe um dia e um horário aleatórios para remover uma aula
    d_remove = random.randint(0, diasPorSemana - 1)
    h_remove = random.randint(0, aulasPorDia - 1)
    if neighbor_solution[p][t][d_remove][h_remove] == 1:
        neighbor_solution[p][t][d_remove][h_remove] = 0

        # Escolhe um dia e um horário aleatórios para adicionar uma aula
        d_add = random.randint(0, diasPorSemana - 1)
        h_add = random.randint(0, aulasPorDia - 1)
        if neighbor_solution[p][t][d_add][h_add] == 0:
            neighbor_solution[p][t][d_add][h_add] = 1

    return neighbor_solution

# Simulated Annealing
def simulated_annealing():
    current_solution = generate_initial_solution()
    current_cost = calculate_cost(current_solution)
    best_solution = current_solution
    best_cost = current_cost
    temperature = initial_temperature

    for iteration in range(max_iterations):
        neighbor_solution = generate_neighbor(current_solution)
        neighbor_cost = calculate_cost(neighbor_solution)

        if neighbor_cost < current_cost or random.random() < math.exp((current_cost - neighbor_cost) / temperature):
            current_solution = neighbor_solution
            current_cost = neighbor_cost

            if current_cost < best_cost:
                best_solution = current_solution
                best_cost = current_cost

        temperature *= cooling_rate
        if temperature < min_temperature:
            break

    return best_solution, best_cost

# Executar o Simulated Annealing
best_solution, best_cost = simulated_annealing()
print("Melhor custo encontrado:", best_cost)