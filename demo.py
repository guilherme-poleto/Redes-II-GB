import argparse

import numpy as np

import config
from simulador import fonte, metricas
from simulador.sistema import transmitir

ESQUEMAS = config.CODIGOS_LINHA + config.MODULACOES


def mostrar_erros(bits_tx, bits_rx, limite=8):
    errados = metricas.posicoes_erradas(bits_tx, bits_rx)
    caracteres = sorted(set(errados // 8))
    for c in caracteres[:limite]:
        tx = bits_tx[8 * c: 8 * c + 8]
        rx = bits_rx[8 * c: 8 * c + 8]
        ch_tx = fonte.texto_imprimivel(fonte.bits_para_texto(tx))
        ch_rx = fonte.texto_imprimivel(fonte.bits_para_texto(rx))
        marca = "".join("^" if a != b else " " for a, b in zip(tx, rx))
        prefixo = f"    caractere {c:3d}: '{ch_tx}' "
        print(f"{prefixo}{''.join(map(str, tx))}  ->  '{ch_rx}' {''.join(map(str, rx))}")
        print(" " * len(prefixo) + marca)
    if len(caracteres) > limite:
        print(f"    ... e mais {len(caracteres) - limite} caracteres com erro")


def caso_detalhado(esquema, canal, snr, semente):
    bits = fonte.texto_para_bits(config.MENSAGEM)
    r = transmitir(bits, esquema, canal, snr, np.random.default_rng(semente))
    erros, ber = metricas.contar_erros(bits, r["bits_rx"])
    texto_rx = fonte.texto_imprimivel(fonte.bits_para_texto(r["bits_rx"]))

    print(f"Esquema: {esquema} | canal: {canal} | Eb/N0: {snr} dB")
    print(f"Enviada : {config.MENSAGEM}")
    print(f"Recebida: {texto_rx}")
    print(f"Bits: {len(bits)} | errados: {erros} | BER = {ber:.4f}"
          f" | eficiência nominal = {metricas.eficiencia_espectral(esquema):.2f} bit/s/Hz")
    if erros:
        print("Bits errados (^):")
        mostrar_erros(bits, r["bits_rx"])


def tabela_geral(semente):
    bits = fonte.texto_para_bits(config.MENSAGEM)
    print(f"Mensagem: \"{config.MENSAGEM}\"  ({len(bits)} bits)")
    print("Primeiros caracteres em bits: "
          + " ".join(f"{c}={''.join(map(str, fonte.texto_para_bits(c)))}" for c in config.MENSAGEM[:3]))
    print()
    cenarios = [("ideal", None), ("awgn", 12), ("awgn", 6), ("awgn", 2), ("rajadas", 12)]
    print("Bits errados em cada cenário (canal/Eb/N0):")
    print(f"{'esquema':12s}" + "".join(f"{c}/{s if s is not None else '-'}dB".rjust(16) for c, s in cenarios))
    for esquema in ESQUEMAS:
        linha = f"{esquema:12s}"
        for canal, snr in cenarios:
            r = transmitir(bits, esquema, canal, snr, np.random.default_rng(semente))
            erros, _ = metricas.contar_erros(bits, r["bits_rx"])
            linha += f"{erros:16d}"
        print(linha)
    print("\nDetalhe de um caso (16QAM, AWGN, 6 dB):\n")
    caso_detalhado("16QAM", "awgn", 6, semente)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--esquema", choices=ESQUEMAS)
    p.add_argument("--snr", type=float, default=None)
    p.add_argument("--canal", default="awgn", choices=["ideal", "awgn", "rajadas"])
    p.add_argument("--semente", type=int, default=1)
    a = p.parse_args()
    if a.esquema:
        caso_detalhado(a.esquema, a.canal, a.snr, a.semente)
    else:
        tabela_geral(a.semente)
