import pandas as pd
import matplotlib.pyplot as plt

# Carregar a planilha com os dados
df = pd.read_excel("Planilhas/resultados_calibracao2.xlsx", sheet_name="Sheet1")

# Identificar as configurações de interesse
mais_rapido_maior_custo = df.loc[df['avg_cost'].idxmax()]
mais_demorado_menor_custo = df.loc[df['avg_cost'].idxmin()]

# Plot
plt.figure(figsize=(10, 6))
plt.scatter(df['avg_time'], df['avg_cost'], label='Configurações Testadas', alpha=0.7)
plt.scatter(mais_rapido_maior_custo['avg_time'], mais_rapido_maior_custo['avg_cost'],
            color='red', label='Mais rápido com maior custo', s=100, marker='X')
plt.scatter(mais_demorado_menor_custo['avg_time'], mais_demorado_menor_custo['avg_cost'],
            color='green', label='Mais demorado com menor custo', s=100, marker='o')

plt.title('Custo Médio vs Tempo Médio das Calibrações do Simulated Annealing')
plt.xlabel('Tempo Médio (s)')
plt.ylabel('Custo Médio')
plt.legend()
plt.grid(True)
plt.tight_layout()

# Salvar o gráfico como imagem
plt.savefig("grafico_calibracao_sa3.png", dpi=300)

# Mensagem de confirmação
print("Gráfico salvo como 'grafico_calibracao_sa3.png'.")

