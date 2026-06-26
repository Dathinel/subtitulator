"""Compone una pista corporativa/optimista (Am-F-C-G) para el vídeo. Sin samples externos."""
import numpy as np
import soundfile as sf

SR = 44100
BPM = 96.0
beat = 60.0 / BPM            # 0.625 s
bar = 4 * beat               # 2.5 s
prog_bars = 4                # Am F C G
loop = bar * prog_bars       # 10 s
loops = 6
total = loop * loops         # 50 s
N = int(total * SR)
t_total = np.arange(N) / SR

def note(freq, dur, env, amp=1.0, harmonics=(1.0, 0.35, 0.12), detune=0.0):
    n = int(dur * SR)
    tt = np.arange(n) / SR
    sig = np.zeros(n)
    for i, h in enumerate(harmonics, start=1):
        f = freq * i * (1.0 + detune)
        sig += h * np.sin(2 * np.pi * f * tt)
    sig /= sum(harmonics)
    return sig * env(n) * amp

def env_pad(n):
    a = int(0.18 * SR); r = int(0.30 * SR); e = np.ones(n)
    a = min(a, n // 2); r = min(r, n // 2)
    e[:a] = np.linspace(0, 1, a)
    e[n - r:] = np.linspace(1, 0, r)
    return e

def env_pluck(n, decay=0.5):
    tt = np.arange(n) / SR
    a = int(0.005 * SR)
    e = np.exp(-tt / decay)
    if a > 0 and a < n:
        e[:a] *= np.linspace(0, 1, a)
    return e

def env_bass(n):
    tt = np.arange(n) / SR
    a = int(0.01 * SR)
    e = np.exp(-tt / 0.9)
    if a > 0 and a < n:
        e[:a] *= np.linspace(0, 1, a)
    return e

# Frecuencias
NOTE = {
    'A2':110.00,'F2':87.31,'C3':130.81,'G2':98.00,
    'A3':220.00,'C4':261.63,'E4':329.63,'F3':174.61,'G3':196.00,'B3':246.94,'D4':293.66,
    'E5':659.25,'C5':523.25,'A4':440.00,'G4':392.00,'F4':349.23,'B4':493.88,'D5':587.33,
}
chords = [
    {'root':'A2','pad':['A3','C4','E4'],'arp':['A3','C4','E4','A4'],'bell':['A4','C5','E5','C5']},
    {'root':'F2','pad':['F3','A3','C4'],'arp':['F3','A3','C4','F4'],'bell':['A4','C5','F4','C5']},
    {'root':'C3','pad':['C4','E4','G4'],'arp':['C4','E4','G4','C5'],'bell':['C5','E4','G4','E4']},
    {'root':'G2','pad':['G3','B3','D4'],'arp':['G3','B3','D4','G4'],'bell':['B4','D5','G4','D5']},
]

pad = np.zeros(N + SR)
arp = np.zeros(N + SR)
bass = np.zeros(N + SR)
bell = np.zeros(N + SR)

for L in range(loops):
    for b in range(prog_bars):
        ch = chords[b]
        bar_start = (L * loop) + b * bar
        si = int(bar_start * SR)
        # Pad: triada sostenida toda la barra
        for nm in ch['pad']:
            seg = note(NOTE[nm], bar, env_pad, amp=0.22, harmonics=(1.0,0.3,0.08), detune=0.004)
            pad[si:si+len(seg)] += seg
        # Bajo: raiz, pulso en cada beat
        for k in range(4):
            bs = int((bar_start + k*beat) * SR)
            seg = note(NOTE[ch['root']], beat, env_bass, amp=0.5, harmonics=(1.0,0.25))
            bass[bs:bs+len(seg)] += seg
        # Arpegio: corcheas (8 por barra)
        arpn = ch['arp']
        pattern = [0,1,2,3,2,1,2,3]
        for k in range(8):
            ns = int((bar_start + k*(beat/2)) * SR)
            nm = arpn[pattern[k] % len(arpn)]
            seg = note(NOTE[nm], beat/2*1.4, lambda n: env_pluck(n,0.28), amp=0.16, harmonics=(1.0,0.5,0.2))
            arp[ns:ns+len(seg)] += seg
        # Bell: notas largas brillantes (2 por barra) para sparkle
        for k in range(2):
            ns = int((bar_start + k*2*beat) * SR)
            nm = ch['bell'][(k*2) % len(ch['bell'])]
            seg = note(NOTE[nm], beat*2, lambda n: env_pluck(n,0.9), amp=0.07, harmonics=(1.0,0.4,0.15))
            bell[ns:ns+len(seg)] += seg

pad = pad[:N]; arp = arp[:N]; bass = bass[:N]; bell = bell[:N]

def delay(sig, ms, fb, mix, taps=3):
    out = sig.copy()
    d = int(ms/1000*SR)
    for i in range(1, taps+1):
        if d*i < len(sig):
            out[d*i:] += sig[:-d*i] * (fb**i) * mix
    return out

# Espacio (reverb sencilla via taps) sobre arp y bell
arp = delay(arp, 180, 0.5, 0.35)
bell = delay(bell, 240, 0.55, 0.5)
pad_rev = delay(pad, 300, 0.4, 0.25)
pad = 0.85*pad + 0.15*pad_rev

# Lowpass suave (media movil) sobre el conjunto melodico para quitar dureza
def lowpass(sig, cutoff=0.25):
    # filtro de 1er orden simple
    out = np.zeros_like(sig)
    a = cutoff
    prev = 0.0
    for i in range(len(sig)):
        prev = prev + a*(sig[i]-prev)
        out[i] = prev
    return out

# Mezcla L/R con ligero paneo del arpegio para anchura estereo
left  = 0.9*pad + 0.95*bass + 0.85*arp + 0.9*bell
right = 0.9*pad + 0.95*bass + 1.0*arp  + 1.0*bell
# pequeño desfase del arp en R para amplitud
shift = int(0.012*SR)
right[shift:] += 0.15*arp[:-shift]

stereo = np.stack([left, right], axis=1)

# Normalizacion suave
peak = np.max(np.abs(stereo))
if peak > 0:
    stereo = stereo / peak * 0.85

# Fades maestro
fin = int(2.0*SR); fout = int(5.0*SR)
stereo[:fin] *= np.linspace(0,1,fin)[:,None]
stereo[-fout:] *= np.linspace(1,0,fout)[:,None]

sf.write('assets/music.wav', stereo, SR)
print(f"OK music.wav  {total:.1f}s  shape={stereo.shape}")
