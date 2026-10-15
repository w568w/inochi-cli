#!/usr/bin/env python3
"""Verify GUI-equivalent results; a zero exit code alone is not an assertion."""
import json, math, os, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BIN=Path(sys.argv[1])
ENV=os.environ.copy()
WORK=ROOT/'tests/results/semantics';WORK.mkdir(parents=True,exist_ok=True)
results=[]
def call(model,command,**options):
    argv=[str(BIN),str(model),*command.split(),'--json']
    for k,v in options.items():
        if isinstance(v,(dict,list)):v=json.dumps(v)
        if isinstance(v,bool):v=str(v).lower()
        argv.append('--'+k.replace('_','-')+'='+str(v))
    p=subprocess.run(argv,cwd=ROOT,env=ENV,capture_output=True,text=True,timeout=60)
    assert p.returncode==0,(command,p.stderr)
    return json.loads(p.stdout)
def batch(model,operations,path):
    plan=WORK/'edit.json';plan.write_text(json.dumps([{'command':c,'options':o} for c,o in operations]))
    return call(model,'batch '+str(plan),output=path)
def check(name,fn):
    fn();results.append({'case':name,'verified':True});print('PASS',name,flush=True)
def preset():
    path=WORK/'mouth.inx';call('new','param mouth-shape',name='Mouth',output=path)
    p=call(path,'param get',param='Mouth')
    assert p['min']==[-1,0] and p['max']==[1,1]
    assert p['is_vec2'] is True
    assert all(math.isclose(x,y,abs_tol=1e-6) for x,y in zip(p['axis_points'][0],[0,.25,.5,.6,1]))
    assert all(math.isclose(x,y,abs_tol=1e-6) for x,y in zip(p['axis_points'][1],[0,.3,.5,.6,1]))
    assert len(p['axis_points'][0])==len(p['axis_points'][1])==5

def range_presets():
    path=WORK/'ranges.inx'
    ops=[]
    for dim in (1,2):
        for lo in (0,-1):
            ops.append(('param add',{'name':f'p{dim}_{lo}','vec2':dim==2,'min':f'{lo},{lo}','max':'1,1'}))
    batch('new',ops,path)
    for dim in (1,2):
        for lo in (0,-1):
            p=call(path,'param get',param=f'p{dim}_{lo}')
            assert p['axis_points'][0]==([0,1] if lo==0 else [0,.5,1])
            assert p['axis_points'][1]==([0] if dim==1 else [0,1] if lo==0 else [0,.5,1])

def animation():
    path=WORK/'animation.inx'
    batch(ROOT/'tests/results/fixture.inx',[
        ('animation add',{'name':'Turn','length':12,'fps':60}),
        ('animation lane-add',{'name':'Turn','param':'XY'}),
        ('animation key-set',{'name':'Turn','param':'XY','frame':0,'value':-1}),
        ('animation key-set',{'name':'Turn','param':'XY','frame':11,'value':1}),
        ('animation set',{'name':'Turn','lead-in':2,'lead-out':10,'new-name':'Renamed'}),
    ],path)
    a=call(path,'animation list');assert set(a)=={'Renamed'}
    assert a['Renamed']['leadIn']==2 and a['Renamed']['leadOut']==10
    def render(name,**opts):
        output=WORK/(name+'.png');call(path,'render',animation='Renamed',max_size=64,output=output,**opts)
        return json.loads(output.with_suffix('.json').read_text())
    at=render('at',frame=5)
    assert at['animation']['frame']==5 and at['animation']['paused']
    assert math.isclose(at['parameters']['XY'][0],-1+10/11,abs_tol=1e-5)
    end=render('end',time=.5)
    assert not end['animation']['playing'] and end['animation']['looped']==0
    looping=render('loop',time=.5,loop=True)
    assert looping['animation']['looped']>=2 and looping['animation']['looping']
    assert 2<=looping['animation']['frame']<=10
    snap=render('snap',time=.041,snap_to_frames=True)
    assert math.isclose(snap['parameters']['XY'][0],-1+2*2/11,abs_tol=1e-5)
    renamed=WORK/'rename.inx';call(path,'animation rename',name='Renamed',target='Final',output=renamed)
    assert set(call(renamed,'animation list'))=={'Final'}
    video=WORK/'loops.mp4';call(renamed,'export video',animation='Final',loops=2,fps='auto',size='64,64',output=video)
    stream=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_entries','stream=nb_read_frames,r_frame_rate','-of','json',str(video)],text=True))['streams'][0]
    # UI export formula: lead-in 2 + loop segment 8*2 + lead-out 2.
    assert int(stream['nb_read_frames'])==20,stream

def automation():
    path=WORK/'automation.inx'
    batch(ROOT/'tests/results/fixture.inx',[
        ('automation add',{'name':'Wave','type':'sine'}),
        ('automation bind',{'name':'Wave','param':'XY','axis':0,'range':'-0.4,0.7'}),
        ('automation set',{'name':'Wave','speed':2,'phase':.5,'enabled':False}),
        ('automation add',{'name':'Spring','type':'physics'}),
        ('automation bind',{'name':'Spring','param':'XY','axis':0,'range':'-1,1','position':'0,0','distance':2}),
        ('automation bind',{'name':'Spring','param':'XY','axis':1,'range':'-1,1','position':'0,2','distance':2}),
        ('automation set',{'name':'Spring','damping':.2,'bounciness':.8,'gravity':3,'enabled':False}),
    ],path)
    sine=call(path,'automation get',name='Wave');assert sine['enabled'] is False
    assert math.isclose(sine['phase'],.5) and math.isclose(sine['speed'],2)
    assert all(math.isclose(x,y,abs_tol=1e-6) for x,y in zip(sine['bindings'][0]['range'],[-.4,.7]))
    spring=call(path,'automation get',name='Spring');assert len(spring['nodes'])==2 and len(spring['bindings'])==2
    assert spring['enabled'] is False and math.isclose(spring['gravity'],3)
    assert spring['nodes'][1]['distance']==2 and spring['nodes'][1]['position']==[0,2]
    out=WORK/'unbind.inx';call(path,'automation unbind',name='Spring',index=1,output=out)
    spring=call(out,'automation get',name='Spring');assert len(spring['nodes'])==len(spring['bindings'])==1

def coordinates():
    path=WORK/'coordinates.inx'
    quad={'vertices':[[-16,-16],[-16,16],[16,-16],[16,16]],'uvs':[[0,0],[0,1],[1,0],[1,1]],'triangles':[0,1,2,2,1,3]}
    batch('new',[
        ('node add',{'name':'Head'}),('node set',{'node':'Head','position':'10,20','rotation':'0,0,1.57079632679','scale':'2,3'}),
        ('node add',{'name':'Part','type':'Part','parent':'Head'}),('texture load',{'node':'Part','file':str(ROOT/'tests/fixtures/part.png')}),
        ('mesh set',{'node':'Part','data':quad}),('node set',{'node':'Part','origin':'3,5'}),
        ('param add',{'name':'XY','vec2':True}),
    ],path)
    picture=WORK/'coordinates.png';call(path,'render',output=picture,max_size=128)
    meta=json.loads(picture.with_suffix('.json').read_text())
    vertex=next(v for v in meta['vertices'] if v['index']==0)
    assert math.isclose(vertex['world'][0],73,abs_tol=1e-4),vertex
    assert math.isclose(vertex['world'][1],-18,abs_tol=1e-4),vertex
    assert all(0<=v['pixel'][0]<=meta['width'] and 0<=v['pixel'][1]<=meta['height'] for v in meta['vertices'])
    def apply(m,xy):return [m[i][0]*xy[0]+m[i][1]*xy[1]+m[i][2] for i in (0,1)]
    assert all(math.isclose(x,y,abs_tol=1e-4) for x,y in zip(apply(meta['pixelToWorld'],vertex['pixel']),vertex['world']))
    desired=[50,60];pixel=apply(meta['worldToPixel'],desired)
    moved=WORK/'moved.inx';call(path,'node set',node='Part',position=','.join(map(str,pixel)),space='image',reference=picture.with_suffix('.json'),output=moved)
    transform=call(moved,'node get',node='Part')['transform']['trans']
    assert math.isclose(transform[0],20,abs_tol=1e-4) and math.isclose(transform[1],-40/3,abs_tol=1e-4),transform
    grid=WORK/'grid-coordinates.png';call(path,'render grid',param='XY',values='-1,0,1',output=grid,max_size=64)
    gm=json.loads(grid.with_suffix('.json').read_text());tile=gm['tiles'][8]
    pixel=apply(tile['sheetWorldToPixel'],desired)
    assert all(math.isclose(x,y,abs_tol=1e-4) for x,y in zip(apply(tile['sheetPixelToWorld'],pixel),desired))
    moved=WORK/'grid-moved.inx';call(path,'node set',node='Part',position=','.join(map(str,pixel)),space='image',reference=grid.with_suffix('.json'),tile='2,2',output=moved)
    transform=call(moved,'node get',node='Part')['transform']['trans']
    assert math.isclose(transform[0],20,abs_tol=1e-4) and math.isclose(transform[1],-40/3,abs_tol=1e-4),transform

def brush_modes():
    base=ROOT/'tests/results/fixture.inx'
    for flow,expected in [(False,-14),(True,-14.21)]:
        target=WORK/('flow.inx' if flow else 'normal-stroke.inx')
        call(base,'mesh brush',node='Part',vertices='0',radius=10,stroke=[[-16,-16],[-15,-16],[-14,-16]],flow=flow,output=target)
        mesh=call(target,'mesh get',node='Part')
        assert math.isclose(mesh['verts'][0],expected,abs_tol=1e-4),(flow,mesh['verts'][0])
        assert mesh['verts'][1]==-16 and mesh['verts'][2:]==[-16,16,16,-16,16,16]

def binding_queries():
    model=ROOT/'tests/results/edited.inx'
    b=call(model,'binding get',param='XY',node='Part',property='deform')
    assert b['param_name']=='deform' and len(b['values'])==3 and len(b['values'][0])==3
    selected=call(model,'key get',param='XY',node='Part',property='deform',at='1,0')
    assert selected['selectedIndex']==[2,1] and selected['selectedValue']==b['values'][2][1]
    assert selected['selectedIsSet']==b['isSet'][2][1]

def project_merge():
    source=WORK/'merge-source.inx'
    batch(ROOT/'tests/results/fixture.inx',[
        ('param set',{'param':'XY','group':'Expressions'}),
        ('physics map',{'node':'Pendulum','param':'XY'}),
        ('param pair-add',{'first':'Part','second':'Eye'}),
        ('key set',{'param':'XY','node':'Part','property':'transform.t.x','at':'1,0','value':4}),
        ('animation add',{'name':'Turn','length':5}),('animation lane-add',{'name':'Turn','param':'XY'}),
        ('animation key-set',{'name':'Turn','param':'XY','frame':0,'value':1}),
        ('automation add',{'name':'Wave'}),('automation bind',{'name':'Wave','param':'XY','range':'-0.2,0.3'}),
        ('automation set',{'name':'Wave','enabled':False}),
    ],source)
    destination=WORK/'merged.inx';call(source,'project merge',file=source,output=destination)
    model=call(destination,'project inspect');nodes=[]
    def walk(n):
        nodes.append(n)
        for child in n.get('children',[]):walk(child)
    walk(model['nodes'])
    ids=[n['uuid'] for n in nodes];assert len(ids)==len(set(ids))==14
    params={p['name']:p for p in model['param']};assert len(params)==4
    assert len({p['uuid'] for p in params.values()})==4
    imported=params['XY (2)'];original=params['XY'];assert imported['uuid']!=original['uuid']
    imported_root=model['nodes']['children'][-1];assert imported_root['name']=='merge-source'
    descendants=[]
    def visit(n):
        descendants.append(n)
        for child in n.get('children',[]):visit(child)
    visit(imported_root);imported_ids={n['uuid'] for n in descendants}
    assert all(b['node'] in imported_ids for b in imported['bindings'])
    driver=next(n for n in descendants if n['type']=='SimplePhysics');assert driver['param']==imported['uuid']
    assert imported['parentUUID']!=original['parentUUID']
    assert model['animations']['Turn (2)']['lanes'][0]['uuid']==imported['uuid']
    auto=call(destination,'automation get',name='Wave (2)');assert auto['bindings'][0]['param']=='XY (2)'
    pairs=call(destination,'param pair-list');assert len(pairs)==2
    assert {pairs[1]['uuid1'],pairs[1]['uuid2']}.issubset(imported_ids)

def reparent_coordinates():
    base=WORK/'reparent.inx'
    batch('new',[
        ('node add',{'name':'First'}),('node set',{'node':'First','position':'10,20','zsort':10}),
        ('node add',{'name':'Second'}),('node set',{'node':'Second','position':'40,60','zsort':30}),
        ('node add',{'name':'Child','parent':'First'}),('node set',{'node':'Child','position':'2,3','zsort':12}),
    ],base)
    world=WORK/'world-parent.inx';call(base,'node reparent',node='Child',parent='Second',output=world)
    n=call(world,'node get',node='Child');assert n['transform']['trans'][:2]==[-28,-37],n
    assert n['zsort']==-8,n
    local=WORK/'local-parent.inx';call(base,'node reparent',node='Child',parent='Second',local=True,output=local)
    n=call(local,'node get',node='Child');assert n['transform']['trans'][:2]==[2,3] and n['zsort']==12,n

def isolated_grid():
    model=WORK/'isolated-grid.inx'
    batch(ROOT/'tests/results/fixture.inx',[('node set',{'node':'Eye','position':'100,200'})],model)
    single=WORK/'isolated-single.png';call(model,'render',isolate='Part',output=single,max_size=64)
    grid=WORK/'isolated-nine.png';call(model,'render grid',param='XY',values='-1,0,1',isolate='Part',output=grid,max_size=64)
    a=json.loads(single.with_suffix('.json').read_text());b=json.loads(grid.with_suffix('.json').read_text())
    assert b['width']==a['width']*3 and b['height']==a['height']*3
    assert all(tile['bounds']==a['bounds'] for tile in b['tiles'])
    assert all(abs(x-y)<1e-6 for row1,row2 in zip(a['worldToPixel'],b['tiles'][0]['worldToPixel']) for x,y in zip(row1,row2))

def viewport_guides():
    from PIL import Image,ImageChops
    model=ROOT/'tests/results/fixture.inx'
    plain=WORK/'plain-guides.png';call(model,'render',focus='Part',max_size=128,output=plain)
    mirrored=WORK/'mirror-view.png';call(model,'render',focus='Part',max_size=128,mirror_view=True,output=mirrored)
    a=Image.open(plain).convert('RGBA');b=Image.open(mirrored).convert('RGBA')
    diff=ImageChops.difference(a.transpose(Image.Transpose.FLIP_LEFT_RIGHT),b)
    # SDK camera reflection preserves the image; floating texture sampling can
    # differ at transparent boundaries after triangle winding is reversed.
    expected=a.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    changes=[]
    for first,second in zip(expected.get_flattened_data(),b.get_flattened_data()):
        errors=[abs(first[i]*first[3]/255-second[i]*second[3]/255) for i in range(3)]+[abs(first[3]-second[3])]
        changes.append(max(errors))
        if first[3]==second[3]==255:assert max(abs(first[i]-second[i]) for i in range(3))<=1
    assert max(changes)<=9 and sum(changes)/len(changes)<.05
    original=json.loads(plain.with_suffix('.json').read_text());meta=json.loads(mirrored.with_suffix('.json').read_text())
    first=original['vertices'][0]['pixel'];second=meta['vertices'][0]['pixel']
    assert abs(first[0]+second[0]-meta['width'])<1e-4 and abs(first[1]-second[1])<1e-4
    annotated=WORK/'guides.png';call(model,'render',focus='Part',max_size=128,overlay_bounds=True,orientation=True,output=annotated)
    meta=json.loads(annotated.with_suffix('.json').read_text());assert meta['guides']
    assert any('boundsWorld' in g for g in meta['guides']) and any('originPixel' in g for g in meta['guides'])
    assert ImageChops.difference(a,Image.open(annotated).convert('RGBA')).getbbox() is not None

def property_errors():
    for cmd,options in [('node set',{'node':'Head','opacity':.4}),('camera get',{'node':'Part'})]:
        out=WORK/'invalid.inx'
        p=subprocess.run([str(BIN),str(ROOT/'tests/results/fixture.inx'),*cmd.split(),'--json','--output='+str(out),*[f'--{k}={v}' for k,v in options.items()]],env=ENV,capture_output=True,text=True)
        assert p.returncode!=0,(cmd,p.stdout)
        assert not out.exists()
try:
    check('Creator mouth shape range and all ten axis coordinates',preset)
    check('four GUI parameter range presets',range_presets)
    check('SDK animation seek, looping, snapping, rename and video frame count',animation)
    check('automation fields and binding ranges survive SDK reload',automation)
    check('pixel/world/local coordinates with rotated parents, mesh origins and grid tiles',coordinates)
    check('viewport brush normal and flow strokes with explicit sampling',brush_modes)
    check('binding queries return SDK data and selected key values',binding_queries)
    check('project merge remaps colliding identifiers and preserves linked graph objects',project_merge)
    check('Creator reparent preserves world coordinates once, while local mode preserves local values',reparent_coordinates)
    check('grid isolation uses the same actual view bounds as a single isolated render',isolated_grid)
    check('viewport mirror and bounding/orientation guides affect image and matching coordinate metadata',viewport_guides)
    check('inapplicable properties fail instead of silently doing nothing',property_errors)
finally:
    (WORK/'results.json').write_text(json.dumps(results,indent=2)+'\n')
