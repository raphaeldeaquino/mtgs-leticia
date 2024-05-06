
def calcular_financiamento(valor_total_financiado, numero_prestacoes, taxa_juros_anual, tipo_financiamento):
    def calcular_prestacoes_price(valor_total, numero_prestacoes, taxa_juros_mensal):
        prestacao = valor_total * (taxa_juros_mensal * (1 + taxa_juros_mensal) ** numero_prestacoes) / ((1 + taxa_juros_mensal) ** numero_prestacoes - 1)
        prestacoes = [prestacao] * numero_prestacoes
        return prestacoes

    def calcular_prestacoes_sac(valor_total, numero_prestacoes, taxa_juros_mensal):
        prestacoes = []
        amortizacao = valor_total / numero_prestacoes

        for i in range(numero_prestacoes):
            juros = (valor_total - i * amortizacao) * taxa_juros_mensal
            prestacao = amortizacao + juros
            prestacoes.append(prestacao)

        return prestacoes

    # Converter a taxa de juros anual para mensal
    taxa_juros_mensal = (1 + taxa_juros_anual) ** (1/12) - 1

    if tipo_financiamento == 'price':
        return calcular_prestacoes_price(valor_total_financiado, numero_prestacoes, taxa_juros_mensal)
    elif tipo_financiamento == 'sac':
        return calcular_prestacoes_sac(valor_total_financiado, numero_prestacoes, taxa_juros_mensal)
    else:
        print("Tipo de financiamento inválido. Por favor, escolha 'price' ou 'sac'.")