MENSAGEM = "Redes de Computadores - Unisinos 2026: transmissao digital com ruido!"

EBN0_DB = [0, 2, 4, 6, 8, 10, 12, 14, 16]
N_BITS = 100_000
SEMENTES = [1, 2, 3, 4, 5]

MODULACOES = ["BPSK", "QPSK", "16QAM"]
CODIGOS_LINHA = ["Manchester", "AMI"]
CANAIS = ["awgn", "rajadas"]

RAJADA_P_BOM_PARA_RUIM = 0.002
RAJADA_P_RUIM_PARA_BOM = 0.05
RAJADA_FATOR_RUIDO = 100

BER_ALVO = 1e-3

PASTA_RESULTADOS = "resultados"
PASTA_FIGURAS = "figuras"
