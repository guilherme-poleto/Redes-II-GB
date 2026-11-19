import csv
import math
import os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import config
from simulador import metricas

T_STUDENT_95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571,
                6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262}
CORES = {"BPSK": "tab:blue", "QPSK": "tab:orange", "16QAM": "tab:green",
         "Manchester": "tab:red", "AMI": "tab:purple"}
ESQUEMAS = config.CODIGOS_LINHA + config.MODULACOES


def carregar_e_resumir():
    grupos = defaultdict(list)
    with open(os.path.join(config.PASTA_RESULTADOS, "ber_bruto.csv")) as f:
        for linha in csv.DictReader(f):
            chave = (linha["canal"], linha["esquema"], float(linha["ebn0_db"]))
            grupos[chave].append((float(linha["ber"]), int(linha["n_erros"]), int(linha["n_bits"])))

    resumo = {}
    for chave, valores in grupos.items():
        bers = np.array([v[0] for v in valores])
        n = len(bers)
        desvio = bers.std(ddof=1) if n > 1 else 0.0
        resumo[chave] = {
            "media": bers.mean(), "desvio": desvio,
            "ic95": T_STUDENT_95.get(n - 1, 1.96) * desvio / math.sqrt(n),
            "min": bers.min(), "max": bers.max(), "n_rep": n,
            "erros_total": sum(v[1] for v in valores),
            "bits_total": sum(v[2] for v in valores),
        }
    return resumo


def curva(resumo, canal, esquema):
    snrs = sorted(k[2] for k in resumo if k[:2] == (canal, esquema))
    return np.array(snrs), [resumo[(canal, esquema, s)] for s in snrs]


def salvar_resumo_csv(resumo):
    caminho = os.path.join(config.PASTA_RESULTADOS, "ber_resumo.csv")
    with open(caminho, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["canal", "esquema", "ebn0_db", "ber_media", "desvio", "ic95",
                    "ber_min", "ber_max", "repeticoes", "erros_total", "bits_total"])
        for k in sorted(resumo):
            r = resumo[k]
            w.writerow([*k, f"{r['media']:.3e}", f"{r['desvio']:.3e}", f"{r['ic95']:.3e}",
                        f"{r['min']:.3e}", f"{r['max']:.3e}", r["n_rep"],
                        r["erros_total"], r["bits_total"]])
    print("  ", caminho)


def desenhar(ax, snrs, pontos, rotulo, cor, marcador="o", estilo="-"):
    media = np.array([p["media"] for p in pontos])
    ic = np.array([p["ic95"] for p in pontos])
    com_erro = media > 0
    baixo = np.minimum(ic, media * 0.95)
    ax.errorbar(snrs[com_erro], media[com_erro], yerr=[baixo[com_erro], ic[com_erro]],
                color=cor, marker=marcador, linestyle=estilo, capsize=3, label=rotulo)
    for s, p in zip(snrs[~com_erro], np.array(pontos)[~com_erro]):
        ax.plot(s, 3 / p["bits_total"], marker="v", color=cor, markerfacecolor="none")


def formatar(ax, titulo):
    ax.set_yscale("log")
    ax.set_ylim(1e-6, 1)
    ax.set_xlabel("Eb/N0 (dB)")
    ax.set_ylabel("BER")
    ax.set_title(titulo)
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(fontsize=8)


def salvar(fig, nome):
    fig.tight_layout()
    caminho = os.path.join(config.PASTA_FIGURAS, nome)
    fig.savefig(caminho, dpi=150)
    plt.close(fig)
    print("  ", caminho)


def fig_awgn(resumo, esquemas, titulo, nome):
    fig, ax = plt.subplots(figsize=(7, 5))
    for esq in esquemas:
        snrs, pts = curva(resumo, "awgn", esq)
        desenhar(ax, snrs, pts, esq, CORES[esq])
    formatar(ax, titulo)
    salvar(fig, nome)


def fig_awgn_vs_rajadas(resumo):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5), sharey=True)
    grupos = [(config.MODULACOES, "Modulações"), (config.CODIGOS_LINHA, "Códigos de linha")]
    for ax, (esquemas, titulo) in zip(axes, grupos):
        for esq in esquemas:
            for canal, marc, est in [("awgn", "o", "-"), ("rajadas", "x", "--")]:
                snrs, pts = curva(resumo, canal, esq)
                desenhar(ax, snrs, pts, f"{esq} - {canal}", CORES[esq], marc, est)
        formatar(ax, f"{titulo}: AWGN x rajadas (média ± IC95%)")
    salvar(fig, "ber_awgn_vs_rajadas.png")


def snr_necessaria(snrs, pontos, alvo):
    bers = [max(p["media"], 3 / p["bits_total"]) for p in pontos]
    if bers[0] <= alvo:
        return f"< {snrs[0]:g}"
    for i in range(len(bers) - 1):
        if bers[i] > alvo >= bers[i + 1]:
            a, b = math.log10(bers[i]), math.log10(bers[i + 1])
            frac = (math.log10(alvo) - a) / (b - a)
            return f"{snrs[i] + frac * (snrs[i + 1] - snrs[i]):.1f}"
    return f"> {snrs[-1]:g}"


def fmt_ber(p):
    return f"{p['media']:.1e}" if p["media"] > 0 else f"< {3 / p['bits_total']:.0e}"


def tabela_compromisso(resumo):
    snr_ref = 10.0
    cab = ["Esquema", "Eficiência (bit/s/Hz)",
           f"Eb/N0 p/ BER {config.BER_ALVO:g} - AWGN (dB)",
           f"Eb/N0 p/ BER {config.BER_ALVO:g} - rajadas (dB)",
           f"BER @ {snr_ref:g} dB AWGN", f"BER @ {snr_ref:g} dB rajadas"]
    linhas = []
    for esq in ESQUEMAS:
        celulas = [esq, f"{metricas.eficiencia_espectral(esq):.2f}"]
        for canal in ["awgn", "rajadas"]:
            snrs, pts = curva(resumo, canal, esq)
            celulas.append(snr_necessaria(snrs, pts, config.BER_ALVO))
        for canal in ["awgn", "rajadas"]:
            celulas.append(fmt_ber(resumo[(canal, esq, snr_ref)]))
        linhas.append(celulas)

    md = ["| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
    md += ["| " + " | ".join(l) + " |" for l in linhas]
    caminho = os.path.join(config.PASTA_RESULTADOS, "tabela_compromisso.md")
    with open(caminho, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    with open(caminho.replace(".md", ".csv"), "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows([cab] + linhas)
    print("  ", caminho)
    print("\n".join(md))


if __name__ == "__main__":
    os.makedirs(config.PASTA_FIGURAS, exist_ok=True)
    resumo = carregar_e_resumir()
    print("Arquivos:")
    salvar_resumo_csv(resumo)
    fig_awgn(resumo, config.MODULACOES, "BER x Eb/N0 - modulações, AWGN (média ± IC95%)",
             "ber_awgn_modulacoes.png")
    fig_awgn(resumo, config.CODIGOS_LINHA, "BER x Eb/N0 - códigos de linha, AWGN (média ± IC95%)",
             "ber_awgn_codigos_linha.png")
    fig_awgn_vs_rajadas(resumo)
    print("Tabela de compromisso:")
    tabela_compromisso(resumo)
