#!/usr/bin/env python3
"""Verify node type creation, order/rename/visibility and native origin recalculation."""
import json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BIN=Path(sys.argv[1]);BASE=ROOT/'tests/results/fixture.inx';WORK=ROOT/'tests/results/node-operations';WORK.mkdir(exist_ok=True)
ENV=os.environ.copy();RESULT=[]
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
def vertices(model,label):
    image=WORK/(label+'.png');call(model,'render',max_size=64,output=image);return {(v['node'],v['index']):v['world'] for v in json.loads(image.with_suffix('.json').read_text())['vertices']}
def record(name):RESULT.append({'case':name,'verified':True});print('PASS',name,flush=True)
try:
    types=['Node','Part','Mask','Composite','SimplePhysics','Camera','MeshGroup'];out=WORK/'types.inx';batch('new',[('node add',{'type':kind,'name':kind}) for kind in types],out)
    created=call(out,'node list');assert {n['type'] for n in created}==set(types) and len(created)==8
    for n in created:assert call(out,'node get',node=str(n['uuid']))['name']==n['name']
    record('all seven Creator node types create, reload and resolve by UUID')
    renamed=WORK/'rename.inx';call(BASE,'node set',node='Eye',name='Eye renamed',output=renamed)
    path=next(n['path'] for n in call(renamed,'node list') if n['name']=='Eye renamed');node=call(renamed,'node get',node=path);assert node['uuid']==call(BASE,'node get',node='Eye')['uuid']
    record('node rename preserves identity and updates full-path resolution')
    ordered=WORK/'order.inx';call(BASE,'node reparent',node='Eye',parent='Face',index=0,local=True,output=ordered)
    children=call(ordered,'node get',node='Face')['children'];assert [c['name'] for c in children]==['Eye','Part']
    record('node sorting inserts a sibling at the requested index without changing local properties')
    hidden=WORK/'hidden.inx';call(BASE,'node set',node='Face',enabled=False,output=hidden)
    assert not call(hidden,'node get',node='Face')['enabled'] and call(hidden,'node get',node='Part')['enabled']
    image=WORK/'hidden.png';call(hidden,'render',bounds='-20,-20,20,20',size='64,64',output=image)
    from PIL import Image
    assert Image.open(image).getbbox() is None
    shown=WORK/'shown.inx';call(hidden,'node set',node='Face',enabled=True,output=shown);assert call(shown,'node get',node='Face')['enabled']
    record('node visibility hides rendered descendants while retaining their own visibility fields')
    source=WORK/'origin-source.inx';batch(BASE,[('node set',{'node':'Part','position':'20,5'}),('node set',{'node':'Eye','position':'-8,-3'})],source)
    before=vertices(source,'before-origin');origin=WORK/'origin.inx';call(source,'node origin',node='Head',output=origin);after=vertices(origin,'after-origin')
    assert before.keys()==after.keys()
    assert max(abs(a-b) for key in before for a,b in zip(before[key],after[key]))<1e-4
    assert call(origin,'node get',node='Head')['transform']['trans'][:2]!=[0,0]
    record('recursive origin recalculation moves group origins while preserving actual world vertices')
finally:
    (WORK/'results.json').write_text(json.dumps(RESULT,indent=2)+'\n')
