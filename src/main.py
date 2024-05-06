## Instituto Federal de Educação, Ciência e Tecnologia de Goiás
## Mestrado em Tecnologia, Gestão e Sustentabilidade
## Discente: Letícia Chaves Fonseca Ucker
## Título: Ferramenta computacional para análise de viabilidade econômica da implantação de eletropostos

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import numpy_financial as npf
from financiamento import calcular_financiamento
from simples_nacional_anexo import calcular_simples_nacional
from fluxo_caixa import calcular_fluxo_de_caixa
from fotovoltaico import calcular_geracao_fotovoltaica
from fatura_4 import calcular_fatura_4

#############################################################
## Dados de entrada:
#############################################################
# Carregar dados do Simples Nacional do arquivo Excel
simples_nacional = pd.read_excel('simples_nacional.xlsx', sheet_name='Dados Simples Nacional')
anexo1 = simples_nacional.iloc[5:13, 0:5]

# Dados eletropostos
num_eletropostos = 4 # Número de eletropostos
pot_eletroposto = 22 # Potência do eletroposto kW
recarga_dia = 6 # Recarga h/dia

# Dados sistema fotovoltaico
pot_fv = 125  # Potência do sistema fotovoltaico (kW)
h_inc = 5.45 # Zomer (2014) - Horas de irradiação solar média por dia (irradiância kWh/m2.dia Cresesb dividido por 1kW/m2 que é a irradiância de referência)
pr = 0.80  # Performance ratio
perda_eficiencia_anual = 0.016 # Perda de eficiência anual do sistema (em decimal)

# Dados econômicos
preco_eletroposto = 120000 # Preço de cada eletroposto em R$
preco_fv = 5000 # Preço do sistema fotovoltaico em R$/kWp
implantacao = 30000 # Outros custos de implantação em R$
o_e_m = 10000 # Valor da operação e manutenção por eletroposto em R$/ano
valor_recarga = 2 # Valor da recarga R$/kWh
tarifa_energia = 0.9 # Valor da tarifa de energia com impostos em R$/kWh
tma = 0.1 # Taxa Mínima de Atratividade
aluguel_mes = 3000 # Aluguel em R$/mês
vida_util = 10 # Vida útil financeira do fluxo de caixa - vida útil dos eletropostos

# Dados de financiamento
perc_finan = 70 # Digite o percentual a ser financiado de 0 a 100%
numero_prestacoes = 60 # Digite o número total de prestações em meses
taxa_juros_anual = 0.1 # Digite a taxa de juros anual (em decimal)
tipo_financiamento = 'price' # Digite o tipo de financiamento (price ou sac)
#tipo_financiamento = input("Digite o tipo de financiamento (price ou sac): ").lower()

# Sistema de compensação de energia elétrica
tusd = 0.3
fator_simult = 0.35       # Fator de simultaneidade entre consumo e geração
custo_disponibilidade = 100 # Monofásico = 30 kWh; Bifásico = 50 kWh; Trifásico = 100 kWh.

# Dados de sensibilidade
valor_recarga_inicial = 1     # Valor inicial do range valor de recarga (R$)
valor_recarga_final = 4       # Valor final do range valor de recarga (R$)
recarga_dia_inicial = 0       # Valor inicial do range recarga por dia (h/dia)
recarga_dia_final = 12        # Valor final do range recarga por dia (h/dia)
pot_fv_inicial = 1            # Valor inicial do range potência do FV (kW)
pot_fv_final = 200            # Valor final do range potência do FV (kW)

#************************************************************
# ANÁLISE DE SENSIBILIDADE
#************************************************************
# Menu de opções para o usuário
print("Selecione o tipo de análise de sensibilidade:")
print("Opção 1: Sem análise de sensibilidade")
print("Opção 2: Análise de sensibilidade do valor_recarga")
print("Opção 3: Análise de sensibilidade do recarga_dia")
print("Opção 4: Análise de sensibilidade do pot_fv")

opcao_selecionada = int(input("Digite o número da opção desejada: "))

print(recarga_dia)

def realizar_analise_sensibilidade(opcao):
    if opcao == 1:
        print("Opção selecionada: Sem análise de sensibilidade")
        #*************************************************************************************************
        # Código base - sem análise de sensibilidade

        #############################################################
        ## Cálculo do investimento inicial
        #############################################################
        invest_ini = num_eletropostos*preco_eletroposto + pot_fv*preco_fv + implantacao

        #############################################################
        ## Cálculo da demanda de energia elétrica dos eletropostos
        #############################################################
        demanda = [num_eletropostos*pot_eletroposto*recarga_dia*365]*int(vida_util) # Demanda em kWh/ano
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
        fator_residual_fv = 1 - vida_util/25 - 0.2 # Considera-se uma perda imediata de 20% + uma perda proporcional aos anos.
        valor_residual_fv = pot_fv*preco_fv*fator_residual_fv # Valor residual do sistema FV a ser adicionado no último ano do fluxo de caixa
        print('Valor residual FV:', valor_residual_fv)

        #############################################################
        # Cálculo da fatura de energia
        #############################################################
        tarifa_energia_anos = [tarifa_energia]*int(vida_util)
        tusds = [tusd]*int(vida_util)

        # Calcular a fatura da concessionária para todos os anos
        fatura_energia, abatimento, creditos = calcular_fatura_4(geracoes, demanda, tarifa_energia_anos, tusds, fator_simult, custo_disponibilidade)
        #fatura_energia = calcular_fatura(demanda, geracoes, tarifa_energia_anos)
        print("Faturas concessionária em R$:", fatura_energia)
        print("Abatimento de energia em kWh:", abatimento)
        print("Créditos restantes em kWh", creditos)

        #############################################################
        # Cálculo do custo de operação e manutenção
        #############################################################
        oper_manut = [o_e_m*num_eletropostos]*int(vida_util) # Vetor com os valores de O&M anuais

        #############################################################
        ## Cálculo de financiamento
        #############################################################
        valor_total_financiado = (perc_finan/100)*invest_ini
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
        aluguel_ano = [aluguel_mes*12]*int(vida_util)

        #############################################################
        ## Cálculo da Receita Bruta
        #############################################################
        valor_recarga_anos = [valor_recarga]*int(vida_util)
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
        fluxo, financiamento = calcular_fluxo_de_caixa(receita_bruta_anual, desconto_anual, fatura_energia, oper_manut, aluguel_ano, prestacoes, valor_total_financiado, invest_ini, valor_residual_fv)

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

        nomes_vetores = ["Anos", "Receita Bruta (+)", "Imposto Simples Nacional (-)","Fatura de energia (-)","O&M (-)", "Aluguel (-)", "Financiamento (-)", "Fluxo de Caixa (=)"]
        imprimir_tabela(nomes_vetores, list(range(len(receita_bruta_anual))), receita_bruta_anual, desconto_anual, fatura_energia, oper_manut, aluguel_ano, financiamento, fluxo)
        print()
        print('Investimento inicial:', invest_ini)
        print("Valor financiado:", valor_total_financiado)
        #############################################################
        #Cálculo dos indicadores econômicos
        #############################################################
        vpl = npf.npv(tma,fluxo)
        tir = npf.irr(fluxo)
        tir_percentual = tir*100

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
    #***************************************************************************************************

    elif opcao == 2:
        print("Opção selecionada: Análise de sensibilidade do valor_recarga")
        #***********************************************************************************************
        # Código para análise de sensibilidade do valor_recarga
        #***********************************************************************************************

        #############################################################
        # Cálculo do range do valor de recarga
        #############################################################
        valor_recarga_range = np.linspace(valor_recarga_inicial, valor_recarga_final, num=100) # Intervalo de variação do valor da recarga

        #############################################################
        ## Cálculo do investimento inicial
        #############################################################
        invest_ini = num_eletropostos*preco_eletroposto + pot_fv*preco_fv + implantacao

        #############################################################
        ## Cálculo da demanda de energia elétrica dos eletropostos
        #############################################################
        print("Recarga por dia (h)", recarga_dia)
        demanda = [num_eletropostos*pot_eletroposto*recarga_dia*365]*int(vida_util) # Demanda em kWh/ano
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
        fator_residual_fv = 1 - vida_util/25 - 0.2 # Considera-se uma perda imediata de 20% + uma perda proporcional aos anos.
        valor_residual_fv = pot_fv*preco_fv*fator_residual_fv # Valor residual do sistema FV a ser adicionado no último ano do fluxo de caixa
        print('Valor residual FV:', valor_residual_fv)

        #############################################################
        # Cálculo da fatura de energia
        #############################################################
        tarifa_energia_anos = [tarifa_energia]*int(vida_util)
        tusds = [tusd]*int(vida_util)

        # Calcular a fatura da concessionária para todos os anos
        fatura_energia, abatimento, creditos = calcular_fatura_4(geracoes, demanda, tarifa_energia_anos, tusds, fator_simult, custo_disponibilidade)
        #fatura_energia = calcular_fatura(demanda, geracoes, tarifa_energia_anos)
        print("Faturas concessionária em R$:", fatura_energia)
        print("Abatimento de energia em kWh:", abatimento)
        print("Créditos restantes em kWh", creditos)

        #############################################################
        # Cálculo do custo de operação e manutenção
        #############################################################
        oper_manut = [o_e_m*num_eletropostos]*int(vida_util) # Vetor com os valores de O&M anuais

        #############################################################
        ## Cálculo de financiamento
        #############################################################
        valor_total_financiado = (perc_finan/100)*invest_ini
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
        plt.ylabel('Valor (R$)')
        plt.title(f'Financiamento {tipo_financiamento.upper()}')
        plt.legend()
        plt.grid(True)
        plt.show()

        #############################################################
        ## Cálculo do aluguel
        #############################################################
        aluguel_ano = [aluguel_mes*12]*int(vida_util)

        #############################################################
        ## Cálculo da Receita Bruta
        #############################################################
        # Lista para armazenar resultados da análise de sensibilidade
        vpl_valor_recarga = []

        # Loop para análise de sensibilidade do valor_recarga
        for valor_recarga_2 in valor_recarga_range:
            # (Recalcular todas as métricas relevantes com o novo valor de valor_recarga)
            valor_recarga_anos = [valor_recarga_2]*int(vida_util)
            receita_bruta_anual = [z * w for z, w in zip(demanda, valor_recarga_anos)]

            #############################################################
            # Cálculo do Simples Nacional
            aliquota_efetiva, desconto_mensal, desconto_anual = calcular_simples_nacional(receita_bruta_anual, anexo1)

            #############################################################
            # Cálculo do fluxo de caixa
            invest_ini = invest_ini + 1  # O +1 é para não ter fluxo >= 0 no Ano 0 para não afetar o cálculo da TIR
            fluxo, financiamento = calcular_fluxo_de_caixa(receita_bruta_anual, desconto_anual, fatura_energia, oper_manut, aluguel_ano, prestacoes, valor_total_financiado, invest_ini, valor_residual_fv)

            #############################################################
            # Calcular o VPL
            vpl = npf.npv(tma, fluxo)
            vpl_valor_recarga.append(vpl)

        #############################################################
        # Plotar os resultados da análise de sensibilidade
        # Dividir os dados em duas séries com base na condição VPL >= 0 e VPL < 0
        vpl_positivo = []
        vpl_negativo = []
        for vpl_valor in vpl_valor_recarga:
            if vpl_valor >= 0:
                vpl_positivo.append(vpl_valor)
                vpl_negativo.append(np.nan)
            else:
                vpl_positivo.append(np.nan)
                vpl_negativo.append(vpl_valor)

        # Plotar as duas séries separadamente com cores diferentes
        plt.figure(figsize=(10, 6))
        plt.plot(valor_recarga_range, vpl_positivo, marker='o', color='b', label='Viabilidade (VPL >= 0)')
        plt.plot(valor_recarga_range, vpl_negativo, marker='o', color='r', label='Inviabilidade (VPL < 0)')
        plt.axhline(y=0, color='black', linestyle='--', linewidth=1)  # Adicionar linha horizontal em y=0
        plt.title('Análise de Sensibilidade do VPL')
        plt.xlabel('Valor de Recarga (R$)')
        plt.ylabel('VPL (R$)')
        plt.legend()
        plt.grid(True)
        plt.show()
    #************************************************************************************
    elif opcao == 3:
        print("Opção selecionada: Análise de sensibilidade do recarga_dia")
        # Código para análise de sensibilidade do recarga_dia
        #*************************************************************************************************

        #############################################################
        # Cálculo do range da recarga por dia (h)
        #############################################################
        recarga_dia_range = np.linspace(recarga_dia_inicial, recarga_dia_final, num=100) # Intervalo de variação da recarga por eletroposto

        #############################################################
        ## Cálculo do investimento inicial
        #############################################################
        invest_ini = num_eletropostos*preco_eletroposto + pot_fv*preco_fv + implantacao

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
        fator_residual_fv = 1 - vida_util/25 - 0.2 # Considera-se uma perda imediata de 20% + uma perda proporcional aos anos.
        valor_residual_fv = pot_fv*preco_fv*fator_residual_fv # Valor residual do sistema FV a ser adicionado no último ano do fluxo de caixa
        print('Valor residual FV:', valor_residual_fv)

        #############################################################
        # Cálculo do custo de operação e manutenção
        #############################################################
        oper_manut = [o_e_m*num_eletropostos]*int(vida_util) # Vetor com os valores de O&M anuais

        #############################################################
        ## Cálculo de financiamento
        #############################################################
        valor_total_financiado = (perc_finan/100)*invest_ini
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
        aluguel_ano = [aluguel_mes*12]*int(vida_util)

        #############################################################
        ## Cálculo da Receita Bruta
        #############################################################

        # Listas para armazenar resultados da análise de sensibilidade
        vpl_recarga_dia = []

        # Loop para análise de sensibilidade do valor_recarga
        for recarga_dia_elet in recarga_dia_range:
            # (Recalcular todas as métricas relevantes com o novo valor de recarga por dia)

            #############################################################
            ## Cálculo da demanda de energia elétrica dos eletropostos
            #############################################################
            demanda = [num_eletropostos*pot_eletroposto*recarga_dia_elet*365]*int(vida_util) # Demanda em kWh/ano

            #############################################################
            # Cálculo da fatura de energia
            #############################################################
            tarifa_energia_anos = [tarifa_energia]*int(vida_util)
            tusds = [tusd]*int(vida_util)

            # Calcular a fatura da concessionária para todos os anos
            fatura_energia, abatimento, creditos = calcular_fatura_4(geracoes, demanda, tarifa_energia_anos, tusds, fator_simult, custo_disponibilidade)

            #############################################################
            # Cálculo da receita bruta
            valor_recarga_anos = [valor_recarga]*int(vida_util)
            receita_bruta_anual = [z * w for z, w in zip(demanda, valor_recarga_anos)]

            #############################################################
            # Cálculo do Simples Nacional
            aliquota_efetiva, desconto_mensal, desconto_anual = calcular_simples_nacional(receita_bruta_anual, anexo1)

            #############################################################
            # Cálculo do fluxo de caixa
            invest_ini = invest_ini + 1  # O +1 é para não ter fluxo >= 0 no Ano 0 para não afetar o cálculo da TIR
            fluxo, financiamento = calcular_fluxo_de_caixa(receita_bruta_anual, desconto_anual, fatura_energia, oper_manut, aluguel_ano, prestacoes, valor_total_financiado, invest_ini, valor_residual_fv)

            #############################################################
            # Calcular o VPL
            vpl = npf.npv(tma, fluxo)
            vpl_recarga_dia.append(vpl)

        #############################################################
        # Plotar os resultados da análise de sensibilidade
        # Dividir os dados em duas séries com base na condição VPL >= 0 e VPL < 0
        vpl_positivo = []
        vpl_negativo = []
        for vpl_valor in vpl_recarga_dia:
            if vpl_valor >= 0:
                vpl_positivo.append(vpl_valor)
                vpl_negativo.append(np.nan)
            else:
                vpl_positivo.append(np.nan)
                vpl_negativo.append(vpl_valor)

        # Plotar as duas séries separadamente com cores diferentes
        plt.figure(figsize=(10, 6))
        plt.plot(recarga_dia_range, vpl_positivo, marker='o', color='b', label='Viabilidade (VPL >= 0)')
        plt.plot(recarga_dia_range, vpl_negativo, marker='o', color='r', label='Inviabilidade (VPL < 0)')
        plt.axhline(y=0, color='black', linestyle='--', linewidth=1)  # Adicionar linha horizontal em y=0
        plt.title('Análise de Sensibilidade do VPL')
        plt.xlabel('Recarga por eletroposto (h/dia)')
        plt.ylabel('VPL (R$)')
        plt.legend()
        plt.grid(True)
        plt.show()
    #******************************************************************************************************
    elif opcao == 4:
        print("Opção selecionada: Análise de sensibilidade do pot_fv")
        # Código para análise de sensibilidade do pot_fv

        #############################################################
        # Cálculo do range da potência instalada FV (kW)
        #############################################################
        pot_fv_range = np.linspace(pot_fv_inicial, pot_fv_final, num=100) # Intervalo de variação da potência FV

        #############################################################
        ## Cálculo da demanda de energia elétrica dos eletropostos
        #############################################################
        demanda = [num_eletropostos*pot_eletroposto*recarga_dia*365]*int(vida_util) # Demanda em kWh/ano
        print("Demanda dos eletropostos", demanda)

        #############################################################
        # Cálculo do custo de operação e manutenção
        #############################################################
        oper_manut = [o_e_m*num_eletropostos]*int(vida_util) # Vetor com os valores de O&M anuais

        #############################################################
        ## Cálculo do aluguel
        #############################################################
        aluguel_ano = [aluguel_mes*12]*int(vida_util)

        #############################################################
        ## Cálculo da Receita Bruta
        #############################################################
        valor_recarga_anos = [valor_recarga]*int(vida_util)
        receita_bruta_anual = [z * w for z, w in zip(demanda, valor_recarga_anos)]

        #############################################################
        ## Cálculo do Simples Nacional
        #############################################################
        aliquota_efetiva, desconto_mensal, desconto_anual = calcular_simples_nacional(receita_bruta_anual, anexo1)

        # Listas para armazenar resultados da análise de sensibilidade
        vpl_pot_fv = []

        # Loop para análise de sensibilidade do valor_recarga
        for pot_fv_2 in pot_fv_range:
            # (Recalcular todas as métricas relevantes com o novo valor de potência FV)

            #############################################################
            ## Cálculo do investimento inicial
            #############################################################
            invest_ini = num_eletropostos*preco_eletroposto + pot_fv_2*preco_fv + implantacao

            #############################################################
            ## Cálculo da geração de energia do sistema fotovoltaico
            #############################################################
            geracoes, eficiencia = calcular_geracao_fotovoltaica(vida_util, pot_fv_2, h_inc, pr, perda_eficiencia_anual)

            #############################################################
            # Cálculo do valor residual do sistema fotovoltaico
            #############################################################
            fator_residual_fv = 1 - vida_util/25 - 0.2 # Considera-se uma perda imediata de 20% + uma perda proporcional aos anos.
            valor_residual_fv = pot_fv_2*preco_fv*fator_residual_fv # Valor residual do sistema FV a ser adicionado no último ano do fluxo de caixa

            #############################################################
            # Cálculo da fatura de energia
            #############################################################
            tarifa_energia_anos = [tarifa_energia]*int(vida_util)
            tusds = [tusd]*int(vida_util)

            # Calcular a fatura da concessionária para todos os anos
            fatura_energia, abatimento, creditos = calcular_fatura_4(geracoes, demanda, tarifa_energia_anos, tusds, fator_simult, custo_disponibilidade)

            #############################################################
            ## Cálculo de financiamento
            #############################################################
            valor_total_financiado = (perc_finan/100)*invest_ini
            prestacoes = calcular_financiamento(valor_total_financiado, numero_prestacoes, taxa_juros_anual, tipo_financiamento)

            meses = [i for i in range(numero_prestacoes)]
            juros_mensais = [(prestacoes[i] - valor_total_financiado / numero_prestacoes) for i in range(numero_prestacoes)]
            amortizacao_mensal = [valor_total_financiado / numero_prestacoes for _ in range(numero_prestacoes)]

            #############################################################
            ## Cálculo do fluxo de caixa
            #############################################################
            invest_ini = invest_ini + 1  # O +1 é para não ter fluxo >= 0 no Ano 0 para não afetar o cálculo da TIR
            fluxo, financiamento = calcular_fluxo_de_caixa(receita_bruta_anual, desconto_anual, fatura_energia, oper_manut, aluguel_ano, prestacoes, valor_total_financiado, invest_ini, valor_residual_fv)

            #############################################################
            # Calcular o VPL
            vpl = npf.npv(tma, fluxo)
            vpl_pot_fv.append(vpl)

        #############################################################

        # Encontrar a posição do maior valor de VPL
        posicao_max_vpl = np.argmax(vpl_pot_fv)

        # Encontrar o maior valor de VPL
        maior_vpl = vpl_pot_fv[posicao_max_vpl]
        print("Valor ótimo do VPL em R$:", maior_vpl )

        # Encontrar a potência correspondente usando a posição encontrada
        potencia_correspondente = pot_fv_range[posicao_max_vpl]
        print("Potência ótima do sistema fotovoltaico em kW", potencia_correspondente)

        # Plotar os resultados da análise de sensibilidade
        # Dividir os dados em duas séries com base na condição VPL >= 0 e VPL < 0
        vpl_positivo = []
        vpl_negativo = []
        for vpl_valor in vpl_pot_fv:
            if vpl_valor >= 0:
                vpl_positivo.append(vpl_valor)
                vpl_negativo.append(np.nan)
            else:
                vpl_positivo.append(np.nan)
                vpl_negativo.append(vpl_valor)

        # Plotar as duas séries separadamente com cores diferentes
        plt.figure(figsize=(10, 6))
        plt.plot(pot_fv_range, vpl_positivo, marker='o', color='b', label='Viabilidade (VPL >= 0)')
        plt.plot(pot_fv_range, vpl_negativo, marker='o', color='r', label='Inviabilidade (VPL < 0)')
        plt.axhline(y=0, color='black', linestyle='--', linewidth=1)  # Adicionar linha horizontal em y=0
        plt.title('Análise de Sensibilidade do VPL')
        plt.xlabel('Potência do sistema fotovoltaico (kW)')
        plt.ylabel('VPL (R$)')
        plt.legend()
        plt.grid(True)
        plt.show()

    else:
        print("Opção inválida. Por favor, escolha uma opção válida.")

# Realizar a análise de sensibilidade de acordo com a opção selecionada
realizar_analise_sensibilidade(opcao_selecionada)

#************************************************************


