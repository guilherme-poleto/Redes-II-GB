import numpy as np

from .modulacao import BITS_POR_SIMBOLO


def contar_erros(bits_tx, bits_rx):
    erros = int(np.sum(bits_tx != bits_rx))
    return erros, erros / len(bits_tx)


def posicoes_erradas(bits_tx, bits_rx):
    return np.flatnonzero(bits_tx != bits_rx)


def eficiencia_espectral(esquema):
    if esquema in BITS_POR_SIMBOLO:
        return float(BITS_POR_SIMBOLO[esquema])
    bits_por_chip = {"AMI": 1.0, "Manchester": 0.5}[esquema]
    return 2 * bits_por_chip

