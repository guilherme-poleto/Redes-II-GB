import numpy as np

BITS_POR_SIMBOLO = {"BPSK": 1, "QPSK": 2, "16QAM": 4}

_GRAY_2BITS = {(0, 0): -3, (0, 1): -1, (1, 1): 1, (1, 0): 3}


def criar_constelacao(nome):
    if nome == "BPSK":
        return np.array([-1 + 0j, +1 + 0j])

    if nome == "QPSK":
        pontos = []
        for indice in range(4):
            b0, b1 = (indice >> 1) & 1, indice & 1
            pontos.append((2 * b0 - 1) + 1j * (2 * b1 - 1))
        return np.array(pontos) / np.sqrt(2)

    if nome == "16QAM":
        pontos = []
        for indice in range(16):
            b = [(indice >> s) & 1 for s in (3, 2, 1, 0)]
            i = _GRAY_2BITS[(b[0], b[1])]
            q = _GRAY_2BITS[(b[2], b[3])]
            pontos.append(i + 1j * q)
        return np.array(pontos) / np.sqrt(10)

    raise ValueError(f"modulação desconhecida: {nome}")


CONSTELACOES = {nome: criar_constelacao(nome) for nome in BITS_POR_SIMBOLO}


def modular(bits, nome):
    k = BITS_POR_SIMBOLO[nome]
    grupos = bits.reshape(-1, k)
    pesos = 2 ** np.arange(k - 1, -1, -1)
    indices = grupos @ pesos
    return CONSTELACOES[nome][indices]


def demodular(recebido, nome):
    k = BITS_POR_SIMBOLO[nome]
    constelacao = CONSTELACOES[nome]
    distancias = np.abs(recebido[:, None] - constelacao[None, :]) ** 2
    indices = np.argmin(distancias, axis=1)
    deslocamentos = np.arange(k - 1, -1, -1)
    bits = (indices[:, None] >> deslocamentos) & 1
    return bits.reshape(-1).astype(np.uint8)
