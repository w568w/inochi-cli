#!/usr/bin/env python3
"""Check viewport scale, pan/reset, focus and preview state through pixel transforms."""
import json,os,subprocess,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];BIN=Path(sys.argv[1]);BASE=ROOT/'tests/results/fixture.inx';WORK=ROOT/'tests/results/preview';WORK.mkdir(exist_ok=True)
ENV=os.environ.copy();RESULT=[]
def call(model,cmd,**opts):
    args=[str(BIN),str(model),*cmd.split(),'--json']
    for k,v in opts.items():
        if isinstance(v,(dict,list)):v=json.dumps(v)
        if isinstance(v,bool):v=str(v).lower()
        args.append('--'+k.replace('_','-')+'='+str(v))
    p=subprocess.run(args,cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=90)
    assert p.returncode==0,(cmd,p.stderr);return json.loads(p.stdout)
def render(label,**opts):
    image=WORK/(label+'.png');call(BASE,'render',size='128,128',output=image,**opts);return Image.open(image),json.loads(image.with_suffix('.json').read_text())
def record(name):RESULT.append({'case':name,'verified':True});print('PASS',name,flush=True)
try:
    im,meta=render('reset',zoom=1,view_center='0,0');m=meta['worldToPixel'];assert abs(m[0][0]-1)<1e-6 and abs(m[1][1]-1)<1e-6 and m[0][2]==m[1][2]==64
    im,meta=render('zoom-pan',zoom=2,view_center='5,7');m=meta['worldToPixel'];assert abs(m[0][0]-2)<1e-6 and abs(m[1][1]-2)<1e-6;assert abs(m[0][2]-54)<1e-6 and abs(m[1][2]-50)<1e-6
    record('viewport zoom, panning and reset use native camera scale and world-center transforms')
    shifted=WORK/'shifted.inx';call(BASE,'node set',node='Part',position='30,20',output=shifted)
    image=WORK/'focus.png';call(shifted,'render',focus='Part',isolate='Part',size='128,128',padding=0,output=image)
    meta=json.loads(image.with_suffix('.json').read_text());m=meta['worldToPixel'];assert abs(m[0][0]*30+m[0][2]-64)<1e-4 and abs(m[1][1]*20+m[1][2]-64)<1e-4
    record('Focus Selected centers the isolated node using its actual SDK world geometry')
    im,_=render('colored',background='.2,.3,.4,1',zoom=1,view_center='0,0');assert im.getpixel((0,0))==(51,76,102,255)
    im,_=render('transparent-reset',zoom=1,view_center='0,0');assert im.getpixel((0,0))[3]==0
    record('explicit canvas color and default color reset appear in exported pixels')
    im,meta=render('annotated',focus='Face',overlay_bounds=True,orientation=True,vertices=True)
    assert meta['guides'] and meta['vertices'];assert any('zAxisPixel' in g for g in meta['guides'])
    record('MeshGroup child bounds, orientation axes and vertex overlays have image and coordinate evidence')
    defaults=WORK/'defaults.inx';call(BASE,'param set',param='XY',defaults='.25,.5',output=defaults)
    for label,extra,expected in [('override',{'param':'XY=1,1'},[1,1]),('defaults',{},[.25,.5])]:
        image=WORK/(label+'.png');call(defaults,'render',max_size=64,output=image,**extra)
        assert json.loads(image.with_suffix('.json').read_text())['parameters']['XY']==expected
    record('new static previews reset every parameter to its model default unless explicitly overridden')
    physics=ROOT/'tests/results/render-effects/pendulum-xy.inx'
    first=WORK/'physics-first.png';second=WORK/'physics-second.png'
    for image in [first,second]:call(physics,'render',physics=True,time=.2,size='64,64',output=image)
    assert Image.open(first).tobytes()==Image.open(second).tobytes()
    assert json.loads(first.with_suffix('.json').read_text())['vertices']==json.loads(second.with_suffix('.json').read_text())['vertices']
    record('physics preview resets native simulation and repeats the same fixed-step pose and pixels')

finally:
    (WORK/'results.json').write_text(json.dumps(RESULT,indent=2)+'\n')
