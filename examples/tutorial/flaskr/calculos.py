"""C do MVC: ferramentas financeiras em memória (sem persistência no banco).

Fluxo: Requisição -> Processamento lógico (funções puras) -> Resposta.
Toda a lógica fica aqui; os templates apenas exibem os resultados.
"""
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from flask import Blueprint, flash, render_template, request

bp = Blueprint("calculos", __name__)

CENT = Decimal("0.01")

# Tabela progressiva mensal do IRPF (vigente desde mai/2025, mantida em 2026):
# (limite superior da faixa, alíquota, parcela a deduzir)
TABELA_IRPF = [
    (Decimal("2428.80"), Decimal("0"), Decimal("0")),
    (Decimal("2826.65"), Decimal("0.075"), Decimal("182.16")),
    (Decimal("3751.05"), Decimal("0.15"), Decimal("394.16")),
    (Decimal("4664.68"), Decimal("0.225"), Decimal("675.49")),
    (None, Decimal("0.275"), Decimal("908.73")),
]

# Redutor da Lei 15.270/2025 (em vigor desde 01/01/2026)
LIMITE_ISENCAO = Decimal("5000.00")
LIMITE_REDUTOR = Decimal("7350.00")
REDUTOR_A = Decimal("978.62")
REDUTOR_B = Decimal("0.133145")


def _money(value):
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def _to_decimal(raw, campo):
    try:
        value = Decimal(raw.strip().replace(".", "").replace(",", ".")
                        if "," in raw else raw.strip())
    except (InvalidOperation, AttributeError):
        raise ValueError(f"Valor inválido para {campo}.")
    if value < 0:
        raise ValueError(f"{campo} não pode ser negativo.")
    return value


def calcular_irpf(salario_bruto):
    """Retorna o IRPF mensal estimado sobre o salário bruto informado.

    Simplificação didática: usa o rendimento bruto como base (sem INSS,
    dependentes ou outras deduções).
    """
    salario = Decimal(salario_bruto)

    aliquota, parcela = Decimal("0"), Decimal("0")
    for limite, aliq, ded in TABELA_IRPF:
        if limite is None or salario <= limite:
            aliquota, parcela = aliq, ded
            break

    imposto_tabela = max(Decimal("0"), salario * aliquota - parcela)

    if salario <= LIMITE_ISENCAO:
        redutor = imposto_tabela  # zera o imposto
    elif salario <= LIMITE_REDUTOR:
        redutor = max(Decimal("0"), REDUTOR_A - REDUTOR_B * salario)
    else:
        redutor = Decimal("0")
    redutor = min(redutor, imposto_tabela)

    imposto = imposto_tabela - redutor
    return {
        "salario": _money(salario),
        "aliquota": aliquota * 100,
        "parcela_deduzir": _money(parcela),
        "imposto_tabela": _money(imposto_tabela),
        "redutor": _money(redutor),
        "imposto": _money(imposto),
        "aliquota_efetiva": (
            _money(imposto / salario * 100) if salario > 0 else Decimal("0.00")
        ),
        "liquido": _money(salario - imposto),
    }


def calcular_13o_proporcional(salario_base, meses):
    """13º proporcional aproximado: salário / 12 * meses trabalhados."""
    if not 0 <= meses <= 12:
        raise ValueError("Meses trabalhados deve estar entre 0 e 12.")
    salario = Decimal(salario_base)
    valor = salario / 12 * meses
    return {
        "salario": _money(salario),
        "meses": meses,
        "avo": _money(salario / 12),
        "decimo_terceiro": _money(valor),
    }


@bp.route("/painel", methods=("GET", "POST"))
def painel():
    resultado_irpf = resultado_13 = None

    if request.method == "POST":
        ferramenta = request.form.get("ferramenta")
        try:
            if ferramenta == "irpf":
                salario = _to_decimal(request.form.get("salario_bruto", ""),
                                      "salário bruto")
                resultado_irpf = calcular_irpf(salario)
            elif ferramenta == "rescisao":
                salario = _to_decimal(request.form.get("salario_base", ""),
                                      "salário base")
                meses = int(request.form.get("meses", ""))
                resultado_13 = calcular_13o_proporcional(salario, meses)
            else:
                flash("Ferramenta desconhecida.", "danger")
        except (ValueError, InvalidOperation) as e:
            flash(str(e) if isinstance(e, ValueError) and not str(e).startswith(
                "invalid literal") else "Preencha todos os campos com valores válidos.",
                "danger")

    return render_template(
        "calculos/index.html",
        irpf=resultado_irpf,
        decimo=resultado_13,
        form=request.form,
    )
