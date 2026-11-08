"""Solver FEM Q8 2D independente, baseado em NumPy/SciPy.

Elasticidade isotropica em tensao plana; 8 nos por elemento, 2 DOFs/no,
integracao volumetrica 3x3, tracao de aresta 3 pontos consistente.
Nao invoca o CalculiX nem usa suas matrizes de rigidez/deslocamentos.
Executa a mesma geometria Q8 vinda de Gmsh; solver de pesquisa,
NAO software certificado para dimensionamento industrial.
"""
from __future__ import annotations

import argparse
import json
import math
import shutil
import subprocess
import time
from pathlib import Path

from .gmsh_chapa import gerar_geo, importar_msh2
from .kirsch import tensoes_kirsch


def q8_dshape(r: float, s: float) -> tuple[tuple[float,...],tuple[float,...]]:
    """Derivadas analiticas da familia serendipidade Q8, ordem CCW."""
    dr=(
        (1-s)*(2*r+s)/4, (1-s)*(2*r-s)/4,
        (1+s)*(2*r+s)/4, (1+s)*(2*r-s)/4,
        -r*(1-s), (1-s*s)/2,
        -r*(1+s), -(1-s*s)/2,
    )
    ds=(
        (1-r)*(r+2*s)/4, (1+r)*(-r+2*s)/4,
        (1+r)*(r+2*s)/4, (1-r)*(-r+2*s)/4,
        -(1-r*r)/2, -(1+r)*s,
        (1-r*r)/2, -(1-r)*s,
    )
    return dr,ds


def q8_shape(r:float,s:float)->tuple[float,...]:
    return (
        -(1-r)*(1-s)*(1+r+s)/4,
        -(1+r)*(1-s)*(1-r+s)/4,
        -(1+r)*(1+s)*(1-r-s)/4,
        -(1-r)*(1+s)*(1+r-s)/4,
        (1-r*r)*(1-s)/2,
        (1+r)*(1-s*s)/2,
        (1-r*r)*(1+s)/2,
        (1-r)*(1-s*s)/2,
    )


def _matriz_constitutiva(E:float,nu:float):
    if not math.isfinite(E) or E<=0 or not math.isfinite(nu) or not -.49<nu<.49:
        raise ValueError("E/nu fora do dominio")
    import numpy as np
    return E/(1-nu*nu)*np.array([
        [1.,nu,0.],
        [nu,1.,0.],
        [0.,0.,(1-nu)/2],
    ])


def _b_matrix(xy, r:float,s:float):
    """Retorna B, jacobiano e vetor de coordenadas de ponto de Gauss."""
    import numpy as np
    dr,ds=q8_dshape(r,s)
    dr=np.asarray(dr,dtype=float);ds=np.asarray(ds,dtype=float)
    x=xy[:,0];y=xy[:,1]
    dxr=dr@x;dxs=ds@x;dyr=dr@y;dys=ds@y
    det=dxr*dys-dxs*dyr
    if not np.isfinite(det) or det<=0:
        raise ValueError(f"Elemento Q8 invertido/degenerado em ponto ({r}, {s}): J={det}")
    dndx=(dr*dys-ds*dyr)/det
    dndy=(ds*dxr-dr*dxs)/det
    B=np.zeros((3,16),dtype=float)
    B[0,0::2]=dndx
    B[1,1::2]=dndy
    B[2,0::2]=dndy
    B[2,1::2]=dndx
    coord=np.asarray(q8_shape(r,s))@xy
    return B,det,coord


def _gauss_3():
    z=math.sqrt(3./5.)
    return [(-z,5./9.),(0.,8./9.),(z,5./9.)]


def resolver(mesh:dict, *, E:float=200e9,nu:float=.3,
             thickness:float=.005,traction:float=10e6,
             hole_radius:float=.01,halfwidth:float=.04)->dict:
    """Montagem Q8 3x3, solucao esparsa, reacoes e pico de tensao no furo."""
    import numpy as np
    from scipy.sparse import coo_matrix
    from scipy.sparse.linalg import spsolve
    start=time.perf_counter()
    if thickness<=0 or traction<=0 or halfwidth<=3*hole_radius*.99999:
        raise ValueError("Geometria/espessura/tracao invalidas")
    D=_matriz_constitutiva(E,nu)
    nodes=mesh["nodes"]
    labels=sorted(nodes)
    loc={tag:i for i,tag in enumerate(labels)}
    coords=np.array([nodes[tag][:2] for tag in labels],dtype=float)
    ndof=2*len(labels)
    ii=[];jj=[];vv=[]
    gauss=_gauss_3()
    bad_jac=0
    min_jac=float("inf")
    # Conjunto de dados de elemento/solucao preservado para recuperacao.
    contributions=[]
    for element,conn in mesh['elements'].items():
        idn=np.array([loc[n] for n in conn],dtype=int)
        xy=coords[idn]
        dof=np.empty(16,dtype=int)
        dof[0::2]=2*idn
        dof[1::2]=2*idn+1
        Ke=np.zeros((16,16),dtype=float)
        for r,wr in gauss:
            for s,ws in gauss:
                B,det,_=_b_matrix(xy,r,s)
                min_jac=min(min_jac,det)
                Ke+=thickness*wr*ws*det*(B.T@D@B)
        # COO com somas de contribuicoes compartilhadas nos mesmos DOFs.
        ii.extend(np.repeat(dof,16).tolist())
        jj.extend(np.tile(dof,16).tolist())
        vv.extend(Ke.ravel().tolist())
        contributions.append((element,conn,dof,xy))
    K=coo_matrix((vv,(ii,jj)),shape=(ndof,ndof)).tocsr()
    if K.nnz==0 or min_jac<=0:
        raise RuntimeError("Matriz global não montada")
    f=np.zeros(ndof,dtype=float)
    for n1,nmid,n2 in mesh['right_edges']:
        length=abs(nodes[n2][1]-nodes[n1][1])
        for node,w in ((n1,1/6),(nmid,4/6),(n2,1/6)):
            f[2*loc[node]]+=traction*thickness*length*w
    fx=float(f[0::2].sum())
    expected=traction*thickness*halfwidth
    if not math.isclose(fx,expected,rel_tol=1e-10,abs_tol=1e-5):
        raise ValueError("Tração integrada não conserva resultante")
    constrained={2*loc[n] for n in mesh['symmetry_x']}
    constrained.update(2*loc[n]+1 for n in mesh['symmetry_y'])
    fixed=np.array(sorted(constrained),dtype=int)
    free=np.setdiff1d(np.arange(ndof,dtype=int),fixed,assume_unique=True)
    if free.size==0 or fixed.size==0:
        raise ValueError("Contornos de simetria não impostos")
    u=np.zeros(ndof,dtype=float)
    u[free]=spsolve(K[free][:,free],f[free])
    if not np.all(np.isfinite(u)):
        raise ValueError("Solver esparso gerou deslocamento inválido")
    residual=(K@u)-f
    residual_free=float(np.linalg.norm(residual[free])/
                        max(float(np.linalg.norm(f)),1.))
    residual_x=abs(float(residual[0::2].sum()+fx))/fx
    # Esta soma inclui reacoes e minimos residuos de DOFs livres.
    reaction_x=float(residual[0::2].sum())
    reaction_y=float(residual[1::2].sum())
    if residual_free>1e-6 or abs(reaction_x+fx)/fx>1e-5 or abs(reaction_y)/fx>1e-5:
        raise ValueError("Equilibrio de reacoes nao satisfeito")
    # Condicao critica no contorno livre x=0, y=a. So um elemento por quadrante
    # contem este vertice. Avaliar gradiente do deslocamento *no ponto de contorno*.
    point_nodes=[n for n,p in nodes.items()
                 if abs(p[0])<1e-10 and abs(p[1]-hole_radius)<1e-10]
    if len(point_nodes)!=1:
        raise ValueError(f"Ponto critico do furo nao identificado: {point_nodes}")
    vertex=point_nodes[0]
    elements=[(e,conn,dof,xy) for e,conn,dof,xy in contributions
              if vertex in conn[:4]]
    if len(elements)!=1:
        raise ValueError("Ponto critico nao possui exatamente um elemento adjacente")
    _,conn,dof,xy=elements[0]
    nodeidx=conn.index(vertex)
    rs=((-1.,-1.),(1.,-1.),(1.,1.),(-1.,1.))
    rcrit,scrit=rs[nodeidx]
    B,det,xycrit=_b_matrix(xy,rcrit,scrit)
    sigma=D@(B@u[dof])
    # Na direcao theta=pi/2, tensao tangencial = sigma_xx.
    kt=float(sigma[0]/traction)
    # Verificacao separada da aproximacao espacial pelo campo analitico Kirsch.
    # Exatamente o mesmo B e interpolacao dos nos (nao solver FEM).
    node_disp=np.array([_kirsch_displacement(x,y,hole_radius,traction,E,nu)
                        for x,y in xy],dtype=float).reshape(16)
    analytic_interpolated=D@(B@node_disp)
    analytic_interp_kt=float(analytic_interpolated[0]/traction)
    # Outra grandeza mecanica: tensao radial da parede livre ~= sigma_yy.
    normalized_radial=float(sigma[1]/traction)
    normalized_shear=float(sigma[2]/traction)
    gauss_near=[]
    for _,conn2,dof2,xy2 in contributions:
        for r,wr in gauss:
            for s,ws in gauss:
                Bgp,detgp,pt=_b_matrix(xy2,r,s)
                radius=math.hypot(pt[0],pt[1])
                theta=math.atan2(pt[1],pt[0])
                if radius<hole_radius*1.2 and theta>math.pi/2-.2:
                    stress=D@(Bgp@u[dof2])
                    s_tt=(stress[0]*math.sin(theta)**2+
                          stress[1]*math.cos(theta)**2-
                          2*stress[2]*math.sin(theta)*math.cos(theta))
                    gauss_near.append(float(s_tt/traction))
    if not gauss_near:
        raise ValueError("Nenhum Gauss proximo ao bordo critico")
    reference_points={}
    for key,(cx,cy,dof_id) in {
        "hole_top_uy":(0.,hole_radius,1),
        "hole_right_ux":(hole_radius,0.,0),
        "right_axis_ux":(halfwidth,0.,0),
        "top_axis_uy":(0.,halfwidth,1),
    }.items():
        selected=[n for n,coord in nodes.items()
                  if abs(coord[0]-cx)<1e-10 and abs(coord[1]-cy)<1e-10]
        if len(selected)!=1:
            raise ValueError("Ponto de referencia nao unico: "+key)
        reference_points[key]=float(u[2*loc[selected[0]]+dof_id])
    runtime=time.perf_counter()-start
    return {
        "deslocamentos_pontos_referencia_m":reference_points,
        "solver":"solucionador Q8 independente Python NumPy/SciPy",
        "formulacao":"tensao plana, matriz B e elasticidade linear, 3x3 Gauss",
        "nos":len(labels),"elementos":len(contributions),
        "graus_liberdade":ndof,"fixados":len(fixed),
        "min_det_jacobiano_m2":min_jac,
        "carga_quadrante_N":fx,"reacao_x_N":reaction_x,
        "reacao_y_N":reaction_y,
        "residuo_equilibrio_x_rel":abs(reaction_x+fx)/fx,
        "residuo_equilibrio_y_rel":abs(reaction_y)/fx,
        "residuo_algebraico_livre_rel":residual_free,
        "kt_gross_gradiente_direto_bordo":kt,
        "kt_net_gradiente_direto_bordo":kt*(1-hole_radius/halfwidth),
        "s_rr_normalizada_no_bordo":normalized_radial,
        "s_rt_normalizada_no_bordo":normalized_shear,
        "kt_kirsch_analitico_amostrado_interpolacao":analytic_interp_kt,
        "kt_proxy_max_gauss_proximo_furo":max(gauss_near),
        "deslocamento_max_abs_m":float(np.max(np.abs(u))),
        "tempo_montagem_e_solve_s":runtime,
        "metodo_tensao":"gradiente direto B(vertice do furo) @ deslocamentos FEM; SEM extrapolacao polinomial dos Gauss",
        "aviso":"Solver de pesquisa independente, sem validacao fisica ou industrial",
    }


def _kirsch_displacement(x:float,y:float,a:float,T:float,E:float,nu:float)->tuple[float,float]:
    from .kirsch import deslocamentos_kirsch
    return deslocamentos_kirsch(x,y,a,T,E,nu)


def executar(destino:str|Path,*,nr:int=16,nt:int=32,
             raio_m:float=.01,semilargura_m:float=.04,gmsh_exe:str="gmsh")->dict:
    if not shutil.which(gmsh_exe):
        raise RuntimeError("Gmsh não instalado")
    dest=Path(destino)
    dest.mkdir(parents=True,exist_ok=True)
    (dest/"model.geo").write_text(
        gerar_geo(nr=nr,nt=nt,raio_m=raio_m,semilargura_m=semilargura_m),
        encoding="utf-8"
    )
    p=subprocess.run([gmsh_exe,"model.geo","-2","-order","2","-format","msh2",
                      "-o","model.msh"],cwd=dest,text=True,capture_output=True,timeout=120)
    (dest/"gmsh.log").write_text(p.stdout+"\n"+p.stderr,encoding="utf-8")
    if p.returncode:
        raise RuntimeError("Gmsh falhou: "+(p.stdout+"\n"+p.stderr)[-1300:])
    msh=importar_msh2((dest/"model.msh").read_text(encoding="utf-8"),
                      a=raio_m,H=semilargura_m,nr=nr,nt=nt)
    result=resolver(msh,hole_radius=raio_m,halfwidth=semilargura_m)
    report={
        "caso":"chapa_finita_Q8_solucionador_independente",
        "H_sobre_a":semilargura_m/raio_m,
        "nr":nr,"nt":nt,
        "mesh_source":"Gmsh CAD transfinite Q8",
        "resultado":result
    }
    (dest/"resultado.json").write_text(
        json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"
    )
    return report


def main():
    p=argparse.ArgumentParser(description="Elasticidade plana Q8 scipy independente")
    p.add_argument("--nr",type=int,default=16)
    p.add_argument("--nt",type=int,default=32)
    p.add_argument("--semilargura-m",type=float,default=.04)
    p.add_argument("--raio-m",type=float,default=.01)
    p.add_argument("--saida",required=True)
    v=p.parse_args()
    print(json.dumps(executar(v.saida,nr=v.nr,nt=v.nt,
              semilargura_m=v.semilargura_m,raio_m=v.raio_m),indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
