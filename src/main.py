## Instituto Federal de Educação, Ciência e Tecnologia de Goiás
## Mestrado em Tecnologia, Gestão e Sustentabilidade
## Discente: Letícia Chaves Fonseca Ucker
## Título: Ferramenta computacional para análise de viabilidade econômica da implantação de eletropostos

import matplotlib.pyplot as plt
import pandas as pd
import numpy_financial as npf
from financiamento import calcular_financiamento
from simples_nacional_anexo import calcular_simples_nacional
from fluxo_caixa_3 import calcular_fluxo_de_caixa
from fotovoltaico_2 import calcular_geracao_fotovoltaica
from fatura import calcular_fatura

#############################################################
## Dados de entrada:
#############################################################
# Carregar dados do Simples Nacional do arquivo Excel
simples_nacional = pd.read_excel('simples_nacional.xlsx', sheet_name='Dados Simples Nacional')
anexo1 = simples_nacional.iloc[5:13, 0:5]

# Dados eletropostos
num_eletropostos = 4  # Número de eletropostos
pot_eletroposto = 22  # Potência do eletroposto kW
recarga_dia = 6  # Recarga h/dia

# Dados sistema fotovoltaico
pot_fv = 50  # Potência do sistema fotovoltaico (kW)
h_inc = 5.45  # Zomer (2014) - Horas de irradiação solar média por dia (irradiância kWh/m2.dia Cresesb dividido por 1kW/m2 que é a irradiância de referência)
pr = 0.80  # Performance ratio
perda_eficiencia_anual = 0.016  # Perda de eficiência anual do sistema (em decimal)

# Dados econômicos
preco_eletroposto = 120000  # Preço de cada eletroposto em R$
preco_fv = 5000  # Preço do sistema fotovoltaico em R$/kWp
implantacao = 30000  # Outros custos de implantação em R$
o_e_m = 10000  # Valor da operação e manutenção por eletroposto em R$/ano
valor_recarga = 2  # Valor da recarga R$/kWh
tarifa_energia = 0.9  # Valor da tarifa de energia com impostos em R$/kWh
tma = 0.1  # Taxa Mínima de Atratividade
aluguel_mes = 3000  # Aluguel em R$/mês
vida_util = 10  # Vida útil financeira do fluxo de caixa - vida útil dos eletropostos

# Dados de financiamento
perc_finan = 70  # Digite o percentual a ser financiado de 0 a 100%
numero_prestacoes = 60  # Digite o número total de prestações em meses
taxa_juros_anual = 0.1  # Digite a taxa de juros anual (em decimal)
tipo_financiamento = 'price'  # Digite o tipo de financiamento (price ou sac)
# tipo_financiamento = input("Digite o tipo de financiamento (price ou sac): ").lower()

#############################################################
## Cálculo do investimento inicial
#############################################################
invest_ini = num_eletropostos * preco_eletroposto + pot_fv * preco_fv + implantacao

#############################################################
## Cálculo da demanda de energia elétrica dos eletropostos
#############################################################
demanda = [num_eletropostos * pot_eletroposto * recarga_dia * 365] * int(vida_util)  # Demanda em kWh/ano
print("Demanda dos eletropostos", demanda)

#############################################################
## Cálculo da geração de energia do sistema fotovoltaico
#############################################################
geracoes, eficiencia = calcular_geracao_fotovoltaica(vida_util, pot_fv, h_inc, pr, perda_eficiencia_anual)
print("Geração fotovoltaica:", geracoes)

# Plotar o gráfico da geração fotovoltaica ao longo dos anos
anos = range(1, vida_util + 1)
plt.figure(figsize=(10, 5))
plt.plot(anos, geracoes, marker='o', linestyle='-')
plt.title('Geração Fotovoltaica ao Longo dos Anos')
plt.xlabel('Ano')
plt.ylabel('Geração (kWh)')
plt.grid(True)
plt.show()

#############################################################
# Cálculo do valor residual do sistema fotovoltaico
#############################################################
fator_residual_fv = 1 - vida_util / 25 - 0.2  # Considera-se uma perda imediata de 20% + uma perda proporcional aos anos.
valor_residual_fv = pot_fv * preco_fv * fator_residual_fv  # Valor residual do sistema FV a ser adicionado no último ano do fluxo de caixa
print('Valor residual FV:', valor_residual_fv)

#############################################################
# Cálculo da fatura de energia
#############################################################
tarifa_energia_anos = [tarifa_energia] * int(vida_util)

# Calcular a fatura da concessionária para todos os anos
fatura_energia = calcular_fatura(demanda, geracoes, tarifa_energia_anos)
print("Faturas concessionária em R$:", fatura_energia)

#############################################################
# Cálculo do custo de operação e manutenção
#############################################################
oper_manut = [o_e_m * num_eletropostos] * int(vida_util)  # Vetor com os valores de O&M anuais

#############################################################
## Cálculo de financiamento
#############################################################
valor_total_financiado = (perc_finan / 100) * invest_ini
prestacoes = calcular_financiamento(valor_total_financiado, numero_prestacoes, taxa_juros_anual, tipo_financiamento)
print('Vetor prestações de financiamento:', prestacoes)

meses = [i for i in range(numero_prestacoes)]
juros_mensais = [(prestacoes[i] - valor_total_financiado / numero_prestacoes) for i in range(numero_prestacoes)]
amortizacao_mensal = [valor_total_financiado / numero_prestacoes for _ in range(numero_prestacoes)]

plt.figure(figsize=(10, 6))
plt.plot(meses, juros_mensais, label='Juros Mensais', marker='o')
plt.plot(meses, amortizacao_mensal, label='Amortização Mensal', marker='o')
plt.plot(meses, prestacoes, label='Prestações Mensais', marker='o')
plt.xlabel('Meses')
plt.ylabel('Valor em R$')
plt.title(f'Financiamento {tipo_financiamento.upper()}')
plt.legend()
plt.grid(True)
plt.show()

#############################################################
## Cálculo do aluguel
#############################################################
aluguel_ano = [aluguel_mes * 12] * int(vida_util)

#############################################################
## Cálculo da Receita Bruta
#############################################################
valor_recarga_anos = [valor_recarga] * int(vida_util)
receita_bruta_anual = [z * w for z, w in zip(demanda, valor_recarga_anos)]

#############################################################
## Cálculo do Simples Nacional
#############################################################
aliquota_efetiva, desconto_mensal, desconto_anual = calcular_simples_nacional(receita_bruta_anual, anexo1)

if aliquota_efetiva is not None:
    print('Alíquota efetiva:', aliquota_efetiva)
    print("Desconto Simples Mensal: ", desconto_mensal)

#############################################################
## Cálculo do fluxo de caixa
#############################################################
invest_ini = invest_ini + 1  # O +1 é para não ter fluxo >= 0 no Ano 0 para não afetar o cálculo da TIR
fluxo, financiamento = calcular_fluxo_de_caixa(receita_bruta_anual, desconto_anual, fatura_energia, oper_manut,
                                               aluguel_ano, prestacoes, valor_total_financiado, invest_ini,
                                               valor_residual_fv)

#############################################################
# Incluir zero na primeira posição dos vetores
#############################################################
receita_bruta_anual.insert(0, 0)
desconto_anual.insert(0, 0)
fatura_energia.insert(0, 0)
oper_manut.insert(0, 0)
aluguel_ano.insert(0, 0)
financiamento.insert(0, 0)

#############################################################
# Impressão dos resultados do fluxo de caixa
#############################################################
'''print('Receita bruta anual:', " ".join("{:.2f}".format(valor) for valor in receita_bruta_anual))
print("Desconto Simples Anual: ", " ".join("{:.2f}".format(valor) for valor in desconto_anual))
print('Aluguel anual:', " ".join("{:.2f}".format(valor) for valor in aluguel_ano))
print('Financiamento anual', " ".join("{:.2f}".format(valor) for valor in financiamento))
print('Fluxo de caixa:', " ".join("{:.2f}".format(valor) for valor in fluxo))
print("TIR:", "{:.2f}".format(tir))
print("VPL:", "{:.2f}".format(vpl))'''
print()
print()
print('Resultado final do fluxo de caixa:')
print()


def imprimir_tabela(nomes_vetores, *vetores):
    # Determinar o número de anos
    num_anos = len(vetores[0])

    # Determinar o comprimento máximo do nome do vetor
    max_len_nome = max(len(nome) for nome in nomes_vetores)

    # Imprimir conteúdo
    for nome, vetor in zip(nomes_vetores, vetores):
        print("{:<{}}".format(nome, max_len_nome + 5), end="")
        for valor in vetor:
            print("{:<12.2f}".format(valor), end="")
        print()


nomes_vetores = ["Anos", "Receita Bruta (+)", "Imposto Simples Nacional (-)", "Fatura de energia (-)", "O&M (-)",
                 "Aluguel (-)", "Financiamento (-)", "Fluxo de Caixa (=)"]
imprimir_tabela(nomes_vetores, list(range(len(receita_bruta_anual))), receita_bruta_anual, desconto_anual,
                fatura_energia, oper_manut, aluguel_ano, financiamento, fluxo)
print()
print('Investimento inicial:', invest_ini)
print("Valor financiado:", valor_total_financiado)
#############################################################
# Cálculo dos indicadores econômicos
#############################################################
vpl = npf.npv(tma, fluxo)
tir = npf.irr(fluxo)
tir_percentual = tir * 100

print()
print()
print('Indicadores Econômicos')
print("VPL (R$): ", "{:.2f}".format(vpl))
print("TIR (%): ", "{:2f}".format(tir_percentual))


def calcular_payback_descontado(fluxo, tma):
    saldo_acumulado = 0
    for periodo, valor in enumerate(fluxo, start=0):
        saldo_acumulado += valor / (1 + tma) ** periodo
        if saldo_acumulado >= 0:
            return periodo
    return None  # Se o payback não for atingido


payback_descontado = calcular_payback_descontado(fluxo, tma)
if payback_descontado is not None:
    print("Payback Descontado (anos):", payback_descontado)
else:
    print("O payback descontado não foi atingido.")

#############################################################
