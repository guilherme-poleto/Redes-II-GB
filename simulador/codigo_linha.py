import numpy as np


def manchester_codificar(bits):
    sinal = np.empty(2 * len(bits))
    sinal[0::2] = np.where(bits == 1, -1.0, 1.0)
    sinal[1::2] = -sinal[0::2]
    return sinal


def manchester_decodificar(r):
    primeira, segunda = r[0::2], r[1::2]
    return (segunda - primeira > 0).astype(np.uint8)


def ami_codificar(bits):
    sinal = np.zeros(len(bits))
    posicoes_uns = np.flatnonzero(bits == 1)
    sinal[posicoes_uns] = np.where(np.arange(len(posicoes_uns)) % 2 == 0, 1.0, -1.0)
    return sinal


def ami_decodificar(r):
    return (np.abs(r) > 0.5).astype(np.uint8)


CODIGOS = {
    "Manchester": (manchester_codificar, manchester_decodificar),
    "AMI": (ami_codificar, ami_decodificar),
}


def codificar(bits, nome):
    return CODIGOS[nome][0](bits)


def decodificar(r, nome):
    return CODIGOS[nome][1](r)
