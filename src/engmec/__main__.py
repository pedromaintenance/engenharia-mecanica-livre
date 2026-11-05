"""CLI local e reprodutível da Engenharia Mecânica Livre."""
from __future__ import annotations

import argparse
import json
from . import __version__
from . import calculadoras, catalogo, recursos, descoberta


def _saida(valor: object) -> None:
    print(json.dumps(valor, ensure_ascii=False, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(prog="engmec", description="Catálogo e cálculos didáticos de Engenharia Mecânica")
    parser.add_argument("--versao", action="version", version=__version__)
    comando = parser.add_subparsers(dest="comando", required=True)

    fontes = comando.add_parser("fontes", help="Buscar fontes no catálogo")
    fontes.add_argument("--consulta", default="", help="Termos de busca (acentos opcionais)")
    fontes.add_argument("--dominio", default="", help="Filtro de área")
    fontes.add_argument("--tipo", default="", help="Filtro de tipo")

    novo = comando.add_parser("recursos", help="Pesquisar cursos, portais e ferramentas adicionais")
    novo.add_argument("--tipo", choices=["todos", "cursos", "portais", "ferramentas"], default="todos")
    novo.add_argument("--consulta", default="")
    novo.add_argument("--area", default="")
    novo.add_argument("--nivel", default="")

    scout = comando.add_parser("descobrir", help="Consultar metadados públicos sem importar PDFs")
    scout.add_argument("--fonte", choices=["crossref", "openalex"], required=True)
    scout.add_argument("--consulta", required=True)
    scout.add_argument("--limite", type=int, default=5)
    scout.add_argument("--email", default=None, help="Identificação para API polite pool; não é salva")
    scout.add_argument("--saida", default=None, help="Arquivo JSON opcional de candidatos; não altera catálogos")

    comando.add_parser("validar", help="Verificar consistência do catálogo")
    calcular = comando.add_parser("calcular", help="Executar modelo didático")
    modelos = calcular.add_subparsers(dest="modelo", required=True)

    c = modelos.add_parser("cilindro", help="Força teórica de cilindro")
    c.add_argument("--pressao-bar", type=float, required=True)
    c.add_argument("--diametro-mm", type=float, required=True)
    c.add_argument("--haste-mm", type=float, required=True)
    c.add_argument("--curso", choices=["extensao", "retracao"], default="extensao")

    p = modelos.add_parser("potencia", help="Potência mecânica de eixo")
    p.add_argument("--torque-nm", type=float, required=True)
    p.add_argument("--rpm", type=float, required=True)

    a = modelos.add_parser("disponibilidade", help="Disponibilidade inerente")
    a.add_argument("--mtbf-h", type=float, required=True)
    a.add_argument("--mttr-h", type=float, required=True)

    v = modelos.add_parser("viga", help="Viga biapoiada com carga central")
    v.add_argument("--carga-n", type=float, required=True)
    v.add_argument("--vao-m", type=float, required=True)
    v.add_argument("--e-gpa", type=float, required=True)
    v.add_argument("--largura-mm", type=float, required=True)
    v.add_argument("--altura-mm", type=float, required=True)

    h = modelos.add_parser("bomba", help="Potência hidráulica e potência de acionamento")
    h.add_argument("--pressao-bar", type=float, required=True)
    h.add_argument("--vazao-lpm", type=float, required=True)
    h.add_argument("--eficiencia", type=float, default=1)

    term = modelos.add_parser("conducao", help="Condução plana unidimensional")
    term.add_argument("--k-w-mk", type=float, required=True)
    term.add_argument("--area-m2", type=float, required=True)
    term.add_argument("--delta-t-k", type=float, required=True)
    term.add_argument("--espessura-m", type=float, required=True)

    vib = modelos.add_parser("vibracao", help="Frequência natural massa-mola 1 GDL")
    vib.add_argument("--massa-kg", type=float, required=True)
    vib.add_argument("--rigidez-n-m", type=float, required=True)

    re = modelos.add_parser("reynolds", help="Número de Reynolds adimensional")
    re.add_argument("--densidade-kg-m3", type=float, required=True)
    re.add_argument("--velocidade-m-s", type=float, required=True)
    re.add_argument("--diametro-m", type=float, required=True)
    re.add_argument("--viscosidade-pa-s", type=float, required=True)

    args = parser.parse_args()
    try:
        if args.comando == "validar":
            erros = catalogo.validar()
            erros.extend(recursos.validar())
            _saida({"valido": not erros, "erros": erros,
                    "quantidade_fontes": len(catalogo.carregar()["fontes"]),
                    "recursos": recursos.contagem()})
            if erros:
                parser.exit(status=1)
        elif args.comando == "fontes":
            _saida(catalogo.buscar(args.consulta, args.dominio, args.tipo))
        elif args.comando == "recursos":
            _saida(recursos.buscar(args.tipo, args.consulta, args.area, args.nivel))
        elif args.comando == "descobrir":
            resultado = descoberta.descobrir(args.fonte, args.consulta, args.limite, args.email)
            if args.saida:
                from pathlib import Path
                destino = Path(args.saida)
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                _saida({"arquivo": str(destino), "quantidade": len(resultado["records"])})
            else:
                _saida(resultado)
        elif args.modelo == "cilindro":
            _saida(calculadoras.cilindro_hidraulico(args.pressao_bar, args.diametro_mm, args.haste_mm, args.curso))
        elif args.modelo == "potencia":
            _saida(calculadoras.potencia_mecanica(args.torque_nm, args.rpm))
        elif args.modelo == "disponibilidade":
            _saida(calculadoras.disponibilidade_inerente(args.mtbf_h, args.mttr_h))
        elif args.modelo == "viga":
            _saida(calculadoras.viga_carga_central(args.carga_n, args.vao_m, args.e_gpa, args.largura_mm, args.altura_mm))
        elif args.modelo == "bomba":
            _saida(calculadoras.potencia_hidraulica(args.pressao_bar, args.vazao_lpm, args.eficiencia))
        elif args.modelo == "conducao":
            _saida(calculadoras.conducao_plana(args.k_w_mk, args.area_m2, args.delta_t_k, args.espessura_m))
        elif args.modelo == "vibracao":
            _saida(calculadoras.frequencia_natural(args.massa_kg, args.rigidez_n_m))
        elif args.modelo == "reynolds":
            _saida(calculadoras.numero_reynolds(args.densidade_kg_m3, args.velocidade_m_s, args.diametro_m, args.viscosidade_pa_s))
    except (ValueError, TypeError) as exc:
        parser.exit(status=2, message=f"Erro: {exc}\n")


if __name__ == "__main__":
    main()
