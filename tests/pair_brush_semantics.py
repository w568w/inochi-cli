#!/usr/bin/env python3
"""Verify mirror pairing persistence and every Creator brush weight function."""
import json,math,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BIN=Path(sys.argv[1]);BASE=ROOT/'tests/results/fixture.inx';WORK=ROOT/'tests/results/pair-brush';WORK.mkdir(exist_ok=True)
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
def record(name):RESULT.append({'case':name,'verified':True});print('PASS',name,flush=True)
try:
    paired=WORK/'paired.inx';batch(BASE,[('node set',{'node':'Part','name':'eye-l'}),('node set',{'node':'Eye','name':'eye-r'}),('param pair-auto',{'first-pattern':'-l','second-pattern':'-r'})],paired)
    pairs=call(paired,'param pair-list');assert len(pairs)==1
    assert pairs[0]['uuid1']==call(paired,'node get',node='eye-l')['uuid'] and pairs[0]['uuid2']==call(paired,'node get',node='eye-r')['uuid']
    record('automatic mirror pairing uses the native name-substitution patterns')
    removed=WORK/'removed.inx';call(paired,'param pair-remove',node='eye-l',output=removed)
    assert not call(removed,'param pair-list')
    again=WORK/'again.inx';call(removed,'project save',output=again);assert not call(again,'param pair-list')
    record('removing the final mirror pair remains removed after save and reload')
    deleted=WORK/'deleted.inx';call(paired,'node delete',node='eye-l',output=deleted)
    pairs=call(deleted,'param pair-list');assert len(pairs)==1 and pairs[0]['uuid1']==call(deleted,'node get',node='eye-r')['uuid'] and pairs[0]['uuid2']==4294967295
    record('node deletion clears missing mirror members while preserving their surviving counterpart')
    point=(-16,-16);center=(0,-16)
    for brush,opts,weight in [('circle',{'radius':32},.5),('soft',{'radius':32,'inner-radius':8},1-(16-8)/(32-8)),('rectangle',{'radius':32,'height':20,'inner-ratio':.5},.5)]:
        out=WORK/(brush+'.inx');call(BASE,'mesh brush',node='Part',vertices='0',brush=brush,center='0,-16',move='6,3',output=out,**{k.replace('-','_'):v for k,v in opts.items()})
        verts=call(out,'mesh get',node='Part')['verts'];expected=[point[0]+6*weight,point[1]+3*weight]
        assert max(abs(a-b) for a,b in zip(verts[:2],expected))<1e-4,(brush,verts,expected)
        assert verts[2:]==[-16,16,16,-16,16,16]
        record(brush+' brush controls produce the native selected-vertex weight and displacement')
finally:
    (WORK/'results.json').write_text(json.dumps(RESULT,indent=2)+'\n')
