import pandas as pd

professores = 82
turmas = 43
horarios = 16
dia = 5

contCP1 = 0

g2 = pd.read_excel('Matrizes.xlsx', sheet_name='G2')
g22 = pd.read_excel('Matrizes.xlsx', sheet_name='G22')
g3 = pd.read_excel('Matrizes.xlsx', sheet_name='G3')

g2.drop(0, inplace=True)
g2.drop("Unnamed: 0", axis=1, inplace=True)
g2.dropna(inplace=True)

g22.drop(0, inplace=True)
g22.drop("Unnamed: 0", axis=1, inplace=True)
g22.dropna(inplace=True)

g3.drop(0, inplace=True)
g3.drop("Unnamed: 0", axis=1, inplace=True)
g3.dropna(inplace=True)

for d in range(dia):
    for t in range(turmas):
        for p in range(professores):
            if g2.iat[p, t] == 1 or g22.iat[p,t] == 1:
                contCP1 = contCP1 + 1

for d in range(dia):
    for t in range(turmas):
        for p in range(professores):
            if g3.iat[p, t] == 1:
                contCP1 = contCP1 + 1


print(f"Quantidade CP1: {contCP1}")