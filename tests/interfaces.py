#!/usr/bin/env python3
"""Check catalog/schema parity and Agent-facing command/input contracts."""
import json, os, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BIN = Path(sys.argv[1])
WORK = ROOT / 'tests/results/interfaces'
WORK.mkdir(exist_ok=True)
BASE = ROOT / 'tests/results/fixture.inx'
ENV = os.environ.copy()
RESULT = []
def run(*args, stdin=None, ok=True):
    p = subprocess.run([str(BIN), *map(str,args)], input=stdin, text=True,
                       capture_output=True, env=ENV, cwd=ROOT, timeout=90)
    assert (p.returncode == 0) == ok, (args, p.stderr)
    return p

def record(case):
    RESULT.append({'case':case,'verified':True})
    print('PASS',case,flush=True)
try:
    cap = json.loads(run('capabilities','--json').stdout)
    schema = cap['batchSchema']
    variants = schema['items']['oneOf']
    assert schema['type']=='array'
    assert len(variants)==len(cap['commands'])
    for command, variant in zip(cap['commands'],variants):
        assert variant['required']==['command'] and variant['additionalProperties'] is False
        assert variant['properties']['command']['const']==command['command']
        options=variant['properties']['options']
        assert options['additionalProperties'] is False
        assert set(options['properties'])==set(command['options'])|{'output'}
        assert all(value=={} for value in options['properties'].values())
    (WORK/'batch.schema.json').write_text(json.dumps(schema,indent=2)+'\n')
    record('generated batch schema has exact command and option parity with the registry')
    p=run(BASE,'batch','-','--help')
    assert 'zero-based operation index' in p.stdout
    p=run(BASE,'node','typo','--help',ok=False)
    assert 'Unknown command' in p.stderr
    record('batch format help is available without loading a model and unknown command help fails')
    output=WORK/'stdin.inx'
    ops=[{'command':'node set','options':{'node':'Part','position':[3,4]}},
         {'command':'mesh select','options':{'node':'Part','polygon':[[-20,-20],[0,-20],[0,0],[-20,0]]}}]
    p=run(BASE,'batch','-','-o',output,'--json',stdin=json.dumps(ops))
    assert json.loads(p.stdout)[1]==[0]
    node=json.loads(run(output,'node','get','--node=Part','--json').stdout)
    assert node['transform']['trans'][:2]==[3,4]
    offsets=[[1,2]]*4
    p=run(BASE,'key','set','--param=XY','--node=Part','--at=1,0','--offsets=-','-o',output,
          stdin=json.dumps(offsets))
    key=json.loads(run(output,'key','get','--param=XY','--node=Part','--at=1,0','--json').stdout)
    assert key['selectedValue']==offsets
    record('stdin batches and nested arrays share the standalone operation implementation')
    for ops, expected in [([{'command':'node set','options':{'node':'Part','typo':1}}], 'Unknown option'),
                          ([{'command':'node list','typo':1}], 'Unknown batch field')]:
        fail=WORK/'must-not-exist.inx'
        fail.unlink(missing_ok=True)
        p=run(BASE,'batch','-','-o',fail,stdin=json.dumps(ops),ok=False)
        assert 'Batch operation 0' in p.stderr and expected in p.stderr and not fail.exists()
    record('unknown batch fields and command options report the index and publish no model')
    duplicate=WORK/'duplicate-parameters.inx'
    run(BASE,'batch','-','-o',duplicate,stdin=json.dumps([{'command':'param add','options':{'name':'XY','vec2':True}}]))
    p=run(duplicate,'param','get','--param=XY','--json',ok=False)
    assert 'Ambiguous parameter' in p.stderr and 'candidates:' in p.stderr and p.stderr.count('XY (')==2,p.stderr
    record('ambiguous parameter names report both UUID candidates')
    fail=WORK/'unbound-query.inx';fail.unlink(missing_ok=True)
    p=run(BASE,'batch','-','-o',fail,stdin=json.dumps([{'command':'mesh select','options':{'node':'Eye','param':'XY','at':'0,0'}}]),ok=False)
    assert 'Deformation binding not found' in p.stderr and not fail.exists()
    record('key-form selection without a binding fails instead of creating model data')

    for first in [{'options':{}},42]:
        p=run(BASE,'batch','-','-o',WORK/'invalid-row.inx',stdin=json.dumps([first]),ok=False)
        assert 'Batch operation 0' in p.stderr,p.stderr
    record('malformed first batch operations retain the indexed failure contract')

    values=WORK/'vertices.json';values.write_text('[0, 2]')
    p=run(BASE,'mesh','select','--node=Part','--vertices=@'+str(values),'--json')
    assert json.loads(p.stdout)==[0,2]
    position=WORK/'position.json';position.write_text('[3, 4]')
    output=WORK/'array-position.inx';run(BASE,'node','set','--node=Part','--position=@'+str(position),'-o',output)
    assert json.loads(run(output,'node','get','--node=Part','--json').stdout)['transform']['trans'][:2]==[3,4]
    output=WORK/'array-grid.inx';run(BASE,'mesh','grid','--node=Part','--x=[-16,0,16]','--y=[-16,0,16]','-o',output)
    assert len(json.loads(run(output,'mesh','get','--node=Part','--json').stdout)['verts'])==18
    record('flat numeric arrays accept JSON literals and file inputs alongside comma-separated values')

    output=WORK/'comma-name.inx'
    ops=[{'command':'node set','options':{'node':'Eye','name':'Eye, left'}},{'command':'key set','options':{'param':'XY','node':'Eye, left','property':'transform.t.x','at':[1,0],'value':4}},{'command':'param split','options':{'param':'XY','name':'Eye parameter','nodes':['Eye, left']}}]
    run(BASE,'batch','-','-o',output,stdin=json.dumps(ops))
    assert json.loads(run(output,'key','get','--param=Eye parameter','--node=Eye, left','--property=transform.t.x','--at=1,0','--json').stdout)['selectedValue']==4
    record('JSON node selector arrays preserve names containing commas')

    filtered=json.loads(run(BASE,'node','list','--filter=eYe','--json').stdout)
    assert [n['name'] for n in filtered]==['Eye']
    filtered=json.loads(run(BASE,'param','list','--filter=bLiNk','--json').stdout)
    assert [p['name'] for p in filtered]==['Blink']
    record('node and parameter filters match names without case sensitivity')

finally:
    (WORK/'results.json').write_text(json.dumps(RESULT,indent=2)+'\n')
