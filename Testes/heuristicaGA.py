import random
import numpy as np
import copy
import math
import time
import pandas as pd

# Parâmetros (conforme arquivo .dat)
diasPorSemana = 5
aulasPorDia = 16
totalTurmas = 43
totalProfessores = 82

# Custos (valores conforme arquivo .dat)
CP1 = 8
CP2 = 6
CP3 = 1
CP4 = 1
PD1 = 1
PD2 = 1
PD3 = 1
PD4 = 1
PD5 = 1

# Função que define os horários permitidos para cada turma, conforme restrições do modelo
def allowed_hours(turma):
    if 1 <= turma <= 4:
        return list(range(1, 7))        # Ensino Médio 1 a 4: apenas manhã (1-6)
    elif 5 <= turma <= 8:
        return list(range(7, 13))       # Ensino Médio 5 a 8: apenas tarde (7-12)
    elif 9 <= turma <= 20:
        return list(range(13, 17))      # Concomitante: apenas noite (13-16)
    elif turma in [21, 23]:
        return list(range(1, 7))        # Superior (bsi e bsi5): apenas manhã (1-6)
    elif turma in [22, 24]:
        return list(range(7, 13))       # Superior (bsi3 e bsi7): apenas tarde (7-12)
    elif 25 <= turma <= 31:
        return list(range(1, 13))       # Engenharia de minas, EMe1, EMe3: manhã e tarde (1-12)
    elif turma in [32, 34]:
        return list(range(7, 13))       # EMe5 e EMe9: apenas tarde (7-12)
    elif turma == 33:
        return list(range(1, 7))        # EMe7: apenas manhã (1-6)
    elif turma == 35:
        return list(range(1, 13))       # EMe10: manhã e tarde (1-12)
    elif 36 <= turma <= 43:
        return list(range(7, 17))       # Licenciatura em Matemática: tarde/noite (7-16)
    else:
        return list(range(1, 17))

matrizes = 'Matrizes.xlsx'

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

# Inicializa as estruturas de solução.
def initialize_schedule():
    schedule = {}
    for t in range(1, totalTurmas + 1):
        schedule[t] = {}
        for d in range(1, diasPorSemana + 1):
            schedule[t][d] = {h: None for h in range(1, aulasPorDia + 1)}
    prof_schedule = {}
    for p in range(1, totalProfessores + 1):
        prof_schedule[p] = {d: set() for d in range(1, diasPorSemana + 1)}
    return schedule, prof_schedule

# Função que gera uma solução inicial (utilizando o método construtivo já desenvolvido)
def initial_solution():
    schedule, prof_schedule = initialize_schedule()
    assignments = []
    for p in range(1, totalProfessores + 1):
        for t in range(1, totalTurmas + 1):
            req = ProfTurma[p - 1, t - 1]
            if req > 0:
                assignments.append((p, t, req))
    assignments.sort(key=lambda x: x[2], reverse=True)
    
    for (p, t, req) in assignments:
        remaining = req
        gem_block = None
        if G2[p - 1, t - 1] == 1:
            gem_block = 2
            remaining -= 2
        elif G3[p - 1, t - 1] == 1:
            gem_block = 3
            remaining -= 3
        elif G22[p - 1, t - 1] == 1:
            gem_block = 2
            remaining -= 2
        
        if gem_block:
            placed = False
            days = list(range(1, diasPorSemana + 1))
            random.shuffle(days)
            for d in days:
                allowed = allowed_hours(t)
                allowed.sort()
                for h in allowed:
                    block_hours = [h + offset for offset in range(gem_block)]
                    if all((hour in allowed and hour <= aulasPorDia) for hour in block_hours):
                        if all(schedule[t][d][hour] is None for hour in block_hours) and \
                           all(hour not in prof_schedule[p][d] for hour in block_hours):
                            for hour in block_hours:
                                schedule[t][d][hour] = p
                                prof_schedule[p][d].add(hour)
                            placed = True
                            break
                if placed:
                    break
            if not placed:
                print(f"Warning: Não foi possível alocar bloco geminado para professor {p}, turma {t}")
        
        while remaining > 0:
            placed = False
            days = list(range(1, diasPorSemana + 1))
            random.shuffle(days)
            for d in days:
                allowed = allowed_hours(t)
                random.shuffle(allowed)
                for h in allowed:
                    if schedule[t][d][h] is None and h not in prof_schedule[p][d]:
                        schedule[t][d][h] = p
                        prof_schedule[p][d].add(h)
                        remaining -= 1
                        placed = True
                        break
                if placed:
                    break
            if not placed:
                print(f"Warning: Falha na alocação individual para professor {p}, turma {t}. Horas restantes: {remaining}")
                break
    return schedule, prof_schedule

# Função para contar as horas já alocadas para um par (p, t)
def count_assigned_hours(schedule, p, t):
    count = 0
    for d in range(1, diasPorSemana + 1):
        for h in range(1, aulasPorDia + 1):
            if schedule[t][d][h] == p:
                count += 1
    return count

# Fase de reparo para preencher alocações faltantes conforme ProfTurma.
def repair_schedule(schedule, prof_schedule):
    for p in range(1, totalProfessores + 1):
        for t in range(1, totalTurmas + 1):
            required = ProfTurma[p - 1, t - 1]
            current = count_assigned_hours(schedule, p, t)
            missing = required - current
            if missing > 0:
                for d in range(1, diasPorSemana + 1):
                    allowed = allowed_hours(t)
                    for h in allowed:
                        if schedule[t][d][h] is None and (h not in prof_schedule[p][d]):
                            schedule[t][d][h] = p
                            prof_schedule[p][d].add(h)
                            missing -= 1
                            if missing == 0:
                                break
                    if missing == 0:
                        break
            if missing > 0:
                print(f"Warning: Ainda faltam {missing} horas para o professor {p} na turma {t}")
    return schedule, prof_schedule

# Função para recalcular a estrutura prof_schedule a partir do schedule
def compute_prof_schedule(schedule):
    prof_schedule = {p: {d: set() for d in range(1, diasPorSemana+1)} for p in range(1, totalProfessores+1)}
    for t in range(1, totalTurmas+1):
        for d in range(1, diasPorSemana+1):
            for h in range(1, aulasPorDia+1):
                p = schedule[t][d][h]
                if p is not None:
                    prof_schedule[p][d].add(h)
    return prof_schedule

# Função de reparo de conflitos: garante que um professor não seja alocado em duas turmas no mesmo dia/hora.
def repair_conflicts(schedule):
    conflict_removed = False
    prof_schedule = compute_prof_schedule(schedule)
    for d in range(1, diasPorSemana+1):
        assignments_by_hour = {}
        for t in range(1, totalTurmas+1):
            for h in range(1, aulasPorDia+1):
                p = schedule[t][d][h]
                if p is not None:
                    key = (p, h)
                    assignments_by_hour.setdefault(key, []).append((t, d, h))
        for (p, h), cells in assignments_by_hour.items():
            if len(cells) > 1:
                for (t, d, h) in cells[1:]:
                    schedule[t][d][h] = None
                    conflict_removed = True
    if conflict_removed:
        prof_schedule = compute_prof_schedule(schedule)
    return schedule, prof_schedule

# Função de custo completa, conforme restrições soft definidas
def compute_cost(schedule, prof_schedule):
    cost = 0

    # CP1: penaliza excesso de aulas por dia, considerando blocos geminados
    for p in range(1, totalProfessores + 1):
        for t in range(1, totalTurmas + 1):
            for d in range(1, diasPorSemana + 1):
                count = sum(1 for h in range(1, aulasPorDia + 1) if schedule[t][d][h] == p)
                if G2[p - 1, t - 1] == 1 or G22[p - 1, t - 1] == 1:
                    if count >= 3:
                        cost += CP1
                elif G3[p - 1, t - 1] == 1:
                    if count >= 4:
                        cost += CP1
                else:
                    if count >= 2:
                        cost += CP1

    # CP2: penaliza se o professor leciona a mesma turma em dias consecutivos
    for p in range(1, totalProfessores + 1):
        for t in range(1, totalTurmas + 1):
            for d in range(2, diasPorSemana + 1):
                count_prev = sum(1 for h in range(1, aulasPorDia + 1) if schedule[t][d - 1][h] == p)
                count_curr = sum(1 for h in range(1, aulasPorDia + 1) if schedule[t][d][h] == p)
                if count_prev >= 1 and count_curr >= 1:
                    cost += CP2

    # CP3: penaliza para professores específicos em horários indesejados
    cp3_set = {1, 4, 6, 7, 22, 24, 43, 54}
    for p in cp3_set:
        for t in range(1, totalTurmas + 1):
            for d in range(1, diasPorSemana + 1):
                if any(schedule[t][d].get(h) == p for h in [5, 6]):
                    cost += CP3
                if any(schedule[t][d].get(h) == p for h in [11, 12]):
                    cost += CP3

    # CP4: penaliza se o professor tem aula na manhã e à tarde no mesmo dia
    for p in range(1, totalProfessores + 1):
        for d in range(1, diasPorSemana + 1):
            has_morning = any(h in prof_schedule[p][d] for h in range(1, 7))
            has_afternoon = any(h in prof_schedule[p][d] for h in range(13, 17))
            if has_morning and has_afternoon:
                cost += CP4

    # PD1: penaliza se o professor tem aula no último horário de um dia e no primeiro do dia seguinte
    for p in range(1, totalProfessores + 1):
        for d in range(1, diasPorSemana):
            if 16 in prof_schedule[p][d] and 1 in prof_schedule[p][d + 1]:
                cost += PD1

    # PD2: para os professores {15,18,23} se houver aula na hora 6 ou 7 em qualquer dia
    pd2_set = {15, 18, 23}
    for t in range(1, totalTurmas + 1):
        for p in pd2_set:
            if any(schedule[t][d].get(h) == p for d in range(1, diasPorSemana + 1) for h in [6, 7]):
                cost += PD2

    # PD3: para o professor 1 se houver aula nas horas 1 ou 2 em qualquer dia
    for t in range(1, totalTurmas + 1):
        for d in range(1, diasPorSemana + 1):
            if any(schedule[t][d].get(h) == 1 for h in [1, 2]):
                cost += PD3

    # PD4: para os professores {10,14,23,18,54} se houver aula na sexta-feira (dia 5)
    pd4_set = {10, 14, 23, 18, 54}
    for t in range(1, totalTurmas + 1):
        for p in pd4_set:
            if any(schedule[t][5].get(h) == p for h in range(1, aulasPorDia + 1)):
                cost += PD4

    # PD4__ (também PD4): para os professores {8,17,32,3,44} se houver aula na segunda-feira (dia 1)
    pd4_set2 = {8, 17, 32, 3, 44}
    for t in range(1, totalTurmas + 1):
        for p in pd4_set2:
            if any(schedule[t][1].get(h) == p for h in range(1, aulasPorDia + 1)):
                cost += PD4

    # PD5: para os professores {33,41,42,48} se houver aula na segunda-feira (dia 1)
    pd5_set = {33, 41, 42, 48}
    for t in range(1, totalTurmas + 1):
        for p in pd5_set:
            if any(schedule[t][1].get(h) == p for h in range(1, aulasPorDia + 1)):
                cost += PD5

    # PD5__: para os professores {4,28,63,76} se houver aula na sexta-feira (dia 5)
    pd5_set2 = {4, 28, 63, 76}
    for t in range(1, totalTurmas + 1):
        for p in pd5_set2:
            if any(schedule[t][5].get(h) == p for h in range(1, aulasPorDia + 1)):
                cost += PD5

    return cost

# Função para gerar um indivíduo usando a solução inicial e o reparo
def generate_individual():
    schedule, prof_schedule = initial_solution()
    schedule, prof_schedule = repair_schedule(schedule, prof_schedule)
    return schedule, prof_schedule

# Operador de crossover: para cada célula (turma, dia, horário) o filho herda de um dos pais
def crossover(parent1, parent2):
    schedule1, _ = parent1
    schedule2, _ = parent2
    child_schedule = {}
    for t in range(1, totalTurmas + 1):
        child_schedule[t] = {}
        for d in range(1, diasPorSemana + 1):
            child_schedule[t][d] = {}
            for h in range(1, aulasPorDia + 1):
                if random.random() < 0.5:
                    child_schedule[t][d][h] = schedule1[t][d][h]
                else:
                    child_schedule[t][d][h] = schedule2[t][d][h]
    child_schedule, child_prof = repair_conflicts(child_schedule)
    child_schedule, child_prof = repair_schedule(child_schedule, child_prof)
    return child_schedule, child_prof

# Operador de mutação: remove aleatoriamente algumas alocações (nas células permitidas) e chama o reparo
def mutation(individual, mutation_rate=0.05):
    schedule, prof_schedule = individual
    for t in range(1, totalTurmas + 1):
        for d in range(1, diasPorSemana + 1):
            allowed = allowed_hours(t)
            for h in allowed:
                if random.random() < mutation_rate:
                    if schedule[t][d][h] is not None:
                        schedule[t][d][h] = None
    prof_schedule = compute_prof_schedule(schedule)
    schedule, prof_schedule = repair_conflicts(schedule)
    schedule, prof_schedule = repair_schedule(schedule, prof_schedule)
    return schedule, prof_schedule

# Seleção por torneio
def tournament_selection(population, tournament_size=3):
    selected = random.sample(population, tournament_size)
    selected.sort(key=lambda ind: compute_cost(ind[0], ind[1]))
    return selected[0]

# Algoritmo Genético
def genetic_algorithm(population_size=50, generations=100, mutation_rate=0.05):
    population = [generate_individual() for _ in range(population_size)]
    best_individual = None
    best_cost = float('inf')
    
    for g in range(generations):
        new_population = []
        while len(new_population) < population_size:
            parent1 = tournament_selection(population)
            parent2 = tournament_selection(population)
            child1 = crossover(parent1, parent2)
            child2 = crossover(parent2, parent1)
            child1 = mutation(child1, mutation_rate)
            child2 = mutation(child2, mutation_rate)
            new_population.extend([child1, child2])
        population = new_population[:population_size]
        for individual in population:
            cost = compute_cost(individual[0], individual[1])
            if cost < best_cost:
                best_cost = cost
                best_individual = individual
        print(f"Geração {g+1}, melhor custo: {best_cost}")
    return best_individual

# Função para salvar a solução final em um arquivo de texto
def save_solution(schedule, filename="solucao_final.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        for t in range(1, totalTurmas + 1):
            f.write(f"--- Turma {t} ---\n")
            for d in range(1, diasPorSemana + 1):
                f.write(f"Dia {d}:\n")
                for h in range(1, aulasPorDia + 1):
                    professor = schedule[t][d][h]
                    if professor is not None:
                        f.write(f"  Aula {h}: Professor {professor}\n")
                f.write("\n")

# Função principal para executar o GA e salvar a melhor solução
def main():
    start_time = time.perf_counter()
    best_schedule, best_prof = genetic_algorithm(population_size=50, generations=100, mutation_rate=0.05)
    best_cost = compute_cost(best_schedule, best_prof)
    print("Melhor custo encontrado:", best_cost)
    save_solution(best_schedule, filename="solucao_final.txt")
    end_time = time.perf_counter()
    print("Tempo de execução:", end_time - start_time, "segundos")

if __name__ == "__main__":
    main()
