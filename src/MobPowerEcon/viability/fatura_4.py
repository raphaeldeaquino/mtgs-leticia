
def calcular_fatura_4(geracao, consumo, tarifas, tusds, fator_simult, custo_disponibilidade):
    abatimento = [0] * len(geracao)
    credito_mensal = [0] * len(geracao)
    credito_e_geracao = [0] * len(geracao)
    abatimento_maximo = [0] * len(geracao)
    consumo_nao_simultaneo = [0] * len(geracao)
    consumo_simultaneo = [0] * len(geracao)
    energia_injetada = [0] * len(geracao)
    faturas = []

    for i in range(len(geracao)):
        if geracao[i] >= consumo[i]:
            consumo_simultaneo[i] = consumo[i] * fator_simult
        else:
            consumo_simultaneo[i] = geracao[i] * fator_simult

        consumo_nao_simultaneo[i] = consumo[i] - consumo_simultaneo[i]
        energia_injetada[i] = geracao[i] - consumo_simultaneo[i]
        credito_mensal[i] = energia_injetada[i]

        if i >= 6:
            credito_mensal[i-6] = 0
        credito_e_geracao[i] = energia_injetada[i] + sum(credito_mensal[:i+1])

        if consumo_nao_simultaneo[i] <= custo_disponibilidade:
            abatimento_maximo[i] = 0
        else:
            abatimento_maximo[i] = consumo_nao_simultaneo[i] - custo_disponibilidade

        if sum(credito_mensal) >= abatimento_maximo[i]:
            soma = 0
            u = 0
            while soma < abatimento_maximo[i]:
                u += 1
                soma += credito_mensal[u-1]
            credito_mensal[u-1] = sum(credito_mensal[:u]) - abatimento_maximo[i]
            for j in range(u - 1):
                credito_mensal[j] = 0
            abatimento[i] = abatimento_maximo[i]
        elif credito_e_geracao[i] >= abatimento_maximo[i]:
            credito_mensal[:i] = [0] * i
            credito_mensal[i] = credito_e_geracao[i] - abatimento_maximo[i]
            abatimento[i] = abatimento_maximo[i]
        else:
            abatimento[i] = credito_e_geracao[i]
            credito_mensal[:i+1] = [0] * (i+1)

        fatura = (consumo_nao_simultaneo[i] - abatimento[i]) * tarifas[i] + abatimento[i] * tusds[i]
        faturas.append(fatura)

    return faturas, abatimento, credito_mensal

'''# Exemplo de uso da função
geracao = [400, 100, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
consumo = [200, 300, 100, 100, 100, 100, 100, 200, 200, 200, 200, 200, 200, 200, 200]
tarifas = [0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9]
tusds = [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3]
fator_simult = 0.3
custo_disponibilidade = 100

faturas, abatimento, credito_mensal = calcular_fatura(geracao, consumo, tarifas, tusds, fator_simult, custo_disponibilidade)
print("Fatura:", fatura)
print("Faturas:", faturas)
print("Abatimento:", abatimento)
print("Credito Mensal:", credito_mensal)'''