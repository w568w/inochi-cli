#!/usr/bin/env python3
"""Check parameter edits preserve or remove dependent native graph references."""
import json,math,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BIN=Path(sys.argv[1])
BASE=ROOT/'tests/results/fixture.inx';WORK=ROOT/'tests/results/parameter-graph';WORK.mkdir(exist_ok=True)
ENV=os.environ.copy();RESULT=[]
def call(model,cmd,**opts):
    args=[str(BIN),str(model),*cmd.split(),'--json']
    for k,v in opts.items():
        if isinstance(v,(dict,list)):v=json.dumps(v)
        if isinstance(v,bool):v=str(v).lower()
        args.append('--'+k.replace('_','-')+'='+str(v))
    p=subprocess.run(args,cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=90)
    assert p.returncode==0,(cmd,p.returncode,p.stderr);return json.loads(p.stdout)
def batch(model,ops,out):
    file=WORK/'ops.json';file.write_text(json.dumps([{'command':c,'options':o} for c,o in ops]));return call(model,'batch '+str(file),output=out)
def record(name):RESULT.append({'case':name,'verified':True});print('PASS',name,flush=True)
try:
    linked=WORK/'linked.inx'
    batch(BASE,[('param set',{'param':'XY','group':'Expressions'}),('physics map',{'node':'Pendulum','param':'XY'}),('automation add',{'name':'Wave'}),('automation bind',{'name':'Wave','param':'XY'}),('automation bind',{'name':'Wave','param':'Blink'}),('animation add',{'name':'Turn'}),('animation lane-add',{'name':'Turn','param':'XY'}),('animation lane-add',{'name':'Turn','param':'Blink'})],linked)
    removed=WORK/'removed.inx';call(linked,'param delete',param='XY',output=removed)
    assert [v['name'] for v in call(removed,'param list')]==['Blink']
    assert [b['param'] for b in call(removed,'automation get',name='Wave')['bindings']]==['Blink']
    assert len(call(removed,'animation get',name='Turn')['lanes'])==1
    assert call(removed,'physics get',node='Pendulum')['param']==4294967295
    call(removed,'render',max_size=64,output=WORK/'deleted.png')
    record('parameter deletion removes dependent animation and automation bindings and unmaps physics')
    # Conversion must redirect live references as well as serialized UUIDs.
    animation_source=WORK/'conversion-source.inx'
    batch(BASE,[('param set',{'param':'Blink','defaults':.25,'merge':'Weighted','group':'Expressions'}),('key set',{'param':'Blink','node':'Part','property':'transform.t.x','at':-1,'value':-4}),('key set',{'param':'Blink','node':'Part','property':'transform.t.x','at':1,'value':4}),('binding set',{'param':'Blink','node':'Part','property':'transform.t.x','interpolation':'Cubic'}),('animation add',{'name':'Turn','length':10}),('animation lane-add',{'name':'Turn','param':'Blink'}),('animation key-set',{'name':'Turn','param':'Blink','frame':0,'value':1}),('animation key-set',{'name':'Turn','param':'Blink','frame':9,'value':1})],animation_source)
    converted=WORK/'converted.inx';image=WORK/'converted-animation.png'
    batch(animation_source,[('param to-2d',{'param':'Blink'}),('render image',{'animation':'Turn','frame':0,'isolate':'Part','max-size':64,'output':str(image)})],converted)
    param=call(converted,'param get',param='Blink');original=call(animation_source,'param get',param='Blink')
    assert param['is_vec2'] and param['uuid']==original['uuid'] and param['parentUUID']==original['parentUUID']
    assert param['defaults'][0]==.25 and param['merge_mode']=='Weighted'
    assert param['bindings'][0]['interpolate_mode']=='Cubic'
    meta=json.loads(image.with_suffix('.json').read_text());assert meta['parameters']['Blink'][0]==1
    part=call(converted,'node get',node='Part')['uuid'];vertex=next(v for v in meta['vertices'] if v['node']==part and v['index']==0)
    assert abs(vertex['world'][0]-(-12))<1e-4,vertex
    record('1D conversion preserves properties and live animation lanes target the replacement parameter')
    driven=WORK/'driver-source.inx';image=WORK/'driver-conversion.png'
    batch(animation_source,[('physics map',{'node':'Pendulum','param':'Blink'}),('node set',{'node':'Pendulum','rotation':'0,0,.78539816339'}),('physics set',{'gravity':.001,'pixels-per-meter':1000}),('physics set',{'node':'Pendulum','mapping':'xy','length':30}),('param to-2d',{'param':'Blink'}),('render image',{'physics':True,'time':.1,'isolate':'Part','max-size':64,'output':str(image)})],driven)
    meta=json.loads(image.with_suffix('.json').read_text());assert max(abs(a-b) for a,b in zip(meta['parameters']['Blink'],[math.sqrt(.5),1-math.sqrt(.5)]))<1e-4,meta['parameters']['Blink']
    record('1D conversion redirects a live physical driver before the next unsaved render')
    automated=WORK/'automation-conversion.inx';image=WORK/'automation-conversion.png'
    batch(animation_source,[('automation add',{'name':'Wave'}),('automation bind',{'name':'Wave','param':'Blink','range':'.75,.75'}),('param to-2d',{'param':'Blink'}),('render image',{'time':.1,'isolate':'Part','max-size':64,'output':str(image)})],automated)
    meta=json.loads(image.with_suffix('.json').read_text())
    manual=WORK/'automation-reference.png';call(animation_source,'render',param='Blink=.1875',isolate='Part',max_size=64,output=manual)
    reference=json.loads(manual.with_suffix('.json').read_text())
    vertex=next(v for v in meta['vertices'] if v['index']==0);expected=next(v for v in reference['vertices'] if v['index']==0)
    assert abs(vertex['world'][0]-expected['world'][0])<1e-4,(vertex,expected)
    record('1D conversion redirects live automation bindings to the replacement parameter')
    physics_auto=WORK/'physics-automation.inx';batch(BASE,[('automation add',{'name':'Chain','type':'physics'}),('automation bind',{'name':'Chain','param':'XY','position':'0,0'}),('automation bind',{'name':'Chain','param':'Blink','position':'0,5'}),('param delete',{'param':'XY'})],physics_auto)
    automation=call(physics_auto,'automation get',name='Chain')
    assert [b['param'] for b in automation['bindings']]==['Blink'] and len(automation['nodes'])==1
    record('deleting a physics automation target removes its matching simulation node')

finally:
    (WORK/'results.json').write_text(json.dumps(RESULT,indent=2)+'\n')
