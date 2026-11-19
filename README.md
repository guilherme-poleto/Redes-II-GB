# Simulador de Transmissão Digital

Trabalho II de Redes de Computadores (Unisinos, 2026/2).

O simulador transmite uma mensagem ASCII pelo caminho **fonte → codificação de linha ou modulação → canal ruidoso → decodificação ou demodulação → mensagem recuperada** e mede a BER e a eficiência espectral.

- **Códigos de linha:** Manchester e AMI
- **Modulações:** BPSK, QPSK e 16-QAM
- **Canais:** AWGN e canal com rajadas (Gilbert-Elliott)

## Arquitetura

```
TRANSMISSOR: texto → bits → código de linha  OU  modulação
                                         │
CANAL:                     ideal | AWGN | rajadas
                                         │
RECEPTOR:    texto ← bits ← decodificação OU demodulação
```

- **Banda base:** o código de linha (Manchester ou AMI) gera os níveis de tensão diretamente, sem portadora.
- **Com portadora:** a modulação (BPSK, QPSK ou 16-QAM) gera símbolos I/Q, representados como números complexos. A demodulação escolhe o ponto da constelação mais próximo.
- **Canal AWGN:** soma ruído gaussiano com variância definida pelo Eb/N0.
- **Canal com rajadas:** alterna entre um estado bom (AWGN normal) e um estado ruim (ruído 20 dB mais forte).
- **Métricas:** a BER compara os bits enviados com os recebidos. A eficiência espectral nominal é log₂M para as modulações e usa a banda mínima de Nyquist para os códigos de linha.

## Instalação

É preciso ter Python 3.10 ou mais recente.

```
pip install -r requirements.txt
```

## Execução

```
python teste_consistencia.py   # canal ideal / SNR alta: a mensagem tem que voltar igual
python demo.py                 # transmite a mensagem e mostra os bits errados
python experimentos.py         # roda todos os ensaios -> resultados/ber_bruto.csv
python graficos.py             # gera figuras/ e resultados/tabela_compromisso.md
```

Exemplo de um caso específico:

```
python demo.py --esquema 16QAM --snr 6 --canal rajadas
```

## Estrutura

```
config.py               parâmetros de todos os experimentos
simulador/
  fonte.py              texto <-> bits
  codigo_linha.py       Manchester, AMI
  modulacao.py          BPSK, QPSK, 16-QAM
  canal.py              AWGN e rajadas
  metricas.py           BER e eficiência espectral
  sistema.py            transmissor -> canal -> receptor
teste_consistencia.py  demo.py  experimentos.py  graficos.py
resultados/             dados brutos (CSV), resumo, tabela e configuração usada
figuras/                gráficos gerados
```

## Parâmetros

| Parâmetro | Valor |
|---|---|
| Eb/N0 | 0 a 16 dB, de 2 em 2 (9 valores) |
| Bits por ensaio | 100.000 |
| Repetições | 5 sementes (1 a 5) |
| Rajadas | 3,8 % do tempo no estado ruim, duração média de 20 símbolos, ruído 20 dB mais forte |

Para alterar algum parâmetro, edite `config.py` e rode `experimentos.py` e `graficos.py` de novo.

## Autor

Guilherme Poleto

## Vídeo

https://youtu.be/oUIvru1t6M8
