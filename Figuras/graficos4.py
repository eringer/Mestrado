import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Configuração do estilo
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 12

# Dados
data = pd.DataFrame({
    'Modalidade': ['Médio']*10 + ['Técnico']*10 + ['Superior']*10,
    'Custo': [142, 162, 129, 96, 129, 143, 110, 108, 166, 110] + 
             [256, 219, 231, 297, 181, 280, 250, 269, 225, 292] + 
             [428, 417, 416, 416, 482, 388, 408, 373, 429, 447],
    'Tempo': [25.27, 24.48, 27.65, 25.14, 24.86, 23.88, 24.9, 23.9, 24.7, 20.02] + 
             [38.83, 39.39, 39.68, 39.76, 38.73, 39.41, 38.24, 38.94, 38.88, 38.13] + 
             [77.67, 76.49, 77.87, 75.87, 75.03, 75.94, 76.23, 74.07, 75.93, 75.3]
})

# Gráfico 1: Variação do Custo
plt.figure(figsize=(8, 6))
ax1 = sns.boxplot(x='Modalidade', y='Custo', data=data, palette="Blues")
plt.title('Distribuição do Custo por Modalidade (SA)', pad=20, fontsize=14)
plt.xlabel('Modalidade de Ensino', labelpad=10)
plt.ylabel('Custo Total', labelpad=10)
plt.savefig('boxplot_custo.png', dpi=300, bbox_inches='tight')
plt.close()

# Gráfico 2: Tempo de Execução
plt.figure(figsize=(8, 6))
ax2 = sns.boxplot(x='Modalidade', y='Tempo', data=data, palette="Greens")
plt.title('Tempo de Execução por Modalidade (SA)', pad=20, fontsize=14)
plt.xlabel('Modalidade de Ensino', labelpad=10)
plt.ylabel('Tempo (segundos)', labelpad=10)
plt.savefig('boxplot_tempo.png', dpi=300, bbox_inches='tight')
plt.close()