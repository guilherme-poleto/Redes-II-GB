import numpy as np


def texto_para_bits(texto):
    bits = []
    for caractere in texto:
        binario = format(ord(caractere), "08b")
        bits.extend(int(b) for b in binario)
    return np.array(bits, dtype=np.uint8)


def bits_para_texto(bits):
    caracteres = []
    for i in range(0, len(bits) - len(bits) % 8, 8):
        grupo = "".join(str(int(b)) for b in bits[i:i + 8])
        caracteres.append(chr(int(grupo, 2)))
    return "".join(caracteres)


def texto_imprimivel(texto):
    return "".join(c if 32 <= ord(c) < 127 else "?" for c in texto)


def bits_aleatorios(n, rng):
    return rng.integers(0, 2, n, dtype=np.uint8)
