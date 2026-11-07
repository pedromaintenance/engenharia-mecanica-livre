"""Ciclo 11: estudo de refinamento das larguras grandes e malha Gmsh externa."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def consolidar(base:str|Path,baseline_path:str|Path)->dict:
    root=Path(base)
    baseline=json.loads(Path(baseline_path).read_text(encoding="utf-8"))
    bench={(c['Ha'],c['nr']):c for c in baseline['cases']}
    width=[]
    for H in (8,16):
        cases=[]
        for n in (16,24,32):
            p=root/'chapa'/f'ha-{H}-n-{n}'/'comparacao.json'
            data=json.loads(p.read_text(encoding='utf-8'))
            inp=data['entrada'];out=data['resultado']
            if not math.isclose(inp['razao_semilargura_raio'],H,rel_tol=1e-10) or inp['nr']!=n:
                raise ValueError('Dados de largura/malha incompatíveis')
            kt=out['kt_gross_estimado_superficie']
            if not math.isfinite(kt) or not 2<kt<5:
                raise ValueError('Kt não finito ou fora do intervalo plausível')
            if not math.isclose(inp['carregamento_borda_quarto_n'],10e6*.005*.01*H,rel_tol=1e-6):
                raise ValueError('Forças externas inconsistentes')
            if n==24:
                previous=bench[H,24]['kt_gross']
                if abs(kt-previous)>5e-5:
                    raise ValueError('Regressão no baseline do ciclo 10')
            cases.append({'nr':n,'nt':2*n,'elementos':inp['elementos'],
                          'kt_gross_extrapolado':kt,
                          'kt_net_extrapolado':out['kt_net_estimado_superficie'],
                          'ajuste_local_residuo':out['residuo_ajuste_real'],
                          'tempo_s':data['tempo_solver_s']})
        width.append({
            'H_sobre_a':H,
            'casos':cases,
            'delta_Kt_absoluto_24_32':abs(cases[-1]['kt_gross_extrapolado']-cases[-2]['kt_gross_extrapolado']),
            'delta_Kt_relativo_24_32':abs(cases[-1]['kt_gross_extrapolado']-cases[-2]['kt_gross_extrapolado'])/abs(cases[-1]['kt_gross_extrapolado']),
        })
    gmsh=[]
    for H,n in ((4,16),(4,24),(8,24)):
        p=root/'gmsh'/f'ha-{H}-n-{n}'/'comparacao.json'
        data=json.loads(p.read_text(encoding='utf-8'))
        inp=data['entradas'];out=data['resultado']
        if inp['elementos']!=n*2*n or not math.isclose(inp['razao_semilargura_raio'],H,rel_tol=1e-10):
            raise ValueError('Malha Gmsh incompatível')
        k=out['kt_gross_estimado_superficie']
        native=bench[H,24]['kt_gross'] if n==24 else bench[4,16]['kt_gross']
        if not math.isfinite(k) or abs(k-native)>.25:
            raise ValueError(f'Diferença excessiva de Kt nativo/Gmsh H={H} n={n}: {k} vs {native}')
        gmsh.append({'H_sobre_a':H,'nr':n,'elementos':inp['elementos'],
                     'qualidade_min_jacobiano':inp['qualidade']['min_det_jacobiano_m2'],
                     'kt_gross_gmsh':k,'kt_gross_autoral_baseline':native,
                     'diferenca_absoluta':k-native,
                     'diferenca_relativa':(k-native)/native,
                     'bias_analitico_ajuste':out['bias_extrapolador_em_Kirsch'],
                     'pontos_extrapolacao':out['pontos_locais']})
    return {
        'modelo':'Ciclo_11_independent_gmsh_vs_autoral',
        'mesmo_solver':'CalculiX CCX 2.21-1',
        'geradores':['malha Q8 polar autoral','Gmsh CAD 2 blocos transfinite quad8'],
        'larguras_refinadas':width,
        'comparacao_gmsh':gmsh,
        'verificacao':'o mesmo solver e a mesma fisica nao constituem validacao por codigo independente',
        'limitacoes':[
            'Gmsh e gerador autoral criam malhas diferentes, com criterios de gradacao distintos',
            'Kt estimado por extrapolacao de tensoes de Gauss, nao medido diretamente no contorno',
            'A concordancia e erro relativo de discretizacao nao provam integridade de pinos ou olhais',
            'Valores de Kirsch aplicam-se a placa infinita, nao a chapa quadrada finita',
        ]
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--pasta',required=True)
    p.add_argument('--baseline',default='docs/dados/chapa-finita-furo-2026-11-07.json')
    a=p.parse_args()
    report=consolidar(a.pasta,a.baseline)
    out=Path(a.pasta)/'resumo_ciclo11.json'
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
