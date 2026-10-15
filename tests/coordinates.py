#!/usr/bin/env python3
"""Verify coordinate edits through posed ancestors and root-lock transforms."""
import json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BIN=Path(sys.argv[1]);BASE=ROOT/'tests/results/fixture.inx';WORK=ROOT/'tests/results/coordinates';WORK.mkdir(exist_ok=True)
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
    file=WORK/'ops.json';file.write_text(json.dumps([{'command':c,'options':o} for c,o in ops]));return call(model,'batch '+str(file),output=out)
def render(model,name,**opts):
    image=WORK/(name+'.png');call(model,'render',isolate='Part',max_size=64,output=image,**opts);return json.loads(image.with_suffix('.json').read_text())
def record(name):RESULT.append({'case':name,'verified':True});print('PASS',name,flush=True)
try:
    source=WORK/'locked-source.inx';batch(BASE,[('node set',{'node':'Head','position':'20,10','rotation':'0,0,.5','scale':'2,3'}),('node set',{'node':'Part','lock-to-root':True})],source)
    moved=WORK/'locked-world.inx';call(source,'node set',node='Part',position='5,7',space='world',output=moved)
    vertices=render(moved,'locked')['vertices'];center=[sum(v['world'][i] for v in vertices)/len(vertices) for i in (0,1)]
    assert max(abs(a-b) for a,b in zip(center,[5,7]))<1e-4,center
    record('world-position edits respect a node already locked to the puppet root')
    posed=WORK/'posed-parent.inx';batch(BASE,[('key set',{'param':'XY','node':'Head','property':'transform.t.x','at':'1,0','value':10}),('key set',{'param':'XY','node':'Part','at':'1,0','offsets':[[0,0]]*4})],posed)
    metadata=render(posed,'posed-parent',param='XY=1,0');v=next(v for v in metadata['vertices'] if v['index']==0)
    expected=[v['world'][0]+2,v['world'][1]];matrix=metadata['worldToPixel'];pixel=[sum(matrix[i][j]*expected[j] for j in (0,1))+matrix[i][2] for i in (0,1)]
    changed=WORK/'posed-edit.inx';call(posed,'mesh vertex-set',node='Part',param='XY',at='1,0',index=0,position=','.join(map(str,pixel)),space='image',reference=WORK/'posed-parent.json',output=changed)
    actual=next(v for v in render(changed,'posed-result',param='XY=1,0')['vertices'] if v['index']==0)['world']
    assert max(abs(a-b) for a,b in zip(actual,expected))<1e-3,(actual,expected)
    record('pixel vertex edits evaluate the selected key and its parameter-driven ancestor transform')

    mesh=call(BASE,'mesh get',node='Face');offsets=[[x*.5,0] for x in mesh['verts'][::2]]
    for dynamic in [False,True]:
        grouped=WORK/f'group-{dynamic}.inx';batch(BASE,[('node set',{'node':'Face','dynamic':dynamic}),('key set',{'param':'XY','node':'Face','at':'1,0','offsets':offsets}),('key set',{'param':'XY','node':'Part','at':'1,0','offsets':[[0,0]]*4})],grouped)
        metadata=render(grouped,f'group-{dynamic}',param='XY=1,0');v=next(v for v in metadata['vertices'] if v['index']==0)
        expected=[v['world'][0]+3,v['world'][1]];matrix=metadata['worldToPixel'];pixel=[sum(matrix[i][j]*expected[j] for j in (0,1))+matrix[i][2] for i in (0,1)]
        changed=WORK/f'group-edit-{dynamic}.inx';call(grouped,'mesh vertex-set',node='Part',param='XY',at='1,0',index=0,position=','.join(map(str,pixel)),space='image',reference=WORK/f'group-{dynamic}.json',output=changed)
        actual=next(v for v in render(changed,f'group-result-{dynamic}',param='XY=1,0')['vertices'] if v['index']==0)['world']
        assert max(abs(a-b) for a,b in zip(actual,expected))<1e-3,(dynamic,actual,expected)
    record('pixel key vertex edits invert both static and dynamic parent MeshGroup deformation')

    for dynamic in [False,True]:
        grouped=WORK/f'group-{dynamic}.inx';metadata=render(grouped,f'base-group-{dynamic}',param='XY=1,0');v=next(v for v in metadata['vertices'] if v['index']==0)
        expected=[v['world'][0]+3,v['world'][1]];matrix=metadata['worldToPixel'];pixel=[sum(matrix[i][j]*expected[j] for j in (0,1))+matrix[i][2] for i in (0,1)]
        changed=WORK/f'base-group-edit-{dynamic}.inx';call(grouped,'mesh vertex-set',node='Part',index=0,position=','.join(map(str,pixel)),space='image',reference=WORK/f'base-group-{dynamic}.json',output=changed)
        actual=next(v for v in render(changed,f'base-group-result-{dynamic}',param='XY=1,0')['vertices'] if v['index']==0)['world']
        assert max(abs(a-b) for a,b in zip(actual,expected))<1e-3,(dynamic,actual,expected)
    record('base vertex placement in image space retains binding remapping and inverts MeshGroup deformation')

    grouped=WORK/'group-True.inx';metadata=render(grouped,'transform-source',param='XY=1,0');before={v['index']:v['world'] for v in metadata['vertices']}
    for keyed in [False,True]:
        extra={'param':'XY','at':'1,0'} if keyed else {}
        changed=WORK/f'world-transform-{keyed}.inx';call(grouped,'mesh transform',node='Part',vertices='0,1',move=','.join(map(str,[metadata['worldToPixel'][0][0]*3+metadata['worldToPixel'][0][1]*2,metadata['worldToPixel'][1][0]*3+metadata['worldToPixel'][1][1]*2])),space='image',reference=WORK/'transform-source.json',output=changed,**extra)
        actual={v['index']:v['world'] for v in render(changed,f'world-transform-{keyed}',param='XY=1,0')['vertices']}
        for i,value in actual.items():
            expected=[before[i][0]+(3 if i in [0,1] else 0),before[i][1]+(2 if i in [0,1] else 0)]
            assert max(abs(a-b) for a,b in zip(value,expected))<1e-3,(keyed,i,value,expected)
    changed=WORK/'literal-world-transform.inx';call(grouped,'mesh transform',node='Part',param='XY',at='1,0',vertices='0',move='3,2',space='world',output=changed)
    actual=next(v for v in render(changed,'literal-world-transform',param='XY=1,0')['vertices'] if v['index']==0)['world']
    assert max(abs(a-b) for a,b in zip(actual,[before[0][0]+3,before[0][1]+2]))<1e-3
    record('world transforms move selected base and key vertices through dynamic MeshGroup mapping')
    changed=WORK/'pixel-transform.inx';call(grouped,'mesh transform',node='Part',param='XY',at='1,0',vertices='0',move='2,3',space='image',reference=WORK/'transform-source.json',output=changed)
    result=render(changed,'pixel-transform',param='XY=1,0');world=next(v for v in result['vertices'] if v['index']==0)['world'];m=metadata['worldToPixel']
    pixel=[sum(m[i][j]*world[j] for j in [0,1])+m[i][2] for i in [0,1]];original=next(v for v in metadata['vertices'] if v['index']==0)['pixel']
    assert max(abs(a-b) for a,b in zip(pixel,[original[0]+2,original[1]+3]))<1e-3,(pixel,original)
    record('image-space transform deltas use image pixels and preserve the reference pose')

    vertex=next(v for v in metadata['vertices'] if v['index']==0);start=vertex['pixel']
    changed=WORK/'pixel-brush.inx';call(grouped,'mesh brush',node='Part',param='XY',at='1,0',vertices='0',stroke=[start,[start[0]+2,start[1]+3]],radius=1000,space='image',reference=WORK/'transform-source.json',output=changed)
    world=next(v for v in render(changed,'pixel-brush',param='XY=1,0')['vertices'] if v['index']==0)['world']
    pixel=[sum(m[i][j]*world[j] for j in [0,1])+m[i][2] for i in [0,1]]
    assert max(abs(a-b) for a,b in zip(pixel,[start[0]+2,start[1]+3]))<1e-3,(pixel,start)
    record('sampled image brush strokes use pixel centers, distances and displacement')
    changed=WORK/'world-path.inx';call(grouped,'mesh path',node='Part',param='XY',at='1,0',vertices='0',space='world',**{'from':[[-50,0],[0,0],[50,0]],'to':[[-50,2],[0,2],[50,2]]},output=changed)
    actual=next(v for v in render(changed,'world-path',param='XY=1,0')['vertices'] if v['index']==0)['world']
    expected=[before[0][0],before[0][1]+2]
    assert max(abs(a-b) for a,b in zip(actual,expected))<1e-3,(actual,expected)
    record('world spline paths deform the selected key through native MeshGroup mapping')
    rectangle=[start[0]-1,start[1]-1,start[0]+1,start[1]+1]
    selected=call(grouped,'mesh select',node='Part',param='XY',at='1,0',space='image',reference=WORK/'transform-source.json',rect=rectangle)
    assert selected==[0],selected
    record('image rectangle selection compares actual posed pixels under parent deformation')

    expected=[3,4];pixel=[sum(m[i][j]*expected[j] for j in [0,1])+m[i][2] for i in [0,1]]
    inserted=WORK/'pixel-insert.inx';call(grouped,'mesh vertex-add',node='Part',position=','.join(map(str,pixel)),space='image',reference=WORK/'transform-source.json',connect_to='0,1',output=inserted)
    actual=next(v for v in render(inserted,'pixel-insert',param='XY=1,0')['vertices'] if v['index']==4)['world']
    assert max(abs(a-b) for a,b in zip(actual,expected))<1e-3,(actual,expected)
    record('image point insertion evaluates new topology and remapped forms before solving its world position')

    rotated=WORK/'rotated-mirror.inx';batch(BASE,[('node set',{'node':'Head','rotation':'0,0,1.57079632679'}),('key set',{'param':'XY','node':'Part','at':'0,0','offsets':[[0,0]]*4})],rotated)
    mirrored=WORK/'world-mirror.inx';call(rotated,'mesh vertex-set',node='Part',param='XY',at='0,0',index=0,position='18,-14',space='world',mirror_x=True,output=mirrored)
    actual={v['index']:v['world'] for v in render(mirrored,'world-mirror')['vertices']}
    assert max(abs(a-b) for a,b in zip(actual[0],[18,-14]))<1e-3
    assert max(abs(a-b) for a,b in zip(actual[1],[-18,-14]))<1e-3,actual
    record('mirrored vertex placement reflects in the chosen world axes under a rotated parent')

finally:
    (WORK/'results.json').write_text(json.dumps(RESULT,indent=2)+'\n')
