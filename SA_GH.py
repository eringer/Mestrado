import random
import math
import copy
import pandas as pd
import time
import numpy as np

class ScheduleProblem:
    def __init__(self, dias_por_semana, aulas_por_dia, total_turmas, total_professores, 
                 ProfTurma, G2, G22, G3, CP_values, PD_values):
        self.dias_por_semana = dias_por_semana
        self.aulas_por_dia = aulas_por_dia
        self.total_turmas = total_turmas
        self.total_professores = total_professores
        self.ProfTurma = ProfTurma
        self.G2 = G2
        self.G22 = G22
        self.G3 = G3
        self.CP1, self.CP2, self.CP3, self.CP4 = CP_values
        self.PD1, self.PD2, self.PD3, self.PD4, self.PD5 = PD_values
        
        # Definir períodos para cada tipo de turma
        self.periodos_turmas = self.definir_periodos_turmas()
        
    def definir_periodos_turmas(self):
        periodos = {}
        
        # Ensino Médio (turmas 1-4: manhã; 5-8: tarde)
        for t in range(1, 5):
            periodos[t] = list(range(1, 7))  # Aulas 1-6 (manhã)
        for t in range(5, 9):
            periodos[t] = list(range(7, 13))  # Aulas 7-12 (tarde)
            
        # Concomitante (turmas 9-20: noite)
        for t in range(9, 21):
            periodos[t] = list(range(13, 17))  # Aulas 13-16 (noite)
            
        # Superior - BSI
        periodos[21] = list(range(1, 7))  # BSI manhã
        periodos[23] = list(range(1, 7))  # BSI5 manhã
        periodos[22] = list(range(7, 13))  # BSI3 tarde
        periodos[24] = list(range(7, 13))  # BSI7 tarde
        
        # Engenharia de Minas e outras
        for t in range(25, 32):
            periodos[t] = list(range(1, 13))  # Integral (exceto noite)
        periodos[33] = list(range(1, 7))     # EMe7 manhã
        periodos[32] = list(range(7, 13))    # EMe5 tarde
        periodos[34] = list(range(7, 13))    # EMe9 tarde
        periodos[35] = list(range(1, 13))    # EMe10 integral
        
        # Licenciatura em Matemática (tarde/noite)
        for t in range(36, 44):
            periodos[t] = list(range(7, 17))  # Aulas 7-16 (tarde/noite)
            
        return periodos

class ScheduleSolution:
    def __init__(self, problem):
        self.problem = problem
        self.schedule = self.initialize_schedule()
        self.cost = self.calculate_total_cost()


    # --- NOVO MÉTODO PARA CONTAGEM APENAS NA SOLUÇÃO FINAL ---
    def contar_violacoes(self):
        """Conta violações APENAS na solução atual (final)"""
        contadores = {
            'CP1': 0, 'CP2': 0, 'CP3': 0, 'CP4': 0,
            'PD1': 0, 'PD2': 0, 'PD3': 0, 'PD4': 0, 'PD5': 0
        }

        # ========== CONTAGEM DAS RESTRIÇÕES PEDAGÓGICAS ==========
    
        # Contagem CP1 (excesso de aulas por dia)
        for p in range(1, self.problem.total_professores + 1):
            for t in range(1, self.problem.total_turmas + 1):
                for d in range(1, self.problem.dias_por_semana + 1):
                    aulas_no_dia = sum(self.schedule[p][t][d][h] for h in range(1, self.problem.aulas_por_dia + 1))
                    tem_g2 = self.problem.G2[p-1][t-1] == 1 or self.problem.G22[p-1][t-1] == 1
                    tem_g3 = self.problem.G3[p-1][t-1] == 1
                    
                    if (tem_g2 and aulas_no_dia >= 3) or (tem_g3 and aulas_no_dia >= 4) or (not tem_g2 and not tem_g3 and aulas_no_dia >= 2):
                        contadores['CP1'] += 1

        # Contagem CP2 (aulas em dias consecutivos)
        for p in range(1, self.problem.total_professores + 1):
            for t in range(1, self.problem.total_turmas + 1):
                for d in range(2, self.problem.dias_por_semana + 1):
                    if (sum(self.schedule[p][t][d-1][h] for h in range(1, self.problem.aulas_por_dia + 1))) >= 1 and \
                    (sum(self.schedule[p][t][d][h] for h in range(1, self.problem.aulas_por_dia + 1)) >= 1):
                        contadores['CP2'] += 1

        # Contagem CP3 (professores de exatas em últimos horários)
        professores_exatas = {5, 11, 14, 18, 26, 31, 33}
        for p in professores_exatas:
            for t in range(1, self.problem.total_turmas + 1):
                for d in range(1, self.problem.dias_por_semana + 1):
                    # Últimos horários da manhã (5,6)
                    if self.schedule[p][t][d][5] == 1 or self.schedule[p][t][d][6] == 1:
                        contadores['CP3'] += 1
                    # Últimos horários da tarde (11,12)
                    if self.schedule[p][t][d][11] == 1 or self.schedule[p][t][d][12] == 1:
                        contadores['CP3'] += 1

        # Contagem CP4 (aulas em turnos distintos no mesmo dia)
        for p in range(1, self.problem.total_professores + 1):
            for d in range(1, self.problem.dias_por_semana + 1):
                tem_manha = any(self.schedule[p][t][d][h] == 1 
                            for t in range(1, self.problem.total_turmas + 1)
                            for h in range(1, 7))
                tem_noite = any(self.schedule[p][t][d][h] == 1 
                            for t in range(1, self.problem.total_turmas + 1)
                            for h in range(13, 17))
                if tem_manha and tem_noite:
                    contadores['CP4'] += 1

        # ========== CONTAGEM DAS RESTRIÇÕES DOCENTES ==========

        # Contagem PD1 (aula no último horário da noite e primeiro da manhã seguinte)
        for p in range(1, self.problem.total_professores + 1):
            for t in range(1, self.problem.total_turmas + 1):
                for d in range(2, self.problem.dias_por_semana + 1):
                    if self.schedule[p][t][d-1][16] == 1 and self.schedule[p][t][d][1] == 1:
                        contadores['PD1'] += 1

        # Contagem PD2 (professores específicos em últimos horários da manhã ou primeiros da tarde)
        professores_pd2 = {15, 18, 23}
        for p in professores_pd2:
            for t in range(1, self.problem.total_turmas + 1):
                for d in range(1, self.problem.dias_por_semana + 1):
                    if self.schedule[p][t][d][6] == 1 or self.schedule[p][t][d][7] == 1:
                        contadores['PD2'] += 1

        # Contagem PD3 (professor 1 nos dois primeiros horários)
        p = 1  # Professor específico
        for t in range(1, self.problem.total_turmas + 1):
            for d in range(1, self.problem.dias_por_semana + 1):
                if self.schedule[p][t][d][1] == 1 or self.schedule[p][t][d][2] == 1:
                    contadores['PD3'] += 1

        # Contagem PD4 (professores que não querem dar aula em determinados dias)
        professores_nao_sexta = {10, 14, 23, 18, 54}
        professores_nao_segunda = {8, 17, 32, 3, 44}
        
        # Verifica sexta-feira (dia 5)
        for p in professores_nao_sexta:
            for t in range(1, self.problem.total_turmas + 1):
                if any(self.schedule[p][t][5][h] == 1 for h in range(1, self.problem.aulas_por_dia + 1)):
                    contadores['PD4'] += 1
        
        # Verifica segunda-feira (dia 1)
        for p in professores_nao_segunda:
            for t in range(1, self.problem.total_turmas + 1):
                if any(self.schedule[p][t][1][h] == 1 for h in range(1, self.problem.aulas_por_dia + 1)):
                    contadores['PD4'] += 1

        # Contagem PD5 (prioridade para professores substitutos)
        professores_sub_segunda = {33, 41, 42, 48}
        professores_sub_sexta = {4, 28, 63, 76}
        
        # Verifica segunda-feira (dia 1)
        for p in professores_sub_segunda:
            for t in range(1, self.problem.total_turmas + 1):
                if any(self.schedule[p][t][1][h] == 1 for h in range(1, self.problem.aulas_por_dia + 1)):
                    contadores['PD5'] += 1
        
        # Verifica sexta-feira (dia 5)
        for p in professores_sub_sexta:
            for t in range(1, self.problem.total_turmas + 1):
                if any(self.schedule[p][t][5][h] == 1 for h in range(1, self.problem.aulas_por_dia + 1)):
                    contadores['PD5'] += 1

        return contadores
        
    def initialize_schedule(self):
        # Inicializa uma solução vazia
        schedule = {}
        for p in range(1, self.problem.total_professores + 1):
            schedule[p] = {}
            for t in range(1, self.problem.total_turmas + 1):
                schedule[p][t] = {}
                for d in range(1, self.problem.dias_por_semana + 1):
                    schedule[p][t][d] = [0] * (self.problem.aulas_por_dia + 1)  # +1 porque os horários começam em 1
        
        # Alocar aulas básicas (sem considerar geminadas ainda)
        for p in range(1, self.problem.total_professores + 1):
            for t in range(1, self.problem.total_turmas + 1):
                aulas = self.problem.ProfTurma[p-1][t-1]  # -1 porque Python é 0-based
                if aulas == 0:
                    continue
                    
                # Obter horários permitidos para esta turma
                horarios_permitidos = self.problem.periodos_turmas.get(t, list(range(1, self.problem.aulas_por_dia + 1)))
                
                # Alocar aulas aleatoriamente
                for _ in range(aulas):
                    alocado = False
                    tentativas = 0
                    max_tentativas = 100
                    
                    while not alocado and tentativas < max_tentativas:
                        d = random.randint(1, self.problem.dias_por_semana)
                        h = random.choice(horarios_permitidos)
                        
                        # Verificar se o professor já está alocado neste horário
                        professor_ocupado = False
                        for t2 in range(1, self.problem.total_turmas + 1):
                            if schedule[p][t2][d][h] == 1:
                                professor_ocupado = True
                                break
                                
                        # Verificar se a turma já tem aula neste horário
                        turma_ocupada = False
                        for p2 in range(1, self.problem.total_professores + 1):
                            if schedule[p2][t][d][h] == 1:
                                turma_ocupada = True
                                break
                                
                        if not professor_ocupado and not turma_ocupada:
                            schedule[p][t][d][h] = 1
                            alocado = True
                            
                        tentativas += 1
                        
                    if not alocado:
                        # Se não conseguiu alocar após várias tentativas, força em algum lugar
                        for d in range(1, self.problem.dias_por_semana + 1):
                            for h in horarios_permitidos:
                                professor_ocupado = False
                                for t2 in range(1, self.problem.total_turmas + 1):
                                    if schedule[p][t2][d][h] == 1:
                                        professor_ocupado = True
                                        break
                                        
                                turma_ocupada = False
                                for p2 in range(1, self.problem.total_professores + 1):
                                    if schedule[p2][t][d][h] == 1:
                                        turma_ocupada = True
                                        break
                                        
                                if not professor_ocupado and not turma_ocupada:
                                    schedule[p][t][d][h] = 1
                                    alocado = True
                                    break
                                    
                            if alocado:
                                break
                                
        # Processar aulas geminadas
        self.process_geminadas(schedule)
        
        return schedule
    
    def process_geminadas(self, schedule):
        # Processar aulas geminadas G2 (uma aula de 2 tempos)
        for p in range(1, self.problem.total_professores + 1):
            for t in range(1, self.problem.total_turmas + 1):
                if self.problem.G2[p-1][t-1] == 1:
                    self.alocar_geminada(schedule, p, t, 2)
        
        # Processar aulas geminadas G22 (duas aulas de 2 tempos)
        for p in range(1, self.problem.total_professores + 1):
            for t in range(1, self.problem.total_turmas + 1):
                if self.problem.G22[p-1][t-1] == 1:
                    self.alocar_geminada(schedule, p, t, 2)
                    self.alocar_geminada(schedule, p, t, 2)
        
        # Processar aulas geminadas G3 (uma aula de 3 tempos)
        for p in range(1, self.problem.total_professores + 1):
            for t in range(1, self.problem.total_turmas + 1):
                if self.problem.G3[p-1][t-1] == 1:
                    self.alocar_geminada(schedule, p, t, 3)
    
    def alocar_geminada(self, schedule, p, t, tamanho):
        horarios_permitidos = self.problem.periodos_turmas.get(t, list(range(1, self.problem.aulas_por_dia + 1)))
        dias_possiveis = list(range(1, self.problem.dias_por_semana + 1))
        random.shuffle(dias_possiveis)
        
        for d in dias_possiveis:
            # Verificar se já tem aula geminada neste dia
            tem_geminada = False
            for h in horarios_permitidos:
                if h + tamanho - 1 > max(horarios_permitidos):
                    continue
                    
                todos_livres = True
                for i in range(tamanho):
                    # Verificar se professor está livre
                    for t2 in range(1, self.problem.total_turmas + 1):
                        if schedule[p][t2][d][h+i] == 1:
                            todos_livres = False
                            break
                    
                    # Verificar se turma está livre
                    if todos_livres:
                        for p2 in range(1, self.problem.total_professores + 1):
                            if schedule[p2][t][d][h+i] == 1:
                                todos_livres = False
                                break
                                
                if todos_livres:
                    # Alocar a aula geminada
                    for i in range(tamanho):
                        schedule[p][t][d][h+i] = 1
                    tem_geminada = True
                    break
                    
            if tem_geminada:
                break
    
    def calculate_total_cost(self):
        total_cost = 0
        
        # Calcular custos pedagógicos
        total_cost += self.calculate_CP1_cost()
        total_cost += self.calculate_CP2_cost()
        total_cost += self.calculate_CP3_cost()
        total_cost += self.calculate_CP4_cost()
        
        # Calcular custos pessoais dos docentes
        total_cost += self.calculate_PD1_cost()
        total_cost += self.calculate_PD2_cost()
        total_cost += self.calculate_PD3_cost()
        total_cost += self.calculate_PD4_cost()
        total_cost += self.calculate_PD5_cost()
        
        return total_cost
    
    def calculate_CP1_cost(self):
        cost = 0
        
        for p in range(1, self.problem.total_professores + 1):
            for t in range(1, self.problem.total_turmas + 1):
                for d in range(1, self.problem.dias_por_semana + 1):
                    aulas_no_dia = sum(self.schedule[p][t][d][h] for h in range(1, self.problem.aulas_por_dia + 1))
                    
                    # Verificar se tem aula geminada
                    tem_g2 = self.problem.G2[p-1][t-1] == 1 or self.problem.G22[p-1][t-1] == 1
                    tem_g3 = self.problem.G3[p-1][t-1] == 1
                    
                    if tem_g2 and aulas_no_dia >= 3:
                        cost += self.problem.CP1
                        
                    elif tem_g3 and aulas_no_dia >= 4:
                        cost += self.problem.CP1
                        
                    elif not tem_g2 and not tem_g3 and aulas_no_dia >= 2:
                        cost += self.problem.CP1
                        
                        
        return cost
    
    def calculate_CP2_cost(self):
        cost = 0
        
        for p in range(1, self.problem.total_professores + 1):
            for t in range(1, self.problem.total_turmas + 1):
                for d in range(2, self.problem.dias_por_semana + 1):
                    aulas_ontem = sum(self.schedule[p][t][d-1][h] for h in range(1, self.problem.aulas_por_dia + 1))
                    aulas_hoje = sum(self.schedule[p][t][d][h] for h in range(1, self.problem.aulas_por_dia + 1))
                    
                    if aulas_ontem >= 1 and aulas_hoje >= 1:
                        cost += self.problem.CP2
                        
                        
        return cost
    
    def calculate_CP3_cost(self):
        cost = 0
        professores_exatas = {5, 11, 14, 18, 26, 31, 33}
        
        for p in professores_exatas:
            for t in range(1, self.problem.total_turmas + 1):
                for d in range(1, self.problem.dias_por_semana + 1):
                    # Verificar últimas aulas da manhã (5,6)
                    if (self.schedule[p][t][d][5] == 1 or self.schedule[p][t][d][6] == 1):
                        cost += self.problem.CP3
                        

                    # Verificar últimas aulas da tarde (11,12)
                    if (self.schedule[p][t][d][11] == 1 or self.schedule[p][t][d][12] == 1):
                        cost += self.problem.CP3
                        
                        
        return cost
    
    def calculate_CP4_cost(self):
        cost = 0
        
        for p in range(1, self.problem.total_professores + 1):
            for d in range(1, self.problem.dias_por_semana + 1):
                tem_manha = False
                tem_noite = False
                
                for t in range(1, self.problem.total_turmas + 1):
                    # Verificar manhã (aulas 1-6)
                    for h in range(1, 7):
                        if self.schedule[p][t][d][h] == 1:
                            tem_manha = True
                            break
                    
                    # Verificar noite (aulas 13-16)
                    for h in range(13, 17):
                        if self.schedule[p][t][d][h] == 1:
                            tem_noite = True
                            break
                
                if tem_manha and tem_noite:
                    cost += self.problem.CP4
                    
                    
        return cost
    
    def calculate_PD1_cost(self):
        cost = 0
        
        for p in range(1, self.problem.total_professores + 1):
            for t in range(1, self.problem.total_turmas + 1):
                for d in range(2, self.problem.dias_por_semana + 1):
                    # Verificar se teve aula no último horário da noite (16) no dia anterior
                    # e no primeiro horário da manhã (1) no dia atual
                    if self.schedule[p][t][d-1][16] == 1 and self.schedule[p][t][d][1] == 1:
                        cost += self.problem.PD1
                        
                        
        return cost
    
    def calculate_PD2_cost(self):
        cost = 0
        professores_afetados = {15, 18, 23}
        
        for p in professores_afetados:
            for t in range(1, self.problem.total_turmas + 1):
                for d in range(1, self.problem.dias_por_semana + 1):
                    # Verificar se está na última aula da manhã (6) ou primeira da tarde (7)
                    if self.schedule[p][t][d][6] == 1 or self.schedule[p][t][d][7] == 1:
                        cost += self.problem.PD2
                        
                        
        return cost
    
    def calculate_PD3_cost(self):
        cost = 0
        
        # Professor 1 não pode dar aula nos dois primeiros horários
        p = 1
        for t in range(1, self.problem.total_turmas + 1):
            for d in range(1, self.problem.dias_por_semana + 1):
                if self.schedule[p][t][d][1] == 1 or self.schedule[p][t][d][2] == 1:
                    cost += self.problem.PD3
                    
                    
        return cost
    
    def calculate_PD4_cost(self):
        cost = 0
        professores_sexta = {10, 14, 23, 18, 54}
        professores_segunda = {8, 17, 32, 3, 44}
        
        # Professores que não querem dar aula na sexta
        for p in professores_sexta:
            for t in range(1, self.problem.total_turmas + 1):
                d = 5  # Sexta-feira (assumindo que dia 5 é sexta)
                if sum(self.schedule[p][t][d][h] for h in range(1, self.problem.aulas_por_dia + 1)) > 0:
                    cost += self.problem.PD4
                    
                    
        # Professores que não querem dar aula na segunda
        for p in professores_segunda:
            for t in range(1, self.problem.total_turmas + 1):
                d = 1  # Segunda-feira (assumindo que dia 1 é segunda)
                if sum(self.schedule[p][t][d][h] for h in range(1, self.problem.aulas_por_dia + 1)) > 0:
                    cost += self.problem.PD4
                    
                    
        return cost
    
    def calculate_PD5_cost(self):
        cost = 0
        professores_sub_segunda = {33, 41, 42, 48}
        professores_sub_sexta = {4, 28, 63, 76}
        
        # Priorizar substitutos na segunda
        for p in professores_sub_segunda:
            for t in range(1, self.problem.total_turmas + 1):
                d = 1  # Segunda-feira
                if sum(self.schedule[p][t][d][h] for h in range(1, self.problem.aulas_por_dia + 1)) > 0:
                    cost += self.problem.PD5
                   
                    
        # Priorizar substitutos na sexta
        for p in professores_sub_sexta:
            for t in range(1, self.problem.total_turmas + 1):
                d = 5  # Sexta-feira
                if sum(self.schedule[p][t][d][h] for h in range(1, self.problem.aulas_por_dia + 1)) > 0:
                    cost += self.problem.PD5
                    
                    
        return cost
    
    def generate_neighbor(self):
        # Cria uma cópia da solução atual
        neighbor = copy.deepcopy(self)
        
        # Escolhe uma operação aleatória para gerar o vizinho
        operation = random.choice(["swap", "move", "change"])
        
        if operation == "swap":
            # Troca duas aulas de professores/turmas diferentes no mesmo horário
            d = random.randint(1, self.problem.dias_por_semana)
            h = random.randint(1, self.problem.aulas_por_dia)
            
            # Encontrar duas aulas para trocar
            aulas = []
            for p in range(1, self.problem.total_professores + 1):
                for t in range(1, self.problem.total_turmas + 1):
                    if self.schedule[p][t][d][h] == 1:
                        aulas.append((p, t))
            
            if len(aulas) >= 2:
                # Escolher duas aulas aleatórias para trocar
                a1, a2 = random.sample(aulas, 2)
                p1, t1 = a1
                p2, t2 = a2
                
                # Verificar se a troca é válida (professores e turmas não estão ocupados nos novos horários)
                p1_ocupado = any(neighbor.schedule[p1][t][d][h] == 1 for t in range(1, self.problem.total_turmas + 1) if t != t1)
                p2_ocupado = any(neighbor.schedule[p2][t][d][h] == 1 for t in range(1, self.problem.total_turmas + 1) if t != t2)
                t1_ocupado = any(neighbor.schedule[p][t1][d][h] == 1 for p in range(1, self.problem.total_professores + 1) if p != p1)
                t2_ocupado = any(neighbor.schedule[p][t2][d][h] == 1 for p in range(1, self.problem.total_professores + 1) if p != p2)
                
                if not p1_ocupado and not p2_ocupado and not t1_ocupado and not t2_ocupado:
                    # Realizar a troca
                    neighbor.schedule[p1][t1][d][h] = 0
                    neighbor.schedule[p2][t2][d][h] = 0
                    neighbor.schedule[p1][t2][d][h] = 1
                    neighbor.schedule[p2][t1][d][h] = 1
        
        elif operation == "move":
            # Move uma aula para outro horário vazio
            p = random.randint(1, self.problem.total_professores)
            t = random.randint(1, self.problem.total_turmas)
            
            # Encontrar uma aula para mover
            aulas = []
            for d in range(1, self.problem.dias_por_semana + 1):
                for h in range(1, self.problem.aulas_por_dia + 1):
                    if self.schedule[p][t][d][h] == 1:
                        aulas.append((d, h))
            
            if aulas:
                d_orig, h_orig = random.choice(aulas)
                
                # Encontrar um horário vazio para mover
                horarios_permitidos = self.problem.periodos_turmas.get(t, list(range(1, self.problem.aulas_por_dia + 1)))
                horarios_vazios = []
                
                for d in range(1, self.problem.dias_por_semana + 1):
                    for h in horarios_permitidos:
                        # Verificar se o professor está livre
                        professor_livre = True
                        for t2 in range(1, self.problem.total_turmas + 1):
                            if self.schedule[p][t2][d][h] == 1:
                                professor_livre = False
                                break
                        
                        # Verificar se a turma está livre
                        turma_livre = True
                        for p2 in range(1, self.problem.total_professores + 1):
                            if self.schedule[p2][t][d][h] == 1:
                                turma_livre = False
                                break
                        
                        if professor_livre and turma_livre and (d, h) != (d_orig, h_orig):
                            horarios_vazios.append((d, h))
                
                if horarios_vazios:
                    d_new, h_new = random.choice(horarios_vazios)
                    
                    # Mover a aula
                    neighbor.schedule[p][t][d_orig][h_orig] = 0
                    neighbor.schedule[p][t][d_new][h_new] = 1
        
        elif operation == "change":
            # Altera o horário de uma aula geminada
            p = random.randint(1, self.problem.total_professores)
            t = random.randint(1, self.problem.total_turmas)
            
            # Verificar se tem aula geminada
            tem_g2 = self.problem.G2[p-1][t-1] == 1 or self.problem.G22[p-1][t-1] == 1
            tem_g3 = self.problem.G3[p-1][t-1] == 1
            
            if tem_g2 or tem_g3:
                tamanho = 2 if tem_g2 else 3
                
                # Encontrar a aula geminada atual
                geminada_encontrada = False
                for d in range(1, self.problem.dias_por_semana + 1):
                    for h in range(1, self.problem.aulas_por_dia - tamanho + 2):
                        todos_um = True
                        for i in range(tamanho):
                            if self.schedule[p][t][d][h+i] != 1:
                                todos_um = False
                                break
                        
                        if todos_um:
                            # Encontrou a aula geminada
                            geminada_encontrada = True
                            break
                    
                    if geminada_encontrada:
                        break
                
                if geminada_encontrada:
                    # Remover a aula geminada atual
                    for i in range(tamanho):
                        neighbor.schedule[p][t][d][h+i] = 0
                    
                    # Tentar realocar em outro lugar
                    horarios_permitidos = self.problem.periodos_turmas.get(t, list(range(1, self.problem.aulas_por_dia + 1)))
                    dias_possiveis = list(range(1, self.problem.dias_por_semana + 1))
                    random.shuffle(dias_possiveis)
                    
                    realocado = False
                    for d_new in dias_possiveis:
                        for h_new in horarios_permitidos:
                            if h_new + tamanho - 1 > max(horarios_permitidos):
                                continue
                                
                            # Verificar se está livre
                            livre = True
                            for i in range(tamanho):
                                # Verificar professor
                                for t2 in range(1, self.problem.total_turmas + 1):
                                    if neighbor.schedule[p][t2][d_new][h_new+i] == 1:
                                        livre = False
                                        break
                                
                                # Verificar turma
                                if livre:
                                    for p2 in range(1, self.problem.total_professores + 1):
                                        if neighbor.schedule[p2][t][d_new][h_new+i] == 1:
                                            livre = False
                                            break
                            
                            if livre:
                                # Alocar a nova aula geminada
                                for i in range(tamanho):
                                    neighbor.schedule[p][t][d_new][h_new+i] = 1
                                realocado = True
                                break
                        
                        if realocado:
                            break
                    
                    if not realocado:
                        # Se não conseguiu realocar, volta ao original
                        for i in range(tamanho):
                            neighbor.schedule[p][t][d][h+i] = 1
        
        # Recalcular o custo da nova solução
        neighbor.cost = neighbor.calculate_total_cost()
        
        return neighbor
    
    def mostrar_contadores(self):
        print("\nCONTAGEM DE RESTRIÇÕES VIOLADAS NA SOLUÇÃO FINAL:")
        print("\nPedagógicas:")
        for cp, count in self.contadores_cp.items():
            print(f"{cp}: {count} violações")
            
        print("\nDocentes:")
        for pd, count in self.contadores_pd.items():
            print(f"{pd}: {count} violações")


def simulated_annealing(problem, initial_temp, cooling_rate, min_temp, max_iter):
    current_solution = ScheduleSolution(problem)
    best_solution = copy.deepcopy(current_solution)
    
    temp = initial_temp
    
    iteration = 0
    while temp > min_temp and iteration < max_iter:
        # Gerar um vizinho
        neighbor = current_solution.generate_neighbor()
        
        # Calcular a diferença de custo
        delta_cost = neighbor.cost - current_solution.cost
        
        # Decidir se aceita o vizinho
        if delta_cost < 0 or random.random() < math.exp(-delta_cost / temp):
            current_solution = neighbor
            
            # Atualizar a melhor solução se necessário
            if current_solution.cost < best_solution.cost:
                best_solution = copy.deepcopy(current_solution)
        
        # Resfriar
        temp *= cooling_rate
        iteration += 1
        
        # Print progresso a cada 100 iterações
        if iteration % 100 == 0:
            print(f"Iteração {iteration}, Temperatura: {temp:.2f}, Custo Atual: {current_solution.cost}, Melhor Custo: {best_solution.cost}")
    
    return best_solution



# [ADDED] Função para executar o SA com um conjunto específico de parâmetros
def run_sa_with_params(problem, initial_temp, cooling_rate, min_temp, max_iter):
    start_time = time.perf_counter()
    best_solution = simulated_annealing(problem, initial_temp, cooling_rate, min_temp, max_iter)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    return best_solution.cost, elapsed_time

# [ADDED] Função para calibração dos parâmetros via grid search
def calibrate_parameters(problem, param_grid, n_reps=3):
    results = []
    for initial_temp in param_grid['initial_temp']:
        for cooling_rate in param_grid['cooling_rate']:
            for max_iter in param_grid['max_iter']:
                # Pode-se manter min_temp fixo ou incluir no grid se desejado
                min_temp = param_grid.get('min_temp', [0.1])[0]
                
                costs = []
                times = []
                for _ in range(n_reps):
                    cost, elapsed_time = run_sa_with_params(problem, initial_temp, cooling_rate, min_temp, max_iter)
                    costs.append(cost)
                    times.append(elapsed_time)
                
                avg_cost = np.mean(costs)
                avg_time = np.mean(times)
                
                results.append({
                    'initial_temp': initial_temp,
                    'cooling_rate': cooling_rate,
                    'max_iter': max_iter,
                    'min_temp': min_temp,
                    'avg_cost': avg_cost,
                    'avg_time': avg_time
                })
                print(f"Parâmetros: T0={initial_temp}, cooling_rate={cooling_rate}, max_iter={max_iter} => Custo médio: {avg_cost}, Tempo médio: {avg_time:.2f}s")
    return results



# Exemplo de uso
if __name__ == "__main__":
    # Parâmetros do problema
    dias_por_semana = 5
    aulas_por_dia = 16
    total_turmas = 43
    total_professores = 82

    matrizes = './Planilhas/Matrizes.xlsx'
    
    # ProfTurma: quantas aulas um professor deve dar em uma turma (valores típicos 0, 2 ou 3)
    dfProfTurma = pd.read_excel(matrizes, sheet_name="ProfTurma", usecols="B:AR", skiprows=2, nrows=82, header=None)
    ProfTurma = dfProfTurma.values

    # Matrizes binárias para aulas geminadas (G2, G22, G3)
    dfG2 = pd.read_excel(matrizes, sheet_name="G2", usecols="B:AR", skiprows=2, nrows=82, header=None)
    G2 = dfG2.values

    dfG22 = pd.read_excel(matrizes, sheet_name="G22", usecols="B:AR", skiprows=2, nrows=82, header=None)
    G22 = dfG22.values

    dfG3 = pd.read_excel(matrizes, sheet_name="G3", usecols="B:AR", skiprows=2, nrows=82, header=None)
    G3 = dfG3.values

    # # Matrizes binárias para aulas geminadas (G2, G22, G3)
    # dfG2 = pd.read_excel(matrizes, sheet_name="G2", usecols="B:C", skiprows=2, nrows=82, header=None)
    # G2 = dfG2.values

    # dfG22 = pd.read_excel(matrizes, sheet_name="G22", usecols="B:C", skiprows=2, nrows=82, header=None)
    # G22 = dfG22.values

    # dfG3 = pd.read_excel(matrizes, sheet_name="G3", usecols="B:C", skiprows=2, nrows=82, header=None)
    # G3 = dfG3.values

    # Preencher algumas aulas (exemplo)
    # ProfTurma[0][0] = 4  # Professor 1 tem 4 aulas na turma 1
    # G2[0][0] = 1         # Professor 1 tem aula geminada de 2 tempos na turma 1
    
    # Custos
    CP_values = (8, 6, 1, 1)  # CP1, CP2, CP3, CP4
    PD_values = (1, 1, 1, 1, 1)  # PD1, PD2, PD3, PD4, PD5
    
    # Criar o problema
    problem = ScheduleProblem(dias_por_semana, aulas_por_dia, total_turmas, total_professores,
                             ProfTurma, G2, G22, G3, CP_values, PD_values)
    

    # # Definir a grade de parâmetros para calibração
    # param_grid = {
    #     'initial_temp': [1000, 5000, 10000, 20000, 40000],
    #     'cooling_rate': [0.85, 0.90, 0.95, 0.99],
    #     'max_iter': [1000, 5000, 10000, 20000],
    #     'min_temp': [0.1] 
    # }

    # #  Executar a calibração dos parâmetros
    # results = calibrate_parameters(problem, param_grid, n_reps=3)

    # #  Exibir as melhores configurações com base no custo médio
    # df_results = pd.DataFrame(results)
    
    # print("\nMelhores configurações:")
    # print(df_results.sort_values(by='avg_cost').head())

    # df_results.to_excel('Planilhas/resultados_calibracao4.xlsx', index=False)
    
    
    # Executar Simulated Annealing
    initial_temp = 40000
    cooling_rate = 0.99
    min_temp = 0.1
    max_iter = 10000

    start_time = time.perf_counter()
    
    best_solution = simulated_annealing(problem, initial_temp, cooling_rate, min_temp, max_iter)

    end_time = time.perf_counter()
    
    # Imprimir resultados
    print("\nMelhor solução encontrada:")
    print(f"Custo total: {best_solution.cost}")
    print("Tempo de execução:", end_time - start_time, "segundos")

    # Obter contagem de violações
    violacoes = best_solution.contar_violacoes()

    # Exibir resultados detalhados
    print("\nVIOLAÇÕES NA MELHOR SOLUÇÃO:")
    print("----------------------------")
    print("Pedagógicas:")
    print(f"CP1 (excesso de aulas/dia): {violacoes['CP1']}")
    print(f"CP2 (aulas em dias consecutivos): {violacoes['CP2']}")
    print(f"CP3 (exatas em horários ruins): {violacoes['CP3']}")
    print(f"CP4 (turnos distintos no mesmo dia): {violacoes['CP4']}")

    print("\nDocentes:")
    print(f"PD1 (noite→manhã): {violacoes['PD1']}")
    print(f"PD2 (professores específicos em horários ruins): {violacoes['PD2']}")
    print(f"PD3 (professor 1 nos primeiros horários): {violacoes['PD3']}")
    print(f"PD4 (aulas em dias indesejados): {violacoes['PD4']}")
    print(f"PD5 (substitutos em dias de planejamento): {violacoes['PD5']}")
    
    # Imprimir detalhes da alocação (opcional)
    # for t in range(1, total_turmas + 1):
    #     print(f"\nTurma {t}:")
    #     for d in range(1, dias_por_semana + 1):
    #         print(f"  Dia {d}: ", end="")
    #         for h in range(1, aulas_por_dia + 1):
    #             for p in range(1, total_professores + 1):
    #                 if best_solution.schedule[p][t][d][h] == 1:
    #                     print(f"{h}:P{p} ", end="")
    #         print()

    

    