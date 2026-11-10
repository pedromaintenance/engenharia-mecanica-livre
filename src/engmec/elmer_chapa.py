"""Benchmark de elasticidade plana em solver EXTERNO Elmer FEM.

Gmsh MSH2 quad8, ElmerGrid 14 2, StressSolve/StressSolver.
Compara deslocamentos nos nós com o solucionador SciPy sobre a mesma malha.
Pico tangencial: mesmo operador de recuperação B do benchmark SciPy,
alimentado por deslocamentos Elmer (isola diferença do campo de deslocamento).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import time
from pathlib import Path

from .gmsh_chapa import gerar_geo, importar_msh2
from .progressao_radial import razao_progressao
from .fem2d_indep import resolver as resolver_scipy, _b_matrix, _matriz_constitutiva


def geo_elmer(*, nr:int=16, nt:int=32, H:float=.04, a:float=.01,
              L:float|None=None, estrategia_progressao:str="fixa",
              angular:str="uniforme",topologia:str="dois-blocos")->str:
    """Mesmo CAD, agora com IDs físicos explícitos para ElmerGrid."""
    L=H if L is None else L
    if L<H or not math.isfinite(L):
        raise ValueError('Semicomprimento L deve ser finito e >= semilargura H')
    if topologia not in ("dois-blocos","anel-quatro-blocos","anel-seis-blocos"):
        raise ValueError("Topologia nao reconhecida")
    if topologia=="anel-seis-blocos":
        if angular!="uniforme" or estrategia_progressao!="escalonada":
            raise ValueError("Seis blocos exigem angular uniforme e baseline escalonada")
        from .multibloco_externo import gerar_geo_seis_blocos
        return gerar_geo_seis_blocos(nr=nr,nt=nt,a=a,Hy=H,Hx=L)
    if topologia=="anel-quatro-blocos":
        if angular!="uniforme" or estrategia_progressao!="escalonada":
            raise ValueError("Anel quatro-blocos verificado somente com angular uniforme e referencia radial escalonada")
        from .multibloco_anel import gerar_geo_anel_quatro_blocos
        return gerar_geo_anel_quatro_blocos(nr=nr,nt=nt,a=a,Hy=H,Hx=L)
    q=razao_progressao(nr,estrategia_progressao)
    if math.isclose(L,H,rel_tol=0.,abs_tol=1e-15):
        geo=gerar_geo(nr=nr,nt=nt,raio_m=a,semilargura_m=H,progressao=q)
    else:
        from .chapa_retangular import gerar_geo_retangular
        geo=gerar_geo_retangular(nr=nr,nt=nt,a=a,Hy=H,Hx=L,progressao=q)
    from .angular_transfinite import aplicar_distribuicao_angular
    geo=aplicar_distribuicao_angular(geo,modo=angular,nt=nt)
    return geo+"""
// Identificadores físicos: ElmerGrid pode remapear, verifique mesh.boundary.
Physical Surface("elastic_domain", 101) = {1,2};
Physical Curve("traction_right", 201) = {2};
Physical Curve("symmetry_x_zero", 202) = {6};
Physical Curve("symmetry_y_zero", 203) = {1};
Physical Curve("traction_free_top", 204) = {5};
Physical Curve("traction_free_hole", 205) = {4,7};
"""


def _parse_elmer_mesh(folder:Path, *, H:float, a:float,
                      Hx:float|None=None)->dict:
    """Deriva tags de BC do arquivo convertido, sem presumir IDs do Gmsh."""
    Hx=H if Hx is None else Hx
    if Hx<H:
        raise ValueError('Semicomprimento menor que semilargura')
    points={}
    for line in (folder/"mesh.nodes").read_text().splitlines():
        t=line.split()
        if len(t)<5:
            raise ValueError("Elmer mesh.nodes incompleto")
        k=int(t[0]);pt=tuple(float(v) for v in t[2:5])
        points[k]=pt
    bodies=set()
    surface_count=0
    for line in (folder/"mesh.elements").read_text().splitlines():
        t=line.split()
        if len(t)<4:
            raise ValueError("Elmer mesh.elements incompleto")
        bodies.add(int(t[1]))
        if int(t[2]) not in (408,409):
            raise ValueError("Elemento Elmer não é quadrilátero quadrático")
        surface_count+=1
    boundaries={"right":set(),"sym_x":set(),"sym_y":set(),"top":set(),"hole":set()}
    counts={k:0 for k in boundaries}
    for line in (folder/"mesh.boundary").read_text().splitlines():
        t=line.split()
        if len(t)<6:
            raise ValueError("Elmer mesh.boundary incompleto")
        tag=int(t[1]);kind=int(t[4])
        if kind not in (202,203):
            raise ValueError(f"Tipo de aresta Elmer inesperado: {kind}")
        n=[int(z) for z in t[5:]]
        xyz=[points[k] for k in n]
        eps=max(Hx,H,a)*1e-6
        if all(abs(p[0]-Hx)<eps for p in xyz):
            key="right"
        elif all(abs(p[0])<eps for p in xyz):
            key="sym_x"
        elif all(abs(p[1])<eps for p in xyz):
            key="sym_y"
        elif all(abs(p[1]-H)<eps for p in xyz):
            key="top"
        elif all(abs(math.hypot(p[0],p[1])-a)<eps for p in xyz):
            key="hole"
        else:
            raise ValueError("Aresta externa Elmer com geometria não reconhecida")
        boundaries[key].add(tag);counts[key]+=1
    if len(bodies)!=1 or not all(len(v)==1 for v in boundaries.values()):
        raise ValueError(f"Etiquetas Elmer ambíguas: bodies={bodies}, boundaries={boundaries}")
    labels={k:next(iter(v)) for k,v in boundaries.items()}
    if len(set(labels.values()))!=len(labels):
        raise ValueError("Duas fronteiras físicas receberam a mesma etiqueta")
    return {"body":next(iter(bodies)),"bc":labels,"boundary_edges":counts,
            "elmer_nodes":len(points),"elmer_elements":surface_count}


def _sif(mesh:dict, *, T:float=10e6, E:float=200e9, nu:float=.3)->str:
    b=mesh["bc"]
    return f"""Header
  CHECK KEYWORDS Warn
  Mesh DB "." "elmermesh"
  Include Path ""
  Results Directory ""
End

Simulation
  Coordinate System = Cartesian 2D
  Simulation Type = Steady State
  Steady State Max Iterations = 1
  Output Intervals = 1
  Max Output Level = 5
End

Body 1
  Target Bodies(1) = {mesh["body"]}
  Equation = 1
  Material = 1
End

Equation 1
  Name = "Linear elasticity, plane stress"
  Active Solvers(2) = 1 2
  Plane Stress = Logical True
End

Material 1
  Name = "Linear isotropic reference"
  Youngs Modulus = Real {E:.12g}
  Poisson Ratio = Real {nu:.12g}
  Density = Real 7800
End

Solver 1
  Equation = "Linear elasticity"
  Variable = -dofs 2 Displacement
  Procedure = "StressSolve" "StressSolver"
  Calculate Stresses = Logical True
  Linear System Solver = Direct
  Linear System Direct Method = Umfpack
  Linear System Convergence Tolerance = 1.0e-11
  Nonlinear System Max Iterations = 1
  Steady State Convergence Tolerance = 1.0e-11
End

Solver 2
  Exec Solver = After All
  Equation = "Result Output"
  Procedure = "ResultOutputSolve" "ResultOutputSolver"
  Output File Name = "elmer"
  Vtu Format = Logical True
  Displace Mesh = Logical False
End

Boundary Condition 1
  Name = "Right traction 10 MPa"
  Target Boundaries(1) = {b["right"]}
  Force 1 = Real {T:.12g}
End

Boundary Condition 2
  Name = "Symmetry x equals zero"
  Target Boundaries(1) = {b["sym_x"]}
  Displacement 1 = Real 0
End

Boundary Condition 3
  Name = "Symmetry y equals zero"
  Target Boundaries(1) = {b["sym_y"]}
  Displacement 2 = Real 0
End
"""


def _meshio_displacements(root:Path, mesh:dict, *, a:float,H:float):
    import numpy as np
    import meshio
    candidates=sorted(root.rglob("*.vtu"),key=lambda p:p.stat().st_mtime)
    if not candidates:
        raise RuntimeError("Elmer não produziu VTU; inspecione solver.log")
    view=meshio.read(candidates[-1])
    fields=[(k,v) for k,v in view.point_data.items() if 'displacement' in k.lower()]
    if not fields:
        raise ValueError(f"Variável Displacement não encontrada no VTU; chaves: {list(view.point_data)}")
    vector=None
    for k,v in fields:
        arr=np.asarray(v)
        if arr.ndim==2 and arr.shape[1]>=2:
            vector=arr[:,:2];break
    if vector is None:
        raise ValueError("VTU não contém deslocamento vetorial 2D")
    xy=np.asarray(view.points)[:,:2]
    if len(vector)!=len(xy) or not np.all(np.isfinite(vector)):
        raise ValueError("Nodal displacement VTU não finito ou incompleto")
    # Elmer ResultOutputSolver pode usar configuracao de visualizacao com
    # coordenadas deslocadas. Nao aumentar tolerancia para ocultar o fato:
    # tentar geometria original ou subtrair campo U ANTES do confronto.
    from scipy.spatial import cKDTree
    labels=sorted(mesh["nodes"])
    source=np.asarray([mesh["nodes"][tag][:2] for tag in labels],dtype=float)
    tol=max(H,a)*2e-5
    choice=None
    for mode,candidate in (
        ("coordenadas_originais",xy),
        ("coordenadas_deformadas_corrigidas",xy-vector),
    ):
        distances,matched=cKDTree(candidate).query(source,k=1)
        if (np.all(np.isfinite(distances))
            and float(np.max(distances))<=tol
            and len(set(int(j) for j in matched))==len(labels)):
            choice=(mode,distances,matched)
            break
    if choice is None:
        d0,_=cKDTree(xy).query(source,k=1)
        d1,_=cKDTree(xy-vector).query(source,k=1)
        raise ValueError("VTU nao equivale a MSH2 em referencia ou configuracao deformada; "
                         f"max_original={max(d0):.4e}, max_corrigida={max(d1):.4e}, tol={tol}")
    mode,distances,matched=choice
    original={tag:vector[int(j)] for tag,j in zip(labels,matched)}
    return original,candidates[-1],{"modo":mode,"max_erro_m":float(max(distances)),"tolerancia_m":tol}


def _crit_stress(mesh:dict, disp:dict, *, E:float,nu:float,a:float,T:float,H:float)->dict:
    """Mesmo operador B aplicado a Elmer e SciPy, com solucao independente."""
    import numpy as np
    critical=[n for n,(x,y,z) in mesh["nodes"].items() if abs(x)<1e-10 and abs(y-a)<1e-10]
    if len(critical)!=1:
        raise ValueError("Nó do furo não encontrado")
    target=critical[0]
    elems=[conn for conn in mesh["elements"].values() if target in conn[:4]]
    if len(elems)!=1:
        raise ValueError("Nó do furo deve estar num único quadrilátero")
    conn=elems[0]
    j=conn.index(target)
    rs=((-1.,-1.),(1.,-1.),(1.,1.),(-1.,1.))
    coords=np.asarray([mesh["nodes"][n][:2] for n in conn])
    U=np.asarray([disp[n] for n in conn]).reshape(16)
    B,det,p=_b_matrix(coords,*rs[j])
    s=_matriz_constitutiva(E,nu)@(B@U)
    return {
        "kt_gross_gradiente_direto":float(s[0]/T),
        "kt_net_gradiente_direto":float((s[0]/T)*(1-a/H)),
        "sigma_rr_sobre_T":float(s[1]/T),
        "sigma_rtheta_sobre_T":float(s[2]/T),
    }


def executar(out_dir:str|Path, *, nr:int=16,nt:int=32,H:float=.04,a:float=.01,
             L:float|None=None,T:float=10e6,E:float=200e9,nu:float=.3,
             estrategia_progressao:str="fixa",angular:str="uniforme",
             topologia:str="dois-blocos",gmsh_cmd:str="gmsh",
             grid_cmd:str="ElmerGrid",solver_cmd:str="ElmerSolver")->dict:
    for app in (gmsh_cmd,grid_cmd,solver_cmd):
        if shutil.which(app) is None:
            raise RuntimeError(f"Programa requerido não encontrado: {app}")
    L=H if L is None else L
    if L<H or not math.isfinite(L):
        raise ValueError('L deve ser >=H')
    out=Path(out_dir).resolve()
    out.mkdir(parents=True,exist_ok=True)
    (out/"model.geo").write_text(geo_elmer(nr=nr,nt=nt,H=H,a=a,L=L,
                estrategia_progressao=estrategia_progressao,
                angular=angular,topologia=topologia),encoding="utf-8")
    t0=time.perf_counter()
    commands=[
        ("gmsh",[gmsh_cmd,"model.geo","-2","-order","2","-format","msh2","-o","model.msh"]),
        ("elmergrid",[grid_cmd,"14","2","model.msh","-autoclean","-out","elmermesh"]),
    ]
    for phase,command in commands:
        p=subprocess.run(command,cwd=out,capture_output=True,text=True,timeout=160)
        (out/(phase+".log")).write_text(p.stdout+"\n"+p.stderr,encoding="utf-8")
        if p.returncode:
            raise RuntimeError(f"{phase} falhou rc={p.returncode}: {(p.stdout+p.stderr)[-2500:]}")
    mesh=importar_msh2((out/"model.msh").read_text(encoding="utf-8"),a=a,H=H,nr=nr,nt=nt,Hx=L)
    controle_topologia=None
    if topologia=="anel-seis-blocos":
        from .multibloco_externo import parametros_seis_blocos, verificar_seis_blocos
        controle_topologia={
            "parametros":parametros_seis_blocos(nr,nt,a=a,Hy=H,Hx=L),
            "conformidade":verificar_seis_blocos(mesh,a=a,Hy=H,Hx=L,nr=nr,nt=nt)
        }
    if topologia=="anel-quatro-blocos":
        from .multibloco_anel import parametros_anel, verificar_anel_conforme
        controle_topologia={
            "parametros":parametros_anel(nr,nt,a=a,Hy=H,Hx=L),
            "conformidade":verificar_anel_conforme(mesh,a=a,nr=nr,nt=nt)
        }
    info=_parse_elmer_mesh(out/"elmermesh",H=H,a=a,Hx=L)
    if info["elmer_elements"]!=len(mesh["elements"]):
        raise ValueError("Perda de elementos na conversão do ElmerGrid")
    (out/"case.sif").write_text(_sif(info,T=T,E=E,nu=nu),encoding="utf-8")
    p=subprocess.run([solver_cmd,"case.sif"],cwd=out,capture_output=True,text=True,timeout=240)
    (out/"solver.log").write_text(p.stdout+"\n"+p.stderr,encoding="utf-8")
    if p.returncode:
        raise RuntimeError(f"ElmerSolver falhou rc={p.returncode}: {(p.stdout+p.stderr)[-3000:]}")
    disp,vtu,conferencia_vtu=_meshio_displacements(out,mesh,a=a,H=max(H,L))
    stress=_crit_stress(mesh,disp,E=E,nu=nu,a=a,T=T,H=H)
    # Ciclo 14: MESMO vetor de deslocamentos Elmer; variar so a recuperacao.
    from .recuperar_tensao import recuperar, escrever_csv
    recuperacao, gauss_rows = recuperar(mesh,disp,a=a,H=H,T=T,E=E,nu=nu)
    if abs(recuperacao["metodos"]["A_gradiente_bordo"]["kt_gross"]-
           stress["kt_gross_gradiente_direto"])>1e-9:
        raise ValueError("Regressao no recuperador de gradiente da parede")
    (out/"recuperacao.json").write_text(
        json.dumps(recuperacao,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    escrever_csv(out/"gauss_tensoes.csv",gauss_rows)
    (out/"deslocamentos_elmer.json").write_text(json.dumps(
        {str(n):[float(v[0]),float(v[1])] for n,v in disp.items()},
        indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    native=resolver_scipy(mesh,E=E,nu=nu,thickness=.005,traction=T,hole_radius=a,halfwidth=H,length_x=L)
    pairs={}
    for name,(x,y,k) in {
        "hole_top_uy":(0.,a,1),
        "hole_right_ux":(a,0.,0),
        "right_axis_ux":(L,0.,0),
        "top_axis_uy":(0.,H,1)
    }.items():
        nodes=[tag for tag,(xx,yy,z) in mesh["nodes"].items()
               if abs(xx-x)<1e-10 and abs(yy-y)<1e-10]
        if len(nodes)!=1:
            raise ValueError(f"Vertex expected once: {name} {nodes}")
        elmer_value=float(disp[nodes[0]][k])
        scipy_value=float(native["deslocamentos_pontos_referencia_m"][name])
        pairs[name]={
            "elmer_m":elmer_value,
            "scipy_m":scipy_value,
            "diff_m":elmer_value-scipy_value,
            "diff_rel":(elmer_value-scipy_value)/max(abs(scipy_value),1e-12)
        }
    report={
        "case":"finite_square_hole_elmer_vs_scipy",
        "H_over_a":H/a,"nr":nr,"nt":nt,
        "L_over_W":L/H,"d_over_W":a/H,
        "distribuicao_angular":angular,
        "topologia":topologia,
        "controle_multibloco":controle_topologia,
        "estrategia_progressao_radial":estrategia_progressao,
        "q_radial_efetivo":(razao_progressao(nr,estrategia_progressao)
                            if topologia=="dois-blocos" else None),
        "q_radial_acumulado":(razao_progressao(nr,estrategia_progressao)**nr
                              if topologia=="dois-blocos" else None),
        "semicomprimento_x_m":L,"semilargura_y_m":H,
        "mesh_sha256":hashlib.sha256((out/"model.msh").read_bytes()).hexdigest(),
        "mesh_info":info,"recovery":stress,
        "scipy_reference":{
            "kt_gross_gradiente_direto":native["kt_gross_gradiente_direto_bordo"],
            "kt_net_gradiente_direto":native["kt_net_gradiente_direto_bordo"],
            "sigma_rr_sobre_T":native["s_rr_normalizada_no_bordo"],
            "sigma_rtheta_sobre_T":native["s_rt_normalizada_no_bordo"],
            "reacoes_equilibrio_x":native["residuo_equilibrio_x_rel"],
        },
        "point_displacements":pairs,
        "vtu":str(vtu.relative_to(out)),
        "conferencia_vtu":conferencia_vtu,
        "arquivos_recuperacao":{
            "resumo":"recuperacao.json",
            "gauss":"gauss_tensoes.csv",
            "deslocamentos":"deslocamentos_elmer.json"
        },
        "duration_s":time.perf_counter()-t0,
        "note":"Stress recovery SAME B operator; displacement solved independently by Elmer and SciPy."
    }
    (out/"comparison.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--nr",type=int,default=16)
    parser.add_argument("--nt",type=int,default=32)
    parser.add_argument("--semilargura-m",type=float,default=.04)
    parser.add_argument("--semicomprimento-x-m",type=float,default=None)
    parser.add_argument("--raio-m",type=float,default=.01)
    parser.add_argument("--progressao-radial",choices=["fixa","escalonada"],default="fixa")
    parser.add_argument("--distribuicao-angular",choices=["uniforme","ampliada-topo"],default="uniforme")
    parser.add_argument("--topologia",choices=["dois-blocos","anel-quatro-blocos","anel-seis-blocos"],default="dois-blocos")
    parser.add_argument("--saida",required=True)
    opt=parser.parse_args()
    print(json.dumps(executar(opt.saida,nr=opt.nr,nt=opt.nt,H=opt.semilargura_m,L=opt.semicomprimento_x_m,a=opt.raio_m,
                    estrategia_progressao=opt.progressao_radial,
                    angular=opt.distribuicao_angular,
                    topologia=opt.topologia),
                     indent=2,ensure_ascii=False))


if __name__=="__main__":
    main()
