# Código para gerar o gráfico de sensibilidade (opcional)
import matplotlib.pyplot as plt
import numpy as np

experimentos = ['Exp.1', 'Exp.2', 'Exp.3', 'Exp.4', 'Exp.5']
custos = [38, 50, 18, 88, 111]
tempos = [175.36, 352.64, 147.78, 774.06, 345.39]

fig, ax1 = plt.subplots(figsize=(10,6))
ax1.bar(experimentos, custos, color='skyblue')
ax1.set_ylabel('Custo Total', color='skyblue')
ax2 = ax1.twinx()
ax2.plot(experimentos, tempos, 'r-o')
ax2.set_ylabel('Tempo (s)', color='red')
plt.title('Relação entre Custo e Tempo por Configuração')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.savefig('sensibilidade_pesos.png', dpi=300, bbox_inches='tight')