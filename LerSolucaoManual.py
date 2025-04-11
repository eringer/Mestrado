import pandas as pd

def calcular_custo_alocacao_manual(matriz_alocacoes, problem_params):
    """
    Calcula o custo total da alocação manual conforme as regras do IFES
    
    Args:
        matriz_alocacoes: Lista de listas no formato [p, t, d, h]
        problem_params: Dicionário com os parâmetros do problema:
            - total_professores: int
            - total_turmas: int
            - dias_por_semana: int
            - aulas_por_dia: int
            - G2: Matriz [professores x turmas] indicando aulas geminadas de 2 tempos
            - G22: Matriz [professores x turmas] indicando 2 aulas geminadas de 2 tempos
            - G3: Matriz [professores x turmas] indicando aulas geminadas de 3 tempos
            - CP_values: Tuple com (CP1, CP2, CP3, CP4)
            - PD_values: Tuple com (PD1, PD2, PD3, PD4, PD5)
            - professores_exatas: Set com IDs dos professores de exatas
            - professores_pd2: Set com IDs dos professores com restrição PD2
            - professores_nao_segunda: Set com IDs dos professores que não querem 2ª
            - professores_nao_sexta: Set com IDs dos professores que não querem 6ª
            - professores_sub_segunda: Set com IDs dos substitutos preferenciais para 2ª
            - professores_sub_sexta: Set com IDs dos substitutos preferenciais para 6ª
    
    Returns:
        Dicionário com:
            - custo_total: float
            - custos_parciais: dict com custos CP1-CP4 e PD1-PD5
            - contadores: dict com contagem de violações por tipo
    """
    
    # Inicializa estruturas para contagem
    contadores = {
        'CP1': 0, 'CP2': 0, 'CP3': 0, 'CP4': 0,
        'PD1': 0, 'PD2': 0, 'PD3': 0, 'PD4': 0, 'PD5': 0
    }
    
    custos_parciais = {
        'CP1': 0, 'CP2': 0, 'CP3': 0, 'CP4': 0,
        'PD1': 0, 'PD2': 0, 'PD3': 0, 'PD4': 0, 'PD5': 0
    }
    
    CP1, CP2, CP3, CP4 = problem_params['CP_values']
    PD1, PD2, PD3, PD4, PD5 = problem_params['PD_values']
    
    # Pré-processa as alocações por professor/turma/dia
    from collections import defaultdict
    alocacoes = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    
    for p, t, d, h in matriz_alocacoes:
        alocacoes[p][t][d].append(h)
    
    # ========== CÁLCULO DAS RESTRIÇÕES PEDAGÓGICAS ==========
    
    # CP1: Excesso de aulas por dia
    for p in alocacoes:
        for t in alocacoes[p]:
            for d in alocacoes[p][t]:
                aulas_no_dia = len(alocacoes[p][t][d])
                tem_g2 = problem_params['G2'][p-1][t-1] == 1 or problem_params['G22'][p-1][t-1] == 1
                tem_g3 = problem_params['G3'][p-1][t-1] == 1
                
                if (tem_g2 and aulas_no_dia >= 3) or (tem_g3 and aulas_no_dia >= 4) or (not tem_g2 and not tem_g3 and aulas_no_dia >= 2):
                    contadores['CP1'] += 1
                    custos_parciais['CP1'] += CP1
    
    # CP2: Aulas em dias consecutivos
    for p in alocacoes:
        for t in alocacoes[p]:
            for d in range(2, problem_params['dias_por_semana'] + 1):
                if d in alocacoes[p][t] and (d-1) in alocacoes[p][t]:
                    if len(alocacoes[p][t][d]) >= 1 and len(alocacoes[p][t][d-1]) >= 1:
                        contadores['CP2'] += 1
                        custos_parciais['CP2'] += CP2
    
    # CP3: Professores de exatas em últimos horários
    for p in problem_params['professores_exatas']:
        if p in alocacoes:
            for t in alocacoes[p]:
                for d in alocacoes[p][t]:
                    # Verifica últimos horários da manhã (5,6)
                    if any(h in {5,6} for h in alocacoes[p][t][d]):
                        contadores['CP3'] += 1
                        custos_parciais['CP3'] += CP3
                    # Verifica últimos horários da tarde (11,12)
                    if any(h in {11,12} for h in alocacoes[p][t][d]):
                        contadores['CP3'] += 1
                        custos_parciais['CP3'] += CP3
    
    # CP4: Aulas em turnos distintos no mesmo dia
    for p in alocacoes:
        for d in range(1, problem_params['dias_por_semana'] + 1):
            tem_manha = False
            tem_noite = False
            
            for t in alocacoes[p]:
                if d in alocacoes[p][t]:
                    # Verifica manhã (horários 1-6)
                    if any(1 <= h <= 6 for h in alocacoes[p][t][d]):
                        tem_manha = True
                    # Verifica noite (horários 13-16)
                    if any(13 <= h <= 16 for h in alocacoes[p][t][d]):
                        tem_noite = True
            
            if tem_manha and tem_noite:
                contadores['CP4'] += 1
                custos_parciais['CP4'] += CP4
    
    # ========== CÁLCULO DAS RESTRIÇÕES DOCENTES ==========
    
    # PD1: Aula no último horário da noite e primeiro da manhã seguinte
    for p in alocacoes:
        for t in alocacoes[p]:
            for d in range(2, problem_params['dias_por_semana'] + 1):
                if d in alocacoes[p][t] and (d-1) in alocacoes[p][t]:
                    if 16 in alocacoes[p][t][d-1] and 1 in alocacoes[p][t][d]:
                        contadores['PD1'] += 1
                        custos_parciais['PD1'] += PD1
    
    # PD2: Professores específicos em últimos horários da manhã ou primeiros da tarde
    for p in problem_params['professores_pd2']:
        if p in alocacoes:
            for t in alocacoes[p]:
                for d in alocacoes[p][t]:
                    if 6 in alocacoes[p][t][d] or 7 in alocacoes[p][t][d]:
                        contadores['PD2'] += 1
                        custos_parciais['PD2'] += PD2
    
    # PD3: Professor 1 nos dois primeiros horários
    p = 1
    if p in alocacoes:
        for t in alocacoes[p]:
            for d in alocacoes[p][t]:
                if 1 in alocacoes[p][t][d] or 2 in alocacoes[p][t][d]:
                    contadores['PD3'] += 1
                    custos_parciais['PD3'] += PD3
    
    # PD4: Professores que não querem dar aula em determinados dias
    # Sexta-feira (dia 5)
    for p in problem_params['professores_nao_sexta']:
        if p in alocacoes:
            for t in alocacoes[p]:
                if 5 in alocacoes[p][t]:
                    contadores['PD4'] += 1
                    custos_parciais['PD4'] += PD4
    
    # Segunda-feira (dia 1)
    for p in problem_params['professores_nao_segunda']:
        if p in alocacoes:
            for t in alocacoes[p]:
                if 1 in alocacoes[p][t]:
                    contadores['PD4'] += 1
                    custos_parciais['PD4'] += PD4
    
    # PD5: Prioridade para professores substitutos
    # Segunda-feira (dia 1)
    for p in problem_params['professores_sub_segunda']:
        if p in alocacoes:
            for t in alocacoes[p]:
                if 1 in alocacoes[p][t]:
                    contadores['PD5'] += 1
                    custos_parciais['PD5'] += PD5
    
    # Sexta-feira (dia 5)
    for p in problem_params['professores_sub_sexta']:
        if p in alocacoes:
            for t in alocacoes[p]:
                if 5 in alocacoes[p][t]:
                    contadores['PD5'] += 1
                    custos_parciais['PD5'] += PD5
    
    # Cálculo do custo total
    custo_total = sum(custos_parciais.values())
    
    return {
        'custo_total': custo_total,
        'custos_parciais': custos_parciais,
        'contadores': contadores
    }

# ========== EXEMPLO DE USO ==========
if __name__ == "__main__":

    matrizes = './Planilhas/Matrizes.xlsx'

    # Exemplo de parâmetros (substitua pelos seus dados reais)
    params = {
        'total_professores': 82,
        'total_turmas': 43,
        'dias_por_semana': 5,
        'aulas_por_dia': 16,
        'G2': pd.read_excel(matrizes, sheet_name="G2", usecols="B:AR", skiprows=2, nrows=82, header=None).values, 
        'G22': pd.read_excel(matrizes, sheet_name="G22", usecols="B:AR", skiprows=2, nrows=82, header=None).values,
        'G3': pd.read_excel(matrizes, sheet_name="G3", usecols="B:AR", skiprows=2, nrows=82, header=None).values,
        'CP_values': (8, 6, 1, 1),  # CP1, CP2, CP3, CP4
        'PD_values': (1, 1, 1, 1, 1),  # PD1, PD2, PD3, PD4, PD5
        'professores_exatas': {5, 11, 14, 18, 26, 31, 33},
        'professores_pd2': {15, 18, 23},
        'professores_nao_segunda': {8, 17, 32, 3, 44},
        'professores_nao_sexta': {10, 14, 23, 18, 54},
        'professores_sub_segunda': {33, 41, 42, 48},
        'professores_sub_sexta': {4, 28, 63, 76}
    }
    
    # Exemplo de matriz de alocação (substitua pela sua matriz real)
    # matriz_exemplo = [
    #     [1, 1, 1, 1],
    #     [1, 1, 1, 2],
    #     # ... suas 956 linhas ...
    # ]

    

    sheet = pd.read_excel('./Planilhas/Professores-Aulas-Turmas-2024-1.xlsx', sheet_name='Solução Manual', usecols="A:D", nrows=956, header=None)

    matriz_exemplo = sheet.values
    
    resultado = calcular_custo_alocacao_manual(matriz_exemplo, params)
    
    print(f"Custo Total da Alocação Manual: {resultado['custo_total']}")
    print("\nCustos Parciais:")
    for tipo, valor in resultado['custos_parciais'].items():
        print(f"{tipo}: {valor}")
    
    print("\nContagem de Violações:")
    for tipo, quantidade in resultado['contadores'].items():
        print(f"{tipo}: {quantidade}")







                
        

