"""Benchmark autoral de Kirsch com elementos CPS8R e malha anular de quarto de placa.

Modelo de elasticidade isotrópica em tensão plana, furo sem tração,
deslocamentos analíticos prescritos no contorno externo. SI: N, m, Pa.
Sem dependência de Gmsh, NumPy ou solver para gerar o deck.
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


def _positive(name: str, value: float) -> float:
    x = float(value)
    if not math.isfinite(x) or x <= 0:
        raise ValueError(f"{name}: esperado número positivo e finito")
    return x


def tensoes_kirsch(x: float, y: float, raio_m: float, tensao_pa: float) -> dict[str, float]:
    """Tensões exatas de Kirsch sob tração sigma_infinito orientada no eixo x."""
    a = _positive("raio_m", raio_m)
    T = _positive("tensao_pa", tensao_pa)
    r = math.hypot(x, y)
    if r < a*(1 - 1e-11):
        raise ValueError("Ponto interno ao furo")
    th = math.atan2(y, x)
    c, s = math.cos(th), math.sin(th)
    q = a/r
    co, si = math.cos(2*th), math.sin(2*th)
    rr = T/2*(1-q*q) + T/2*(1-4*q*q+3*q**4)*co
    tt = T/2*(1+q*q) - T/2*(1+3*q**4)*co
    rt = -T/2*(1+2*q*q-3*q**4)*si
    return {
        "r_m":r, "theta_rad":th,
        "sigma_rr_pa":rr, "sigma_tt_pa":tt, "sigma_rt_pa":rt,
        "sigma_xx_pa":rr*c*c+tt*s*s-2*rt*c*s,
        "sigma_yy_pa":rr*s*s+tt*c*c+2*rt*c*s,
        "sigma_xy_pa":(rr-tt)*s*c+rt*(c*c-s*s)
    }


def deslocamentos_kirsch(x: float, y: float, raio_m: float, tensao_pa: float,
                          e_pa: float, poisson: float) -> tuple[float,float]:
    """Solução exata em tensão plana via potenciais de Kolosov/Muskhelishvili.

    A expressão de deformação plana está publicada no benchmark Coreform;
    para tensão plana substitui-se kappa=(3-nu)/(1+nu), G=E/(2(1+nu)).
    """
    a=_positive("raio_m",raio_m)
    T=_positive("tensao_pa",tensao_pa)
    E=_positive("e_pa",e_pa)
    nu=float(poisson)
    if not math.isfinite(nu) or not -0.49<nu<0.49:
        raise ValueError("poisson fora do domínio de elasticidade adotado")
    r=math.hypot(x,y)
    if r<a*(1-1e-11):
        raise ValueError("Ponto dentro do furo")
    th=math.atan2(y,x)
    kappa=(3-nu)/(1+nu)
    mu=E/(2*(1+nu))
    q=a/r
    fac=T*a/(8*mu)
    ux=fac*((r/a)*(kappa+1)*math.cos(th)
            +2*q*((kappa+1)*math.cos(th)+math.cos(3*th))
            -2*q**3*math.cos(3*th))
    uy=fac*((r/a)*(kappa-3)*math.sin(th)
            +2*q*((1-kappa)*math.sin(th)+math.sin(3*th))
            -2*q**3*math.sin(3*th))
    return ux,uy


def criar_malha(*, nr: int=8, nt: int=16, raio_m: float=0.01,
                 raio_externo_m: float=0.08, graduacao: float=2.0) -> tuple[dict,dict]:
    """Malha isoparamétrica CPS8R no primeiro quadrante; arcos quadráticos.

    Quatro pontos de integração em XY, expandidos internamente em oito no CCX.
    """
    if any(isinstance(n,bool) or not isinstance(n,int) for n in (nr,nt)):
        raise ValueError("nr e nt devem ser inteiros")
    if not (3<=nr<=40 and 6<=nt<=128):
        raise ValueError("nr entre 3..40 e nt entre 6..128")
    a=_positive("raio_m",raio_m)
    R=_positive("raio_externo_m",raio_externo_m)
    grad=_positive("graduacao",graduacao)
    if not (R>=3*a and grad<=4):
        raise ValueError("raio externo >=3a e graduacao <=4 obrigatórios")
    radii=[a+(R-a)*(i/nr)**grad for i in range(nr+1)]
    angles=[(math.pi/2)*j/nt for j in range(nt+1)]
    nodes={}
    labels={}
    def add(kind, i, j, rr, th):
        ident=len(nodes)+1
        nodes[ident]=(rr*math.cos(th),rr*math.sin(th),0.0)
        labels[(kind,i,j)]=ident
        return ident
    for i in range(nr+1):
        for j in range(nt+1):
            add('v',i,j,radii[i],angles[j])
    for i in range(nr):
        for j in range(nt+1):
            add('r',i,j,(radii[i]+radii[i+1])/2,angles[j])
    for i in range(nr+1):
        for j in range(nt):
            add('t',i,j,radii[i],(angles[j]+angles[j+1])/2)
    elements={}
    for i in range(nr):
        for j in range(nt):
            elements[len(elements)+1]=(
                labels['v',i,j],labels['v',i+1,j],
                labels['v',i+1,j+1],labels['v',i,j+1],
                labels['r',i,j],labels['t',i+1,j],
                labels['r',i,j+1],labels['t',i,j]
            )
    outer=[labels['v',nr,j] for j in range(nt+1)]+[
        labels['t',nr,j] for j in range(nt)]
    sym_y=[labels['v',i,0] for i in range(nr)]+[
        labels['r',i,0] for i in range(nr)]
    sym_x=[labels['v',i,nt] for i in range(nr)]+[
        labels['r',i,nt] for i in range(nr)]
    hole=[labels['v',0,j] for j in range(nt+1)]+[
        labels['t',0,j] for j in range(nt)]
    return {"nodes":nodes,"elements":elements,"outer":outer,
            "sym_x":sym_x,"sym_y":sym_y,"hole":hole,
            "radii":radii,"angles":angles}, labels


def jacobianos_q8(mesh: dict) -> dict[str, float]:
    """Jacobiano 2D Q8 em quatro pontos de Gauss por elemento."""
    points=(-1/math.sqrt(3),1/math.sqrt(3))
    values=[]
    xyz=mesh['nodes']
    for conn in mesh['elements'].values():
        x=[xyz[n][0] for n in conn]
        y=[xyz[n][1] for n in conn]
        for r in points:
            for s in points:
                dr=(
                    (1-s)*(2*r+s)/4,
                    (1-s)*(2*r-s)/4,
                    (1+s)*(2*r+s)/4,
                    (1+s)*(2*r-s)/4,
                    -r*(1-s),
                    (1-s*s)/2,
                    -r*(1+s),
                    -(1-s*s)/2
                )
                ds=(
                    (1-r)*(r+2*s)/4,
                    (1+r)*(-r+2*s)/4,
                    (1+r)*(r+2*s)/4,
                    (1-r)*(-r+2*s)/4,
                    -(1-r*r)/2,
                    -(1+r)*s,
                    (1-r*r)/2,
                    -(1-r)*s
                )
                dxr=sum(a*b for a,b in zip(dr,x))
                dys=sum(a*b for a,b in zip(ds,y))
                dxs=sum(a*b for a,b in zip(ds,x))
                dyr=sum(a*b for a,b in zip(dr,y))
                J=dxr*dys-dxs*dyr
                if not math.isfinite(J) or J<=0:
                    raise ValueError('Elemento Q8 degenerado ou com jacobiano não positivo')
                values.append(J)
    return {'min_det_jacobiano_m2':min(values),'max_det_jacobiano_m2':max(values),
            'pontos_jacobiano':len(values)}


def montar_deck(*,nr:int=8,nt:int=16,raio_m:float=.01,raio_externo_m:float=.08,
                 graduacao:float=2.0,tensao_pa:float=10e6,e_gpa:float=200,
                 poisson:float=.3,espessura_m:float=.005) -> tuple[str,dict]:
    """Quarto de anel, furo livre e deslocamento de Kirsch no arco externo.

    Essa condição externa exata NÃO equivale a tensão uniforme aplicada
    em borda de chapa de largura finita.
    """
    T=_positive("tensao_pa",tensao_pa)
    E=_positive("e_gpa",e_gpa)*1e9
    thickness=_positive("espessura_m",espessura_m)
    nu=float(poisson)
    if not math.isfinite(nu) or not -0.49<nu<0.49:
        raise ValueError("poisson inválido")
    mesh,_=criar_malha(nr=nr,nt=nt,raio_m=raio_m,
                      raio_externo_m=raio_externo_m,graduacao=graduacao)
    nodes,elements=mesh["nodes"],mesh["elements"]
    qualidade=jacobianos_q8(mesh)
    lines=["** Engenharia Mecanica Livre - kirsch CPS8R plane stress",
           "** Kirsch exact outer displacement, symmetry axes, free hole",
           "*NODE"]
    lines += [f"{n}, {x:.16g}, {y:.16g}, {z:.16g}"
              for n,(x,y,z) in nodes.items()]
    lines.append("*ELEMENT,TYPE=CPS8R,ELSET=EALL")
    lines += [f"{elem}, "+", ".join(map(str,conn))
              for elem,conn in elements.items()]
    def nset_lines(values):
        return [", ".join(map(str,values[i:i+16])) for i in range(0,len(values),16)]
    lines += ["*NSET,NSET=OUTER",*nset_lines(mesh["outer"]),
              "*NSET,NSET=HOLE",*nset_lines(mesh["hole"]),
              "*MATERIAL,NAME=ELASTIC_ISOTROPIC", "*ELASTIC", f"{E:.16g}, {nu:.16g}",
              "*SOLID SECTION,ELSET=EALL,MATERIAL=ELASTIC_ISOTROPIC",
              f"{thickness:.16g}","*STEP","*STATIC","*BOUNDARY"]
    constraints={}
    for n in mesh['sym_x']:
        constraints[n,1]=0.0
    for n in mesh['sym_y']:
        constraints[n,2]=0.0
    for n in mesh['outer']:
        x,y,_=nodes[n]
        ux,uy=deslocamentos_kirsch(x,y,raio_m,T,E,nu)
        constraints[n,1]=0 if abs(ux)<1e-16 else ux
        constraints[n,2]=0 if abs(uy)<1e-16 else uy
    for (node,dof),val in sorted(constraints.items()):
        lines.append(f"{node}, {dof}, {dof}, {val:.9g}")
    lines += ["*EL PRINT,ELSET=EALL,GLOBAL=YES","COORD,S",
              "*NODE PRINT,NSET=OUTER","RF", "*END STEP"]
    meta={
        "elemento":"CPS8R","modelo":"kirsch_quarto_anel_tensao_plana",
        "bc_externa":"deslocamentos_analiticos_kirsch",
        "raio_m":float(raio_m),"raio_externo_m":float(raio_externo_m),
        "razao_raios":float(raio_externo_m/raio_m),
        "nr":nr,"nt":nt,"graduacao":graduacao,
        "elementos":len(elements),"nos":len(nodes),
        "nos_furo":len(mesh["hole"]),"nos_externos":len(mesh["outer"]),
        "e_pa":E,"poisson":nu,"espessura_m":thickness,
        "tensao_remota_pa":T,"kt_exato_borda":3.0,
        "kt_estimado_ip_nao_e_kt_borda":True,
        "primeira_camada_m":mesh["radii"][1]-mesh["radii"][0],
        "restricoes_dof":len(constraints),
        "qualidade_malha":qualidade
    }
    return "\n".join(lines)+"\n",meta


_HDR = re.compile(r"for set\s+eall\s+and time",re.I)


def extrair_dat(texto:str,meta:dict) ->dict:
    """Lê COORD e S nos pontos de integração; sem extrapolação a nós."""
    parts={"coord":{},"stress":{}}
    group=None
    for line in texto.splitlines():
        line_low=line.strip().lower()
        if " for set " in line_low and " and time " in line_low:
            group=None
            if _HDR.search(line_low):
                if line_low.startswith(('stresses ','stress ')):
                    group='stress'
                elif 'coord' in line_low:
                    group='coord'
            continue
        if group is None:
            continue
        tokens=line.split()
        needed=5 if group=='coord' else 8
        if len(tokens)<needed:
            continue
        try:
            key=(int(tokens[0]),int(tokens[1]))
            values=tuple(float(v.replace('D','E').replace('d','E'))
                         for v in tokens[2:needed])
        except ValueError:
            continue
        if not all(math.isfinite(v) for v in values):
            raise ValueError('Saída COORD/S não finita')
        if key in parts[group]:
            raise ValueError('Registro repetido de ponto de integração')
        parts[group][key]=values
    expected=meta['elementos']*8
    if len(parts['stress'])!=expected or set(parts['stress'])!=set(parts['coord']):
        raise ValueError(f"IP ausentes/inesperados: S={len(parts['stress'])}, "
                         f"COORD={len(parts['coord'])}, esperado={expected}")
    norm=meta['tensao_remota_pa']
    sumerr=0.0
    sumerr_near=0.0
    nnear=0
    near=[]
    for key,coord in parts['coord'].items():
        x,y,z=coord
        ref=tensoes_kirsch(x,y,meta['raio_m'],norm)
        stress=parts['stress'][key]
        sxx,syy,szz,sxy,sxz,syz=stress
        err=((sxx-ref['sigma_xx_pa'])**2+(syy-ref['sigma_yy_pa'])**2
             +2*(sxy-ref['sigma_xy_pa'])**2)
        sumerr+=err
        r=ref['r_m']
        if r < meta['raio_m']+1.15*meta['primeira_camada_m']:
            sumerr_near+=err
            nnear+=1
            th=ref['theta_rad']
            stt=sxx*math.sin(th)**2+syy*math.cos(th)**2-2*sxy*math.sin(th)*math.cos(th)
            near.append((th,r,stt))
    if not near:
        raise ValueError('Sem pontos de Gauss na camada do furo')
    maxnear=max(t[2] for t in near)/norm
    return {
        'pontos_integracao':expected,
        'pontos_perto_furo':nnear,
        'erro_rms_tensor_pa':math.sqrt(sumerr/expected),
        'erro_rms_tensor_rel':math.sqrt(sumerr/expected)/norm,
        'erro_rms_proximo_furo_rel':math.sqrt(sumerr_near/nnear)/norm,
        'max_sigma_tangencial_ip_pa':maxnear*norm,
        'kt_proxy_pontos_integracao':maxnear,
        'kt_borda_analitico':3.0,
        'aviso_kt':'proxy interior, não avaliação direta de Kt no bordo r=a',
        'modelo':'tensao_plana_quarto_anel_displacements_exatos'
    }


def executar(pasta:str|Path,*,nr:int=8,nt:int=16,solver:str|None=None,**kw)->dict:
    out=Path(pasta).resolve()
    out.mkdir(parents=True,exist_ok=True)
    inp,meta=montar_deck(nr=nr,nt=nt,**kw)
    job='kirsch_cps8r'
    (out/(job+'.inp')).write_text(inp,encoding='utf-8')
    (out/'entrada.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    if solver is None:
        solver=next((v for v in ('ccx','ccx_2.21','ccx_2.22','ccx_2.23') if shutil.which(v)),None)
    if not solver or not shutil.which(solver):
        raise RuntimeError('CalculiX não localizado; use --somente-gerar ou instale ccx')
    start=time.perf_counter()
    p=subprocess.run([solver,'-i',job],cwd=out,capture_output=True,text=True,timeout=180)
    duration=time.perf_counter()-start
    (out/'solver.log').write_text(p.stdout+'\n'+p.stderr,encoding='utf-8')
    dat=out/(job+'.dat')
    if p.returncode or not dat.exists():
        raise RuntimeError(f'CalculiX falhou rc={p.returncode}, dat={dat.exists()}; '+(p.stdout+' '+p.stderr)[-1500:])
    r=extrair_dat(dat.read_text(encoding='utf-8',errors='replace'),meta)
    result={'modelo':'kirsch_CPS8R','solver':shutil.which(solver),
            'tempo_solver_s':duration,'entrada':meta,'resultado':r}
    (out/'comparacao.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return result


def main():
    p=argparse.ArgumentParser(description='Benchmark Kirsch anular CPS8R (tensão plana)')
    p.add_argument('--nr',type=int,default=8)
    p.add_argument('--nt',type=int,default=16)
    p.add_argument('--raio-m',type=float,default=0.01)
    p.add_argument('--raio-externo-m',type=float,default=0.08)
    p.add_argument('--graduacao',type=float,default=2.0)
    p.add_argument('--saida',required=True)
    p.add_argument('--somente-gerar',action='store_true')
    p.add_argument('--solver',default=None)
    a=p.parse_args()
    kw={'nr':a.nr,'nt':a.nt,'raio_m':a.raio_m,
        'raio_externo_m':a.raio_externo_m,'graduacao':a.graduacao}
    if a.somente_gerar:
        inp,meta=montar_deck(**kw)
        out=Path(a.saida)
        out.mkdir(parents=True,exist_ok=True)
        (out/'kirsch_cps8r.inp').write_text(inp,encoding='utf-8')
        (out/'entrada.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        print(json.dumps({'gerado':str(out),'entrada':meta},indent=2,ensure_ascii=False))
    else:
        print(json.dumps(executar(a.saida,solver=a.solver,**kw),indent=2,ensure_ascii=False))


if __name__=='__main__':
    main()
