#!/usr/bin/env python3
"""Assert rendered pixels against v0.8.6 shader and blend equations."""
import json, math, os, subprocess, sys
from pathlib import Path
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1];BIN=Path(sys.argv[1])
ENV=os.environ.copy()
WORK=ROOT/'tests/results/render-effects';WORK.mkdir(exist_ok=True)
RESULT=[]
def call(model,cmd,**opts):
    args=[str(BIN),str(model),*cmd.split(),'--json']
    for k,v in opts.items():
        if isinstance(v,(dict,list)):v=json.dumps(v)
        if isinstance(v,bool):v=str(v).lower()
        args.append('--'+k.replace('_','-')+'='+str(v))
    p=subprocess.run(args,env=ENV,cwd=ROOT,text=True,capture_output=True,timeout=60)
    assert p.returncode==0,(cmd,p.stderr)
    return json.loads(p.stdout)
def batch(model,ops,out):
    path=WORK/'edits.json';path.write_text(json.dumps([{'command':c,'options':o} for c,o in ops]))
    return call(model,'batch '+str(path),output=out)
def texture(name,rgba):
    path=WORK/(name+'.png');Image.new('RGBA',(16,16),rgba).save(path);return str(path)
B=[64,128,192];F=[192,64,128]
BG=texture('background',tuple(B)+(255,));FG=texture('foreground',tuple(F)+(255,));WHITE=texture('white',(255,255,255,255))
QUAD={'vertices':[[-8,-8],[-8,8],[8,-8],[8,8]],'uvs':[[0,0],[0,1],[1,0],[1,1]],'triangles':[0,1,2,2,1,3]}
BASE=WORK/'layers.inx'
setup=[]
for name,z,file in [('Background',10,BG),('Foreground',0,FG)]:
    setup += [('node add',{'name':name,'type':'Part'}),('texture load',{'node':name,'file':file}),('mesh set',{'node':name,'data':QUAD}),('node set',{'node':name,'zsort':z})]
batch('new',setup,BASE)
def render(model,label,**opts):
    out=WORK/(label+'.png');call(model,'render',size='64,64',bounds='-8,-8,8,8',padding=0,output=out,**opts)
    return Image.open(out).convert('RGBA'),json.loads(out.with_suffix('.json').read_text())
def near(actual,expected,tolerance=3):
    assert max(abs(a-e) for a,e in zip(actual,expected))<=tolerance,(actual,expected)
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
    if mode in ('DestinationIn','ClipToLower'):return b if mode=='DestinationIn' else f
    if mode=='SliceFromLower':return 0
    if mode=='Exclusion':return b+f-2*b*f
    if not advanced:return f
    if mode=='Overlay':return 2*b*f if b<=.5 else 1-2*(1-b)*(1-f)
    if mode=='Darken':return min(b,f)
    if mode=='ColorBurn':return 1-min(1,(1-b)/f)
    if mode=='HardLight':return 2*b*f if f<=.5 else 1-2*(1-b)*(1-f)
    if mode=='SoftLight':return b-(1-2*f)*b*(1-b) if f<=.5 else b+(2*f-1)*(math.sqrt(b)-b)
    if mode=='Difference':return abs(b-f)
    raise AssertionError(mode)
try:
    modes=['Normal','Multiply','Screen','Overlay','Darken','Lighten','ColorDodge','LinearDodge','AddGlow','ColorBurn','HardLight','SoftLight','Difference','Exclusion','Subtract','Inverse','DestinationIn','ClipToLower','SliceFromLower']
    for mode in modes:
        model=WORK/(mode+'.inx');call(BASE,'node set',node='Foreground',blend=mode,output=model)
        image,meta=render(model,mode)
        expected=[round(255*blend(mode,b/255,f/255,meta['advancedBlending'])) for b,f in zip(B,F)]
        near(image.getpixel((32,32))[:3],expected)
        record('rendered '+mode+' blend equation')
    # Shader screen color, then multiply tint, then opacity over background.
    model=WORK/'tint.inx';call(BASE,'node set',node='Foreground',tint='.5,.75,1',screen_tint='.1,.2,.3',opacity=.5,output=model)
    image,_=render(model,'tint')
    expected=[round(((1-(1-f/255)*(1-s))*t*.5+(b/255)*.5)*255) for b,f,s,t in zip(B,F,[.1,.2,.3],[.5,.75,1])]
    near(image.getpixel((32,32))[:3],expected);record('screen tint, multiply tint and opacity shader order')
    # An opaque half-width mask covers the left half of the foreground.
    mask={'vertices':[[-8,-8],[-8,8],[0,-8],[0,8]],'uvs':[[0,0],[0,1],[1,0],[1,1]],'triangles':[0,1,2,2,1,3]}
    model=WORK/'mask.inx';batch(BASE,[('node add',{'name':'Clip','type':'Mask'}),('mesh set',{'node':'Clip','data':mask}),('mask add',{'node':'Foreground','source':'Clip','mode':'Mask'})],model)
    image,_=render(model,'mask');near(image.getpixel((16,32))[:3],F);near(image.getpixel((48,32))[:3],B);record('Mask rendered coverage')
    dodge=WORK/'dodge.inx';call(model,'mask set',node='Foreground',source='Clip',mode='DodgeMask',output=dodge)
    image,_=render(dodge,'dodge');near(image.getpixel((16,32))[:3],B);near(image.getpixel((48,32))[:3],F);record('DodgeMask rendered coverage')
    comp=WORK/'composite.inx';batch(BASE,[('node add',{'name':'Group','type':'Composite'}),('node reparent',{'node':'Foreground','parent':'Group','local':True}),('node set',{'node':'Group','opacity':.5})],comp)
    image,_=render(comp,'composite');near(image.getpixel((32,32))[:3],[(b+f)/2 for b,f in zip(B,F)]);record('Composite opacity acts on its rendered child result')
    for dynamic in (False,True):
        for propagate in (False,True):
            model=WORK/f'propagate-{dynamic}-{propagate}.inx'
            batch(BASE,[('node add',{'name':'Warp','type':'MeshGroup'}),('mesh grid',{'node':'Warp','x':'-20,0,20','y':'-20,0,20'}),('node set',{'node':'Warp','dynamic':dynamic,'translate-children':True}),('node add',{'name':'Group','type':'Composite','parent':'Warp'}),('node reparent',{'node':'Foreground','parent':'Group','local':True}),('node set',{'node':'Group','propagate':propagate}),('param add',{'name':'WarpXY','vec2':True}),('key set',{'param':'WarpXY','node':'Warp','at':'1,0','offsets':[[-6,0],[4,0],[14,0]]*3})],model)
            image,meta=render(model,f'propagation-{dynamic}-{propagate}',param='WarpXY=1,0')
            foreground=call(model,'node get',node='Foreground')['uuid']
            vertex=next(v for v in meta['vertices'] if v['node']==foreground and v['index']==0)
            assert abs(vertex['world'][0]-(-8 if propagate else -4))<1e-4,(dynamic,propagate,vertex)
            right=next(v for v in meta['vertices'] if v['node']==foreground and v['index']==2)
            assert abs(right['world'][0]-(16 if propagate else 12))<1e-4,(dynamic,propagate,right)
            record(f'MeshGroup dynamic={dynamic} Composite propagation={propagate}')
    for physics in ('pendulum','spring_pendulum'):
        for mapping,expected in [('angle_length',[-.25,1]),('length_angle',[1,-.25]),('xy',[math.sqrt(.5),1-math.sqrt(.5)]),('yx',[1-math.sqrt(.5),math.sqrt(.5)])]:
            model=WORK/(physics+'-'+mapping+'.inx')
            batch(BASE,[('param add',{'name':'Physics','vec2':True}),('key set',{'param':'Physics','node':'Foreground','property':'transform.t.x','at':'-1,0','value':-4}),('key set',{'param':'Physics','node':'Foreground','property':'transform.t.x','at':'1,0','value':4}),('node add',{'name':'Driver','type':'SimplePhysics'}),('node set',{'node':'Driver','rotation':'0,0,0.78539816339'}),('physics set',{'gravity':.001,'pixels-per-meter':1000}),('physics set',{'node':'Driver','model':physics,'mapping':mapping,'length':30,'frequency':2,'angle-damping':.5,'length-damping':.5}),('physics map',{'node':'Driver','param':'Physics'})],model)
            image,meta=render(model,physics+'-'+mapping,physics=True,time=.1)
            actual=meta['parameters']['Physics'];assert max(abs(a-b) for a,b in zip(actual,expected))<1e-4,(physics,mapping,actual,expected)
            foreground=call(model,'node get',node='Foreground')['uuid'];vertex=next(v for v in meta['vertices'] if v['node']==foreground and v['index']==0)
            assert abs(vertex['world'][0]-(-8+4*expected[0]))<1e-3,(mapping,vertex)
            record(physics+' '+mapping+' drives actual rendered vertices')
    ambient=WORK/'ambient.inx';batch(BASE,[('scene set',{'ambient-light':'.25,.5,.75'}),('render image',{'postprocess':True,'bounds':'-8,-8,8,8','size':'64,64','padding':0,'output':str(WORK/'ambient.png')}),('scene get',{})],ambient)
    image=Image.open(WORK/'ambient.png').convert('RGBA');near(image.getpixel((32,32))[:3],[48,32,96]);record('scene ambient light changes postprocessed pixels through the SDK lighting shader')
    immediate=WORK/'immediate-map.inx';mapped_image=WORK/'immediate-map.png';unmapped_image=WORK/'immediate-unmap.png'
    batch(BASE,[('param add',{'name':'Driven','vec2':True}),('key set',{'param':'Driven','node':'Foreground','property':'transform.t.x','at':'1,0','value':4}),('node add',{'name':'LiveDriver','type':'SimplePhysics'}),('node set',{'node':'LiveDriver','rotation':'0,0,0.78539816339'}),('physics set',{'gravity':.001,'pixels-per-meter':1000}),('physics set',{'node':'LiveDriver','mapping':'xy','length':30}),('physics map',{'node':'LiveDriver','param':'Driven'}),('render image',{'physics':True,'time':.1,'bounds':'-12,-12,12,12','size':'64,64','padding':0,'output':str(mapped_image)}),('physics unmap',{'node':'LiveDriver'}),('render image',{'physics':True,'time':.1,'bounds':'-12,-12,12,12','size':'64,64','padding':0,'output':str(unmapped_image)})],immediate)
    a=json.loads(mapped_image.with_suffix('.json').read_text());b=json.loads(unmapped_image.with_suffix('.json').read_text())
    assert abs(a['parameters']['Driven'][0]-math.sqrt(.5))<1e-4 and b['parameters']['Driven']==[0,0]
    record('physics map and unmap immediately update driven parameters within one unsaved batch')
finally:
    (WORK/'results.json').write_text(json.dumps(RESULT,indent=2)+'\n')
