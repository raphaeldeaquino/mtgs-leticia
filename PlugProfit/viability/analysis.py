import os
import pandas as pd
import numpy as np
import numpy_financial as npf
from os.path import dirname, join as joinpath
from .fotovoltaico import calcular_geracao_fotovoltaica
from .fatura_4 import calcular_fatura_4
from .financiamento import calcular_financiamento
from .simples_nacional_anexo import calcular_simples_nacional
from .fluxo_caixa import calcular_fluxo_de_caixa


def format_two_digits(number):
    s = "{:,.2f}".format(number).replace(',', '.')
    return s[:-3] + ',' + s[-2:]


def calcular_payback_descontado(fluxo, tma):
    saldo_acumulado = 0
    for periodo, valor in enumerate(fluxo, start=0):
        saldo_acumulado += valor / (1 + tma) ** periodo
        if saldo_acumulado >= 0:
            return periodo
    return None  # Se o payback não for atingido


def calculate_viability(input_data, opcao_selecionada):
    use_photovoltaic = input_data['show_hide_fotovoltaico'] == 'on'
    use_financing = input_data['show_hide_financiamento'] == 'on'

    if opcao_selecionada == '1':
        result = {'opcao': 'Sem análise de sensibilidade'}

        # *************************************************************************************************
        # Código base - sem análise de sensibilidade

        #############################################################
        ## Cálculo do investimento inicial
        #############################################################

        invest_ini = input_data['num_eletropostos'] * input_data['preco_eletroposto'] + input_data['implantacao']
        if use_photovoltaic:
            invest_ini = invest_ini + input_data['pot_fv'] * input_data['preco_fv']

        #############################################################
        ## Cálculo da demanda de energia elétrica dos eletropostos
        #############################################################
        result["Recarga por dia"] = input_data['recarga_dia']
        demanda = [input_data['num_eletropostos'] * input_data['pot_eletroposto'] * input_data['recarga_dia'] * 365] * \
                  int(input_data['vida_util'])  # Demanda em kWh/ano
        result["Demanda dos eletropostos"] = list(map(format_two_digits, demanda))

        #############################################################
        ## Cálculo da geração de energia do sistema fotovoltaico
        #############################################################
        result['anos'] = [str(x) for x in list(range(1, int(input_data['vida_util']) + 1))]
        if use_photovoltaic:
            geracoes, eficiencia = calcular_geracao_fotovoltaica(input_data['vida_util'], input_data['pot_fv'],
                                                                 input_data['h_inc'], input_data['pr'],
                                                                 input_data['perda_eficiencia_anual'])
            result["Geração fotovoltaica"] = list(map(format_two_digits, geracoes))
            result["geracoes"] = geracoes


            #############################################################
            # Cálculo do valor residual do sistema fotovoltaico
            #############################################################
            fator_residual_fv = 1 - input_data[
                'vida_util'] / 25 - 0.2  # Considera-se uma perda imediata de 20% + uma perda proporcional aos anos.
            valor_residual_fv = input_data['pot_fv'] * input_data[
                'preco_fv'] * fator_residual_fv  # Valor residual do sistema FV a ser adicionado no último ano do fluxo
            # de caixa
            result['Valor residual FV'] = format_two_digits(valor_residual_fv)
        else:
            valor_residual_fv = 0.0
            geracoes = list(np.zeros(input_data['vida_util']))

        #############################################################
        # Cálculo da fatura de energia
        #############################################################
        tarifa_energia_anos = [input_data['tarifa_energia']] * int(input_data['vida_util'])
        tusds = [input_data['tusd']] * int(input_data['vida_util'])

        # Calcular a fatura da concessionária para todos os anos
        fatura_energia, abatimento, creditos = calcular_fatura_4(geracoes, demanda, tarifa_energia_anos, tusds,
                                                                 input_data['fator_simult'],
                                                                 input_data['custo_disponibilidade'])
        result["Faturas concessionária"] = list(map(format_two_digits, fatura_energia))
        result["Abatimento de energia"] = list(map(format_two_digits, abatimento))
        result["Créditos restantes"] = list(map(format_two_digits, creditos))

        #############################################################
        # Cálculo do custo de operação e manutenção
        #############################################################
        oper_manut = [input_data['o_e_m'] * input_data['num_eletropostos']] * int(
            input_data['vida_util'])  # Vetor com os valores de O&M anuais

        #############################################################
        ## Cálculo de financiamento
        #############################################################
        if use_financing:
            valor_total_financiado = (input_data['perc_finan'] / 100) * invest_ini
            prestacoes = calcular_financiamento(valor_total_financiado, input_data['numero_prestacoes'],
                                                input_data['taxa_juros_anual'], input_data['tipo_financiamento'])
            result['Vetor prestações de financiamento'] = list(map(format_two_digits, prestacoes))

            meses = [i for i in range(1, input_data['numero_prestacoes'] + 1)]
            juros_mensais = [(prestacoes[i] - valor_total_financiado / input_data['numero_prestacoes'])
                             for i in range(input_data['numero_prestacoes'])]
            amortizacao_mensal = [valor_total_financiado / input_data['numero_prestacoes']
                                  for _ in range(input_data['numero_prestacoes'])]

            result['meses'] = meses
            result['juros_mensais'] = juros_mensais
            result['amortizacao_mensal'] = amortizacao_mensal
            result['prestacoes'] = prestacoes
            result['tipo_financiamento'] = input_data['tipo_financiamento']
        else:
            valor_total_financiado = 0.0
            prestacoes = list(np.zeros(input_data['numero_prestacoes']))

        #############################################################
        ## Cálculo do aluguel
        #############################################################
        aluguel_ano = [input_data['aluguel_mes'] * 12] * int(input_data['vida_util'])

        #############################################################
        ## Cálculo da Receita Bruta
        #############################################################
        valor_recarga_anos = [input_data['valor_recarga']] * int(input_data['vida_util'])
        receita_bruta_anual = [z * w for z, w in zip(demanda, valor_recarga_anos)]

        #############################################################
        ## Cálculo do Simples Nacional
        #############################################################
        # Carregar dados do Simples Nacional do arquivo Excel
        DATA_DIR = joinpath(dirname(__file__), 'data')
        simples_path = os.path.join(DATA_DIR, 'simples_nacional.xlsx')
        simples_nacional = pd.read_excel(simples_path, sheet_name='Dados Simples Nacional')
        anexo1 = simples_nacional.iloc[5:13, 0:5]
        aliquota_efetiva, desconto_mensal, desconto_anual = calcular_simples_nacional(receita_bruta_anual, anexo1)

        if aliquota_efetiva is not None:
            result['Alíquota efetiva'] = list(map(format_two_digits, aliquota_efetiva))
            result['Desconto Simples Mensal'] = list(map(format_two_digits, desconto_mensal))

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
        # Geração dos resultados do fluxo de caixa
        #############################################################
        result["Receita Bruta"] = list(map(format_two_digits, receita_bruta_anual))
        result["Imposto Simples Nacional"] = list(map(format_two_digits, desconto_anual))
        result["Fatura de energia"] = list(map(format_two_digits, fatura_energia))
        result["O&M"] = list(map(format_two_digits, oper_manut))
        result["Aluguel"] = list(map(format_two_digits, aluguel_ano))
        result["Financiamento"] = list(map(format_two_digits, financiamento))
        result["Fluxo de Caixa"] = list(map(format_two_digits, fluxo))
        result['Investimento inicial'] = format_two_digits(invest_ini)
        result["Valor financiado"] = format_two_digits(valor_total_financiado)
        #############################################################
        # Cálculo dos indicadores econômicos
        #############################################################
        vpl = npf.npv(input_data['tma'], fluxo)
        tir = npf.irr(fluxo)
        tir_percentual = tir * 100
        result["VPL"] = format_two_digits(vpl)
        result["TIR"] = format_two_digits(tir_percentual)

        payback_descontado = calcular_payback_descontado(fluxo, input_data['tma'])
        if payback_descontado is not None:
            result["Payback Descontado"] = payback_descontado

        return result
    # ***************************************************************************************************

    elif opcao_selecionada == '2':
        result = {'opcao': 'Análise de sensibilidade do valor da recarga'}

        # ***********************************************************************************************
        # Código para análise de sensibilidade do valor_recarga
        # ***********************************************************************************************

        #############################################################
        # Cálculo do range do valor de recarga
        #############################################################
        valor_recarga_range = np.linspace(input_data['valor_recarga_inicial'], input_data['valor_recarga_final'],
                                          num=100)  # Intervalo de variação do valor da recarga

        #############################################################
        ## Cálculo do investimento inicial
        #############################################################
        invest_ini = input_data['num_eletropostos'] * input_data['preco_eletroposto'] + input_data['implantacao']
        if use_photovoltaic:
            invest_ini = invest_ini + input_data['pot_fv'] * input_data['preco_fv']

        #############################################################
        ## Cálculo da demanda de energia elétrica dos eletropostos
        #############################################################
        result["Recarga por dia"] = input_data['recarga_dia']
        demanda = [input_data['num_eletropostos'] * input_data['pot_eletroposto'] * input_data['recarga_dia'] * 365] * \
                  int(input_data['vida_util'])  # Demanda em kWh/ano
        result["Demanda dos eletropostos"] = list(map(format_two_digits, demanda))

        #############################################################
        ## Cálculo da geração de energia do sistema fotovoltaico
        #############################################################
        # Dados do gráfico da geração fotovoltaica ao longo dos anos
        result['anos'] = [x for x in range(1, input_data['vida_util'] + 1)]
        if use_photovoltaic:
            geracoes, eficiencia = calcular_geracao_fotovoltaica(input_data['vida_util'], input_data['pot_fv'],
                                                                 input_data['h_inc'], input_data['pr'],
                                                                 input_data['perda_eficiencia_anual'])
            result["Geração fotovoltaica"] = list(map(format_two_digits, geracoes))
            result['geracoes'] = geracoes

            #############################################################
            # Cálculo do valor residual do sistema fotovoltaico
            #############################################################
            fator_residual_fv = 1 - input_data['vida_util'] / 25 - 0.2  # Considera-se uma perda imediata de 20% + uma
            # perda proporcional aos anos.
            valor_residual_fv = input_data['pot_fv'] * input_data['preco_fv'] * fator_residual_fv  # Valor residual do
            # sistema FV a ser adicionado no último ano do fluxo de caixa
            result['Valor residual FV'] = format_two_digits(valor_residual_fv)
        else:
            valor_residual_fv = 0.0
            geracoes = list(np.zeros(input_data['vida_util']))

        #############################################################
        # Cálculo da fatura de energia
        #############################################################
        tarifa_energia_anos = [input_data['tarifa_energia']] * int(input_data['vida_util'])
        tusds = [input_data['tusd']] * int(input_data['vida_util'])

        # Calcular a fatura da concessionária para todos os anos
        fatura_energia, abatimento, creditos = calcular_fatura_4(geracoes, demanda, tarifa_energia_anos, tusds,
                                                                 input_data['fator_simult'],
                                                                 input_data['custo_disponibilidade'])
        result["Faturas concessionária"] = list(map(format_two_digits, fatura_energia))
        result["Abatimento de energia"] = list(map(format_two_digits, abatimento))
        result["Créditos restantes"] = list(map(format_two_digits, creditos))

        #############################################################
        # Cálculo do custo de operação e manutenção
        #############################################################
        oper_manut = [input_data['o_e_m'] * input_data['num_eletropostos']] * int(input_data['vida_util'])  # Vetor
        # com os valores de O&M anuais

        #############################################################
        ## Cálculo de financiamento
        #############################################################
        if use_financing:
            valor_total_financiado = (input_data['perc_finan'] / 100) * invest_ini
            prestacoes = calcular_financiamento(valor_total_financiado, input_data['numero_prestacoes'],
                                                input_data['taxa_juros_anual'], input_data['tipo_financiamento'])
            result['Vetor prestações de financiamento'] = list(map(format_two_digits, prestacoes))

            meses = [i for i in range(input_data['numero_prestacoes'])]
            juros_mensais = [(prestacoes[i] - valor_total_financiado / input_data['numero_prestacoes']) for i in
                             range(input_data['numero_prestacoes'])]
            amortizacao_mensal = [valor_total_financiado / input_data['numero_prestacoes'] for _ in
                                  range(input_data['numero_prestacoes'])]

            result['meses'] = meses
            result['juros_mensais'] = juros_mensais
            result['amortizacao_mensal'] = amortizacao_mensal
            result['prestacoes'] = prestacoes
        else:
            valor_total_financiado = 0.0
            prestacoes = list(np.zeros(input_data['numero_prestacoes']))

        #############################################################
        ## Cálculo do aluguel
        #############################################################
        aluguel_ano = [input_data['aluguel_mes'] * 12] * int(input_data['vida_util'])

        #############################################################
        ## Cálculo da Receita Bruta
        #############################################################
        # Lista para armazenar resultados da análise de sensibilidade
        vpl_valor_recarga = []

        DATA_DIR = joinpath(dirname(__file__), 'data')
        simples_path = os.path.join(DATA_DIR, 'simples_nacional.xlsx')
        simples_nacional = pd.read_excel(simples_path, sheet_name='Dados Simples Nacional')
        anexo1 = simples_nacional.iloc[5:13, 0:5]

        # Loop para análise de sensibilidade do valor_recarga
        for valor_recarga_2 in valor_recarga_range:
            # (Recalcular todas as métricas relevantes com o novo valor de valor_recarga)
            valor_recarga_anos = [valor_recarga_2] * int(input_data['vida_util'])
            receita_bruta_anual = [z * w for z, w in zip(demanda, valor_recarga_anos)]

            #############################################################
            # Cálculo do Simples Nacional
            aliquota_efetiva, desconto_mensal, desconto_anual = calcular_simples_nacional(receita_bruta_anual, anexo1)

            #############################################################
            # Cálculo do fluxo de caixa
            invest_ini = invest_ini + 1  # O +1 é para não ter fluxo >= 0 no Ano 0 para não afetar o cálculo da TIR
            fluxo, financiamento = calcular_fluxo_de_caixa(receita_bruta_anual, desconto_anual, fatura_energia,
                                                           oper_manut, aluguel_ano, prestacoes, valor_total_financiado,
                                                           invest_ini, valor_residual_fv)

            #############################################################
            # Calcular o VPL
            vpl = npf.npv(input_data['tma'], fluxo)
            vpl_valor_recarga.append(vpl)

        #############################################################
        # Gerar os resultados da análise de sensibilidade
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

        # Gerar as duas séries separadamente com cores diferentes
        result['valor_recarga_range'] = list(map(format_two_digits, list(valor_recarga_range)))
        result['vpl_positivo'] = vpl_positivo
        result['vpl_negativo'] = vpl_negativo

        return result
    # ************************************************************************************
    elif opcao_selecionada == '3':
        result = {'opcao': 'Análise de sensibilidade da recarga por dia'}
        # Código para análise de sensibilidade do recarga_dia
        # *************************************************************************************************

        #############################################################
        # Cálculo do range da recarga por dia (h)
        #############################################################
        recarga_dia_range = np.linspace(input_data['recarga_dia_inicial'], input_data['recarga_dia_final'],
                                        num=100)  # Intervalo de variação da recarga por eletroposto

        #############################################################
        ## Cálculo do investimento inicial
        #############################################################
        invest_ini = input_data['num_eletropostos'] * input_data['preco_eletroposto'] + input_data['implantacao']
        if use_photovoltaic:
            invest_ini = invest_ini + input_data['pot_fv'] * input_data['preco_fv']

        #############################################################
        ## Cálculo da geração de energia do sistema fotovoltaico
        #############################################################
        result['anos'] = [x for x in range(1, input_data['vida_util'] + 1)]
        if use_photovoltaic:
            geracoes, eficiencia = calcular_geracao_fotovoltaica(input_data['vida_util'], input_data['pot_fv'],
                                                                 input_data['h_inc'], input_data['pr'],
                                                                 input_data['perda_eficiencia_anual'])
            result["Geração fotovoltaica"] = list(map(format_two_digits, geracoes))
            result['geracoes'] = geracoes


            #############################################################
            # Cálculo do valor residual do sistema fotovoltaico
            #############################################################
            fator_residual_fv = 1 - input_data['vida_util'] / 25 - 0.2  # Considera-se uma perda imediata de 20% + uma
            # perda proporcional aos anos.
            valor_residual_fv = input_data['pot_fv'] * input_data['preco_fv'] * fator_residual_fv  # Valor residual do
            # sistema FV a ser adicionado no último ano do fluxo de caixa
            result['Valor residual FV'] = format_two_digits(valor_residual_fv)
        else:
            valor_residual_fv = 0.0
            geracoes = list(np.zeros(input_data['vida_util']))

        #############################################################
        # Cálculo do custo de operação e manutenção
        #############################################################
        oper_manut = [input_data['o_e_m'] * input_data['num_eletropostos']] * int(input_data['vida_util'])  # Vetor
        # com os valores de O&M anuais

        #############################################################
        ## Cálculo de financiamento
        #############################################################
        if use_financing:
            valor_total_financiado = (input_data['perc_finan'] / 100) * invest_ini
            prestacoes = calcular_financiamento(valor_total_financiado, input_data['numero_prestacoes'],
                                                input_data['taxa_juros_anual'], input_data['tipo_financiamento'])
            result['Vetor prestações de financiamento'] = list(map(format_two_digits, prestacoes))

            meses = [i for i in range(input_data['numero_prestacoes'])]
            juros_mensais = [(prestacoes[i] - valor_total_financiado / input_data['numero_prestacoes']) for i in
                             range(input_data['numero_prestacoes'])]
            amortizacao_mensal = [valor_total_financiado / input_data['numero_prestacoes'] for _ in
                                  range(input_data['numero_prestacoes'])]

            result['meses'] = meses
            result['juros_mensais'] = juros_mensais
            result['amortizacao_mensal'] = amortizacao_mensal
            result['prestacoes'] = prestacoes
        else:
            valor_total_financiado = 0.0
            prestacoes = list(np.zeros(input_data['numero_prestacoes']))

        #############################################################
        ## Cálculo do aluguel
        #############################################################
        aluguel_ano = [input_data['aluguel_mes'] * 12] * int(input_data['vida_util'])

        #############################################################
        ## Cálculo da Receita Bruta
        #############################################################

        # Listas para armazenar resultados da análise de sensibilidade
        vpl_recarga_dia = []

        DATA_DIR = joinpath(dirname(__file__), 'data')
        simples_path = os.path.join(DATA_DIR, 'simples_nacional.xlsx')
        simples_nacional = pd.read_excel(simples_path, sheet_name='Dados Simples Nacional')
        anexo1 = simples_nacional.iloc[5:13, 0:5]

        # Loop para análise de sensibilidade do valor_recarga
        for recarga_dia_elet in recarga_dia_range:
            # (Recalcular todas as métricas relevantes com o novo valor de recarga por dia)

            #############################################################
            ## Cálculo da demanda de energia elétrica dos eletropostos
            #############################################################
            demanda = [input_data['num_eletropostos'] * input_data['pot_eletroposto'] * recarga_dia_elet * 365] * int(
                input_data['vida_util'])  # Demanda em kWh/ano

            #############################################################
            # Cálculo da fatura de energia
            #############################################################
            tarifa_energia_anos = [input_data['tarifa_energia']] * int(input_data['vida_util'])
            tusds = [input_data['tusd']] * int(input_data['vida_util'])

            # Calcular a fatura da concessionária para todos os anos
            fatura_energia, abatimento, creditos = calcular_fatura_4(geracoes, demanda, tarifa_energia_anos, tusds,
                                                                     input_data['fator_simult'],
                                                                     input_data['custo_disponibilidade'])

            #############################################################
            # Cálculo da receita bruta
            valor_recarga_anos = [input_data['valor_recarga']] * int(input_data['vida_util'])
            receita_bruta_anual = [z * w for z, w in zip(demanda, valor_recarga_anos)]

            #############################################################
            # Cálculo do Simples Nacional
            aliquota_efetiva, desconto_mensal, desconto_anual = calcular_simples_nacional(receita_bruta_anual, anexo1)

            #############################################################
            # Cálculo do fluxo de caixa
            invest_ini = invest_ini + 1  # O +1 é para não ter fluxo >= 0 no Ano 0 para não afetar o cálculo da TIR
            fluxo, financiamento = calcular_fluxo_de_caixa(receita_bruta_anual, desconto_anual, fatura_energia,
                                                           oper_manut, aluguel_ano, prestacoes, valor_total_financiado,
                                                           invest_ini, valor_residual_fv)

            #############################################################
            # Calcular o VPL
            vpl = npf.npv(input_data['tma'], fluxo)
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

        # Gerar as duas séries separadamente com cores diferentes
        result['valor_recarga_range'] = list(map(format_two_digits, list(recarga_dia_range)))
        result['vpl_positivo'] = vpl_positivo
        result['vpl_negativo'] = vpl_negativo

        return result
    # ******************************************************************************************************
    elif opcao_selecionada == '4':
        result = {'opcao': 'Análise de sensibilidade da potência do sistema fotovoltaico'}

        #############################################################
        # Cálculo do range da potência instalada FV (kW)
        #############################################################
        pot_fv_range = np.linspace(input_data['pot_fv_inicial'], input_data['pot_fv_final'], num=100)  # Intervalo de
        # variação da potência FV

        #############################################################
        ## Cálculo da demanda de energia elétrica dos eletropostos
        #############################################################
        demanda = [input_data['num_eletropostos'] * input_data['pot_eletroposto'] * input_data['recarga_dia'] * 365] * \
                  int(input_data['vida_util'])  # Demanda em kWh/ano
        result["Demanda dos eletropostos"] = demanda

        #############################################################
        # Cálculo do custo de operação e manutenção
        #############################################################
        oper_manut = [input_data['o_e_m'] * input_data['num_eletropostos']] * int(input_data['vida_util'])  # Vetor
        # com os valores de O&M anuais

        #############################################################
        ## Cálculo do aluguel
        #############################################################
        aluguel_ano = [input_data['aluguel_mes'] * 12] * int(input_data['vida_util'])

        #############################################################
        ## Cálculo da Receita Bruta
        #############################################################
        valor_recarga_anos = [input_data['valor_recarga']] * int(input_data['vida_util'])
        receita_bruta_anual = [z * w for z, w in zip(demanda, valor_recarga_anos)]

        #############################################################
        ## Cálculo do Simples Nacional
        #############################################################
        DATA_DIR = joinpath(dirname(__file__), 'data')
        simples_path = os.path.join(DATA_DIR, 'simples_nacional.xlsx')
        simples_nacional = pd.read_excel(simples_path, sheet_name='Dados Simples Nacional')
        anexo1 = simples_nacional.iloc[5:13, 0:5]
        aliquota_efetiva, desconto_mensal, desconto_anual = calcular_simples_nacional(receita_bruta_anual, anexo1)

        # Listas para armazenar resultados da análise de sensibilidade
        vpl_pot_fv = []

        # Loop para análise de sensibilidade do valor_recarga
        for pot_fv_2 in pot_fv_range:
            # (Recalcular todas as métricas relevantes com o novo valor de potência FV)

            #############################################################
            ## Cálculo do investimento inicial
            #############################################################
            invest_ini = input_data['num_eletropostos'] * input_data['preco_eletroposto'] + pot_fv_2 * \
                         input_data['preco_fv'] + input_data['implantacao']

            #############################################################
            ## Cálculo da geração de energia do sistema fotovoltaico
            #############################################################
            geracoes, eficiencia = calcular_geracao_fotovoltaica(input_data['vida_util'], pot_fv_2,
                                                                 input_data['h_inc'], input_data['pr'],
                                                                 input_data['perda_eficiencia_anual'])

            #############################################################
            # Cálculo do valor residual do sistema fotovoltaico
            #############################################################
            fator_residual_fv = 1 - input_data['vida_util'] / 25 - 0.2  # Considera-se uma perda imediata de 20% +
            # uma perda proporcional aos anos.
            valor_residual_fv = pot_fv_2 * input_data['preco_fv'] * fator_residual_fv  # Valor residual do sistema FV
            # a ser adicionado no último ano do fluxo de caixa

            #############################################################
            # Cálculo da fatura de energia
            #############################################################
            tarifa_energia_anos = [input_data['tarifa_energia']] * int(input_data['vida_util'])
            tusds = [input_data['tusd']] * int(input_data['vida_util'])

            # Calcular a fatura da concessionária para todos os anos
            fatura_energia, abatimento, creditos = calcular_fatura_4(geracoes, demanda, tarifa_energia_anos, tusds,
                                                                     input_data['fator_simult'],
                                                                     input_data['custo_disponibilidade'])

            #############################################################
            ## Cálculo de financiamento
            #############################################################
            if use_financing:
                valor_total_financiado = (input_data['perc_finan'] / 100) * invest_ini
                prestacoes = calcular_financiamento(valor_total_financiado, input_data['numero_prestacoes'],
                                                    input_data['taxa_juros_anual'],
                                                    input_data['tipo_financiamento'])

                meses = [i for i in range(input_data['numero_prestacoes'])]
                juros_mensais = [(prestacoes[i] - valor_total_financiado / input_data['numero_prestacoes']) for i in
                                 range(input_data['numero_prestacoes'])]
                amortizacao_mensal = [valor_total_financiado / input_data['numero_prestacoes'] for _ in
                                      range(input_data['numero_prestacoes'])]
            else:
                valor_total_financiado = 0.0
                prestacoes = list(np.zeros(input_data['numero_prestacoes']))

            #############################################################
            ## Cálculo do fluxo de caixa
            #############################################################
            invest_ini = invest_ini + 1  # O +1 é para não ter fluxo >= 0 no Ano 0 para não afetar o cálculo da TIR
            fluxo, financiamento = calcular_fluxo_de_caixa(receita_bruta_anual, desconto_anual, fatura_energia,
                                                           oper_manut, aluguel_ano, prestacoes, valor_total_financiado,
                                                           invest_ini, valor_residual_fv)

            #############################################################
            # Calcular o VPL
            vpl = npf.npv(input_data['tma'], fluxo)
            vpl_pot_fv.append(vpl)

        #############################################################

        # Encontrar a posição do maior valor de VPL
        posicao_max_vpl = np.argmax(vpl_pot_fv)

        # Encontrar o maior valor de VPL
        maior_vpl = vpl_pot_fv[posicao_max_vpl]
        result["Valor ótimo do VPL em R$"] = format_two_digits(maior_vpl)

        # Encontrar a potência correspondente usando a posição encontrada
        potencia_correspondente = pot_fv_range[posicao_max_vpl]
        result["Potência ótima do sistema fotovoltaico em kW"] = format_two_digits(potencia_correspondente)

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

        # Gerar as duas séries separadamente com cores diferentes
        result['pot_fv_range'] = list(map(format_two_digits, list(pot_fv_range)))
        result['vpl_positivo'] = vpl_positivo
        result['vpl_negativo'] = vpl_negativo

        return result
