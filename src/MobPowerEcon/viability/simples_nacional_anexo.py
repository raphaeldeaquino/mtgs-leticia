
def calcular_simples_nacional(receita_bruta_anual, anexo1):
    aliquota_efetiva = []
    desconto_mensal = []
    desconto_anual = []

    for j in range(len(receita_bruta_anual)):
        # Inicialize as variáveis dentro do loop for j
        aliquota_efetiva_j = None
        desconto_mensal_j = None
        desconto_anual_j = None

        # Determinar em qual faixa do Anexo I a receita bruta se enquadra
        for i in range(2, 8):
            if anexo1.iloc[i, 1] <= receita_bruta_anual[j] <= anexo1.iloc[i, 2]:
                #print(f"A receita bruta anual está dentro da {i-1}ª Faixa do Anexo I.")
                aliquota_efetiva_j = ((receita_bruta_anual[j] * anexo1.iloc[i, 3]) - anexo1.iloc[i, 4]) / receita_bruta_anual[j]
                #print("Alíquota efetiva: ", "{:.4f}".format(aliquota_efetiva_j))
                desconto_mensal_j = receita_bruta_anual[j]/12 * aliquota_efetiva_j
                desconto_anual_j = desconto_mensal_j * 12
                break
        else:
            print("A receita bruta está fora das faixas do Anexo I.")
            return None, None, None

        # Adicione os valores calculados para o índice j
        aliquota_efetiva.append(aliquota_efetiva_j)
        desconto_mensal.append(desconto_mensal_j)
        desconto_anual.append(desconto_anual_j)

    return aliquota_efetiva, desconto_mensal, desconto_anual