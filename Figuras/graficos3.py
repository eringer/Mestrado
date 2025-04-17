import matplotlib.pyplot as plt
import pandas as pd

# Dados atualizados
dados = {
    'Método': ['Solução Manual', 'SA-GH', 'PLI-GH'],
    'Custo Total': [1340, 365.33, 111]
}

df = pd.DataFrame(dados)

# Criando o gráfico
plt.figure(figsize=(9, 6))
bars = plt.bar(df['Método'], df['Custo Total'])
plt.title('Comparação do Custo Total por Método de Geração de Horários')
plt.ylabel('Custo Total')
plt.xlabel('Método')
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Adicionando os valores no topo das barras
for bar in bars:
    yval = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, yval + 30, f'{yval}', ha='center', va='bottom', fontsize=10)

plt.tight_layout()


plt.savefig("Figuras/grafico_comparacao_manual.png", dpi=300)
