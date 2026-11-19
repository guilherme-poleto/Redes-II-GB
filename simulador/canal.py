import numpy as np


def ruido_gaussiano(n, n0, complexo, rng):
    desvio = np.sqrt(n0 / 2)
    if complexo:
        return desvio * (rng.standard_normal(n) + 1j * rng.standard_normal(n))
    return desvio * rng.standard_normal(n)


def estados_gilbert_elliott(n, p_bom_para_ruim, p_ruim_para_bom, rng):
    ruim = np.zeros(n, dtype=bool)
    posicao, estado_ruim = 0, False
    while posicao < n:
        p_sair = p_ruim_para_bom if estado_ruim else p_bom_para_ruim
        duracao = rng.geometric(p_sair)
        if estado_ruim:
            ruim[posicao:posicao + duracao] = True
        posicao += duracao
        estado_ruim = not estado_ruim
    return ruim


def aplicar_canal(sinal, n0, tipo, rng, rajada=None):
    complexo = np.iscomplexobj(sinal)
    n = len(sinal)

    if tipo == "ideal" or n0 == 0:
        return sinal.copy(), None

    if tipo == "awgn":
        return sinal + ruido_gaussiano(n, n0, complexo, rng), None

    if tipo == "rajadas":
        ruim = estados_gilbert_elliott(n, rajada["p_bom_para_ruim"],
                                       rajada["p_ruim_para_bom"], rng)
        ruido = ruido_gaussiano(n, n0, complexo, rng)
        ruido[ruim] *= np.sqrt(rajada["fator_ruido"])
        return sinal + ruido, ruim

    raise ValueError(f"canal desconhecido: {tipo}")
