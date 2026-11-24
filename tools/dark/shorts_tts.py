import json, sys, numpy as np, soundfile as sf
sys.path.insert(0,'.')
from shorts_script import SHORTS
from kokoro_onnx import Kokoro
k=Kokoro('/root/work/kok/kokoro-v1.0.onnx','/root/work/kok/voices-v1.0.bin')
st=k.get_voice_style('am_michael')*0.6+k.get_voice_style('am_onyx')*0.4
sr=24000
SPEED=float(sys.argv[1]) if len(sys.argv)>1 else 0.95
for n,(title,lines) in SHORTS.items():
    out=[np.zeros(int(sr*0.35),np.float32)]; t=0.35; meta=[]
    for i,l in enumerate(lines):
        disp,tts=(l if isinstance(l,tuple) else (l,l))
        if i: g=0.32 if len(disp)<45 else 0.26; out.append(np.zeros(int(sr*g),np.float32)); t+=g
        a,_=k.create(tts,voice=st,speed=SPEED,lang='en-us'); a=a.astype(np.float32)
        idx=np.where(np.abs(a)>0.01)[0]; a=a[max(0,idx[0]-200):idx[-1]+500]
        d=len(a)/sr; meta.append(dict(i=i,text=disp,start=round(t,3),end=round(t+d,3))); out.append(a); t+=d
    y=np.concatenate(out); sf.write(f'v{n}.wav',y,sr); json.dump(meta,open(f'tl{n}.json','w'))
    print(n,title,round(t,1))
