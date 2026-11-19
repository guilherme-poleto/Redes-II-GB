import csv
import json
import os
import platform
import time

import numpy as np

import config
from simulador import fonte, metricas
from simulador.sistema import transmitir


def main():
    os.makedirs(config.PASTA_RESULTADOS, exist_ok=True)
    caminho_csv = os.path.join(config.PASTA_RESULTADOS, "ber_bruto.csv")
    esquemas = config.CODIGOS_LINHA + config.MODULACOES
    total = len(config.CANAIS) * len(esquemas) * len(config.EBN0_DB) * len(config.SEMENTES)
    print(f"{len(config.CANAIS)} canais x {len(esquemas)} esquemas x {len(config.EBN0_DB)} SNRs"
          f" x {len(config.SEMENTES)} sementes = {total} ensaios de {config.N_BITS} bits")

    inicio = time.time()
    with open(caminho_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["canal", "esquema", "ebn0_db", "semente", "n_bits",
                    "n_erros", "ber", "eficiencia_nominal"])
        for canal in config.CANAIS:
            for esquema in esquemas:
                for semente in config.SEMENTES:
                    bits = fonte.bits_aleatorios(config.N_BITS, np.random.default_rng(semente))
                    for ebn0 in config.EBN0_DB:
                        rng_canal = np.random.default_rng([semente, int(ebn0 * 10)])
                        r = transmitir(bits, esquema, canal, ebn0, rng_canal)
                        erros, ber = metricas.contar_erros(bits, r["bits_rx"])
                        w.writerow([canal, esquema, ebn0, semente, config.N_BITS, erros,
                                    f"{ber:.8f}", f"{metricas.eficiencia_espectral(esquema):.2f}"])
                print(f"  {canal:8s} {esquema}")

    registro = {k: getattr(config, k) for k in dir(config) if k.isupper()}
    registro["_execucao"] = {
        "data": time.strftime("%Y-%m-%d %H:%M:%S"),
        "duracao_s": round(time.time() - inicio, 1),
        "python": platform.python_version(),
        "numpy": np.__version__,
    }
    with open(os.path.join(config.PASTA_RESULTADOS, "config_usada.json"), "w") as f:
        json.dump(registro, f, indent=2, ensure_ascii=False)
    print(f"Pronto em {time.time() - inicio:.0f} s -> {caminho_csv}")


if __name__ == "__main__":
    main()
