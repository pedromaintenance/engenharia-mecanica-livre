"""CLI local e reprodutível da Engenharia Mecânica Livre."""
from __future__ import annotations

import argparse
import json
from . import __version__
from . import calculadoras, catalogo, recursos


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
        elif args.modelo == "cilindro":
            _saida(calculadoras.cilindro_hidraulico(args.pressao_bar, args.diametro_mm, args.haste_mm, args.curso))
        elif args.modelo == "potencia":
            _saida(calculadoras.potencia_mecanica(args.torque_nm, args.rpm))
        elif args.modelo == "disponibilidade":
            _saida(calculadoras.disponibilidade_inerente(args.mtbf_h, args.mttr_h))
        elif args.modelo == "viga":
            _saida(calculadoras.viga_carga_central(args.carga_n, args.vao_m, args.e_gpa, args.largura_mm, args.altura_mm))
    except (ValueError, TypeError) as exc:
        parser.exit(status=2, message=f"Erro: {exc}\n")


if __name__ == "__main__":
    main()
