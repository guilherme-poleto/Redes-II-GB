import numpy as np

import config
from . import codigo_linha, modulacao
from .canal import aplicar_canal

RAJADA_PADRAO = {
    "p_bom_para_ruim": config.RAJADA_P_BOM_PARA_RUIM,
    "p_ruim_para_bom": config.RAJADA_P_RUIM_PARA_BOM,
    "fator_ruido": config.RAJADA_FATOR_RUIDO,
}


def completar(bits, multiplo):
    falta = (-len(bits)) % multiplo
    return np.concatenate([bits, np.zeros(falta, dtype=np.uint8)])


def transmitir(bits, esquema, canal="awgn", ebn0_db=None, rng=None, rajada=None):
    rng = rng if rng is not None else np.random.default_rng()
    rajada = rajada or RAJADA_PADRAO
    eh_modulacao = esquema in modulacao.BITS_POR_SIMBOLO
    n_bits = len(bits)

    if eh_modulacao:
        k = modulacao.BITS_POR_SIMBOLO[esquema]
        sinal_tx = modulacao.modular(completar(bits, k), esquema)
    else:
        sinal_tx = codigo_linha.codificar(bits, esquema)

    if ebn0_db is None or canal == "ideal":
        n0 = 0.0
    else:
        eb = np.sum(np.abs(sinal_tx) ** 2) / n_bits
        n0 = eb / 10 ** (ebn0_db / 10)
    sinal_rx, _ = aplicar_canal(sinal_tx, n0, canal, rng, rajada)

    if eh_modulacao:
        bits_rx = modulacao.demodular(sinal_rx, esquema)
    else:
        bits_rx = codigo_linha.decodificar(sinal_rx, esquema)

    return {"bits_rx": bits_rx[:n_bits]}
