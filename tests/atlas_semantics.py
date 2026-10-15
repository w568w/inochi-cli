#!/usr/bin/env python3
"""Assert atlas layout and every native watermark blend using exported pixels."""
import json,math,os,subprocess,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];BIN=Path(sys.argv[1]);WORK=ROOT/'tests/results/atlas';WORK.mkdir(exist_ok=True)
ENV=os.environ.copy();RESULT=[]
B=(100,140,180);F=(50,80,120)
def call(model,cmd,**opts):
    args=[str(BIN),str(model),*cmd.split(),'--json']
    for k,v in opts.items():
        if isinstance(v,(dict,list)):v=json.dumps(v)
        if isinstance(v,bool):v=str(v).lower()
        args.append('--'+k.replace('_','-')+'='+str(v))
    p=subprocess.run(args,cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=120)
    assert p.returncode==0,(cmd,p.stderr);return json.loads(p.stdout)
def record(name):RESULT.append({'case':name,'verified':True});print('PASS',name,flush=True)
def blend(mode,b,f,advanced):
    if mode=='Normal':return f
    if mode=='Multiply':return b*f
    if mode in ('Screen','LinearDodge'):return 1-(1-b)*(1-f)
    if mode=='Lighten':return max(b,f)
    if mode=='ColorDodge':return min(1,b/(1-f)) if advanced else min(1,b*(1+f))
    if mode=='AddGlow':return min(1,b+f)
    if mode=='Subtract':return max(0,b-f*(1-b))
    if mode=='Inverse':return f*(1-b)
    if mode=='DestinationIn':return b
    if mode=='ClipToLower':return f
    if mode=='Exclusion':return b+f-2*b*f
    if not advanced:return f
    if mode=='Overlay':return 2*b*f if b<=.5 else 1-2*(1-b)*(1-f)
    if mode=='Darken':return min(b,f)
    if mode=='ColorBurn':return 1-min(1,(1-b)/f)
    if mode=='HardLight':return 2*b*f if f<=.5 else 1-2*(1-b)*(1-f)
    if mode=='SoftLight':return b-(1-2*f)*b*(1-b) if f<=.5 else b+(2*f-1)*(math.sqrt(b)-b)
    if mode=='Difference':return abs(b-f)
    raise AssertionError(mode)
def packed(model,name,**opts):
    out=WORK/(name+'.inp');call(model,'export inp',resolution=128,output=out,**opts)
    mesh=call(out,'mesh get',node='Block');uv=mesh['uvs'];x=int((min(uv[::2])+max(uv[::2]))*64);y=int((min(uv[1::2])+max(uv[1::2]))*64)
    image=WORK/(name+'.png');call(out,'texture export',node='Block',output=image)
    return Image.open(image).convert('RGBA'),(x,y),mesh
try:
    source=WORK/'source.png';watermark=WORK/'watermark.png';Image.new('RGBA',(32,32),B+(255,)).save(source);Image.new('RGBA',(2,2),F+(255,)).save(watermark)
    quad={'vertices':[[-16,-16],[-16,16],[16,-16],[16,16]],'uvs':[[0,0],[0,1],[1,0],[1,1]],'triangles':[0,1,2,2,1,3]}
    batch=WORK/'setup.json';batch.write_text(json.dumps([{'command':'node add','options':{'name':'Block','type':'Part'}},{'command':'texture load','options':{'node':'Block','file':str(source)}},{'command':'mesh set','options':{'node':'Block','data':quad}}]))
    model=WORK/'source.inx';call('new','batch '+str(batch),output=model)
    image=WORK/'reference.png';call(model,'render',size='64,64',output=image)
    advanced=json.loads(image.with_suffix('.json').read_text())['advancedBlending']
    for mode in ['Normal','Multiply','Screen','Overlay','Darken','Lighten','ColorDodge','LinearDodge','AddGlow','ColorBurn','HardLight','SoftLight','Difference','Exclusion','Subtract','Inverse','DestinationIn','ClipToLower']:
        image,point,_=packed(model,'blend-'+mode,padding=4,watermark=watermark,watermark_blend=mode,watermark_opacity=1,watermark_loops=2)
        actual=image.getpixel(point);expected=[round(blend(mode,b/255,f/255,advanced)*255) for b,f in zip(B,F)]
        assert max(abs(a-b) for a,b in zip(actual[:3],expected))<=2,(mode,actual,expected,point)
        record('atlas watermark '+mode+' matches the native blend equation')
    image,point,_=packed(model,'opacity',padding=4,watermark=watermark,watermark_blend='Normal',watermark_opacity=.25)
    expected=[round(b*.75+f*.25) for b,f in zip(B,F)]
    assert max(abs(a-b) for a,b in zip(image.getpixel(point)[:3],expected))<=2
    record('watermark opacity blends its pixels with packed Albedo by the requested weight')
    base,point,mesh0=packed(model,'padding-0',padding=0)
    padded,point4,mesh4=packed(model,'padding-4',padding=4)
    assert abs(min(mesh4['uvs'][::2])-min(mesh0['uvs'][::2])-4/128)<1e-5
    assert abs(max(mesh4['uvs'][::2])-min(mesh4['uvs'][::2])-32/128)<1e-5
    assert base.getpixel(point)[:3]==padded.getpixel(point4)[:3]==B
    record('atlas padding offsets UV placement without changing the packed texture dimensions or colors')
    pattern=WORK/'pattern.png';im=Image.new('RGBA',(2,1),(0,0,0,0));im.putpixel((0,0),F+(255,));im.save(pattern)
    a,_,_=packed(model,'loops-1',padding=4,watermark=pattern,watermark_blend='Normal',watermark_loops=1)
    b,_,_=packed(model,'loops-2',padding=4,watermark=pattern,watermark_blend='Normal',watermark_loops=2)
    assert a.getpixel((48,64))[3]>80 and b.getpixel((48,64))[3]<10,(a.getpixel((48,64)),b.getpixel((48,64)))
    record('watermark repeat count changes the actual repeated pattern across the atlas')
    for resolution in [2048,4096,8192]:
        out=WORK/f'resolution-{resolution}.inp';call(model,'export inp',resolution=resolution,padding=4,output=out)
        slots=call(out,'texture list');assert slots and all(v['width']==resolution and v['height']==resolution for v in slots)
    record('all three Creator atlas resolution presets export and reload at the requested dimensions')

finally:
    (WORK/'results.json').write_text(json.dumps(RESULT,indent=2)+'\n')
