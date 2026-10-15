#!/usr/bin/env python3
"""Verify Part/Composite inspector mask operations and material pixel effects."""
import json,os,subprocess,sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];BIN=Path(sys.argv[1]);WORK=ROOT/'tests/results/mask-material';WORK.mkdir(exist_ok=True)
ENV=os.environ.copy();RESULT=[]
B=[64,128,192];F=[192,64,128]
def call(model,cmd,**opts):
    args=[str(BIN),str(model),*cmd.split(),'--json']
    for k,v in opts.items():
        if isinstance(v,(dict,list)):v=json.dumps(v)
        if isinstance(v,bool):v=str(v).lower()
        args.append('--'+k.replace('_','-')+'='+str(v))
    p=subprocess.run(args,cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=90)
    assert p.returncode==0,(cmd,p.stderr);return json.loads(p.stdout)
def batch(model,ops,out):
    f=WORK/'ops.json';f.write_text(json.dumps([{'command':c,'options':o} for c,o in ops]));return call(model,'batch '+str(f),output=out)
def render(model,label):
    image=WORK/(label+'.png');call(model,'render',size='64,64',bounds='-8,-8,8,8',padding=0,output=image);return Image.open(image).convert('RGBA')
def near(actual,expected):assert max(abs(a-b) for a,b in zip(actual,expected))<=3,(actual,expected)
def record(name):RESULT.append({'case':name,'verified':True});print('PASS',name,flush=True)
try:
    source=ROOT/'tests/results/render-effects/layers.inx'
    quad={'vertices':[[-8,-8],[-8,8],[0,-8],[0,8]],'uvs':[[0,0],[0,1],[1,0],[1,1]],'triangles':[0,1,2,2,1,3]}
    for target in ['Foreground','Group']:
        ops=[('node add',{'type':'Mask','name':'Clip'}),('mesh set',{'node':'Clip','data':quad})]
        if target=='Group':ops.extend([('node add',{'type':'Composite','name':'Group'}),('node reparent',{'node':'Foreground','parent':'Group','local':True})])
        ops.append(('mask add',{'node':target,'source':'Clip','mode':'Mask'}))
        masked=WORK/(target+'-mask.inx');batch(source,ops,masked)
        im=render(masked,target+'-mask');near(im.getpixel((16,32))[:3],F);near(im.getpixel((48,32))[:3],B)
        dodge=WORK/(target+'-dodge.inx');call(masked,'mask set',node=target,source='Clip',mode='DodgeMask',output=dodge)
        im=render(dodge,target+'-dodge');near(im.getpixel((16,32))[:3],B);near(im.getpixel((48,32))[:3],F)
        removed=WORK/(target+'-removed.inx');call(dodge,'mask remove',node=target,source='Clip',output=removed)
        assert not call(removed,'mask list',node=target)
        im=render(removed,target+'-removed');near(im.getpixel((16,32))[:3],F);near(im.getpixel((48,32))[:3],F)
        record(target+' mask addition, Mask/Dodge changes and deletion affect actual coverage')
    tint=WORK/'composite-tint.inx';batch(source,[('node add',{'type':'Composite','name':'Group'}),('node reparent',{'node':'Foreground','parent':'Group','local':True}),('node set',{'node':'Group','tint':'.5,.75,1','screen-tint':'.1,.2,.3','opacity':.5,'threshold':.6})],tint)
    im=render(tint,'composite-tint');expected=[round(((1-(1-f/255)*(1-s))*t*.5+(b/255)*.5)*255) for b,f,s,t in zip(B,F,[.1,.2,.3],[.5,.75,1])]
    near(im.getpixel((32,32))[:3],expected)
    node=call(tint,'node get',node='Group');assert abs(node['mask_threshold']-.6)<1e-5
    record('Composite tint, screen tint and opacity affect pixels; threshold survives SDK reload')
    order=WORK/'ordered.inx';batch(source,[('node add',{'type':'Mask','name':'A'}),('mesh set',{'node':'A','data':quad}),('node add',{'type':'Mask','name':'B'}),('mesh set',{'node':'B','data':quad}),('mask add',{'node':'Foreground','source':'A'}),('mask add',{'node':'Foreground','source':'B','mode':'DodgeMask'}),('mask order',{'node':'Foreground','source':'B','index':0})],order)
    b=call(order,'node get',node='B')['uuid'];bindings=call(order,'mask list',node='Foreground');assert bindings[0]['source']==b and bindings[0]['mode']=='DodgeMask'
    record('mask reordering persists source order and masking modes')
finally:
    (WORK/'results.json').write_text(json.dumps(RESULT,indent=2)+'\n')
