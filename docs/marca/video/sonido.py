"""Sintetiza la banda sonora del teaser, sincronizada con la línea de tiempo de teaser.html."""
import sys
import wave
import numpy as np

SR = 44100
DUR = 38.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N)
R = np.zeros(N)
seco_rev = np.zeros(N)  # envio a reverberacion


def tiempo(n):
    return np.arange(n) / SR


def poner(señal, t0, gan=1.0, pan=0.0, rev=0.0):
    i = int(t0 * SR)
    if i >= N:
        return
    s = señal[: N - i] * gan
    L[i:i + len(s)] += s * (1 - max(pan, 0))
    R[i:i + len(s)] += s * (1 + min(pan, 0))
    seco_rev[i:i + len(s)] += s * rev


def env(n, ataque, caida):
    t = tiempo(n)
    return np.minimum(1, t / max(ataque, 1e-4)) * np.exp(-t / caida)


def pasabajos(x, corte):
    a = np.exp(-2 * np.pi * corte / SR)
    y = np.zeros_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def pasabajos_rapido(x, corte):
    """Filtro de un polo aplicado en el dominio de la frecuencia (aproximación barata)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / np.sqrt(1 + (f / corte) ** 4), len(x))


def latido():
    n = int(.5 * SR)
    t = tiempo(n)
    golpe = lambda f0: np.sin(2 * np.pi * (f0 * t - 18 * t * t)) * env(n, .004, .09)
    s = golpe(62)
    s2 = np.zeros(n)
    d = int(.16 * SR)
    s2[d:] = golpe(55)[: n - d] * .75
    return s + s2


def boom(f0=58, caida=1.4, ruido=.25):
    n = int(caida * 3 * SR)
    t = tiempo(n)
    f = f0 * np.exp(-t * 1.2) + 28
    fase = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(fase) * env(n, .003, caida)
    nz = pasabajos_rapido(rng.standard_normal(n), 900) * env(n, .001, .12) * ruido
    return np.tanh((s + nz) * 1.6)


def click(caida=.012, brillo=4000):
    n = int(.08 * SR)
    nz = rng.standard_normal(n) * env(n, .0005, caida)
    t = tiempo(n)
    return nz * .5 + np.sin(2 * np.pi * brillo * t) * env(n, .0005, caida * .6) * .4


def glitch(dur):
    n = int(dur * SR)
    t = tiempo(n)
    f = rng.choice([180, 360, 720, 1440, 95])
    s = np.sign(np.sin(2 * np.pi * f * t)) * .5 + rng.standard_normal(n) * .5
    paso = rng.integers(8, 40)
    s = np.repeat(s[::paso], paso)[:n]  # reduccion de muestreo
    s = np.round(s * 4) / 4  # reduccion de bits
    return s * env(n, .001, dur * .6)


def tono(f, dur, ataque, caida, armonicos=(1, .5, .25), vibrato=0.0):
    n = int(dur * SR)
    t = tiempo(n)
    s = sum(a * np.sin(2 * np.pi * f * (k + 1) * t + vibrato * np.sin(2 * np.pi * .3 * t)) for k, a in enumerate(armonicos))
    e = np.minimum(1, t / ataque) * np.minimum(1, np.maximum(0, (dur - t) / caida))
    return s * e


# ---- dron de fondo ----
t = tiempo(N)
volumen = np.interp(t, [0, 1, 7.6, 8.45, 8.6, 9.8, 17.4, 17.55, 18.9, 19.5, 27.6, 28, 32, 32.3, 36.5, 38],
                    [0, .16, .3, .4, .08, .14, .36, .07, .07, .26, .3, .2, .2, .12, .1, 0])
dron = (np.sin(2 * np.pi * 55 * t) + .7 * np.sin(2 * np.pi * 55.4 * t) + .5 * np.sin(2 * np.pi * 82.4 * t)
        + .25 * np.sin(2 * np.pi * 110.3 * t) * (.5 + .5 * np.sin(2 * np.pi * .13 * t)))
textura = pasabajos_rapido(rng.standard_normal(N), 380) * 2.2
L += (dron * .55 + textura * .5) * volumen
R += (dron * .55 + textura[::-1] * .5) * volumen
seco_rev += dron * volumen * .2

# ---- latidos (0 a 7.6 s, cada vez mas rapidos) ----
for x in [0.5, 1.95, 3.25, 4.4, 5.4, 6.25, 6.95, 7.5]:
    poner(latido(), x, .7)

# ---- interferencias ----
for x in [6.62, 7.08, 7.31]:
    poner(glitch(.09), x, .1, pan=rng.uniform(-.6, .6), rev=.2)
x = 7.6
while x < 8.4:
    d = rng.uniform(.03, .08)
    poner(glitch(d), x, .07 + .14 * (x - 7.6), pan=rng.uniform(-.8, .8), rev=.15)
    x += d * rng.uniform(.9, 1.6)
poner(boom(70, .9, .2), 8.45, .45, rev=.6)
poner(click(.03, 2500), 8.45, .15, rev=.5)
poner(click(.006, 2200), 4.72, .12, rev=.3)  # obturador al cambiar de foto

# ---- tecleo (10.1 s) ----
texto = 'Hoy una imagen se edita en segundos.'
for k in range(len(texto)):
    if texto[k] != ' ':
        poner(click(.008, rng.uniform(3000, 5200)), 10.1 + .9 * k / len(texto), .07, pan=rng.uniform(-.3, .3))

# ---- pixeles que se ordenan (12.85 a 14.6 s) ----
for _ in range(70):
    x = 12.85 + 1.75 * rng.random() ** 1.4
    poner(tono(rng.choice([1760, 2093, 2349, 2637, 3136]), .12, .002, .1, (1,)), x, .035, pan=rng.uniform(-.9, .9), rev=.7)

# ---- subida de tension (15 a 17.55 s) ----
n = int(2.55 * SR)
tt = tiempo(n)
sub = np.sin(2 * np.pi * np.cumsum(np.linspace(110, 440, n)) / SR) * (tt / tt[-1]) ** 2
ruido = rng.standard_normal(n)
barrido = np.concatenate([pasabajos_rapido(ruido[i:i + 4410], 200 + 5000 * (i / n) ** 2) for i in range(0, n, 4410)])[:n]
poner(sub * .13 + barrido * (tt / tt[-1]) ** 2 * .22, 15.0, 1, rev=.3)
poner(click(.004, 6000), 17.55, .12)

# ---- ojo (18.3 a 22.8 s) ----
poner(click(.02, 1800), 18.72, .18, pan=-.3, rev=.3)
poner(click(.02, 1700), 18.76, .18, pan=.3, rev=.3)
poner(boom(55, 1.8, .12), 18.95, .3, rev=.5)
for k, f in enumerate([880, 1318.5, 1760]):
    poner(tono(f, 2.6, .4, 1.8, (1, .2)), 19.0 + k * .08, .035, pan=(k - 1) * .5, rev=.9)

# ---- pulso y capas (19.5 a 27.6 s) ----
x = 19.5
while x < 27.6:
    poner(boom(48, .18, .05), x, .2)
    x += .6
for i in range(4):
    x = 22.8 + 1.2 * i
    poner(boom(90, .25, .15), x, .28, rev=.3)
    poner(click(.015, 3200), x, .13, rev=.4)
    poner(tono(1046.5 * (1.12 ** i), .9, .05, .7, (1, .3)), x + .1, .04, pan=.4 - .27 * i, rev=.8)

# ---- informe e indicios (27.7 a 32 s) ----
for x, f in [(27.7, 220), (30.2, 196)]:
    poner(tono(f, 2.2, .3, 1.2, (1, .5, .3, .15)), x, .07, rev=.8)

# ---- entrada del logo (31.4 a 38 s) ----
n = int(.9 * SR)
tt = tiempo(n)
soplo = pasabajos_rapido(rng.standard_normal(n), 2500) * (tt / tt[-1]) ** 3
poner(soplo, 31.4, .28, rev=.4)
poner(boom(52, 2.2, .12), 32.3, .32, rev=.6)
acorde = [110, 164.8, 220, 246.9, 261.6, 329.6, 493.9]
for k, f in enumerate(acorde):
    poner(tono(f, 5.6, 1.2, 2.8, (1, .35, .15), vibrato=.4), 32.3 + k * .03, .04, pan=(k / 3 - 1) * .6, rev=.8)
poner(tono(1318.5, 3.5, .02, 3.2, (1,)), 34.3, .03, rev=1)  # "proximamente"

# ---- reverberacion ----
largo = int(2.4 * SR)
ir = rng.standard_normal(largo) * np.exp(-tiempo(largo) / .55)
ir2 = rng.standard_normal(largo) * np.exp(-tiempo(largo) / .55)
tam = 1 << int(np.ceil(np.log2(N + largo)))
E = np.fft.rfft(seco_rev, tam)
revL = np.fft.irfft(E * np.fft.rfft(ir, tam), tam)[:N]
revR = np.fft.irfft(E * np.fft.rfft(ir2, tam), tam)[:N]
escala = np.abs(np.concatenate([L, R])).max() / max(np.abs(revL).max(), 1e-9)
L += revL * escala * .22
R += revR * escala * .22

# ---- mezcla final ----
mezcla = np.stack([L, R], axis=1)
mezcla /= np.abs(mezcla).max()
mezcla = np.tanh(mezcla * 1.1) / np.tanh(1.1)
fundido = np.interp(t, [0, .05, 37.0, 38], [0, 1, 1, 0])[:, None]
mezcla *= fundido * .89
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mezcla * 32767).astype('<i2').tobytes())
