"""Comparação C3D8 x C3D20R em flexão pura, com tensões em pontos de Gauss.

Gera carregamentos consistentes Q4/Q8 na face, reutiliza a referência de
elasticidade independente do módulo flexao_calculix. N, m e Pa.
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

from . import flexao_calculix


ARESTAS = (
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7)
)
GAUSS3 = (
    (-math.sqrt(3 / 5), 5 / 9),
    (0.0, 8 / 9),
    (math.sqrt(3 / 5), 5 / 9)
)
GAUSS2 = (
    (-1 / math.sqrt(3), 1.0),
    (+1 / math.sqrt(3), 1.0)
)


def forma_q8(r: float, s: float) -> tuple[float, ...]:
    """Oito funções de forma serendipidade no quadrado [-1,1]²."""
    return (
        -(1-r)*(1-s)*(1+r+s)/4,
        -(1+r)*(1-s)*(1-r+s)/4,
        -(1+r)*(1+s)*(1-r-s)/4,
        -(1-r)*(1+s)*(1+r-s)/4,
        (1-r*r)*(1-s)/2,
        (1+r)*(1-s*s)/2,
        (1-r*r)*(1+s)/2,
        (1-r)*(1-s*s)/2
    )


def _registrar_mid(
    a: int, b: int, coordenadas: dict[int, tuple[float, float, float]],
    mids: dict[tuple[int, int], int]
) -> int:
    key = tuple(sorted((a, b)))
    if key not in mids:
        aa, bb = coordenadas[a], coordenadas[b]
        ident = max(coordenadas) + 1
        coordenadas[ident] = tuple((x+y)/2 for x,y in zip(aa,bb))
        mids[key] = ident
    return mids[key]


def montar_deck(
    familia: str = "C3D20R", nx: int = 2, ny: int = 2, nz: int = 2,
    **parametros
) -> tuple[str, dict]:
    """Construir deck de ambos os elementos na mesma geometria/referência.

    C3D20R usa mids de aresta globais compartilhados, integração consistente
    3x3 de tração linear y em face Q8, com cargas nos vértices e mids.
    """
    if familia not in ("C3D8", "C3D20R"):
        raise ValueError("familia deve ser C3D8 ou C3D20R")
    base, meta = flexao_calculix.montar_deck(nx=nx, ny=ny, nz=nz, **parametros)
    meta["familia"] = familia
    if familia == "C3D8":
        return base.replace(
            "*EL FILE,ELSET=EALL\nS\n", "*EL FILE\nS\n"
        ).replace(
            "*END STEP\n",
            "*EL PRINT,ELSET=EALL,GLOBAL=YES\nCOORD,S\n*END STEP\n"
        ), meta

    header, tail = base.split("*ELEMENT,TYPE=C3D8,ELSET=EALL\n", 1)
    elements, rest = tail.split("*NSET,NSET=TIPCENTER\n", 1)
    prefix, nodesblock = header.split("*NODE\n", 1)
    coordinates: dict[int, tuple[float, float, float]] = {}
    for line in nodesblock.splitlines():
        ident, *vals = [s.strip() for s in line.split(",")]
        coordinates[int(ident)] = tuple(float(val) for val in vals)
    mids: dict[tuple[int,int],int] = {}
    conn: list[tuple[int,...]] = []
    for element in elements.splitlines():
        if not element.strip():
            continue
        ids = tuple(int(x.strip()) for x in element.split(","))
        if len(ids) != 9:
            raise ValueError("Elemento C3D8 inválido na malha base")
        corners = ids[1:]
        edge_ids = tuple(_registrar_mid(corners[a],corners[b],coordinates,mids)
                         for a,b in ARESTAS)
        conn.append((ids[0], *corners, *edge_ids))

    # Malha quadrática serendipidade globalmente compatível nas interfaces.
    nbl = "\n".join(
        f"{ident}, {xyz[0]:.16g}, {xyz[1]:.16g}, {xyz[2]:.16g}"
        for ident,xyz in sorted(coordinates.items())
    )
    # Parser CalculiX splitline aceita no máximo 16 entradas por linha.
    # Para C3D20R: 1 ID + 15 nós na 1ª linha, 5 nós na continuação.
    ebl = "\n".join(
        f"{ids[0]}, " + ", ".join(str(i) for i in ids[1:16]) + "\n"
        + ", ".join(str(i) for i in ids[16:])
        for ids in conn
    )
    rebuilt = (prefix+"*NODE\n"+nbl+"\n"+
               "*ELEMENT,TYPE=C3D20R,ELSET=EALL\n"+ebl+"\n"+
               "*NSET,NSET=TIPCENTER\n"+rest)
    before, after = rebuilt.split("*CLOAD\n", 1)
    _, ending = after.split("*NODE PRINT,NSET=TIPCENTER\n",1)

    def nodeid(i: int,j: int,k: int) -> int:
        return 1+i*(ny+1)*(nz+1)+k*(ny+1)+j

    b=float(meta["largura_m"])
    E=float(meta["e_pa"])
    kappa=float(meta["curvatura_m_inv"])
    dy,dz=b/ny,b/nz
    loads: dict[int,float] = {}
    momento={0:0.0,nx:0.0}
    for i,normal in ((0,-1),(nx,+1)):
        for kk in range(nz):
            for j in range(ny):
                corners=(
                    nodeid(i,j,kk),nodeid(i,j+1,kk),
                    nodeid(i,j+1,kk+1),nodeid(i,j,kk+1)
                )
                mids_face=tuple(_registrar_mid(corners[a],corners[b],coordinates,mids)
                                for a,b in ((0,1),(1,2),(2,3),(3,0)))
                quad=(*corners,*mids_face)
                for r,wr in GAUSS3:
                    yg=-b/2+(j+(r+1)/2)*dy
                    for s,ws in GAUSS3:
                        traction=normal*(-E*kappa*yg)
                        factor=traction*wr*ws*dy*dz/4
                        shape=forma_q8(r,s)
                        if abs(sum(shape)-1)>1e-12:
                            raise ArithmeticError("Funções Q8 não somam 1")
                        for node,w in zip(quad,shape):
                            loads[node]=loads.get(node,0.0)+factor*w
    # Todos os mids de face Q8 já correspondem a arestas registradas.
    if len(coordinates) != len(nbl.splitlines()):
        raise ValueError("Nós de face C3D20R ausentes da malha gerada")
    face_forces={str(i):sum(f for node,f in loads.items()
             if abs(coordinates[node][0]-i*meta["comprimento_m"]/nx)<1e-11)
             for i in (0,nx)}
    for node,f in loads.items():
        i=0 if abs(coordinates[node][0])<1e-11 else nx
        momento[i] -= coordinates[node][1]*f
    if any(abs(f)>1e-5 for f in face_forces.values()):
        raise ValueError("Carga C3D20R apresenta resultante axial artificial")
    for i,sign in ((0,-1),(nx,1)):
        if not math.isclose(momento[i],sign*meta["momento_referencia_nm"],rel_tol=1e-10,abs_tol=1e-5):
            raise ValueError("Momento C3D20R não bate com referência")
    # Descartar resíduos de quadratura ~1e-12 N em nós de carga
    # analiticamente nula. CalculiX 2.21 rejeita esses CLOAD minúsculos.
    limite=max(abs(f) for f in loads.values())*1e-10
    aplicadas={n:f for n,f in loads.items() if abs(f)>limite}
    cargas="\n".join(
        f"{node}, 1, {force:.16g}" for node,force in sorted(aplicadas.items())
    )
    rebuilt=(before+"*CLOAD\n"+cargas+"\n"+
             "*NODE PRINT,NSET=TIPCENTER\n"+ending)
    rebuilt=rebuilt.replace(
        "*EL FILE,ELSET=EALL\nS\n", "*EL FILE\nS\n"
    ).replace(
        "*END STEP\n",
        "*EL PRINT,ELSET=EALL,GLOBAL=YES\nCOORD,S\n*END STEP\n"
    )
    meta["elemento"]="C3D20R"
    meta["nos"]=len(coordinates)
    meta["anchor_applied_force_x_n"]={
        str(ident):aplicadas.get(ident,0.0) for ident in meta["anchor_nodes"]
    }
    meta["soma_forcas_face_n"]=face_forces
    meta["soma_momentos_face_nm"]={str(i):m for i,m in momento.items()}
    meta["soma_forcas_total_n"]=sum(face_forces.values())
    meta["soma_momentos_total_nm"]=sum(momento.values())
    meta["total_cload_n"]=sum(aplicadas.values())
    return rebuilt, meta


_CABECALHO = re.compile(r"for set\s+eall\s+and time",re.IGNORECASE)


def extrair_tensoes_dat(texto: str, meta: dict) -> dict:
    """Cruza (elem,ip) entre COORD e S no .dat, sem extrapolação nodal."""
    sections: dict[str, dict[tuple[int,int],tuple[float,...]]] = {
        "coord": {}, "stress": {}
    }
    active=None
    for line in texto.splitlines():
        stripped=line.strip().lower()
        if " for set " in stripped and " and time " in stripped:
            active=None
            if _CABECALHO.search(stripped):
                if stripped.startswith(("stresses ", "stress ")):
                    active="stress"
                elif "coord" in stripped:
                    active="coord"
            continue
        if active is None or not stripped:
            continue
        tokens=line.split()
        if len(tokens) < (5 if active=="coord" else 8):
            continue
        try:
            key=(int(tokens[0]),int(tokens[1]))
            limit=3 if active=="coord" else 6
            values=tuple(float(v.replace("D","E").replace("d","E")) for v in tokens[2:2+limit])
        except ValueError:
            continue
        if not all(math.isfinite(v) for v in values):
            raise ValueError("Tensão/coord não finita na saída do CalculiX")
        if key in sections[active]:
            raise ValueError("Registro duplicado elem/IP (incremento inesperado)")
        sections[active][key]=values

    stress=sections["stress"]
    coords=sections["coord"]
    expected=meta["elementos"]*8
    if not stress or not coords or set(stress)!=set(coords) or len(stress)!=expected:
        raise ValueError(
            f"Saída COORD/S incompleta: tensoes={len(stress)}, coord={len(coords)}, esperado={expected}"
        )
    E=float(meta["e_pa"])
    kappa=float(meta["curvatura_m_inv"])
    sigma_max=float(meta["tensao_max_abs_pa"])
    sum_sxx=0.0
    sum_other=0.0
    worst=0.0
    for key,components in stress.items():
        sigma_ref=-E*kappa*coords[key][1]
        diff=components[0]-sigma_ref
        sum_sxx+=diff*diff
        worst=max(worst,abs(diff))
        sum_other+=sum(v*v for v in components[1:])
    return {
        "pontos_integracao":len(stress),
        "erro_rms_sxx_pa":math.sqrt(sum_sxx/expected),
        "erro_rms_sxx_rel":math.sqrt(sum_sxx/expected)/sigma_max,
        "erro_max_sxx_pa":worst,
        "erro_rms_componentes_nao_axiais_pa":math.sqrt(sum_other/(expected*5)),
        "referencia":"sigma_xx=-E*kappa*y calculada em coordenadas de pontos de integracao emitidas pelo solver"
    }


def executar(pasta: str | Path, familia: str="C3D20R", nx: int=2, ny: int=2,nz:int=2,
             solver: str | None=None, **kwargs) -> dict:
    destino=Path(pasta).resolve()
    destino.mkdir(parents=True,exist_ok=True)
    deck,meta=montar_deck(familia,nx,ny,nz,**kwargs)
    job="flexao_"+familia.lower()
    (destino/(job+".inp")).write_text(deck,encoding="utf-8")
    (destino/"entrada.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if solver is None:
        solver=next((bin for bin in ("ccx","ccx_2.21","ccx_2.22","ccx_2.23")
                     if shutil.which(bin)),None)
    if not solver or not shutil.which(solver):
        raise RuntimeError("CalculiX ausente. Use --somente-gerar ou instale calculix-ccx")
    begin=time.perf_counter()
    proc=subprocess.run([solver,"-i",job],cwd=destino,text=True,capture_output=True,timeout=240)
    runtime=time.perf_counter()-begin
    (destino/"solver.log").write_text(proc.stdout+"\n"+proc.stderr,encoding="utf-8")
    dat=destino/(job+".dat")
    if proc.returncode!=0 or not dat.exists():
        detalhe=(proc.stdout+"\n"+proc.stderr).strip()[-2400:]
        raise RuntimeError(
            f"Solver não concluiu: rc={proc.returncode}; dat={dat.exists()}; detalhe:\n{detalhe}"
        )
    raw=dat.read_text(encoding="utf-8",errors="replace")
    disp=flexao_calculix.extrair_dat(raw,meta)
    stress=extrair_tensoes_dat(raw,meta)
    report={
        "modelo":"flexao_pura_comparacao_elementos",
        "familia":familia,
        "solver":shutil.which(solver),
        "tempo_execucao_s":runtime,
        "entrada":meta,
        "deslocamentos":disp,
        "tensoes":stress
    }
    (destino/"comparacao.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return report


def main() -> None:
    p=argparse.ArgumentParser(description="Comparação C3D8 e C3D20R")
    p.add_argument("--elemento",choices=("C3D8","C3D20R"),required=True)
    p.add_argument("--nx",type=int,default=2)
    p.add_argument("--ny",type=int,default=2)
    p.add_argument("--nz",type=int,default=2)
    p.add_argument("--saida",required=True)
    p.add_argument("--somente-gerar",action="store_true")
    p.add_argument("--solver",default=None)
    args=p.parse_args()
    if args.somente_gerar:
        deck,meta=montar_deck(args.elemento,args.nx,args.ny,args.nz)
        out=Path(args.saida)
        out.mkdir(parents=True,exist_ok=True)
        (out/("flexao_"+args.elemento.lower()+".inp")).write_text(deck,encoding="utf-8")
        (out/"entrada.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(json.dumps({"gerado":str(out),"entrada":meta},ensure_ascii=False,indent=2))
        return
    print(json.dumps(executar(args.saida,args.elemento,args.nx,args.ny,args.nz,solver=args.solver),ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
