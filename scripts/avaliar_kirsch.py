"""Convergência e comparação de domínio de Kirsch — apenas resultados de solver."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path


def avaliar(root: str|Path, malhas: list[int]=(4,8,16)) -> dict:
    root=Path(root)
    if len(malhas)<3 or sorted(set(malhas))!=list(malhas):
        raise ValueError('Informar pelo menos 3 malhas crescentes')
    results=[]
    for n in malhas:
        path=root/f'n-{n}'/'comparacao.json'
        d=json.loads(path.read_text(encoding='utf-8'))
        p=d['resultado']; meta=d['entrada']
        if meta['nr']!=n or meta['nt']!=2*n or meta['razao_raios']!=8:
            raise ValueError('Caso de malha e raio incompatível')
        row={'nr':n,'nt':2*n,'elementos':meta['elementos'],'nos':meta['nos'],
             'min_det_jacobiano_m2':meta['qualidade_malha']['min_det_jacobiano_m2'],
             'tempo_solver_s':d['tempo_solver_s'],
             'erro_tensor_global_rel':p['erro_rms_tensor_rel'],
             'erro_tensor_global_ponderado_rel':p['erro_rms_tensor_ponderado_area_rel'],
             'erro_anel_fixo_1_5a_ponderado_rel':p['erro_rms_anel_fixo_1_5a_rel'],
             'erro_tensor_perto_furo_rel':p['erro_rms_proximo_furo_rel'],
             'kt_proxy_ip':p['kt_proxy_pontos_integracao'],
             'kt_analitico':p['kt_borda_analitico'],
             'pontos_gauss':p['pontos_integracao']}
        if not all(math.isfinite(x) for x in row.values()):
            raise ValueError('Saída não finita')
        results.append(row)
    e0=results[0]['erro_tensor_global_ponderado_rel']
    ef=results[-1]['erro_tensor_global_ponderado_rel']
    h0=results[0]['erro_anel_fixo_1_5a_ponderado_rel']
    hf=results[-1]['erro_anel_fixo_1_5a_ponderado_rel']
    if e0<=1e-8 or ef>=.85*e0:
        raise ValueError('Sem diminuição relevante do erro global de malha')
    if h0<=1e-8 or hf>=.85*h0:
        raise ValueError('Sem diminuição relevante do erro junto ao furo')
    if not 1.8<results[-1]['kt_proxy_ip']<3.3:
        raise ValueError('Proxy próximo ao bordo inconsistente com solução Kirsch')
    rate=[]
    for a,b in zip(results,results[1:]):
        if a['erro_tensor_global_ponderado_rel']>0 and b['erro_tensor_global_ponderado_rel']>0:
            rate.append(math.log(a['erro_tensor_global_ponderado_rel']/b['erro_tensor_global_ponderado_rel'])/
                        math.log(b['nr']/a['nr']))
        else:
            rate.append(None)
    comparison=None
    extra=root/'raio-4a'/'comparacao.json'
    if extra.exists():
        d=json.loads(extra.read_text(encoding='utf-8'))
        p=d['resultado']; m=d['entrada']
        if m['razao_raios']!=4 or m['nr']!=malhas[-1]:
            raise ValueError('Conjunto complementar incompatível')
        comparison={'razao_raios':4,'nr':m['nr'],'nt':m['nt'],
                    'erro_tensor_global_rel':p['erro_rms_tensor_rel'],
                    'erro_tensor_global_ponderado_rel':p['erro_rms_tensor_ponderado_area_rel'],
                    'erro_anel_fixo_1_5a_ponderado_rel':p['erro_rms_anel_fixo_1_5a_rel'],
                    'erro_tensor_perto_furo_rel':p['erro_rms_proximo_furo_rel'],
                    'kt_proxy_ip':p['kt_proxy_pontos_integracao'],
                    'comparacao_nao_e_efeito_de_bordas_fisicas':True}
    return {'modelo':'Kirsch_CPS8R_tensao_plana',
            'referencia':'Kirsch, dominio infinito; deslocamentos exatos na fronteira externa circular',
            'malhas':results,'taxas_aparentes_erro_tensor_ponderado':rate,'dominio_externo_4a':comparison,
            'alertas':(['O erro RMS da primeira camada aumenta na malha fina; sua faixa fisica muda com a malha']
                       if results[-1]['erro_tensor_perto_furo_rel']>results[-2]['erro_tensor_perto_furo_rel'] else []),
            'criterios':{'jacobianos_positivos':True,'erro_global_e_proximo_furo_reduzido':True,
                         'sem_fabricar_kt_na_borda':True,'prova_solver_externo_requerida':True},
            'caveat':'Não representa chapa finita com tração uniforme nas bordas; Kt=3 analítico, proxy interior não equivale a Kt no bordo'}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--pasta',required=True)
    p.add_argument('--malhas',nargs='+',type=int,default=[4,8,16])
    a=p.parse_args()
    report=avaliar(a.pasta,a.malhas)
    out=Path(a.pasta)/'resumo_kirsch.json'
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))


if __name__=='__main__':
    main()
