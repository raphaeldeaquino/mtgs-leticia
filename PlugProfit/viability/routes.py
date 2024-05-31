from flask import render_template, request
from PlugProfit.viability import bp
from .analysis import *


@bp.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        # Dados eletropostos

        # Número de eletropostos
        num_eletropostos = int(request.form.get('num_eletropostos')) if request.form.get('num_eletropostos') else 1

        # Potência do eletroposto kW
        pot_eletroposto = float(request.form.get('pot_eletroposto')) if request.form.get('pot_eletroposto') else 22

        # Recarga h/dia
        recarga_dia = int(request.form.get('recarga_dia')) if request.form.get('recarga_dia') else 6

        # Dados sistema fotovoltaico

        # Potência do sistema fotovoltaico (kW)
        pot_fv = int(request.form.get('pot_fv')) if request.form.get('pot_fv') else 125

        # Zomer (2014) - Horas de irradiação solar média por dia (irradiância kWh/m2.dia Cresesb dividido por 1kW/m2
        # que é a irradiância de referência)
        h_inc = float(request.form.get('h_inc')) if request.form.get('h_inc') else 5.45

        # Performance ratio
        pr = float(request.form.get('pr')) if request.form.get('pr') else 0.8

        # Perda de eficiência anual do sistema (em decimal)
        perda_eficiencia_anual = float(request.form.get('perda_eficiencia_anual')) \
            if request.form.get('perda_eficiencia_anual') else 0.016

        # Dados econômicos

        # Preço de cada eletroposto em R$
        preco_eletroposto = float(request.form.get('preco_eletroposto')) \
            if request.form.get('preco_eletroposto') else 120000.0

        # Preço do sistema fotovoltaico em R$/kWp
        preco_fv = float(request.form.get('preco_fv')) if request.form.get('preco_fv') else 5000.0

        # Outros custos de implantação em R$
        implantacao = float(request.form.get('implantacao')) if request.form.get('implantacao') else 30000.0

        # Valor da operação e manutenção por eletroposto em R$/ano
        o_e_m = float(request.form.get('o_e_m')) if request.form.get('o_e_m') else 10000.0

        # Valor da recarga R$/kWh
        valor_recarga = float(request.form.get('valor_recarga')) if request.form.get('valor_recarga') else 2.0

        # Valor da tarifa de energia com impostos em R$/kWh
        tarifa_energia = float(request.form.get('tarifa_energia')) if request.form.get('tarifa_energia') else 0.9

        # Taxa Mínima de Atratividade
        tma = float(request.form.get('tma')) if request.form.get('tma') else 0.1

        # Aluguel em R$/mês
        aluguel_mes = float(request.form.get('aluguel_mes')) if request.form.get('aluguel_mes') else 3000.0

        # Vida útil financeira do fluxo de caixa - vida útil dos eletropostos
        vida_util = int(request.form.get('vida_util')) if request.form.get('vida_util') else 10

        # Dados de financiamento

        # Percentual a ser financiado de 0 a 100%
        perc_finan = float(request.form.get('perc_finan')) if request.form.get('perc_finan') else 30

        # Número total de prestações em meses
        numero_prestacoes = int(request.form.get('numero_prestacoes')) if request.form.get('numero_prestacoes') else 12

        # Taxa de juros anual (em decimal)
        taxa_juros_anual = float(request.form.get('taxa_juros_anual')) / 100 if request.form.get('taxa_juros_anual') \
            else 0.05

        # Tipo de financiamento (price ou sac)
        tipo_financiamento = request.form.get('tipo_financiamento')

        opcao_selecionada = request.form.get('opcao_selecionada')

        # Sistema de compensação de energia elétrica
        tusd = 0.3
        fator_simult = 0.35             # Fator de simultaneidade entre consumo e geração
        custo_disponibilidade = 100     # Monofásico = 30 kWh; Bifásico = 50 kWh; Trifásico = 100 kWh.

        # Dados de sensibilidade
        valor_recarga_inicial = float(request.form.get('valor_recarga_inicial')) if request.form.get('valor_recarga_inicial')\
            else 0  # Valor inicial do range valor de recarga (R$)
        valor_recarga_final = float(request.form.get('valor_recarga_final')) if request.form.get('valor_recarga_final')\
            else 0  # Valor final do range valor de recarga (R$)
        recarga_dia_inicial = float(request.form.get('recarga_dia_inicial')) if request.form.get('recarga_dia_inicial')\
            else 0  # Valor inicial do range recarga por dia (h/dia)
        recarga_dia_final = float(request.form.get('recarga_dia_final')) if request.form.get('recarga_dia_final')\
            else 0  # Valor final do range recarga por dia (h/dia)
        pot_fv_inicial = float(request.form.get('pot_fv_inicial')) if request.form.get('pot_fv_inicial')\
            else 0  # Valor inicial do range potência do FV (kW)
        pot_fv_final = float(request.form.get('pot_fv_final')) if request.form.get('pot_fv_final')\
            else 0  # Valor final do range potência do FV (kW)
        show_hide_fotovoltaico = request.form.get('show_hide_fotovoltaico')
        show_hide_financiamento = request.form.get('show_hide_financiamento')

        input_data = {
            'num_eletropostos': num_eletropostos,
            'pot_eletroposto': pot_eletroposto,
            'recarga_dia': recarga_dia,
            'pot_fv': pot_fv,
            'h_inc': h_inc,
            'pr': pr,
            'perda_eficiencia_anual': perda_eficiencia_anual,
            'preco_eletroposto': preco_eletroposto,
            'preco_fv': preco_fv,
            'implantacao': implantacao,
            'o_e_m': o_e_m,
            'valor_recarga': valor_recarga,
            'tarifa_energia': tarifa_energia,
            'tma': tma,
            'aluguel_mes': aluguel_mes,
            'vida_util': vida_util,
            'perc_finan': perc_finan,
            'numero_prestacoes': numero_prestacoes,
            'taxa_juros_anual': taxa_juros_anual,
            'tipo_financiamento': tipo_financiamento,
            'tusd': tusd,
            'fator_simult': fator_simult,
            'custo_disponibilidade': custo_disponibilidade,
            'valor_recarga_inicial': valor_recarga_inicial,
            'valor_recarga_final': valor_recarga_final,
            'recarga_dia_inicial': recarga_dia_inicial,
            'recarga_dia_final': recarga_dia_final,
            'pot_fv_inicial': pot_fv_inicial,
            'pot_fv_final': pot_fv_final,
            'show_hide_fotovoltaico': show_hide_fotovoltaico,
            'show_hide_financiamento': show_hide_financiamento
        }

        result = calculate_viability(input_data, opcao_selecionada)
        input_data['pot_eletroposto'] = format_two_digits(input_data['pot_eletroposto'])
        input_data['pot_fv'] = format_two_digits(input_data['pot_fv'])
        input_data['h_inc'] = format_two_digits(input_data['h_inc'])
        input_data['pr'] = format_two_digits(input_data['pr'])
        input_data['perda_eficiencia_anual'] = format_two_digits(input_data['perda_eficiencia_anual'])
        input_data['preco_eletroposto'] = format_two_digits(input_data['preco_eletroposto'])
        input_data['preco_fv'] = format_two_digits(input_data['preco_fv'])
        input_data['implantacao'] = format_two_digits(input_data['implantacao'])
        input_data['o_e_m'] = format_two_digits(input_data['o_e_m'])
        input_data['valor_recarga'] = format_two_digits(input_data['valor_recarga'])
        input_data['tarifa_energia'] = format_two_digits(input_data['tarifa_energia'])
        input_data['tma'] = format_two_digits(input_data['tma'])
        input_data['aluguel_mes'] = format_two_digits(input_data['aluguel_mes'])
        input_data['perc_finan'] = format_two_digits(input_data['perc_finan'])
        input_data['taxa_juros_anual'] = format_two_digits(input_data['taxa_juros_anual'])
        input_data['valor_recarga_inicial'] = format_two_digits(input_data['valor_recarga_inicial'])
        input_data['valor_recarga_final'] = format_two_digits(input_data['valor_recarga_final'])

        result.update(input_data)

        return render_template('viability/result.html', result=result)

    return render_template('viability/index.html')
