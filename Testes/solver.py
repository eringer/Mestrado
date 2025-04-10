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

print(ProfTurma[(0,42)])

