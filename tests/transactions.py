#!/usr/bin/env python3
"""Exercise batch output publication, checkpoints, failure and input boundaries."""
import json, os, subprocess, sys, hashlib
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
BIN=Path(sys.argv[1]);BASE=ROOT/'tests/results/fixture.inx'
ENV=os.environ.copy()
WORK=ROOT/'tests/results/transactions';WORK.mkdir(exist_ok=True)
results=[]
def run(model,command,options=None,success=True):
    argv=[str(BIN),str(model),*command.split(),'--json']
    for k,v in (options or {}).items():argv.append('--'+k+'='+str(v).lower() if isinstance(v,bool) else '--'+k+'='+str(v))
    p=subprocess.run(argv,cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=60)
    assert (p.returncode==0)==success,(command,p.stderr)
    return json.loads(p.stdout) if success else p.stderr

def batch(ops,final,success=True,in_place=False,model=BASE):
    file=WORK/'commands.json';file.write_text(json.dumps([{'command':c,'options':o} for c,o in ops]))
    options={'in-place':True} if in_place else {'output':final}
    return run(model,'batch '+str(file),options,success)

def check(name,fn):fn();results.append({'case':name,'verified':True});print('PASS',name,flush=True)
def failed_operation():
    model=WORK/'unchanged.inp';png=WORK/'unchanged.png';side=png.with_suffix('.json');final=WORK/'unchanged.inx'
    originals={model:b'old model',png:b'old PNG',side:b'old metadata',final:b'old final'}
    for path,value in originals.items():path.write_bytes(value)
    error=batch([
        ('export inp',{'resolution':128,'padding':2,'output':str(model)}),
        ('render image',{'max-size':64,'output':str(png)}),
        ('node set',{'node':'missing','position':'1,2'}),
    ],final,False)
    assert 'Batch operation 2' in error
    assert all(path.read_bytes()==value for path,value in originals.items())
    assert not list(WORK.glob('.inochi-*'))
def prepare_failure():
    first=WORK/'first.png';final=WORK/'prepared-final.inx';first.write_bytes(b'old first');final.write_bytes(b'old final')
    impossible=WORK/'missing-directory'/'other.png'
    batch([('render image',{'output':str(first),'max-size':32}),('render image',{'output':str(impossible),'max-size':32}),('node set',{'node':'Part','position':'4,5'})],final,False)
    assert first.read_bytes()==b'old first' and final.read_bytes()==b'old final'
    assert not impossible.exists() and not list(WORK.glob('.inochi-*'))
def checkpoint_and_read():
    early=WORK/'early.inx';late=WORK/'late.inx';png=WORK/'reference.png'
    output=batch([
        ('node set',{'node':'Part','position':'1,2'}),
        ('project save',{'output':str(early)}),
        ('render image',{'max-size':64,'output':str(png),'creator-reference':True}),
        ('node set',{'node':'Part','position':'3,4'}),
        ('project import',{'file':str(early)}),
    ],late)
    assert run(early,'node get',{'node':'Part'})['transform']['trans'][:2]==[1,2]
    assert run(late,'node get',{'node':'Part'})['transform']['trans'][:2]==[1,2]
    assert output[2]['image']==str(png) and output[2]['metadata']==str(png.with_suffix('.json'))
    meta=json.loads(png.with_suffix('.json').read_text());assert meta['creatorReference']==str(png.with_name('reference.creator.png'))
    assert Image.open(png).width>0

def staged_reference():
    png=WORK/'pixels.png';final=WORK/'pixel-edit.inx'
    batch([('render image',{'output':str(png),'size':'64,64','bounds':'-32,-32,32,32','padding':0}),('mesh vertex-set',{'node':'Part','index':0,'position':'32,32','space':'image','reference':str(png.with_suffix('.json'))})],final)
    mesh=run(final,'mesh get',{'node':'Part'});assert all(abs(x)<1e-4 for x in mesh['verts'][:2])

def runtime_history():
    final=WORK/'runtime.inx';picture=WORK/'runtime.png'
    outputs=batch([
        ('node set',{'node':'Part','pixel-snap':True}),
        ('render image',{'max-size':32,'output':str(picture)}),
        ('node get',{'node':'Part','runtime':True}),
        ('node set',{'node':'Part','pixel-snap':False}),
        ('history undo',{}),('node get',{'node':'Part','runtime':True}),
        ('history redo',{}),('node get',{'node':'Part','runtime':True}),
        ('history begin',{}),('node set',{'node':'Part','pixel-snap':True}),('node set',{'node':'Part','position':'2,3'}),('history end',{}),
        ('history undo',{}),('node get',{'node':'Part','runtime':True}),
        ('history redo',{}),('node get',{'node':'Part','runtime':True}),
    ],final)
    assert outputs[2]['runtime']['pixelSnap'] is True
    assert outputs[5]['runtime']['pixelSnap'] is True
    assert outputs[7]['runtime']['pixelSnap'] is False
    assert outputs[13]['runtime']['pixelSnap'] is False and outputs[13]['transform']['trans'][:2]==[0,0]
    assert outputs[15]['runtime']['pixelSnap'] is True and outputs[15]['transform']['trans'][:2]==[2,3]

def history_selection():
    final=WORK/'selected-history.inx'
    outputs=batch([
        ('node set',{'node':'Part','position':'1,2'}),('node set',{'node':'Part','position':'3,4'}),('history list',{}),
        ('history seek',{'index':0}),('node get',{'node':'Part'}),('history seek',{'index':2}),('node get',{'node':'Part'}),
        ('history clear',{}),('history list',{}),('node get',{'node':'Part'}),
    ],final)
    assert outputs[2]=={'index':2,'count':2}
    assert outputs[4]['transform']['trans'][:2]==[0,0]
    assert outputs[6]['transform']['trans'][:2]==[3,4]
    assert outputs[8]=={'index':0,'count':0} and outputs[9]['transform']['trans'][:2]==[3,4]

def input_protection():
    model=WORK/'input.inx';model.write_bytes(BASE.read_bytes());before=model.read_bytes()
    batch([('export inp',{'resolution':128,'output':str(model)})],WORK/'protected.inx',False,model=model)
    assert model.read_bytes()==before
    batch([('node set',{'node':'Part','position':'7,8'}),('node delete',{'node':'missing'})],model,False,True,model)
    assert model.read_bytes()==before
    batch([('node set',{'node':'Part','position':'7,8'})],model,True,True,model)
    assert run(model,'node get',{'node':'Part'})['transform']['trans'][:2]==[7,8]
    alias=WORK/'input-alias.inx'
    alias.unlink(missing_ok=True)
    alias.hardlink_to(model)
    before=model.read_bytes()
    run(model,'project save',{'output':alias},False)
    assert model.read_bytes()==before and alias.samefile(model)
def native_history():
    native=WORK/'native-history.inx'
    outputs=batch([('node set',{'node':'Part','position':'1,2'}),('node set',{'node':'Part','position':'3,4'}),('history list',{'details':True}),('history undo',{}),('node set',{'node':'Part','position':'5,6'}),('history list',{'details':True}),('history begin',{}),('node set',{'node':'Part','position':'7,8'}),('history begin',{}),('node set',{'node':'Eye','position':'9,10'}),('history end',{}),('history end',{}),('history list',{'details':True}),('history seek',{'index':0}),('node get',{'node':'Part'})],native)
    assert outputs[2]['count']==2 and [v['description'] for v in outputs[2]['actions']]==['node set','node set']
    assert outputs[5]['count']==2 and all(v['applied'] for v in outputs[5]['actions'])
    assert outputs[12]['count']==3 and outputs[12]['index']==3
    assert outputs[14]['transform']['trans'][:2]==[0,0]


try:
    check('later operation failure preserves exported models, images, metadata and final output',failed_operation)
    check('output preparation failure publishes nothing and removes temporary files',prepare_failure)
    check('checkpoints and generated files are readable within a batch without premature publication',checkpoint_and_read)
    check('generated image coordinate metadata can drive later edits in the same batch',staged_reference)
    check('preview and grouped undo/redo retain runtime flags as well as model data',runtime_history)
    check('history selection restores exact positions and clear retains the current model',history_selection)
    check('nested output and file-alias input overwrite protections; failed and successful in-place batches',input_protection)
    check('Creator action stack exposes descriptions, truncates redo branches and keeps nested edit groups together',native_history)

finally:
    (WORK/'results.json').write_text(json.dumps(results,indent=2)+'\n')
