"""Benchmark de flexão pura em elasticidade 3D com CalculiX C3D8.

Trações axiais lineares em y nas duas extremidades, extremidades laterais livres.
A referência é solução exata de elasticidade isotrópica infinitesimal, não apenas
a equação de flecha de Euler-Bernoulli. Unidade: N, m, Pa.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
from pathlib import Path


def _positivo(nome: str, valor: float) -> float:
    valor = float(valor)
    if not math.isfinite(valor) or valor <= 0:
        raise ValueError(f"{nome}: número positivo e finito necessário")
    return valor


def deslocamento_exato(x: float, y: float, z: float,
                        curvatura: float, poisson: float) -> tuple[float, float, float]:
    """Solução 3D: sigma_xx=-E*k*y; outras tensões nulas."""
    k = curvatura
    nu = poisson
    return (
        -k * x * y,
        k * x * x / 2 + nu * k * (y * y - z * z) / 2,
        nu * k * y * z,
    )


def montar_deck(
    nx: int = 2, ny: int = 2, nz: int = 2,
    comprimento_m: float = 0.2, largura_m: float = 0.1,
    e_gpa: float = 200.0, poisson: float = 0.3,
    curvatura_m_inv: float = 0.01
) -> tuple[str, dict]:
    """Malha cúbica C3D8; cargas nodais equivalentes a traction sigma*n.

    A tração de flexão é proporcional a y. Integração Gauss 2x2 na face
    exata para N_i(y,z)*y; os balanços de força/momento são verificados.
    Restrições 6 DOF anulam só os movimentos rígidos e têm u_exato=0.
    """
    if any(isinstance(v, bool) or not isinstance(v, int) for v in (nx, ny, nz)):
        raise ValueError("nx,ny,nz inteiros obrigatórios")
    if not (2 <= nx <= 32 and 2 <= ny <= 16 and 2 <= nz <= 16):
        raise ValueError("nx entre 2-32, ny/nz entre 2-16")
    if ny % 2 or nz % 2:
        raise ValueError("ny e nz devem ser pares para manter nós na linha neutra")
    L = _positivo("comprimento_m", comprimento_m)
    b = _positivo("largura_m", largura_m)
    E = _positivo("e_gpa", e_gpa) * 1e9
    nu = float(poisson)
    kappa = float(curvatura_m_inv)
    if not math.isfinite(nu) or not -0.49 < nu < 0.49:
        raise ValueError("poisson deve estar entre -0.49 e 0.49")
    if not math.isfinite(kappa) or kappa == 0.0:
        raise ValueError("curvatura_m_inv não pode ser zero nem não finita")
    I = b ** 4 / 12
    M = E * kappa * I

    def nid(i: int, j: int, k: int) -> int:
        return 1 + i * (ny + 1) * (nz + 1) + k * (ny + 1) + j

    def ycoord(j: int) -> float:
        return b * (j / ny - 0.5)

    def zcoord(k: int) -> float:
        return b * (k / nz - 0.5)

    linhas = [
        "** EML manufactured pure bending - three-dimensional exact elasticity",
        "** all units N, m, Pa; traction sigma_xx=-E*kappa*y on end faces",
        f"** L={L:.12g} b={b:.12g} E={E:.12g} nu={nu:.8g} kappa={kappa:.12g}",
        "*NODE"
    ]
    for i in range(nx + 1):
        for kk in range(nz + 1):
            for j in range(ny + 1):
                linhas.append(
                    f"{nid(i,j,kk)}, {i*L/nx:.15g}, {ycoord(j):.15g}, {zcoord(kk):.15g}"
                )
    linhas.append("*ELEMENT,TYPE=C3D8,ELSET=EALL")
    ei = 0
    for i in range(nx):
        for kk in range(nz):
            for j in range(ny):
                ei += 1
                ns = [nid(i,j,kk), nid(i+1,j,kk), nid(i+1,j+1,kk), nid(i,j+1,kk),
                      nid(i,j,kk+1), nid(i+1,j,kk+1), nid(i+1,j+1,kk+1), nid(i,j+1,kk+1)]
                linhas.append(f"{ei}, "+", ".join(map(str, ns)))
    root_center = nid(0, ny//2, nz//2)
    root_y = nid(0, ny, nz//2)
    root_z = nid(0, ny//2, nz)
    tip_center = nid(nx, ny//2, nz//2)
    tip_edge = nid(nx, ny, nz//2)
    anchors = [root_center, root_y, root_z]
    linhas.extend([
        "*NSET,NSET=TIPCENTER", str(tip_center),
        "*NSET,NSET=TIPEDGE", str(tip_edge),
        "*NSET,NSET=ANCHORS", ", ".join(map(str, anchors)),
        "*MATERIAL,NAME=ISOTROPIC",
        "*ELASTIC", f"{E:.15g}, {nu:.15g}",
        "*SOLID SECTION,ELSET=EALL,MATERIAL=ISOTROPIC",
        "*BOUNDARY",
        f"{root_center},1,3",
        f"{root_y},1,1",
        f"{root_y},3,3",
        f"{root_z},1,1",
        "*STEP",
        "*STATIC",
        "*CLOAD"
    ])
    # Integrais consistentes nas faces x=0 e x=L: N_i(y,z) * sigma_xx * n_x.
    # Gauss-Legendre 2 pontos em cada quad de face, exato para polinômio grau <=3.
    loads = {}
    total_forces = {0: 0.0, nx: 0.0}
    moments_z = {0: 0.0, nx: 0.0}
    qnodes = (-1 / math.sqrt(3), 1 / math.sqrt(3))
    dy, dz = b/ny, b/nz
    for face_i, normal in ((0, -1), (nx, +1)):
        for kk in range(nz):
            for j in range(ny):
                y0 = ycoord(j)
                # N_i on quad in normalized (xi,eta), x traction sigma_xx * nx.
                for xi in qnodes:
                    for eta in qnodes:
                        yg = y0 + dy * (xi + 1) / 2
                        traction_x = normal * (-E * kappa * yg)
                        jac = dy * dz / 4
                        phi = (
                            ((1-xi)*(1-eta)/4, j, kk),
                            ((1+xi)*(1-eta)/4, j+1, kk),
                            ((1+xi)*(1+eta)/4, j+1, kk+1),
                            ((1-xi)*(1+eta)/4, j, kk+1)
                        )
                        for shape, jj, kkk in phi:
                            idx = nid(face_i, jj, kkk)
                            loads[idx] = loads.get(idx, 0.0) + traction_x * shape * jac
        for kk in range(nz+1):
            for j in range(ny+1):
                idx=nid(face_i,j,kk)
                force=loads.get(idx,0.0)
                total_forces[face_i]+=force
                moments_z[face_i]+=-ycoord(j)*force
                if abs(force)>1e-15:
                    linhas.append(f"{idx}, 1, {force:.15g}")
    linhas.extend([
        "*NODE PRINT,NSET=TIPCENTER", "U",
        "*NODE PRINT,NSET=TIPEDGE", "U",
        "*NODE PRINT,NSET=ANCHORS", "RF",
        "*EL FILE,ELSET=EALL", "S",
        "*END STEP"
    ])
    u_center = deslocamento_exato(L, 0, 0, kappa, nu)
    u_edge = deslocamento_exato(L, b/2, 0, kappa, nu)
    meta = {
        "modelo": "flexao_pura_3d_elasticidade",
        "elemento": "C3D8",
        "unidades": "N,m,Pa",
        "nx": nx, "ny": ny, "nz": nz,
        "elementos": nx*ny*nz,
        "nos": (nx+1)*(ny+1)*(nz+1),
        "comprimento_m": L, "largura_m": b,
        "e_pa": E, "poisson": nu,
        "curvatura_m_inv": kappa,
        "momento_referencia_nm": M,
        "tensao_max_abs_pa": abs(E*kappa*b/2),
        "tip_center_node": tip_center,
        "tip_edge_node": tip_edge,
        "anchor_nodes": anchors,
        "anchor_applied_force_x_n": {str(node): loads.get(node, 0.0) for node in anchors},
        "soma_forcas_face_n": {str(face_i): f for face_i,f in total_forces.items()},
        "soma_momentos_face_nm": {str(face_i): v for face_i,v in moments_z.items()},
        "soma_forcas_total_n": sum(total_forces.values()),
        "soma_momentos_total_nm": sum(moments_z.values()),
        "u_tipcenter_referencia_m": list(u_center),
        "u_tipedge_referencia_m": list(u_edge),
    }
    if not math.isclose(moments_z[nx], M, rel_tol=2e-12, abs_tol=1e-6):
        raise ValueError("Momento de ponta inconsistente com solução analítica")
    if not math.isclose(moments_z[0], -M, rel_tol=2e-12, abs_tol=1e-6):
        raise ValueError("Momento de raiz inconsistente com solução analítica")
    return "\n".join(linhas)+"\n", meta


_RE = re.compile(
    r"^\s*(\d+)\s+([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+)?)\s+"
    r"([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+)?)\s+"
    r"([+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[EeDd][+-]?\d+)?)\s*$"
)
_HDR = re.compile(r"for set\s+([a-z0-9_]+)\s+and time", re.I)


def extrair_dat(texto: str, meta: dict) -> dict:
    """Interpreta saídas reais U e RF, rejeitando conjuntos incompletos."""
    bloco = None
    sets = {"tipcenter": {}, "tipedge": {}, "anchors": {}}
    for linha in texto.splitlines():
        low = linha.strip().lower()
        name = _HDR.search(low)
        if name:
            key = name.group(1)
            if key in ("tipcenter", "tipedge") and low.startswith("displacements "):
                bloco = key
            elif key == "anchors" and low.startswith(("forces ", "reaction forces ")):
                bloco = key
            else:
                bloco = None
            continue
        match = _RE.match(linha)
        if bloco and match:
            vals = [float(v.replace("d","e").replace("D","E")) for v in match.groups()[1:]]
            if not all(math.isfinite(v) for v in vals):
                raise ValueError("CalculiX devolveu valores não finitos")
            sets[bloco][int(match.group(1))] = vals
    cid=meta["tip_center_node"]
    eid=meta["tip_edge_node"]
    if cid not in sets["tipcenter"] or eid not in sets["tipedge"]:
        raise ValueError("Deslocamentos da ponta incompletos")
    if any(i not in sets["anchors"] for i in meta["anchor_nodes"]):
        raise ValueError("Reações dos apoios incompletas")
    uc=sets["tipcenter"][cid]
    ue=sets["tipedge"][eid]
    reference_c=meta["u_tipcenter_referencia_m"]
    reference_e=meta["u_tipedge_referencia_m"]
    # Critérios de erro não trivial: Uy centro e Ux borda, pela elasticidade.
    uy=uc[1]
    ux=ue[0]
    eps=1e-16
    # CalculiX RF = reação + CLOAD nodal nos nós do conjunto.
    # Como há tração na raiz, é obrigatório descontar CLOAD desses nós.
    reacoes = []
    for axis in range(3):
        rf = sum(sets["anchors"][node][axis] for node in meta["anchor_nodes"])
        if axis == 0:
            rf -= sum(meta["anchor_applied_force_x_n"][str(node)] for node in meta["anchor_nodes"])
        reacoes.append(rf)
    rfabs=max(map(abs,reacoes))
    force_scale=abs(meta["momento_referencia_nm"])/meta["largura_m"]
    return {
        "uy_centro_ponta_m": uy,
        "ux_borda_ponta_m": ux,
        "referencia_uy_centro_m": reference_c[1],
        "referencia_ux_borda_m": reference_e[0],
        "erro_uy_rel": abs(uy-reference_c[1])/max(abs(reference_c[1]),eps),
        "erro_ux_rel": abs(ux-reference_e[0])/max(abs(reference_e[0]),eps),
        "soma_reacoes_n": reacoes,
        "reacao_norm_max_rel": rfabs/max(force_scale,eps),
        "status": "obtido_de_saida_calculix"
    }


def executar(pasta: str | Path, *, nx: int=4, ny: int=4, nz: int=4,
             solver: str | None=None, **kwargs) -> dict:
    destino=Path(pasta).resolve()
    destino.mkdir(parents=True,exist_ok=True)
    deck,meta=montar_deck(nx=nx,ny=ny,nz=nz,**kwargs)
    job="flexao_pura_c3d8"
    (destino/(job+".inp")).write_text(deck,encoding="utf-8")
    (destino/"entrada.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if solver is None:
        solver=next((x for x in ("ccx","ccx_2.21","ccx_2.22","ccx_2.23") if shutil.which(x)),None)
    if not solver or not shutil.which(solver):
        raise RuntimeError("CalculiX não instalado; é possível gerar .inp sem executá-lo")
    out=subprocess.run([solver,"-i",job],cwd=destino,text=True,capture_output=True,timeout=240)
    (destino/"solver.log").write_text(out.stdout+"\n"+out.stderr,encoding="utf-8")
    dat=destino/(job+".dat")
    if out.returncode or not dat.exists():
        raise RuntimeError(f"CalculiX não concluiu o job: exit={out.returncode}, dat={dat.exists()}")
    resultado=extrair_dat(dat.read_text(encoding="utf-8",errors="replace"),meta)
    rep={"modelo":"flexao_pura_calculix_3d_c3d8","executavel":shutil.which(solver),
         "entrada":meta,"resultado":resultado}
    (destino/"comparacao.json").write_text(json.dumps(rep,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return rep


def main() -> None:
    p=argparse.ArgumentParser(description="Benchmark de flexão pura 3D - CalculiX")
    p.add_argument("--saida",default="build/flexao-calculix")
    p.add_argument("--nx",type=int,default=4)
    p.add_argument("--ny",type=int,default=4)
    p.add_argument("--nz",type=int,default=4)
    p.add_argument("--somente-gerar",action="store_true")
    p.add_argument("--solver")
    p.add_argument("--tolerancia",type=float,default=None,
                   help="Erro relativo máximo de Uy centro e Ux borda; opcional")
    args=p.parse_args()
    if args.tolerancia is not None and not 0<args.tolerancia<1:
        p.error("tolerancia deve estar em (0,1)")
    if args.somente_gerar:
        deck,meta=montar_deck(nx=args.nx,ny=args.ny,nz=args.nz)
        dest=Path(args.saida)
        dest.mkdir(parents=True,exist_ok=True)
        (dest/"flexao_pura_c3d8.inp").write_text(deck,encoding="utf-8")
        (dest/"entrada.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        print(json.dumps({"gerado":str(dest),"entrada":meta},ensure_ascii=False,indent=2))
        return
    data=executar(args.saida,nx=args.nx,ny=args.ny,nz=args.nz,solver=args.solver)
    print(json.dumps(data,ensure_ascii=False,indent=2))
    if args.tolerancia is not None:
        vals=data["resultado"]
        if max(vals["erro_uy_rel"],vals["erro_ux_rel"])>args.tolerancia:
            p.exit(1,"Erro de flexão acima da tolerância\n")


if __name__=="__main__":
    main()
