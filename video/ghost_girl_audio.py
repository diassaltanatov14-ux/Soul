import numpy as np, wave
sr=44100; D=30; n=sr*D; t=np.arange(n)/sr
rng=np.random.default_rng(3)
def env(a,b,fi=1.0,fo=1.0): return np.clip((t-a)/fi,0,1)*np.clip((b-t)/fo,0,1)
# pad: Am - F - C - G slow chords
chords=[[220,261.63,329.63],[174.61,220,261.63],[261.63,329.63,392],[196,246.94,293.66]]
pad=np.zeros(n)
for i,ch in enumerate(chords*2):
    a=i*3.75; b=a+4.6
    for f in ch:
        for det in (0.997,1.0,1.003):
            pad+=np.sin(2*np.pi*f*det*t+rng.random()*6)*env(a,b,1.5,2.0)*0.05
pad+=np.sin(2*np.pi*55*t)*0.08*env(0,30,2,3)
# wind: filtered noise
w=rng.standard_normal(n); k=np.ones(400)/400; w=np.convolve(w,k,'same'); w=np.convolve(w,np.ones(60)/60,'same')*18
wind=w*(0.5+0.5*np.sin(2*np.pi*t/7))*0.05*env(0,30,1,2)
# crickets
cr=np.zeros(n)
for f in (4300,4700):
    gate=(np.sin(2*np.pi*t*(f/1000.)*0+2*np.pi*5.2*t)>0.2)*(np.sin(2*np.pi*0.18*t+f)>-0.3)
    cr+=np.sin(2*np.pi*f*t)*gate*0.006
# chimes
def chime(at,f,amp=0.12):
    m=t>=at; x=np.zeros(n); tt=t[m]-at
    x[m]=(np.sin(2*np.pi*f*tt)+0.4*np.sin(2*np.pi*f*2.01*tt)+0.2*np.sin(2*np.pi*f*3.02*tt))*np.exp(-tt*1.6)*amp
    return x
ch=np.zeros(n)
for at,f in [(6.2,880),(7.0,1174.7),(7.9,1318.5),(10.6,1046.5),(13.4,1568),(13.9,1318.5),(14.4,1760),(25.5,1318.5),(26.3,1568),(27.0,1760),(27.8,2093),(28.6,1760),(29.0,2637)]:
    ch+=chime(at,f)
# soft dance pulse 16-23
pl=np.zeros(n)
for i,at in enumerate(np.arange(16.0,23.0,0.5)):
    f=[440,523.25,659.25,523.25][i%4]
    pl+=chime(at,f,0.05)*1.0
mix=pad+wind+cr+ch*1.0+pl
mix*=env(0,30,1.5,1.5)
# stereo
L=mix+0.2*np.roll(ch,int(0.03*sr)); Rr=mix+0.2*np.roll(ch,int(0.05*sr))
st=np.stack([L,Rr],1); st/=np.max(np.abs(st))*1.15
with wave.open('audio.wav','wb') as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(sr); wf.writeframes((st*32767).astype('<i2').tobytes())
