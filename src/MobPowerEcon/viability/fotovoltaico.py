
def calcular_geracao_fotovoltaica(vida_util, pot_fv, h_inc, pr, perda_eficiencia_anual):
    geracoes = []
    eficiencia = []  # Lista para armazenar a eficiência

    # Calcular eficiência para cada ano
    for ano in range(1, vida_util + 1):
        eficiencia_atual = (1 - perda_eficiencia_anual) ** (ano - 1)
        eficiencia.append(eficiencia_atual * 100)  # Eficiência em percentual

    # Calcular geração fotovoltaica para cada ano
    for efic in eficiencia:
        geracao = pot_fv * h_inc * pr *365* efic / 100
        geracoes.append(geracao)

    return geracoes, eficiencia


'''# Plotar o gráfico da eficiência do sistema ao longo dos anos
plt.figure(figsize=(10, 5))
plt.plot(anos, eficiencia, marker='o', linestyle='-')
plt.title('Eficiência do Sistema ao Longo dos Anos')
plt.xlabel('Ano')
plt.ylabel('Eficiência (%)')
plt.grid(True)
plt.show()'''