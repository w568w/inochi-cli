#!/usr/bin/env python3
"""Verify node/subtree deletion clears graph links and remains undoable."""
import json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BIN=Path(sys.argv[1]);BASE=ROOT/'tests/results/fixture.inx'
WORK=ROOT/'tests/results/node-graph';WORK.mkdir(exist_ok=True);RESULT=[]
ENV=os.environ.copy()
def call(model,cmd,**opts):
    args=[str(BIN),str(model),*cmd.split(),'--json']
    for k,v in opts.items():
        if isinstance(v,(dict,list)):v=json.dumps(v)
        args.append('--'+k.replace('_','-')+'='+str(v))
    p=subprocess.run(args,cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=90)
    assert p.returncode==0,(cmd,p.returncode,p.stderr);return json.loads(p.stdout)
def batch(model,ops,out):
    f=WORK/'ops.json';f.write_text(json.dumps([{'command':c,'options':o} for c,o in ops]));return call(model,'batch '+str(f),output=out)
def record(name):RESULT.append({'case':name,'verified':True});print('PASS',name,flush=True)
try:
    linked=WORK/'linked.inx';batch(BASE,[('key set',{'param':'XY','node':'Part','property':'transform.t.x','at':'1,0','value':4}),('key set',{'param':'XY','node':'Eye','property':'transform.t.x','at':'1,0','value':2}),('mask add',{'node':'Eye','source':'Part'}),('node add',{'type':'Composite','name':'Composite'}),('mask add',{'node':'Composite','source':'Part'})],linked)
    deleted=WORK/'deleted.inx';call(linked,'node delete',node='Part',output=deleted)
    eye=call(deleted,'node get',node='Eye')['uuid']
    assert [b['node'] for b in call(deleted,'param get',param='XY')['bindings']]==[eye]
    assert not call(deleted,'mask list',node='Eye') and not call(deleted,'mask list',node='Composite')
    record('node deletion clears its parameter bindings and all Part and Composite masks')
    subtree=WORK/'subtree.inx';call(linked,'node delete',node='Face',output=subtree)
    assert not call(subtree,'param get',param='XY')['bindings']
    assert not call(subtree,'mask list',node='Composite')
    names=[n['name'] for n in call(subtree,'node list')];assert not {'Face','Part','Eye'}&set(names)
    record('subtree deletion clears descendant bindings and external masks')
    restored=WORK/'restored.inx';batch(linked,[('node delete',{'node':'Part'}),('history undo',{})],restored)
    assert call(restored,'project inspect')==call(linked,'project inspect')
    record('deletion undo restores the entire node, binding and mask graph')
finally:
    (WORK/'results.json').write_text(json.dumps(RESULT,indent=2)+'\n')
