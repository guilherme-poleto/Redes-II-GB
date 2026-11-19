import numpy as np

import config
from simulador import fonte, metricas
from simulador.sistema import transmitir

ESQUEMAS = config.CODIGOS_LINHA + config.MODULACOES
CENARIOS = [("ideal", None), ("awgn", 30), ("awgn", 20)]


def main():
    bits = fonte.texto_para_bits(config.MENSAGEM)
    print(f"Mensagem: \"{config.MENSAGEM}\" ({len(bits)} bits)\n")
    print(f"{'esquema':12s}{'canal':10s}{'Eb/N0':>8s}{'erros':>8s}  resultado")
    falhas = 0
    for esquema in ESQUEMAS:
        for canal, snr in CENARIOS:
            r = transmitir(bits, esquema, canal, snr, np.random.default_rng(1))
            erros, _ = metricas.contar_erros(bits, r["bits_rx"])
            recuperada = fonte.bits_para_texto(r["bits_rx"]) == config.MENSAGEM
            falhas += not recuperada
            snr_txt = "-" if snr is None else f"{snr} dB"
            print(f"{esquema:12s}{canal:10s}{snr_txt:>8s}{erros:8d}  "
                  f"{'mensagem recuperada' if recuperada else 'DIVERGENCIA'}")
    print()
    print("Consistência OK" if falhas == 0 else f"{falhas} casos com divergência")


if __name__ == "__main__":
    main()
