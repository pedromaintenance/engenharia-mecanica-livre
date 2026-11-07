"""Consolidação reproduzível de malhas e larguras da chapa finita."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def avaliar(root:str|Path)->dict:
    root=Path(root)
    cases=[]
    for H_a,n in [(4,8),(4,16),(4,24),(8,24),(16,24)]:
        path=root/f'h-{H_a}-n-{n}'/'comparacao.json'
        item=json.loads(path.read_text(encoding='utf-8'))
        inp=item["entrada"];out=item["resultado"]
        if abs(inp["razao_semilargura_raio"]-H_a)>1e-10 or inp["nr"]!=n or inp["nt"]!=2*n:
            raise ValueError(f'Case incorreto {path}')
        ratio=inp['relacao_diametro_largura']
        row={'H_sobre_a':H_a,'divisoes_radiais':n,'divisoes_angulares':2*n,
             'elementos':inp['elementos'],'nos':inp['nos'],
             'd_sobre_W':ratio,
             'Kt_gross_extrapolado':out['kt_gross_estimado_superficie'],
             'Kt_net_extrapolado':out['kt_net_estimado_superficie'],
             'Kt_proxy_Gauss':out['kt_interiores_primeira_camada'],
             'bias_extrapolador_em_Kirsch':out['bias_extrapolador_sobre_campo_kirsch_exato'],
             'residuo_ajuste_local':out['residuo_ajuste_real'],
             'carga_quarto_N':inp['carregamento_borda_quarto_n'],
             'tempo_s':item['tempo_solver_s']}
        if any(not math.isfinite(x) for x in row.values()):
            raise ValueError(f'Não finito em {path}')
        if not 1.5<row['Kt_gross_extrapolado']<6:
            raise ValueError(f'Extrapolação sem plausibilidade mecânica em {path}')
        if abs(row['Kt_net_extrapolado']-
               row['Kt_gross_extrapolado']*(1-ratio))>1e-9:
            raise ValueError('Conversão entre referência bruta e líquida incorreta')
        if abs(row['bias_extrapolador_em_Kirsch'])>.1:
            raise ValueError('Extrapolador não reproduz Kirsch sintético com precisão adequada')
        if abs(row['carga_quarto_N']-10e6*.005*H_a*.01)>.01:
            raise ValueError('Carga aplicada não corresponde à tração prescrita')
        cases.append(row)
    h4=[r for r in cases if r['H_sobre_a']==4]
    spread=max(x['Kt_gross_extrapolado'] for x in h4)-min(x['Kt_gross_extrapolado'] for x in h4)
    return {
        'modelo':'chapa_finita_furo_quadrada_tracao_real_CPS8R',
        'fonte_carga':'T=10 MPa nas bordas x=±H; bordas y=±H e furo livres',
        'referencia_gross':'Kt_gross=σ_pico/T',
        'referencia_net':'Kt_net=σ_pico/[T/(1-d/W)]',
        'tipo_estimativa':'extrapolação local dos pontos de integração de Gauss, não tensão de contorno medida diretamente',
        'casos':cases,
        'sensibilidade_malha_Ha4_spread_Kt_gross':spread,
        'criterios':{
            'solver_externo_real_obrigatorio':True,
            'malhas_fisicas_e_forcas_consistentes':True,
            'Kt_analitico_Kirsch_3_nao_e_solucao_exata_chapa_finita':True,
            'convergencia_assintotica_nao_determinada_pelo_spread':True,
        }
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--pasta',required=True)
    a=p.parse_args()
    r=avaliar(a.pasta)
    out=Path(a.pasta)/'resumo_chapa_finita.json'
    out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(r,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
