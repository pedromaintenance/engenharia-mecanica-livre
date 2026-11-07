"""Chapa quadrada FINITA com furo e tração uniforme: FEM CPS8R em CalculiX.

Quarto de placa [-H,H]² com furo central de raio a, tensão plana elástica,
tração externa Tx=T apenas nas faces x=±H, y=±H livres, furo livre.
O campo de Kirsch NÃO é condição de contorno deste problema.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import time
from pathlib import Path

from .kirsch import jacobianos_q8, tensoes_kirsch


def positive(name: str, number: float) -> float:
    x=float(number)
    if not math.isfinite(x) or x<=0:
        raise ValueError(f"{name} deve ser finito e positivo")
    return x


def _square_radius(theta: float, halfwidth: float) -> float:
    return halfwidth/max(math.cos(theta),math.sin(theta))


def gerar_malha(*,nr:int=12,nt:int=24,raio_m:float=.01,
                semilargura_m:float=.04,graduacao:float=2.0)->dict:
    """Q8 polar mapeada: círculo no furo e contorno quadrado na borda.

    A direção de θ=π/4 coincide com uma linha de elementos; nenhum
    elemento cruza a descontinuidade de derivada do contorno quadrado.
    """
    if any(isinstance(v,bool) or not isinstance(v,int) for v in (nr,nt)):
        raise ValueError("nr e nt devem ser inteiros")
    if not 4<=nr<=48 or not 8<=nt<=96 or nt%4:
        raise ValueError("nr 4..48, nt múltiplo de 4 entre 8..96")
    a=positive("raio_m",raio_m)
    H=positive("semilargura_m",semilargura_m)
    g=positive("graduacao",graduacao)
    if H<3*a or g>3:
        raise ValueError("Exigir semilargura/raio >=3 e graduacao <=3")
    nodes={}
    labels={}
    def coordinate(i:float,theta:float):
        fraction=(i/nr)**g
        r=a+(_square_radius(theta,H)-a)*fraction
        x=r*math.cos(theta);y=r*math.sin(theta)
        return (0.0 if abs(x)<1e-14 else x,
                0.0 if abs(y)<1e-14 else y,0.0)
    def register(kind:str,i:int,j:int,pt):
        node=len(nodes)+1
        nodes[node]=pt
        labels[(kind,i,j)]=node
        return node
    for i in range(nr+1):
        for j in range(nt+1):
            register('v',i,j,coordinate(i,math.pi*j/(2*nt)))
    for i in range(nr):
        for j in range(nt+1):
            a0=nodes[labels['v',i,j]]
            a1=nodes[labels['v',i+1,j]]
            register('r',i,j,tuple((x+y)/2 for x,y in zip(a0,a1)))
    for i in range(nr+1):
        for j in range(nt):
            register('t',i,j,coordinate(i,math.pi*(j+.5)/(2*nt)))
    elements={}
    for i in range(nr):
        for j in range(nt):
            elements[len(elements)+1]=(
                labels['v',i,j],labels['v',i+1,j],
                labels['v',i+1,j+1],labels['v',i,j+1],
                labels['r',i,j],labels['t',i+1,j],
                labels['r',i,j+1],labels['t',i,j])
    right=[]
    for j in range(nt//2):
        right.append((
            labels['v',nr,j],
            labels['t',nr,j],
            labels['v',nr,j+1]
        ))
    top=[]
    for j in range(nt//2,nt):
        top.append((labels['v',nr,j],labels['t',nr,j],labels['v',nr,j+1]))
    sym_y=[labels['v',i,0] for i in range(nr+1)]+[
        labels['r',i,0] for i in range(nr)]
    sym_x=[labels['v',i,nt] for i in range(nr+1)]+[
        labels['r',i,nt] for i in range(nr)]
    hole=[labels['v',0,j] for j in range(nt+1)]+[
        labels['t',0,j] for j in range(nt)]
    mesh={'nodes':nodes,'elements':elements,
          'right_segments':right,'top_segments':top,
          'sym_x':sym_x,'sym_y':sym_y,'hole':hole}
    mesh['quality']=jacobianos_q8(mesh)
    for tri in right:
        if any(abs(nodes[n][0]-H)>2e-12 for n in tri):
            raise ValueError('Borda tracionada não é reta em x=H')
    for tri in top:
        if any(abs(nodes[n][1]-H)>2e-12 for n in tri):
            raise ValueError('Borda livre não é reta em y=H')
    return mesh


def _group_lines(values:list[int])->list[str]:
    return [", ".join(map(str,values[i:i+16])) for i in range(0,len(values),16)]


def montar_deck(*,nr:int=12,nt:int=24,raio_m:float=.01,
                 semilargura_m:float=.04,graduacao:float=2.0,
                 tensao_pa:float=10e6,e_gpa:float=200.0,
                 poisson:float=.3,espessura_m:float=.005)->tuple[str,dict]:
    """Carregamento Q8 de borda consistente para tração uniforme T."""
    T=positive('tensao_pa',tensao_pa)
    E=positive('e_gpa',e_gpa)*1e9
    thick=positive('espessura_m',espessura_m)
    nu=float(poisson)
    if not math.isfinite(nu) or not -0.49<nu<0.49:
        raise ValueError('Poisson fora do intervalo adotado')
    mesh=gerar_malha(nr=nr,nt=nt,raio_m=raio_m,
                     semilargura_m=semilargura_m,graduacao=graduacao)
    nodes=mesh['nodes']
    force={}
    # Para tração constante na aresta reta Q8:
    # integral dos pesos quadráticos = L*(1/6, 4/6, 1/6).
    for n1,nm,n2 in mesh['right_segments']:
        length=abs(nodes[n2][1]-nodes[n1][1])
        for node,weight in ((n1,1/6),(nm,4/6),(n2,1/6)):
            force[node]=force.get(node,0.0)+T*thick*length*weight
    F=sum(force.values())
    reference=T*thick*semilargura_m
    if not math.isclose(F,reference,rel_tol=2e-12,abs_tol=1e-6):
        raise ValueError("Carga total da borda direita incompatível com T*H*t")
    lines=[
        '** EML ciclo 10: finite square plate, free hole, uniform x-edge traction',
        f'** halfwidth={semilargura_m:g} hole_r={raio_m:g} T={T:g} Pa',
        '*NODE',
        *[f"{idx}, {x:.16g}, {y:.16g}, 0" for idx,(x,y,z) in nodes.items()],
        '*ELEMENT,TYPE=CPS8R,ELSET=EALL',
        *[f"{e}, "+", ".join(map(str,conn)) for e,conn in mesh['elements'].items()],
        '*NSET,NSET=RIGHT',*_group_lines(sorted(force)),
        '*NSET,NSET=HOLE',*_group_lines(mesh['hole']),
        '*MATERIAL,NAME=ELASTIC_ISOTROPIC','*ELASTIC',f'{E:.12g}, {nu:.12g}',
        '*SOLID SECTION,ELSET=EALL,MATERIAL=ELASTIC_ISOTROPIC',
        f'{thick:.12g}',
        '*STEP','*STATIC','*BOUNDARY',
        *[f'{n}, 1, 1, 0' for n in sorted(mesh['sym_x'])],
        *[f'{n}, 2, 2, 0' for n in sorted(mesh['sym_y'])],
        '*CLOAD',
        *[f'{n}, 1, {fn:.9g}' for n,fn in sorted(force.items()) if abs(fn)>1e-14],
        '*EL PRINT,ELSET=EALL,GLOBAL=YES','COORD,S',
        '*NODE PRINT,NSET=RIGHT','RF',
        '*END STEP'
    ]
    meta={
        'modelo':'chapa_quadrada_finita_furo_CPS8R',
        'condicao_contorno':'tracao_T_uniaxial_borda_x_H_topo_livre',
        'raio_m':raio_m,'semilargura_m':semilargura_m,
        'largura_total_m':2*semilargura_m,
        'razao_semilargura_raio':semilargura_m/raio_m,
        'relacao_diametro_largura':raio_m/semilargura_m,
        'nr':nr,'nt':nt,'graduacao':graduacao,
        'tensao_bruta_pa':T,
        'tensao_liquida_nominal_pa':T/(1-raio_m/semilargura_m),
        'e_pa':E,'poisson':nu,'espessura_m':thick,
        'elementos':len(mesh['elements']),'nos':len(nodes),
        'carregamento_borda_quarto_n':F,
        'carregamento_referencia_quarto_n':reference,
        'segmentos_borda_direita':len(mesh['right_segments']),
        'segmentos_borda_superior_livre':len(mesh['top_segments']),
        'qualidade_malha':mesh['quality'],
        'kt_kirsch_infinito_nao_e_referencia_exata_fisica':3.0,
        'numeros_gdl_restritos':len(mesh['sym_x'])+len(mesh['sym_y'])
    }
    return "\n".join(lines)+"\n",meta


def _parse_dat(text:str,meta:dict)->dict:
    """Importa S e COORD do arquivo .dat, exige 8 pontos/elemento."""
    records={'stress':{},'coord':{}}
    active=None
    for line in text.splitlines():
        low=line.strip().lower()
        if ' for set ' in low and ' and time ' in low:
            active=None
            if 'for set eall and time' in low:
                if low.startswith(('stress ','stresses ')):
                    active='stress'
                elif 'coord' in low:
                    active='coord'
            continue
        if active is None:
            continue
        tokens=line.split()
        need=8 if active=='stress' else 5
        if len(tokens)<need:
            continue
        try:
            key=(int(tokens[0]),int(tokens[1]))
            vals=tuple(float(v.replace('D','E').replace('d','E')) for v in tokens[2:need])
        except ValueError:
            continue
        if not all(math.isfinite(v) for v in vals):
            raise ValueError('Solver devolveu tensão ou coordenada não finita')
        if key in records[active]:
            raise ValueError('Ponto de integração duplicado')
        records[active][key]=vals
    expected=8*meta['elementos']
    if len(records['stress'])!=expected or set(records['stress'])!=set(records['coord']):
        raise ValueError(f'IP ausentes S/COORD: esperados={expected}, '
                         f"S={len(records['stress'])}, COORD={len(records['coord'])}")
    return records


def _solve_linear(a:list[list[float]],b:list[float])->list[float]:
    """Gauss com pivotamento para pequenos sistemas de mínimos quadrados."""
    n=len(b)
    rows=[a[i][:]+[b[i]] for i in range(n)]
    for c in range(n):
        p=max(range(c,n),key=lambda i:abs(rows[i][c]))
        if abs(rows[p][c])<1e-12:
            raise ValueError('Extrapolação de borda mal condicionada')
        rows[p],rows[c]=rows[c],rows[p]
        factor=rows[c][c]
        for j in range(c,n+1):
            rows[c][j]/=factor
        for i in range(n):
            if i==c:continue
            fac=rows[i][c]
            for j in range(c,n+1):
                rows[i][j]-=fac*rows[c][j]
    return [row[n] for row in rows]


def _extrapolar_superficie(pontos:list[tuple[float,float,float]],
                          *,raio_m:float,delta_r:float,delta_theta:float)->dict:
    """Estima Sθθ no ponto r=a, θ=π/2 por ajuste polinomial local.

    NÃO é leitura de tensão nodal nem medição direta no contorno.
    Ajuste local c0+c1*u+c2*u²+c3*v²+c4*u*v²+c5*v⁴.
    """
    n=6
    A=[[0.]*n for _ in range(n)]
    B=[0.]*n
    for r,theta,value in pontos:
        u=(r-raio_m)/delta_r
        v=(math.pi/2-theta)/delta_theta
        phi=[1.,u,u*u,v*v,u*v*v,v**4]
        for i in range(n):
            B[i]+=phi[i]*value
            for j in range(n):
                A[i][j]+=phi[i]*phi[j]
    if len(pontos)<n+4:
        raise ValueError('Amostras insuficientes para extrapolar borda')
    coefs=_solve_linear(A,B)
    rms=math.sqrt(sum((sum(c*p for c,p in zip(coefs,[
        1.,(r-raio_m)/delta_r,((r-raio_m)/delta_r)**2,
        ((math.pi/2-theta)/delta_theta)**2,
        ((r-raio_m)/delta_r)*((math.pi/2-theta)/delta_theta)**2,
        ((math.pi/2-theta)/delta_theta)**4]))-s)**2
        for r,theta,s in pontos)/len(pontos))
    return {'valor_extrapolado':coefs[0],'residuo_ajuste':rms,
            'amostras':len(pontos),
            'metodo':'ajuste local minimos quadrados 6 coeficientes; 3 aneis radiais x 3 celulas angulares'}


def analisar_tensoes(text:str,meta:dict)->dict:
    """Determina proxy interno e extrapolação de contorno com controle sintético."""
    rec=_parse_dat(text,meta)
    nr=meta['nr'];nt=meta['nt'];a=meta['raio_m'];H=meta['semilargura_m']
    T=meta['tensao_bruta_pa']
    delta_r=(H-a)*(1/nr)**meta['graduacao']
    delta_theta=math.pi/(2*nt)
    samples=[]
    analytic=[]
    interior=[]
    for (elem,ip),coords in rec['coord'].items():
        radial=(elem-1)//nt
        angular=(elem-1)%nt
        if radial>=3 or angular<nt-3:
            continue
        x,y,z=coords
        r=math.hypot(x,y);th=math.atan2(y,x)
        sxx,syy,szz,sxy,sxz,syz=rec['stress'][elem,ip]
        # Sigma_tt in Cartesian basis, normalized by T.
        sth=(sxx*math.sin(th)**2+syy*math.cos(th)**2
             -2*sxy*math.sin(th)*math.cos(th))/T
        ref=tensoes_kirsch(x,y,a,T)
        samples.append((r,th,sth))
        analytic.append((r,th,ref['sigma_tt_pa']/T))
        if radial==0:
            interior.append(sth)
    result=_extrapolar_superficie(samples,raio_m=a,delta_r=delta_r,delta_theta=delta_theta)
    chk=_extrapolar_superficie(analytic,raio_m=a,delta_r=delta_r,delta_theta=delta_theta)
    k_gross=result['valor_extrapolado']
    ratio=a/H
    return {
        'pontos_integracao_total':meta['elementos']*8,
        'pontos_locais':len(samples),
        'kt_gross_estimado_superficie':k_gross,
        'kt_net_estimado_superficie':k_gross*(1-ratio),
        'kt_interiores_primeira_camada':max(interior),
        'referencia_kirsch_infinita_kt_gross':3.,
        'bias_extrapolador_sobre_campo_kirsch_exato':chk['valor_extrapolado']-3.,
        'residuo_ajuste_real':result['residuo_ajuste'],
        'residuo_ajuste_kirsch_analitico':chk['residuo_ajuste'],
        'definicao_tensao_nominal_gross':'T, tracao uniforme aplicada nas bordas x=±H',
        'definicao_tensao_nominal_net':'T/(1-d/W), d/W=a/H',
        'aviso':'Estimativa por extrapolação de tensões de IP; requer refinamento de malha e comparação com literatura.'
    }


def executar(pasta:str|Path,*,nr:int=12,nt:int=24,solver:str|None=None,**kwargs)->dict:
    dest=Path(pasta).resolve()
    dest.mkdir(parents=True,exist_ok=True)
    deck,meta=montar_deck(nr=nr,nt=nt,**kwargs)
    job='chapa_finita_cps8r'
    (dest/(job+'.inp')).write_text(deck,encoding='utf-8')
    (dest/'entrada.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if solver is None:
        solver=next((s for s in ('ccx','ccx_2.21','ccx_2.22','ccx_2.23') if shutil.which(s)),None)
    if solver is None or not shutil.which(solver):
        raise RuntimeError('CalculiX indisponível; use --somente-gerar ou instale ccx')
    start=time.perf_counter()
    p=subprocess.run([solver,'-i',job],cwd=dest,text=True,capture_output=True,timeout=180)
    elapsed=time.perf_counter()-start
    (dest/'solver.log').write_text(p.stdout+'\n'+p.stderr,encoding='utf-8')
    dat=dest/(job+'.dat')
    if p.returncode or not dat.exists():
        raise RuntimeError(f'CalculiX falhou, exit={p.returncode}; '+(p.stdout+' '+p.stderr)[-1800:])
    result=analisar_tensoes(dat.read_text(encoding='utf-8',errors='replace'),meta)
    final={'modelo':'chapa_finita_cps8r_tracao_real','solver':shutil.which(solver),
           'tempo_solver_s':elapsed,'entrada':meta,'resultado':result}
    (dest/'comparacao.json').write_text(json.dumps(final,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return final


def main():
    p=argparse.ArgumentParser(description='Chapa quadrada finita com furo, tração uniforme')
    p.add_argument('--nr',type=int,default=12)
    p.add_argument('--nt',type=int,default=24)
    p.add_argument('--semilargura-m',type=float,default=.04)
    p.add_argument('--raio-m',type=float,default=.01)
    p.add_argument('--saida',required=True)
    p.add_argument('--somente-gerar',action='store_true')
    p.add_argument('--solver',default=None)
    args=p.parse_args()
    kw=dict(nr=args.nr,nt=args.nt,semilargura_m=args.semilargura_m,
            raio_m=args.raio_m)
    if args.somente_gerar:
        deck,meta=montar_deck(**kw)
        dest=Path(args.saida)
        dest.mkdir(parents=True,exist_ok=True)
        (dest/'chapa_finita_cps8r.inp').write_text(deck,encoding='utf-8')
        (dest/'entrada.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'gerado':str(dest),'entrada':meta},indent=2,ensure_ascii=False))
    else:
        print(json.dumps(executar(args.saida,solver=args.solver,**kw),indent=2,ensure_ascii=False))


if __name__=='__main__':
    main()
