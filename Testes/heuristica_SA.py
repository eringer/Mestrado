import random
import numpy as np
import copy
import math
import pandas as pd
import time

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
    # turma: número inteiro de 1 a 43
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

# Inicializa a estrutura de solução.
# "schedule" armazena, para cada turma, dia e horário, o professor alocado (ou None)
# "prof_schedule" armazena, para cada professor e dia, o conjunto de horários em que ele já tem aula
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

# Fase Construtiva: gera solução inicial considerando as restrições e as necessidades (ProfTurma).
def initial_solution():
    schedule, prof_schedule = initialize_schedule()
    # Cria uma lista de atribuições: (professor, turma, número de aulas a agendar)
    assignments = []
    for p in range(1, totalProfessores + 1):
        for t in range(1, totalTurmas + 1):
            req = ProfTurma[p - 1, t - 1]  # ajuste de índice (Python usa índice 0)
            if req > 0:
                assignments.append((p, t, req))
    # Ordena os pares por número de aulas requeridas (maior dificuldade primeiro)
    assignments.sort(key=lambda x: x[2], reverse=True)
    
    # Para cada (p, t), tenta alocar as aulas
    for (p, t, req) in assignments:
        remaining = req
        # Se a turma exige aula geminada, tenta alocar o bloco
        gem_block = None
        if G2[p - 1, t - 1] == 1:
            gem_block = 2
            remaining -= 2
        elif G3[p - 1, t - 1] == 1:
            gem_block = 3
            remaining -= 3
        elif G22[p - 1, t - 1] == 1:
            gem_block = 2  # Simplificação: aloca um bloco de 2 (no modelo real pode ser dois blocos distintos)
            remaining -= 2
        
        # Aloca bloco geminado, se necessário
        if gem_block:
            placed = False
            days = list(range(1, diasPorSemana + 1))
            random.shuffle(days)
            for d in days:
                allowed = allowed_hours(t)
                allowed.sort()
                for h in allowed:
                    block_hours = [h + offset for offset in range(gem_block)]
                    # Verifica se o bloco cabe e se os horários estão livres para a turma e o professor
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
        
        # Aloca as horas restantes individualmente
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

# Função para contar quantas horas já foram alocadas para um dado par (professor, turma)
def count_assigned_hours(schedule, p, t):
    count = 0
    for d in range(1, diasPorSemana + 1):
        for h in range(1, aulasPorDia + 1):
            if schedule[t][d][h] == p:
                count += 1
    return count

# Fase de Reparação: verifica e tenta preencher as alocações faltantes de acordo com ProfTurma.
def repair_schedule(schedule, prof_schedule):
    for p in range(1, totalProfessores + 1):
        for t in range(1, totalTurmas + 1):
            required = ProfTurma[p - 1, t - 1]
            current = count_assigned_hours(schedule, p, t)
            missing = required - current
            if missing > 0:
                # Itera por todos os dias e horários permitidos para tentar preencher as vagas
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

# Função de custo (exemplo simplificado com as restrições soft)
def compute_cost(schedule, prof_schedule):
    cost = 0

    # CP1: Penalidade para excesso de aulas por dia, considerando blocos geminados
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

    # CP2: Penalidade se o professor leciona a mesma turma em dias consecutivos
    for p in range(1, totalProfessores + 1):
        for t in range(1, totalTurmas + 1):
            for d in range(2, diasPorSemana + 1):
                count_prev = sum(1 for h in range(1, aulasPorDia + 1) if schedule[t][d - 1][h] == p)
                count_curr = sum(1 for h in range(1, aulasPorDia + 1) if schedule[t][d][h] == p)
                if count_prev >= 1 and count_curr >= 1:
                    cost += CP2

    # CP3: Penalidade para professores específicos em horários indesejados
    cp3_set = {1, 4, 6, 7, 22, 24, 43, 54}
    for p in cp3_set:
        for t in range(1, totalTurmas + 1):
            for d in range(1, diasPorSemana + 1):
                if any(schedule[t][d].get(h) == p for h in [5, 6]):
                    cost += CP3
                if any(schedule[t][d].get(h) == p for h in [11, 12]):
                    cost += CP3

    # CP4: Penalidade se o professor tem aula na manhã e à tarde no mesmo dia
    for p in range(1, totalProfessores + 1):
        for d in range(1, diasPorSemana + 1):
            has_morning = any(h in prof_schedule[p][d] for h in range(1, 7))
            has_afternoon = any(h in prof_schedule[p][d] for h in range(13, 17))
            if has_morning and has_afternoon:
                cost += CP4

    # PD1: Penalidade se o professor tem aula no último horário de um dia e no primeiro do dia seguinte
    for p in range(1, totalProfessores + 1):
        for d in range(1, diasPorSemana):
            if 16 in prof_schedule[p][d] and 1 in prof_schedule[p][d + 1]:
                cost += PD1

    # PD2: Para os professores {15,18,23} - penaliza se houver aula na hora 6 ou 7 em qualquer dia
    pd2_set = {15, 18, 23}
    for t in range(1, totalTurmas + 1):
        for p in pd2_set:
            if any(schedule[t][d].get(h) == p for d in range(1, diasPorSemana + 1) for h in [6, 7]):
                cost += PD2

    # PD3: Para o professor 1 - penaliza se houver aula nas horas 1 ou 2 em qualquer dia
    for t in range(1, totalTurmas + 1):
        for d in range(1, diasPorSemana + 1):
            if any(schedule[t][d].get(h) == 1 for h in [1, 2]):
                cost += PD3

    # PD4: Para os professores {10,14,23,18,54} - penaliza se houver aula na sexta-feira (dia 5)
    pd4_set = {10, 14, 23, 18, 54}
    for t in range(1, totalTurmas + 1):
        for p in pd4_set:
            if any(schedule[t][5].get(h) == p for h in range(1, aulasPorDia + 1)):
                cost += PD4

    # PD4__: Para os professores {8,17,32,3,44} - penaliza se houver aula na segunda-feira (dia 1)
    pd4_set2 = {8, 17, 32, 3, 44}
    for t in range(1, totalTurmas + 1):
        for p in pd4_set2:
            if any(schedule[t][1].get(h) == p for h in range(1, aulasPorDia + 1)):
                cost += PD4

    # PD5: Para os professores {33,41,42,48} - penaliza se houver aula na segunda-feira (dia 1)
    pd5_set = {33, 41, 42, 48}
    for t in range(1, totalTurmas + 1):
        for p in pd5_set:
            if any(schedule[t][1].get(h) == p for h in range(1, aulasPorDia + 1)):
                cost += PD5

    # PD5__: Para os professores {4,28,63,76} - penaliza se houver aula na sexta-feira (dia 5)
    pd5_set2 = {4, 28, 63, 76}
    for t in range(1, totalTurmas + 1):
        for p in pd5_set2:
            if any(schedule[t][5].get(h) == p for h in range(1, aulasPorDia + 1)):
                cost += PD5

    return cost

# Melhoria: uma versão simples de Simulated Annealing para buscar melhorias na solução
def simulated_annealing(schedule, prof_schedule, initial_cost, iterations=1000, initial_temp=500.0, cooling_rate=0.99):
    current_schedule = copy.deepcopy(schedule)
    current_prof = copy.deepcopy(prof_schedule)
    best_schedule = copy.deepcopy(schedule)
    best_prof = copy.deepcopy(prof_schedule)
    current_cost = initial_cost
    best_cost = initial_cost
    temp = initial_temp
    
    for i in range(iterations):
        new_schedule = copy.deepcopy(current_schedule)
        new_prof = copy.deepcopy(current_prof)
        
        # Modificação simples: seleciona aleatoriamente uma alocação e tenta movê-la para outro horário permitido
        t = random.randint(1, totalTurmas)
        d = random.randint(1, diasPorSemana)
        h = random.randint(1, aulasPorDia)
        if new_schedule[t][d][h] is not None:
            p = new_schedule[t][d][h]
            new_schedule[t][d][h] = None
            new_prof[p][d].remove(h)
            
            allowed = allowed_hours(t)
            random.shuffle(allowed)
            found = False
            for d_new in range(1, diasPorSemana + 1):
                for h_new in allowed:
                    if new_schedule[t][d_new][h_new] is None and h_new not in new_prof[p][d_new]:
                        new_schedule[t][d_new][h_new] = p
                        new_prof[p][d_new].add(h_new)
                        found = True
                        break
                if found:
                    break
            if not found:
                new_schedule[t][d][h] = p
                new_prof[p][d].add(h)
        
        new_cost = compute_cost(new_schedule, new_prof)
        delta = new_cost - current_cost
        if delta < 0 or random.random() < math.exp(-delta / temp):
            current_schedule = new_schedule
            current_prof = new_prof
            current_cost = new_cost
            if current_cost < best_cost:
                best_schedule = copy.deepcopy(current_schedule)
                best_prof = copy.deepcopy(current_prof)
                best_cost = current_cost
        
        temp *= cooling_rate
    
    return best_schedule, best_prof, best_cost

# Função para salvar a solução final em um arquivo de texto
def save_solution(schedule, filename="solucao.txt"):
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

# Função principal
def main():
    # Medir o tempo de execução
    start_time = time.perf_counter()

    # Fase construtiva
    schedule, prof_schedule = initial_solution()
    
    # Fase de reparo para preencher alocações faltantes conforme ProfTurma
    schedule, prof_schedule = repair_schedule(schedule, prof_schedule)
    
    initial_cost = compute_cost(schedule, prof_schedule)
    print("Custo inicial:", initial_cost)
    
    # Fase de melhoria com Simulated Annealing
    best_schedule, best_prof, best_cost = simulated_annealing(schedule, prof_schedule, initial_cost, iterations=1000)
    print("Melhor custo após simulated annealing:", best_cost)
    
    # Salva a solução final em arquivo txt
    save_solution(best_schedule, filename="solucao_final.txt")
    
    end_time = time.perf_counter()


if __name__ == "__main__":
    start_time = time.time()  # Marca o início

    main()

    end_time = time.time()  # Marca o fim

    print("Tempo de execução:", end_time - start_time, "segundos")
