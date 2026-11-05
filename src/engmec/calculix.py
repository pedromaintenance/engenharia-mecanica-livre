"""Gerador e verificador de benchmark CalculiX C3D8 (sem dependências externas).

As unidades do deck são N, m, Pa. A geometria é quadrada e homogênea,
com comprimento axial x. Não corresponde a modelo de máquina real.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
from pathlib import Path

from .fem_barra import barra_axial


def _positivo(nome: str, valor: float) -> float:
    v = float(valor)
    if not math.isfinite(v) or v <= 0:
        raise ValueError(f"{nome} deve ser positivo e finito")
    return v


def montar_deck(
    comprimento_m: float = 2.0, area_mm2: float = 1000.0,
    e_gpa: float = 200.0, forca_n: float = 10000.0,
    poisson: float = 0.30, nx: int = 4,
    ny: int = 2, nz: int = 2,
) -> tuple[str, dict]:
    """Retorna deck .inp e metadados, com malha C3D8 orientada positivamente.

    A carga da face livre usa pesos nodais consistentes de área.
    Apoios mínimos: Ux=0 na face x=0; Uy/Uz no centro dessa face;
    Uz em um segundo nó sobre z=0 para bloquear giro rígido em x.
    """
    L = _positivo("comprimento_m", comprimento_m)
    A = _positivo("area_mm2", area_mm2) * 1e-6
    E = _positivo("e_gpa", e_gpa) * 1e9
    F = float(forca_n)
    nu = float(poisson)
    if not math.isfinite(F) or not math.isfinite(nu) or not -0.49 < nu < 0.49:
        raise ValueError("forca_n e poisson devem ser finitos; -0.49 < nu < 0.49")
    if any(isinstance(v, bool) or not isinstance(v, int) for v in (nx, ny, nz)):
        raise ValueError("nx, ny, nz devem ser inteiros")
    if not 1 <= nx <= 128 or ny < 2 or nz < 2 or ny % 2 or nz % 2 or ny > 16 or nz > 16:
        raise ValueError("nx entre 1-128 e ny/nz pares entre 2-16")
    largura = math.sqrt(A)
    def nid(i: int, j: int, k: int) -> int:
        return 1 + i * (ny + 1) * (nz + 1) + k * (ny + 1) + j

    linhas = [
        "** Engenharia Mecanica Livre - benchmark axial C3D8 em SI",
        f"** L={L:.12g}m area={A:.12g}m2 E={E:.12g}Pa nu={nu:.6g} F={F:.12g}N",
        "*NODE"
    ]
    for i in range(nx + 1):
        for k in range(nz + 1):
            for j in range(ny + 1):
                x = L * i / nx
                y = largura * (j / ny - 0.5)
                z = largura * (k / nz - 0.5)
                linhas.append(f"{nid(i,j,k)}, {x:.15g}, {y:.15g}, {z:.15g}")

    linhas.append("*ELEMENT,TYPE=C3D8,ELSET=EALL")
    eid = 0
    for i in range(nx):
        for k in range(nz):
            for j in range(ny):
                eid += 1
                corners = [
                    nid(i,j,k), nid(i+1,j,k), nid(i+1,j+1,k), nid(i,j+1,k),
                    nid(i,j,k+1), nid(i+1,j,k+1), nid(i+1,j+1,k+1), nid(i,j+1,k+1)
                ]
                linhas.append(f"{eid}, " + ", ".join(str(n) for n in corners))
    linhas.extend([
        "*NSET,NSET=ROOT",
        ", ".join(str(nid(0,j,k)) for k in range(nz+1) for j in range(ny+1)),
        "*NSET,NSET=TIPCENTER",
        str(nid(nx,ny//2,nz//2)),
        "*MATERIAL,NAME=STEEL",
        "*ELASTIC",
        f"{E:.15g}, {nu:.15g}",
        "*SOLID SECTION,ELSET=EALL,MATERIAL=STEEL",
        "*BOUNDARY",
        "ROOT,1,1",
        f"{nid(0,ny//2,nz//2)},2,3",
        f"{nid(0,ny,nz//2)},3,3",
        "*STEP",
        "*STATIC",
        "*CLOAD",
    ])
    # Integração consistente da pressão F/A na face x=L: cada nó
    # recebe a área tributária dos quadriláteros adjacentes.
    cargas = {}
    for k in range(nz + 1):
        for j in range(ny + 1):
            weight_y = 0.5 if j in (0, ny) else 1.0
            weight_z = 0.5 if k in (0, nz) else 1.0
            carga = F * weight_y * weight_z / (ny * nz)
            cargas[nid(nx,j,k)] = carga
            linhas.append(f"{nid(nx,j,k)}, 1, {carga:.15g}")
    linhas.extend([
        "*NODE PRINT,NSET=TIPCENTER",
        "U",
        "*NODE PRINT,NSET=ROOT",
        "RF",
        "*END STEP"
    ])
    meta = {
        "elemento": "C3D8",
        "unidades": "N,m,Pa",
        "elementos": nx * ny * nz,
        "nos": (nx + 1) * (ny + 1) * (nz + 1),
        "nx": nx, "ny": ny, "nz": nz,
        "tip_node": nid(nx,ny//2,nz//2),
        "root_nodes": [nid(0,j,k) for k in range(nz+1) for j in range(ny+1)],
        "total_forca_aplicada_n": sum(cargas.values()),
        "forca_referencia_n": F,
        "deslocamento_analitico_m": F * L / (E * A),
        "poisson": nu,
    }
    return "\n".join(linhas) + "\n", meta


_LINHA = re.compile(
    r"^\s*(\d+)\s+([+-]?(?:\d+(?:\.\d*)?|\.\d+)[EeDd]?[+-]?\d*)\s+"
    r"([+-]?(?:\d+(?:\.\d*)?|\.\d+)[EeDd]?[+-]?\d*)\s+"
    r"([+-]?(?:\d+(?:\.\d*)?|\.\d+)[EeDd]?[+-]?\d*)\s*$"
)


def extrair_dat(texto: str, meta: dict) -> dict:
    """Lê *NODE PRINT U e RF; rejeita resultados ausentes ou não finitos."""
    bloco = ""
    desloc = {}
    reacoes = {}
    for linha in texto.splitlines():
        l = linha.strip().lower()
        if l.startswith("displacements ") and "for set tipcenter" in l:
            bloco = "u"
            continue
        if l.startswith("reaction forces ") and "for set root" in l:
            bloco = "rf"
            continue
        if " for set " in l and (" and time " in l):
            bloco = ""
            continue
        m = _LINHA.match(linha)
        if not m or not bloco:
            continue
        try:
            valores = [float(t.replace("D", "E").replace("d", "E")) for t in m.groups()[1:]]
        except ValueError as exc:
            raise ValueError("Valores ilegíveis no .dat") from exc
        if not all(math.isfinite(v) for v in valores):
            raise ValueError("Saída não finita do solver")
        (desloc if bloco == "u" else reacoes)[int(m.group(1))] = valores
    tip = meta["tip_node"]
    if tip not in desloc:
        raise ValueError("Saída U do nó TIPCENTER ausente no arquivo .dat")
    if any(node not in reacoes for node in meta["root_nodes"]):
        raise ValueError("Saída RF incompleta para o conjunto ROOT")
    ux = desloc[tip][0]
    rf = sum(reacoes[n][0] for n in meta["root_nodes"])
    expected = meta["deslocamento_analitico_m"]
    F = meta["forca_referencia_n"]
    return {
        "ux_ponta_m": ux, "reacao_apoio_n": rf,
        "referencia_analitica_m": expected,
        "erro_deslocamento_relativo": abs(ux - expected) / max(abs(expected), 1e-15),
        "erro_equilibrio_relativo": abs(rf + F) / max(abs(F), 1e-12),
        "estado": "resultado_de_solver_externo"
    }


def executar(
    pasta: str | Path, *, nx: int = 4, ny: int = 2, nz: int = 2,
    solver: str | None = None, **parametros
) -> dict:
    """Gera .inp, executa ccx em subprocesso controlado e devolve JSON verificável."""
    destino = Path(pasta).resolve()
    destino.mkdir(parents=True, exist_ok=True)
    deck, meta = montar_deck(nx=nx, ny=ny, nz=nz, **parametros)
    arquivo = destino / "barra_c3d8.inp"
    arquivo.write_text(deck, encoding="utf-8")
    (destino / "entrada.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    if solver is None:
        solver = next((candidate for candidate in (
            "ccx", "ccx_2.23", "ccx_2.22", "ccx_2.21", "ccx_2.20", "ccx_2.19"
        ) if shutil.which(candidate)), None)
    if not solver or not shutil.which(solver):
        raise RuntimeError("CalculiX (ccx) indisponível: instale calculix-ccx para executar")
    cmd = [solver, "-i", arquivo.stem]
    res = subprocess.run(cmd, cwd=destino, capture_output=True, text=True, timeout=120)
    (destino / "solver.log").write_text(res.stdout + "\n" + res.stderr, encoding="utf-8")
    dat = destino / (arquivo.stem + ".dat")
    if res.returncode != 0 or not dat.exists():
        raise RuntimeError(f"CalculiX falhou: exit={res.returncode}, arquivo .dat presente={dat.exists()}")
    resultado = extrair_dat(dat.read_text(encoding="utf-8", errors="replace"), meta)
    relatorio = {
        "modelo": "barra_axial_3d_calculix_c3d8",
        "executavel": shutil.which(solver),
        "entrada": meta, "resultado": resultado,
        "comparacao_1d": barra_axial(
            parametros.get("comprimento_m", 2.0),
            parametros.get("area_mm2", 1000.0),
            parametros.get("e_gpa", 200.0),
            parametros.get("forca_n", 10000.0), 0.0, nx
        )["resultados_si"]["deslocamento_ponta_m"]
    }
    (destino / "comparacao.json").write_text(json.dumps(relatorio, indent=2) + "\n", encoding="utf-8")
    return relatorio


def main() -> None:
    p = argparse.ArgumentParser(description="Benchmark CalculiX C3D8 axial")
    p.add_argument("--saida", default="build/calculix")
    p.add_argument("--nx", type=int, default=4)
    p.add_argument("--ny", type=int, default=2)
    p.add_argument("--nz", type=int, default=2)
    p.add_argument("--solver", default=None)
    p.add_argument("--somente-gerar", action="store_true")
    p.add_argument("--tolerancia", type=float, default=0.02)
    args = p.parse_args()
    if args.tolerancia <= 0 or args.tolerancia >= 1:
        p.error("tolerancia deve estar entre 0 e 1")
    if args.somente_gerar:
        deck, meta = montar_deck(nx=args.nx, ny=args.ny, nz=args.nz)
        dest = Path(args.saida)
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "barra_c3d8.inp").write_text(deck, encoding="utf-8")
        (dest / "entrada.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"gerado": str(dest), "meta": meta}, indent=2))
        return
    result = executar(args.saida, nx=args.nx, ny=args.ny, nz=args.nz, solver=args.solver)
    print(json.dumps(result, indent=2))
    if any(result["resultado"][k] > args.tolerancia for k in ("erro_deslocamento_relativo", "erro_equilibrio_relativo")):
        p.exit(1, "Benchmark externo fora da tolerância\n")


if __name__ == "__main__":
    main()
