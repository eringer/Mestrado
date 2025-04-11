import pandas as pd

# Lê a planilha original
df = pd.read_excel('./Planilhas/Professores-Aulas-Turmas-2024-1.xlsx', sheet_name='Solução Manual', usecols="A:D", nrows=956, header=None, names=['Professor', 'Turma', 'Dia', 'Horário'])

# Mapeia os números dos dias para nomes da semana
dias_semana = {1: 'Seg', 2: 'Ter', 3: 'Qua', 4: 'Qui', 5: 'Sex'}
df['Dia'] = df['Dia'].map(dias_semana)

# Cria um writer para gerar a nova planilha
with pd.ExcelWriter('./Planilhas/grade_por_turma.xlsx', engine='openpyxl') as writer:
    for turma in sorted(df['Turma'].unique()):
        # Cria uma grade vazia com h1 a h16 e colunas Seg a Sex
        grade = pd.DataFrame(index=[f'h{i}' for i in range(1, 17)],
                             columns=['Seg', 'Ter', 'Qua', 'Qui', 'Sex'])

        # Filtra os dados da turma atual
        df_turma = df[df['Turma'] == turma]

        # Preenche a grade com os professores
        for _, row in df_turma.iterrows():
            horario = f'h{int(row["Horário"])}'
            dia = row['Dia']
            professor = f'P{int(row["Professor"])}'
            grade.at[horario, dia] = professor

        # Escreve a aba no Excel com o nome da turma
        grade.to_excel(writer, sheet_name=f'Turma_{int(turma)}')