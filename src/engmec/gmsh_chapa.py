"""Gmsh independente para chapa finita: dois blocos Q8 transfinite.

Gera .geo, executa gmsh CLI, importa MSH2 quad8 (tipo16) e compara
com modelo CPS8R de chapa_finita, sem usar gerador de malha do projeto.
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import time
from pathlib import Path

from .chapa_finita import (_group_lines, _parse_dat, _extrapolar_superficie,
                            positive)
from .kirsch import jacobianos_q8, tensoes_kirsch


def gerar_geo(*,raio_m:float=.01,semilargura_m:float=.04,nr:int=24,
              nt:int=48,progressao:float=1.12)->str:
    a=positive("raio",raio_m)
    H=positive("semilargura",semilargura_m)
    q=positive("progressao",progressao)
    if H<3*a or not (1<=q<=1.3):
        raise ValueError("H/a >=3 e progressao em [1,1.3]")
    if any(isinstance(n,bool) or not isinstance(n,int) for n in (nr,nt)):
        raise ValueError("nr,nt devem ser inteiros")
    if nr<4 or nr>48 or nt<8 or nt>96 or nt%4:
        raise ValueError("nr 4..48, nt 8..96 multiplo de 4")
    return f"""// Modelo alternativo de chapa com furo, gerado pelo Gmsh CAD
// Base fisica: quadrante de chapa quadrada com furo, nao Kirsch truncado
Mesh.MshFileVersion = 2.2;
Mesh.ElementOrder = 2;
Mesh.SecondOrderIncomplete = 1;
Mesh.RecombineAll = 1;
Mesh.Smoothing = 5;
a = {a:.12g}; H = {H:.12g};
q = {q:.12g}; Nr = {nr}; Na = {nt//2};
// Nos geometricos: furo 1,2,3; limites 4,5,6; centro 7
Point(1) = {{ a,0,0,1 }};
Point(2) = {{ a/Sqrt(2),a/Sqrt(2),0,1 }};
Point(3) = {{ 0,a,0,1 }};
Point(4) = {{ H,0,0,1 }};
Point(5) = {{ H,H,0,1 }};
Point(6) = {{ 0,H,0,1 }};
Point(7) = {{ 0,0,0,1 }};
// Bloco 1: theta 0 a 45 graus
Line(1) = {{1,4}};
Line(2) = {{4,5}};
Line(3) = {{5,2}};
Circle(4) = {{2,7,1}};
Curve Loop(1) = {{1,2,3,4}};
Plane Surface(1) = {{1}};
// Bloco 2: theta 45 a 90 graus
Line(5) = {{5,6}};
Line(6) = {{6,3}};
Circle(7) = {{3,7,2}};
Curve Loop(2) = {{-3,5,6,7}};
Plane Surface(2) = {{2}};
// Progressao radial: menor elemento no bordo do furo
Transfinite Curve {{1,-3,-6}} = Nr+1 Using Progression q;
Transfinite Curve {{2,4,5,7}} = Na+1;
Transfinite Surface {{1}} = {{1,4,5,2}};
Transfinite Surface {{2}} = {{2,5,6,3}};
Recombine Surface {{1,2}};
"""


def importar_msh2(texto:str,*,a:float,H:float,nr:int,nt:int)->dict:
    lines=texto.splitlines()
    def section(name:str):
        start=f'${name}';stop=f'$End{name}'
        try:
            i=lines.index(start)
            j=lines.index(stop,i+1)
        except ValueError as exc:
            raise ValueError(f"Seção MSH2 ausente: {name}") from exc
        return lines[i+1:j]
    fmt=section("MeshFormat")
    if not fmt or not fmt[0].startswith("2.2 "):
        raise ValueError("MSH v2.2 ASCII necessário")
    raw_nodes=section("Nodes")
    nn=int(raw_nodes[0])
    if len(raw_nodes)-1!=nn:
        raise ValueError("Contagem de nós MSH incompatível")
    nodes={}
    for line in raw_nodes[1:]:
        values=line.split()
        if len(values)!=4:
            raise ValueError("Linha de nó MSH inválida")
        idx=int(values[0])
        xyz=tuple(float(x) for x in values[1:])
        if any(not math.isfinite(v) for v in xyz) or idx in nodes:
            raise ValueError("Nó duplicado ou não finito")
        x,y,z=xyz
        nodes[idx]=(0.0 if abs(x)<1e-13 else x,
                    0.0 if abs(y)<1e-13 else y,0.0 if abs(z)<1e-13 else z)
    raw_elements=section("Elements")
    if len(raw_elements)-1!=int(raw_elements[0]):
        raise ValueError("Contagem de elementos MSH incompatível")
    quads={}
    edges=[]
    other_surface_types=set()
    for line in raw_elements[1:]:
        values=[int(x) for x in line.split()]
        if len(values)<3:
            raise ValueError("Elemento MSH inválido")
        _,etype,ntags=values[:3]
        data=values[3+ntags:]
        if etype==16:
            if len(data)!=8:
                raise ValueError("Quad8 necessita 8 nós")
            quads[len(quads)+1]=tuple(data)
        elif etype==8:
            if len(data)!=3:
                raise ValueError("Segmento quadrático necessita 3 nós")
            edges.append(tuple(data))
        elif etype in (2,3,9,10,15):
            if etype!=15:
                other_surface_types.add(etype)
        else:
            raise ValueError(f"Tipo MSH não suportado: {etype}")
    if not quads or other_surface_types or len(quads)!=nr*nt:
        raise ValueError(f"Somente quad8 esperado: {len(quads)} quadrilateros, tipos={other_surface_types}, esperado={nr*nt}")
    if any(any(n not in nodes for n in conn) for conn in quads.values()):
        raise ValueError("Conectividade contém nó desconhecido")
    right=[];top=[];hole=[]
    for n1,n2,nmid in edges:
        xyz=[nodes[n] for n in (n1,nmid,n2)]
        if all(abs(p[0]-H)<2e-9 for p in xyz):
            right.append((n1,nmid,n2))
        elif all(abs(p[1]-H)<2e-9 for p in xyz):
            top.append((n1,nmid,n2))
        elif all(abs(math.hypot(p[0],p[1])-a)<2e-9 for p in xyz):
            hole.append((n1,nmid,n2))
    if len(right)!=nt//2 or len(top)!=nt//2 or len(hole)!=nt:
        raise ValueError(f"Contornos incompletos right={len(right)},top={len(top)},hole={len(hole)}")
    cset={n for conn in quads.values() for n in conn[:4]}
    radial=sorted(set(round(nodes[n][1],12) for n in cset
                      if abs(nodes[n][0])<1e-12 and nodes[n][1]>=a-1e-12))
    angular=sorted(set(round(math.atan2(nodes[n][1],nodes[n][0]),12) for n in cset
                       if abs(math.hypot(*nodes[n][:2])-a)<2e-9))
    if len(radial)!=nr+1 or len(angular)!=nt+1:
        raise ValueError(f"Rings invalid: radial={len(radial)}, angular={len(angular)}")
    symmetry_x=sorted(n for n,(x,y,z) in nodes.items() if abs(x)<1e-12)
    symmetry_y=sorted(n for n,(x,y,z) in nodes.items() if abs(y)<1e-12)
    if not symmetry_x or not symmetry_y:
        raise ValueError("Eixos de simetria ausentes")
    quality=jacobianos_q8({'nodes':nodes,'elements':quads})
    return {'nodes':nodes,'elements':quads,'right_edges':right,
            'top_edges':top,'hole_edges':hole,
            'symmetry_x':symmetry_x,'symmetry_y':symmetry_y,
            'radial_levels':radial,'angular_levels':angular,
            'quality':quality}


def montar_deck(mesh:dict,*,nr:int=24,nt:int=48,raio_m:float=.01,
                 semilargura_m:float=.04,tensao_pa:float=10e6,
                 espessura_m:float=.005,e_gpa:float=200,poisson:float=.3)->tuple[str,dict]:
    a=positive("raio",raio_m)
    H=positive("H",semilargura_m)
    T=positive("T",tensao_pa)
    thickness=positive("espessura",espessura_m)
    E=positive("E",e_gpa)*1e9
    nu=float(poisson)
    if not math.isfinite(nu) or not -.49<nu<.49:
        raise ValueError("Poisson inválido")
    forces={}
    for n1,nmid,n2 in mesh['right_edges']:
        length=abs(mesh['nodes'][n2][1]-mesh['nodes'][n1][1])
        for node,factor in ((n1,1/6),(nmid,4/6),(n2,1/6)):
            forces[node]=forces.get(node,0)+T*thickness*length*factor
    resultant=sum(forces.values())
    if not math.isclose(resultant,T*thickness*H,rel_tol=1e-10,abs_tol=1e-6):
        raise ValueError("Tração integrada não conserva T*H*t")
    nodes=mesh['nodes']
    lines=[
        '** Imported independent Gmsh transfinite quad8 mesh; CPS8R CalculiX',
        '*NODE',
        *[f'{idx}, {x:.16g}, {y:.16g}, {z:.16g}'
          for idx,(x,y,z) in sorted(nodes.items())],
        '*ELEMENT,TYPE=CPS8R,ELSET=EALL',
        *[f'{e}, '+", ".join(map(str,conn))
          for e,conn in mesh['elements'].items()],
        '*NSET,NSET=RIGHT',*_group_lines(sorted(forces)),
        '*MATERIAL,NAME=ELASTIC_ISOTROPIC','*ELASTIC',
        f'{E:.12g}, {nu:.12g}',
        '*SOLID SECTION,ELSET=EALL,MATERIAL=ELASTIC_ISOTROPIC',
        f'{thickness:.12g}',
        '*STEP','*STATIC','*BOUNDARY',
        *[f'{node},1,1,0' for node in mesh['symmetry_x']],
        *[f'{node},2,2,0' for node in mesh['symmetry_y']],
        '*CLOAD',
        *[f'{node},1,{force:.9g}' for node,force in sorted(forces.items()) if abs(force)>1e-14],
        '*EL PRINT,ELSET=EALL,GLOBAL=YES','COORD,S',
        '*NODE PRINT,NSET=RIGHT','RF','*END STEP'
    ]
    meta={
        'modelo':'chapa_finita_gmsh_quad8_CPS8R',
        'gerador':'Gmsh CAD transfinite 2 blocos, independente de malha polar autoral',
        'nr':nr,'nt':nt,'elementos':len(mesh['elements']),'nos':len(nodes),
        'raio_m':a,'semilargura_m':H,
        'razao_semilargura_raio':H/a,
        'e_pa':E,'poisson':nu,'espessura_m':thickness,
        'tensao_bruta_pa':T,'tensao_liquida_nominal_pa':T/(1-a/H),
        'resultante_borda_quarto_n':resultant,
        'qualidade':mesh['quality'],
        'radial_levels_m':mesh['radial_levels'],
        'angular_levels_rad':mesh['angular_levels']
    }
    return "\n".join(lines)+"\n",meta


def avaliar_dat(dat:str,meta:dict)->dict:
    """Mesmo ajuste local de 6 coeficientes do modelo autoral.

    Seleção de Gauss independente dos IDs de elemento Gmsh, via localização
    nas três primeiras faixas radiais e três células angulares do furo.
    """
    rec=_parse_dat(dat,meta)
    a,H=meta['raio_m'],meta['semilargura_m']
    nr,nt=meta['nr'],meta['nt']
    radius_levels=meta['radial_levels_m']
    angles=meta['angular_levels_rad']
    r_max=radius_levels[3]
    radial_fraction=(r_max-a)/(H-a)
    dr=radius_levels[1]-a
    dtheta=angles[-1]-angles[-2]
    limit_angle=angles[-4]
    if dr<=0 or dtheta<=0:
        raise ValueError("Faixas de extrapolação inválidas")
    entries=[];refs=[];internal=[]
    for key,xyz in rec['coord'].items():
        x,y,z=xyz
        theta=math.atan2(y,x)
        rr=math.hypot(x,y)
        r_outer=H/max(math.cos(theta),math.sin(theta))
        alpha=(rr-a)/(r_outer-a)
        if theta<limit_angle-1e-8 or alpha>radial_fraction+1e-8:
            continue
        sxx,syy,szz,sxy,sxz,syz=rec['stress'][key]
        sigtt=(sxx*math.sin(theta)**2+syy*math.cos(theta)**2-
               2*sxy*math.sin(theta)*math.cos(theta))/meta['tensao_bruta_pa']
        ref=tensoes_kirsch(x,y,a,meta['tensao_bruta_pa'])
        entries.append((rr,theta,sigtt))
        refs.append((rr,theta,ref['sigma_tt_pa']/meta['tensao_bruta_pa']))
        if alpha < (radius_levels[1]-a)/(H-a)+1e-9:
            internal.append(sigtt)
    if not internal:
        raise ValueError("Primeira camada junto ao furo sem pontos de Gauss")
    fit=_extrapolar_superficie(entries,raio_m=a,delta_r=dr,delta_theta=dtheta)
    synthetic=_extrapolar_superficie(refs,raio_m=a,delta_r=dr,delta_theta=dtheta)
    if abs(synthetic['valor_extrapolado']-3)>0.1:
        raise ValueError("Ajuste não reproduz o Kirsch analítico")
    gross=fit['valor_extrapolado']
    return {
        'pontos_integracao_total':meta['elementos']*8,
        'pontos_locais':len(entries),
        'kt_gross_estimado_superficie':gross,
        'kt_net_estimado_superficie':gross*(1-a/H),
        'kt_interiores_primeira_camada':max(internal),
        'bias_extrapolador_em_Kirsch':synthetic['valor_extrapolado']-3.,
        'residuo_ajuste_local':fit['residuo_ajuste'],
        'residuo_kirsch':synthetic['residuo_ajuste'],
        'aviso':'Estimativa de tensao superficial a partir de Gauss, nao valor nodal medido'
    }


def executar(out_dir:str|Path,*,nr:int=24,nt:int=48,raio_m:float=.01,
             semilargura_m:float=.04,progressao:float=1.12,
             gmsh_exe:str="gmsh",ccx_exe:str="ccx")->dict:
    if not shutil.which(gmsh_exe):
        raise RuntimeError("Gmsh indisponível: instalar gmsh para execução")
    if not shutil.which(ccx_exe):
        raise RuntimeError("CalculiX indisponível: instalar calculix-ccx para execução")
    dest=Path(out_dir).resolve()
    dest.mkdir(parents=True,exist_ok=True)
    geo=gerar_geo(raio_m=raio_m,semilargura_m=semilargura_m,
                  nr=nr,nt=nt,progressao=progressao)
    (dest/'chapa_gmsh.geo').write_text(geo,encoding='utf-8')
    start=time.perf_counter()
    p=subprocess.run([gmsh_exe,"chapa_gmsh.geo","-2","-order","2","-format","msh2",
                      "-o","chapa_gmsh.msh"],cwd=dest,capture_output=True,text=True,timeout=120)
    (dest/'gmsh.log').write_text(p.stdout+'\n'+p.stderr,encoding='utf-8')
    if p.returncode:
        raise RuntimeError("Gmsh falhou: "+(p.stdout+'\n'+p.stderr)[-2400:])
    mesh=importar_msh2((dest/'chapa_gmsh.msh').read_text(encoding='utf-8'),
                      a=raio_m,H=semilargura_m,nr=nr,nt=nt)
    deck,meta=montar_deck(mesh,nr=nr,nt=nt,raio_m=raio_m,
                          semilargura_m=semilargura_m)
    (dest/'chapa_gmsh_cps8r.inp').write_text(deck,encoding='utf-8')
    (dest/'entrada.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    ccx=subprocess.run([ccx_exe,'-i','chapa_gmsh_cps8r'],cwd=dest,
                       capture_output=True,text=True,timeout=180)
    (dest/'solver.log').write_text(ccx.stdout+'\n'+ccx.stderr,encoding='utf-8')
    dat=dest/'chapa_gmsh_cps8r.dat'
    if ccx.returncode or not dat.exists():
        raise RuntimeError("CCX sobre malha Gmsh falhou: "+(ccx.stdout+'\n'+ccx.stderr)[-2400:])
    result=avaliar_dat(dat.read_text(encoding='utf-8',errors='replace'),meta)
    report={'modelo':'chapa_finita_CPS8R_com_malha_externa_Gmsh',
            'tempo_gmsh_mais_ccx_s':time.perf_counter()-start,
            'entradas':meta,'resultado':result}
    (dest/'comparacao.json').write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return report


def main():
    p=argparse.ArgumentParser(description="Chapa finita: malha independente Gmsh")
    p.add_argument('--nr',type=int,default=24)
    p.add_argument('--nt',type=int,default=48)
    p.add_argument('--semilargura-m',type=float,default=.04)
    p.add_argument('--raio-m',type=float,default=.01)
    p.add_argument('--progressao',type=float,default=1.12)
    p.add_argument('--saida',required=True)
    p.add_argument('--somente-geo',action='store_true')
    args=p.parse_args()
    if args.somente_geo:
        dest=Path(args.saida)
        dest.mkdir(parents=True,exist_ok=True)
        (dest/'chapa_gmsh.geo').write_text(
            gerar_geo(nr=args.nr,nt=args.nt,raio_m=args.raio_m,
                      semilargura_m=args.semilargura_m,progressao=args.progressao),
            encoding='utf-8')
        print(f'Arquivo Gmsh criado em {dest}/chapa_gmsh.geo')
    else:
        result=executar(args.saida,nr=args.nr,nt=args.nt,raio_m=args.raio_m,
                        semilargura_m=args.semilargura_m,progressao=args.progressao)
        print(json.dumps(result,indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
