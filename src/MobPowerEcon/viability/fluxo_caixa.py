
def calcular_fluxo_de_caixa(receita_bruta_anual, desconto_anual, fatura_energia, oper_manut, aluguel_ano, prestacoes, valor_total_financiado, invest_ini, valor_residual_pv):
    saldo = valor_total_financiado - invest_ini
    fluxo_de_caixa = [saldo]
    anos_completos = len(receita_bruta_anual)  # Número de anos completos
    finan_anual = []

    for i in range(anos_completos):
        finan_anual.append(sum(prestacoes[i*12:(i+1)*12]))  # Soma das prestações anuais
        saldo = receita_bruta_anual[i] - desconto_anual[i] - fatura_energia[i] - oper_manut[i] - aluguel_ano[i] - finan_anual[i]
        fluxo_de_caixa.append(saldo)

    # Adicionar o valor residual do sistema fotovoltaico ao valor do último ano do fluxo de caixa
    fluxo_de_caixa[-1] += valor_residual_pv

    return fluxo_de_caixa, finan_anual