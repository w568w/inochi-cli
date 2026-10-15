#!/usr/bin/env python3
"""Compare all GUI automesh presets and controls with generated native topology."""
import json,os,subprocess,sys
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];BIN=Path(sys.argv[1]);WORK=ROOT/'tests/results/automesh';WORK.mkdir(exist_ok=True)
ENV=os.environ.copy();RESULT=[]
def call(model,cmd,**opts):
    args=[str(BIN),str(model),*cmd.split(),'--json']
    for k,v in opts.items():
        if isinstance(v,(dict,list)):v=json.dumps(v)
        if isinstance(v,bool):v=str(v).lower()
        args.append('--'+k.replace('_','-')+'='+str(v))
    p=subprocess.run(args,cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=120)
    assert p.returncode==0,(cmd,p.stderr);return json.loads(p.stdout)
def generate(label,**opts):
    out=WORK/(label+'.inx');call(MODEL,'mesh automesh',node='Shape',uv_policy='creator',output=out,**opts)
    mesh=call(out,'mesh get',node='Shape');assert len(mesh['verts'])==len(mesh['uvs']) and mesh['indices'] and len(mesh['indices'])%3==0
    assert max(mesh['indices'])<len(mesh['verts'])//2;return mesh

def record(name):RESULT.append({'case':name,'verified':True});print('PASS',name,flush=True)
try:
    image=WORK/'shape.png';im=Image.new('RGBA',(256,256),(0,0,0,0));d=ImageDraw.Draw(im);d.ellipse((32,40,220,210),fill=(100,180,240,255));im.save(image)
    MODEL=WORK/'shape.inx';call('new','project import',file=image,output=MODEL)
    call(MODEL,'node set',node='shape.png',name='Shape',output=WORK/'named.inx');MODEL=WORK/'named.inx'
    presets={'normal':(50,15,16,[1,1.1,.9,.7,.4,.2,.1,0]),'detailed':(32,15,16,[1,1.1,.9,.7,.4,.2,.1,0]),'large':(80,15,24,[1,1.1,.9,.7,.4,.2,.1,0]),'small':(24,15,12,[1,1.1,.6,.2]),'thin':(12,1,4,[1]),'edges':(24,15,8,[1,1.2,.8])}
    for name,(sampling,threshold,distance,rings) in presets.items():
        actual=generate(name,preset=name)
        explicit=generate(name+'-explicit',sampling=sampling,threshold=threshold,distance=distance,max_distance=sampling*2,rings=rings)
        assert actual==explicit,name
        record('contour preset '+name+' matches the GUI settings and native generated topology')
    segments=generate('segments',mode='grid',x_segments=4,y_segments=3,margin=.2)
    explicit=generate('axes',mode='grid',x=[-.2,0,.25,.5,.75,1,1.2],y=[-.2,0,1/3,2/3,1,1.2])
    assert segments==explicit
    record('grid segment counts and margins generate the same axes and topology as explicit scales')
    a=generate('rings-one',sampling=12,distance=4,max_distance=24,rings=[1])
    b=generate('rings-many',sampling=12,distance=4,max_distance=24,rings=[1,.8,.5,.2])
    assert len(b['verts'])>len(a['verts'])
    record('contour ring editing adds inner scaled topology rather than only changing stored settings')
    a=generate('sampling-sparse',sampling=80,distance=4,max_distance=160,rings=[1])
    b=generate('sampling-dense',sampling=12,distance=4,max_distance=24,rings=[1])
    assert len(b['verts'])>len(a['verts'])
    record('contour sampling and maximum-distance controls change generated vertex density')
    a=generate('distance-close',sampling=12,distance=4,max_distance=24,rings=[1,.8,.6])
    b=generate('distance-far',sampling=12,distance=30,max_distance=60,rings=[1,.8,.6])
    assert len(b['verts'])<len(a['verts'])
    record('contour minimum-distance control removes densely packed candidates')
    original=MODEL;alpha=WORK/'alpha.png';im=Image.new('RGBA',(256,256),(0,0,0,0));d=ImageDraw.Draw(im);d.rectangle((24,40,110,210),fill=(100,180,240,80));d.rectangle((130,40,220,210),fill=(100,180,240,255));im.save(alpha)
    MODEL=WORK/'threshold.inx';call(original,'texture load',node='Shape',file=alpha,output=MODEL)
    for mode in ['grid','contour']:
        options={'mode':mode} if mode=='grid' else {'sampling':12,'distance':4,'max-distance':24,'rings':[1]}
        a=generate(mode+'-threshold-low',threshold=40,**options);b=generate(mode+'-threshold-high',threshold=120,**options)
        assert min(a['verts'][::2])<min(b['verts'][::2])-40,(mode,min(a['verts'][::2]),min(b['verts'][::2]))
        record(mode+' mask threshold changes the alpha-derived mesh boundary')
    MODEL=original
    mirrored=generate('mirror-x',sampling=12,distance=4,max_distance=24,rings=[1],mirror_x=True,mirror_origin='0,0')
    plain=generate('mirror-none',sampling=12,distance=4,max_distance=24,rings=[1])
    assert mirrored['verts']!=plain['verts']
    record('contour horizontal mirror mode changes native sampling and closest-contour matching')
    p=subprocess.run([str(BIN),str(MODEL),'mesh','automesh','--node=Shape','--mirror-y','-o',str(WORK/'unsupported.inx')],env=ENV,capture_output=True,text=True,timeout=90)
    assert p.returncode!=0 and 'unimplemented' in p.stderr
    record('upstream unimplemented vertical contour mirroring reports an explicit failure')

finally:
    (WORK/'results.json').write_text(json.dumps(RESULT,indent=2)+'\n')
