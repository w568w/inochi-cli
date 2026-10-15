#!/usr/bin/env python3
"""Check project lifecycle and recovery tools on actual native model data."""
import json,os,struct,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BIN=Path(sys.argv[1]);BASE=ROOT/'tests/results/fixture.inx';WORK=ROOT/'tests/results/projects';WORK.mkdir(exist_ok=True)
ENV=os.environ.copy();RESULT=[]
def call(model,cmd,ok=True,**opts):
    args=[str(BIN),str(model),*cmd.split(),'--json']
    for k,v in opts.items():
        if isinstance(v,(dict,list)):v=json.dumps(v)
        args.append('--'+k.replace('_','-')+'='+str(v))
    p=subprocess.run(args,cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=90)
    assert (p.returncode==0)==ok,(cmd,p.returncode,p.stderr)
    return json.loads(p.stdout) if ok else p.stderr

def batch(model,ops,out):
    f=WORK/'ops.json';f.write_text(json.dumps([{'command':c,'options':o} for c,o in ops]));return call(model,'batch '+str(f),output=out)
def record(name):RESULT.append({'case':name,'verified':True});print('PASS',name,flush=True)
try:
    empty=WORK/'new.inx';call('new','project new',output=empty)
    assert len(call(empty,'node list'))==1 and not call(empty,'param list') and not call(empty,'texture list')
    saved=WORK/'save.inx';call(empty,'project save',output=saved);assert saved.read_bytes()==empty.read_bytes();call(saved,'project check')
    record('new projects and explicit saves reload through the SDK with identical bytes')
    linked=WORK/'linked.inx';batch(BASE,[('key set',{'param':'XY','node':'Part','property':'transform.t.x','at':'1,0','value':4}),('mask add',{'node':'Eye','source':'Part','mode':'DodgeMask'}),('param pair-add',{'first':'Part','second':'Eye'})],linked)
    previous={n['name']:n['uuid'] for n in call(linked,'node list')}
    for command in ['project regenerate-ids','project repair']:
        out=WORK/(command.split()[1]+'.inx');call(linked,command,output=out)
        updated={n['name']:n['uuid'] for n in call(out,'node list')};assert previous.keys()==updated.keys() and all(previous[n]!=updated[n] for n in previous)
        assert len(set(updated.values()))==len(updated)
        assert call(out,'key get',param='XY',node='Part',property='transform.t.x',at='1,0')['selectedValue']==4
        mask=call(out,'mask list',node='Eye')[0];assert mask['source']==updated['Part'] and mask['mode']=='DodgeMask',mask
        pair=call(out,'param pair-list')[0];assert pair['uuid1']==updated['Part'] and pair['uuid2']==updated['Eye']
    record('ID regeneration and repair preserve bindings, masks and mirror pairs while assigning unique IDs')
    fake=WORK/'layers.inx';call(BASE,'project layer-names',output=fake)
    assert call(fake,'node get',node='Part')['psdLayerPath']=='/Part' and call(fake,'node get',node='Eye')['psdLayerPath']=='/Eye'
    record('fake layer metadata derives native layer paths from part names')
    raw=BASE.read_bytes();size=struct.unpack('>I',raw[8:12])[0];data=json.loads(raw[12:12+size])
    def walk(n):
        yield n
        for child in n.get('children',[]):yield from walk(child)
    nodes={n['name']:n for n in walk(data['nodes'])};nodes['Eye']['uuid']=nodes['Part']['uuid']
    encoded=json.dumps(data,separators=(',',':')).encode();broken=WORK/'duplicate-ids.inx';broken.write_bytes(raw[:8]+struct.pack('>I',len(encoded))+encoded+raw[12+size:])
    error=call(broken,'project check',ok=False);assert 'Duplicate node UUID' in error
    repaired=WORK/'recovered.inx';call(broken,'project repair',output=repaired);call(repaired,'project check')
    ids=[n['uuid'] for n in call(repaired,'node list')];assert len(ids)==len(set(ids))
    record('recovery loads a duplicate-ID model and produces a validated unique-ID output')
    recovered_batch=WORK/'recovered-batch.inx';batch(broken,[('project repair',{}),('project check',{})],recovered_batch)
    ids=[n['uuid'] for n in call(recovered_batch,'node list')];assert len(ids)==len(set(ids))
    record('batch recovery shares validation and repair behavior with standalone commands')

finally:
    (WORK/'results.json').write_text(json.dumps(RESULT,indent=2)+'\n')
