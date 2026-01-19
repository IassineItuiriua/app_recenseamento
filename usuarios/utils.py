from datetime import date


def calcular_idade(data_nascimento):
    """
    Calcula a idade em anos completos.
    """
    if not data_nascimento:
        return None

    hoje = date.today()
    return hoje.year - data_nascimento.year - (
        (hoje.month, hoje.day) < (data_nascimento.month, data_nascimento.day)
    )

