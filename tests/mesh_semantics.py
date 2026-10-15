#!/usr/bin/env python3
"""Verify Creator mesh/layout operations by vertex, UV and key-form results."""
import json, math, os, subprocess, sys, hashlib
from PIL import Image, ImageChops
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BIN=Path(sys.argv[1])
ENV=os.environ.copy()
WORK=ROOT/'tests/results/mesh-semantics';WORK.mkdir(exist_ok=True)
RESULT=[]
def call(model,cmd,**opts):
    args=[str(BIN),str(model),*cmd.split(),'--json']
    for k,v in opts.items():
        if isinstance(v,(dict,list)):v=json.dumps(v)
        if isinstance(v,bool):v=str(v).lower()
        args.append('--'+k.replace('_','-')+'='+str(v))
    p=subprocess.run(args,cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=60)
    assert p.returncode==0,(cmd,p.stderr)
    return json.loads(p.stdout)
def batch(model,ops,out):
    path=WORK/'edits.json';path.write_text(json.dumps([{'command':c,'options':o} for c,o in ops]));return call(model,'batch '+str(path),output=out)
def near(actual,expected):
    assert len(actual)==len(expected),(len(actual),len(expected))
    assert max((abs(a-b) for a,b in zip(actual,expected)),default=0)<1e-4,(actual,expected)
def record(name):RESULT.append({'case':name,'verified':True});print('PASS',name,flush=True)
BASE=ROOT/'tests/results/fixture.inx'
try:
    altered=WORK/'altered.inx';call(BASE,'mesh vertex-set',node='Part',index=0,uv='.2,.3',output=altered)
    layout=WORK/'layout.inx';call(altered,'mesh layout',node='Part',output=layout)
    near(call(layout,'mesh get',node='Part')['uvs'],[0,0,0,1,1,0,1,1]);record('Creator layout derives every UV from vertex coordinates and texture size')
    moved=WORK/'moved.inx';call(BASE,'mesh vertex-set',node='Part',index=0,position='-8,-8',uv_policy='creator',output=moved)
    mesh=call(moved,'mesh get',node='Part');near(mesh['verts'][:2],[-8,-8]);near(mesh['uvs'][:2],[.25,.25]);record('vertex editor layout policy updates UVs with moved base vertices')
    moved=WORK/'preserved.inx';call(altered,'mesh vertex-set',node='Part',index=0,position='-8,-8',output=moved)
    near(call(moved,'mesh get',node='Part')['uvs'][:2],[.2,.3]);record('explicit preserve policy retains existing arbitrary UV mapping')
    added=WORK/'connected.inx';call(BASE,'mesh vertex-add',node='Part',position='0,0',connect_to='0,1',output=added)
    mesh=call(added,'mesh get',node='Part');assert len(mesh['verts'])==10;near(mesh['verts'][8:],[0,0]);near(mesh['uvs'][8:],[.5,.5])
    edges=set()
    for i in range(0,len(mesh['indices']),3):
        t=mesh['indices'][i:i+3]
        for a,b in zip(t,t[1:]+t[:1]):edges.add(frozenset([a,b]))
    assert frozenset([0,4]) in edges and frozenset([1,4]) in edges,edges
    record('point insertion with auto-connect uses native mesh connections')
    field=[[.5*x+2,.25*y-1] for x,y in [(-16,-16),(-16,16),(16,-16),(16,16)]]
    keyed=WORK/'keyed.inx';call(BASE,'key set',param='XY',node='Part',at='1,0',offsets=field,output=keyed)
    refined=WORK/'refined.inx';call(keyed,'mesh grid',node='Part',x='-16,0,16',y='-16,0,16',output=refined)
    mesh=call(refined,'mesh get',node='Part');key=call(refined,'key get',param='XY',node='Part',at='1,0')
    expected=[[.5*x+2,.25*y-1] for x,y in zip(mesh['verts'][::2],mesh['verts'][1::2])]
    for a,b in zip(key['selectedValue'],expected):near(a,b)
    assert len(key['selectedValue'])==9 and key['selectedIsSet'];record('topology refinement remaps a linear deformation field to all new vertices')
    path=WORK/'path.inx';call(BASE,'mesh path',node='Part',**{'from':[[-32,0],[0,0],[32,0]],'to':[[-32,2],[0,2],[32,2]]},output=path)
    mesh=call(path,'mesh get',node='Part');near(mesh['verts'],[-16,-14,-16,18,16,-14,16,18]);record('native spline path translates all base vertices as defined by its controls')
    keyed=WORK/'path-key-base.inx';call(BASE,'key set',param='XY',node='Part',at='1,0',offsets=[[3,4]]*4,output=keyed)
    path=WORK/'path-key.inx';call(keyed,'mesh path',node='Part',param='XY',at='1,0',vertices='0',**{'from':[[-32,0],[0,0],[32,0]],'to':[[-32,2],[0,2],[32,2]]},output=path)
    key=call(path,'key get',param='XY',node='Part',at='1,0');near(key['selectedValue'][0],[3,6])
    for v in key['selectedValue'][1:]:near(v,[3,4])
    near(call(path,'mesh get',node='Part')['verts'],[-16,-16,-16,16,16,-16,16,16]);record('path editing retains prior key offsets, respects selected vertices and leaves base geometry untouched')
    for axis,expected in [(0,[16,-16,16,16,-16,-16,-16,16]),(1,[-16,16,-16,-16,16,16,16,-16])]:
        out=WORK/f'mirror-{axis}.inx';call(BASE,'mesh mirror',node='Part',axis=axis,output=out);near(call(out,'mesh get',node='Part')['verts'],expected)
    record('horizontal and vertical mesh mirrors produce the defined reflected positions')
    refined=WORK/'copy-source.inx';call(BASE,'mesh grid',node='Part',x='-16,0,16',y='-16,0,16',output=refined)
    copied=WORK/'copy-target.inx';call(refined,'mesh copy',node='Eye',source='Part',uv_policy='creator',output=copied)
    source=call(refined,'mesh get',node='Part');target=call(copied,'mesh get',node='Eye')
    near(target['verts'],source['verts']);assert target['indices']==source['indices']
    expected=[value/32+.5 for value in target['verts']];near(target['uvs'],expected)
    record('mesh copy keeps source topology and applies the native target texture layout')
    symmetric=WORK/'symmetric.inx'
    call(BASE,'mesh transform',node='Part',vertices='0',move='2,3',mirror_x=True,mirror_y=True,output=symmetric)
    near(call(symmetric,'mesh get',node='Part')['verts'],[-14,-13,-14,13,14,-13,14,13])
    assert set(call(BASE,'mesh select',node='Part',vertices='0',mirror_x=True,mirror_y=True))=={0,1,2,3}
    record('two-axis editing reflects displacement and includes all mirrored selection counterparts')
    centered=WORK/'centered.inx'
    call(BASE,'mesh transform',node='Part',move='5,9',output=centered)
    call(centered,'mesh vertex-set',node='Part',index=0,position='-9,-4',mirror_x=True,mirror_y=True,mirror_origin='5,9',output=symmetric)
    near(call(symmetric,'mesh get',node='Part')['verts'],[-9,-4,-9,22,19,-4,19,22])
    record('vertex placement reflects around a nonzero horizontal and vertical mirror origin')
    call(BASE,'mesh vertex-add',node='Part',position='-8,-8',mirror_x=True,mirror_y=True,connect_to='0',output=symmetric)
    mesh=call(symmetric,'mesh get',node='Part');near(mesh['verts'][8:],[-8,-8,8,-8,-8,8,8,8])
    call(symmetric,'mesh vertex-remove',node='Part',vertices='4',mirror_x=True,mirror_y=True,output=centered)
    near(call(centered,'mesh get',node='Part')['verts'],call(BASE,'mesh get',node='Part')['verts'])
    record('mirrored insertion creates each counterpart once and mirrored removal deletes all counterparts')
    call(BASE,'mesh vertex-add',node='Part',position='0,0',mirror_x=True,mirror_y=True,output=symmetric)
    assert len(call(symmetric,'mesh get',node='Part')['verts'])==10
    record('insertion on both mirror axes creates one shared center vertex')
    call(BASE,'mesh disconnect',node='Part',a=0,b=1,mirror_x=True,output=symmetric)
    mesh=call(symmetric,'mesh get',node='Part')
    assert not mesh['indices'],mesh['indices']
    record('mirrored disconnection removes both triangle boundaries in the native exported mesh')

    selected=call(BASE,'mesh select',node='Part',polygon=[[-20,-20],[0,-20],[0,0],[-20,0]])
    assert selected==[0],selected
    selected=call(BASE,'mesh select',node='Part',polygon=[[-20,-20],[0,-20],[0,0],[-20,0]],mirror_x=True,mirror_y=True)
    assert set(selected)=={0,1,2,3},selected
    record('native lasso polygon selection and reflected selection return the expected vertex indices')

    preview=WORK/'preview-base.inx'
    call(BASE,'mesh set',node='Part',data={'vertices':[[-16,-16],[-16,16],[16,-16],[16,16]],'uvs':[[0,0],[0,1],[1,0],[1,1]],'triangles':[]},output=preview)
    digest=hashlib.sha256(preview.read_bytes()).hexdigest()
    plain=WORK/'preview-plain.png';triangulated=WORK/'preview-triangulated.png'
    call(preview,'render',isolate='Part',mesh=True,max_size=64,output=plain)
    call(preview,'render',isolate='Part',mesh=True,triangulate=True,max_size=64,output=triangulated)
    assert Image.open(plain).getbbox() is None
    assert ImageChops.difference(Image.open(plain),Image.open(triangulated)).convert("RGB").getbbox() is not None
    assert any(pixel[:3]==(0,220,255) for pixel in Image.open(triangulated).get_flattened_data())
    assert hashlib.sha256(preview.read_bytes()).hexdigest()==digest
    assert json.loads(triangulated.with_suffix('.json').read_text())['triangulationPreview'] is True
    record('native triangulation preview renders proposed connections without modifying the model')

    selected=call(keyed,'mesh select',node='Part',param='XY',at='1,0',polygon=[[-20,-20],[0,-20],[0,0],[-20,0]])
    assert selected==[0],selected
    record('key-form lasso selection queries deformed vertex positions')

    axis=WORK/'axes.inx';call(BASE,'mesh grid',node='Part',x='-16,0,16',y='-16,0,16',output=axis)
    added=WORK/'axis-added.inx';call(axis,'mesh grid',node='Part',x='-16,0,8,16',y='-16,0,16',output=added)
    assert len(call(added,'mesh get',node='Part')['verts'])==24
    moved=WORK/'axis-moved.inx';call(added,'mesh grid',node='Part',x='-16,0,10,16',y='-16,0,16',output=moved)
    assert 10 in call(moved,'mesh get',node='Part')['verts'][::2]
    removed=WORK/'axis-removed.inx';call(moved,'mesh grid',node='Part',x='-16,0,16',y='-16,0,16',output=removed)
    assert call(removed,'mesh get',node='Part')['verts']==call(axis,'mesh get',node='Part')['verts']
    record('grid axis addition, movement and removal regenerate the requested native rows and columns')

    empty=WORK/'connections-base.inx';call(BASE,'mesh set',node='Part',data={'vertices':[[-16,-16],[-16,16],[16,-16]],'uvs':[[0,0],[0,1],[1,0]],'triangles':[]},output=empty)
    constructed=WORK/'constructed.inx';preview=WORK/'edge-preview.png'
    result=batch(empty,[('mesh connect',{'node':'Part','a':0,'b':1}),('mesh get',{'node':'Part'}),('render image',{'isolate':'Part','mesh':True,'size':'64,64','output':str(preview)}),('mesh connect',{'node':'Part','a':1,'b':2}),('mesh connect',{'node':'Part','a':2,'b':0}),('mesh get',{'node':'Part'})],constructed)
    assert result[1]['edges']==[[0,1]] and not result[1]['indices']
    assert Image.open(preview).getbbox() is not None
    assert len(call(constructed,'mesh get',node='Part')['indices'])==3
    record('batch connection editing retains isolated edges through previews until a complete triangle can be saved')
    restored=WORK/'connections-restored.inx'
    result=batch(empty,[('mesh connect',{'node':'Part','a':0,'b':1}),('mesh connect',{'node':'Part','a':1,'b':2}),('history undo',{}),('mesh get',{'node':'Part'}),('history redo',{}),('mesh get',{'node':'Part'}),('mesh connect',{'node':'Part','a':2,'b':0})],restored)
    assert result[3]['edges']==[[0,1]] and len(result[5]['edges'])==2
    assert len(call(restored,'mesh get',node='Part')['indices'])==3
    record('undo and redo restore transient mesh connectivity as well as serialized geometry')

finally:
    (WORK/'results.json').write_text(json.dumps(RESULT,indent=2)+'\n')
