#!/usr/bin/env python3
"""Execute native CLI commands and verify persisted state and rendered artifacts."""
import json, os, struct, subprocess, tempfile, sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
BIN=Path(sys.argv[1])
ENV=os.environ.copy()
FIX=ROOT/'tests/fixtures'
WORK=ROOT/'tests/results'; WORK.mkdir(exist_ok=True)
results=[]
def call(model,command,options=None,ok=True):
    args=[str(BIN),str(model),*command.split(), '--json']
    for k,v in (options or {}).items():
        if isinstance(v,(dict,list)):v=json.dumps(v,separators=(',',':'))
        elif isinstance(v,bool):v=str(v).lower()
        args.append('--'+k+'='+str(v))
    run=subprocess.run(args,cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=60)
    results.append({'command':'render image' if command=='render' else command,'options':options or {},'success':run.returncode==0,'error':run.stderr.strip()})
    if ok and run.returncode:raise AssertionError(f'{command}: {run.stderr.strip()}')
    if not ok:
        assert run.returncode!=0,command
        return run
    return json.loads(run.stdout)
def batch(model,ops,out):
    file=WORK/'batch.json';file.write_text(json.dumps([{'command':c,'options':o} for c,o in ops]))
    result=call(model,'batch '+str(file),{'output':str(out)})
    results.extend({'command':cmd,'options':opts,'success':True,'batch':True} for cmd,opts in ops)
    return result
quad={'vertices':[[-16,-16],[-16,16],[16,-16],[16,16]],'uvs':[[0,0],[0,1],[1,0],[1,1]],'triangles':[0,1,2,2,1,3]}
base=WORK/'fixture.inx'
setup=[('node add',{'type':'Node','name':'Head'}),('node add',{'type':'MeshGroup','name':'Face','parent':'Head'}),('mesh grid',{'node':'Face','x':'-20,0,20','y':'-20,0,20'}),('node add',{'type':'Part','name':'Part','parent':'Face'}),('texture load',{'node':'Part','file':str(FIX/'part.png')}),('mesh set',{'node':'Part','data':json.dumps(quad)}),('node add',{'type':'Part','name':'Eye','parent':'Face'}),('texture load',{'node':'Eye','file':str(FIX/'part.png')}),('mesh set',{'node':'Eye','data':json.dumps(quad)}),('param add',{'name':'XY','vec2':True}),('param add',{'name':'Blink'}),('param group-add',{'name':'Expressions'}),('node add',{'type':'SimplePhysics','name':'Pendulum','parent':'Head'}),('node add',{'type':'Camera','name':'View'})]
try:
    batch('new',setup,base)
    assert len(call(base,'node list'))==7
    edits=[]
    def test(cmd,**o):edits.append((cmd,o))
    test('project meta',name='Fixture',artist='Artist',rigger='Rigger',copyright='Fixture',license='https://example.com',contact='local',reference='fixture',preserve_pixels=False)
    # CLI uses hyphens, while Python keyword arguments use underscores.
    test('project merge-plan',file=str(FIX/'part.psd'));test('project check');test('project inspect');test('node get',node='Part');test('node hit',point='0,0',sort='z')
    test('node set',node='Part',position='1,2',rotation='0,0,0.05',scale='1,1',zsort=2,tint='1,0.8,1',screen_tint='0.1,0,0',opacity=0.8,emission=1,blend='Normal',threshold=0.4,layer_path='/part')
    test('node reparent',node='Eye',parent='Head');test('node reparent',node='Eye',parent='Face')
    test('node origin',node='Head');test('node set',node='Face',dynamic=True,translate_children=True)
    test('camera set',node='View',viewport='64,64',position='0,0',rotation='0,0,0',scale='1,1');test('camera list');test('camera get',node='View')
    test('param set',param='Blink',group='Expressions',defaults='0.1',merge='Additive')
    test('param group-set',group='Expressions',name='Expressions',color='0.2,0.3,0.4');test('param group-list')
    test('param get',param='XY');test('param axis-add',param='XY',axis=0,value=0.5)
    test('param axis-move',param='XY',axis=0,index=2,value=0.4);test('param axis-remove',param='XY',axis=0,index=2)
    test('binding add',param='XY',node='Part',property='transform.t.x')
    test('binding set',param='XY',node='Part',property='transform.t.x',interpolation='Cubic')
    test('key set',param='XY',node='Part',property='transform.t.x',at='1,0',value=3)
    test('key set',param='XY',node='Part',property='deform',at='1,0',offsets=json.dumps([[1,0],[1,0],[2,0],[2,0]]))
    test('key get',param='XY',node='Part',property='deform',at='1,0')
    test('key copy',param='XY',node='Part',property='deform',at='1,0',to='-1,0')
    test('key mirror',param='XY',node='Part',property='deform',at='-1,0',axis=0)
    test('key invert',param='XY',node='Part',property='deform',at='-1,0')
    test('key extrapolate',param='XY',node='Part',property='deform',at='1,1',axis=1)
    test('key reset',param='XY',node='Part',property='deform',at='1,1');test('key unset',param='XY',node='Part',property='deform',at='1,1')
    test('binding get',param='XY',node='Part',property='deform');test('binding list',param='XY')
    test('binding copy',param='XY',node='Part',property='deform',target='Eye')
    test('binding swap',param='XY',node='Part',property='deform',target='Eye')
    test('param flip',param='XY',axis=0);test('param mirror',param='XY',axis=0);test('param autofill',param='XY',axis=0)
    test('param duplicate',param='XY',name='Copy');test('param split',param='Copy',name='Split',nodes='Eye');test('param delete',param='Split');test('param delete',param='Copy')
    test('param to-2d',param='Blink');test('param list')
    test('physics map',node='Pendulum',param='Blink');test('physics set',node='Pendulum',model='spring_pendulum',mapping='xy',gravity=1,length=30,frequency=2,angle_damping=0.5,length_damping=0.5,output_scale='1,1',local_only=True);test('physics get',node='Pendulum');test('physics unmap',node='Pendulum');test('physics set',gravity=9.8,pixels_per_meter=1000);test('physics get')
    test('automation add',name='Wave',type='sine');test('automation bind',name='Wave',param='XY',axis=0,range='-0.1,0.1');test('automation set',name='Wave',speed=1,phase=0,wave='Sin',enabled=False);test('automation list');test('automation get',name='Wave');test('automation unbind',name='Wave',index=0);test('automation delete',name='Wave')
    test('animation add',name='Turn',length=10,fps=30);test('animation set',name='Turn',additive=False,weight=1,lead_in=-1,lead_out=-1)
    test('animation lane-add',name='Turn',param='XY');test('animation lane-set',name='Turn',param='XY',interpolation='Linear',merge='Forced')
    test('animation key-set',name='Turn',param='XY',frame=0,value=-1);test('animation key-set',name='Turn',param='XY',frame=9,value=1)
    test('animation get',name='Turn');test('animation list');test('animation duplicate',name='Turn',target='CopyTurn');test('animation key-remove',name='CopyTurn',param='XY',frame=9);test('animation lane-remove',name='CopyTurn',param='XY');test('animation rename',name='CopyTurn',target='RenamedCopy');test('animation delete',name='RenamedCopy')
    test('mask add',node='Part',source='Eye',mode='Mask');test('mask list',node='Part');test('mask set',node='Part',source='Eye',mode='DodgeMask');test('mask remove',node='Part',source='Eye')
    test('texture list');test('texture export',node='Part',output=str(WORK/'texture.png'));test('texture emissive',node='Part');test('texture remove',node='Part',slot=1);test('texture bleed',radius=2);test('texture mipmaps')
    test('history begin');test('node set',node='Part',position='4,5');test('node set',node='Eye',enabled=False);test('history end');test('history undo');test('history redo');test('history undo')
    test('param pair-add',first='Part',second='Eye');test('param pair-list');test('param pair-set',node='Part',second='none');test('param pair-remove',node='Part')
    test('param paste',param='XY',source='XY',axis=2);test('param order',param='XY',index=0)
    test('key current',param='XY',node='Part',property='deform',at='1,0');test('key flip-deform',param='XY',node='Part',property='deform',at='1,0')
    test('mesh transform',node='Part',param='XY',at='1,0',vertices='0',move='0.1,0')
    test('param group-add',name='Temp');test('param group-delete',group='Temp')
    test('node add',type='Mask',name='TempMask');test('node delete',node='TempMask')
    test('node add',type='Composite',name='TempComposite');test('node set',node='TempComposite',threshold=0.4,propagate=True);test('node delete',node='TempComposite')
    test('param mouth-shape',name='MouthTemp');test('param delete',param='MouthTemp')
    test('texture premultiply')
    test('project layer-names');test('project repair');test('project regenerate-ids')
    test('mesh layout',node='Part');test('mesh copy',node='Eye',source='Part');test('key from-mirror',param='XY',node='Part',property='transform.t.x',at='1,0',axis=0);test('scene set',ambient_light='1,1,1');test('scene get');test('history list');test('history clear');test('project save')
    edits=[(cmd,{k.replace('_','-'):v for k,v in opts.items()}) for cmd,opts in edits]
    out=WORK/'edited.inx';result=batch(base,edits,out)
    call(out,'project check')
    batch(base,[('node set',{'node':'Part','position':'1,2'}),('history seek',{'index':0})],WORK/'history-seek.inx')
    render=call(out,'render',{'output':str(WORK/'render.png'),'focus':'Face','max-size':128,'mesh':True,'vertices':True})
    im=Image.open(WORK/'render.png');assert im.getbbox() and max(im.size)==128
    meta=json.loads((WORK/'render.json').read_text());assert meta['vertices']
    call(out,'render grid',{'param':'XY','values':'-1,0,1','max-size':64,'output':str(WORK/'grid.png')})
    call(out,'export image',{'animation':'Turn','time':0.1,'max-size':64,'output':str(WORK/'anim.png')})
    call(out,'export inp',{'resolution':128,'padding':2,'output':str(WORK/'export.inp')})
    call(out,'export atlas-preview',{'resolution':128,'padding':2,'output':str(WORK/'atlas-preview.png')})
    call(out,'export video',{'animation':'Turn','frames':3,'fps':30,'size':'64,64','output':str(WORK/'video.mp4')})
    assert (WORK/'video.mp4').stat().st_size>0
    for ext in ['jpg','tga']:
        call(out,'export image',{'max-size':64,'output':str(WORK/('format.'+ext))})
        assert Image.open(WORK/('format.'+ext)).width>0
    call(WORK/'mask.inx' if (WORK/'mask.inx').exists() else base,'render',{'max-size':64,'output':str(WORK/'mask-render.png')})
    call('new','project new',{'output':str(WORK/'empty.inx')})
    call(base,'camera add',{'name':'ExtraCamera','viewport':'80,60','position':'1,2','output':str(WORK/'camera.inx')})
    call(base,'project merge',{'file':str(FIX/'part.png'),'output':str(WORK/'merged.inx')})
    call(out,'binding remove',{'param':'XY','node':'Eye','property':'deform','output':str(WORK/'binding.inx')})
    batch(base,[('mask add',{'node':'Part','source':'Eye'}),('mask order',{'node':'Part','source':'Eye','index':0})],WORK/'mask.inx')
    call(base,'param pair-auto',{'first-pattern':'Part','second-pattern':'Eye','output':str(WORK/'pairs.inx')})
    call(base,'render',{'background':'0,0,0,1','creator-reference':True,'max-size':64,'output':str(WORK/'reference.png')})
    from PIL import ImageChops
    assert ImageChops.difference(Image.open(WORK/'reference.png'),Image.open(WORK/'reference.creator.png')).getbbox() is None
    # A real SDK-loadable vendor extension fixture for the UI's Session import.
    key=b'com.inochi2d.inochi-session.bindings';payload=b'{}'
    session=WORK/'session.inp';session.write_bytes(base.read_bytes()+b'EXT_SECT'+struct.pack('>I',1)+struct.pack('>I',len(key))+key+struct.pack('>I',len(payload))+payload)
    call(base,'project import-session',{'file':str(session),'output':str(WORK/'session-copy.inx')})
    # Independent mesh cases keep fixture topology and binding expectations stable.
    mesh_cases=[('mesh get',{}),('mesh select',{'rect':'-16,-16,16,16'}),('mesh vertex-set',{'index':0,'position':'-15,-15','uv':'0,0'}),('mesh transform',{'move':'1,0'}),('mesh mirror',{'axis':0}),('mesh brush',{'move':'1,0','center':'0,0','radius':30}),('mesh path',{'from':'[[-20,0],[0,0],[20,0]]','to':'[[-20,0],[0,2],[20,0]]'}),('mesh grid',{'x':'-16,0,16','y':'-16,0,16'}),('mesh automesh',{'mode':'grid'}),('mesh automesh',{'mode':'contour','sampling':4,'distance':2}),('mesh triangulate',{}),('mesh vertex-add',{'position':'0,0'}),('mesh vertex-remove',{'vertices':'0'}),('mesh connect',{'a':0,'b':3}),('mesh disconnect',{'a':0,'b':1})]
    for cmd,o in mesh_cases:
        options={'node':'Part',**o}
        if cmd not in ('mesh get','mesh select'):options['output']=str(WORK/'mesh.inx')
        call(base,cmd,options)
    for kind in ['png','psd','kra']:
        call('new','project import',{'file':str(FIX/('part.'+kind)),'output':str(WORK/(kind+'.inx'))})
    # Check PSD/KRA merge paths against real imported layer paths.
    for kind in ['psd','kra']:
        call(WORK/(kind+'.inx'),'project merge',{'file':str(FIX/('part.'+kind)),'rename':True,'retranslate':True,'mapping':json.dumps([{'layer':'/part','node':'part','replace':True}]),'output':str(WORK/(kind+'-merged.inx'))})
    # Failure never submits the model file.
    missing=WORK/'must-not-exist.inx'
    if missing.exists():missing.unlink()
    call(base,'mesh vertex-set',{'node':'Part','index':999,'position':'0,0','output':str(missing)},ok=False);assert not missing.exists()
    call(base,'node get',{'node':'missing'},ok=False)
    call(base,'node set',{'node':'Part','bogus':1,'output':str(missing)},ok=False)
    failed=WORK/'fail.json';failed.write_text(json.dumps([{'command':'node set','options':{'node':'Part','name':'Changed'}},{'command':'node delete','options':{'node':'missing'}}]))
    call(base,'batch '+str(failed),{'output':str(missing)},ok=False);assert not missing.exists()
    call(base,'project save',{'output':str(WORK/'missing-directory/model.inx')},ok=False)
    caps=json.loads(subprocess.check_output([str(BIN),'capabilities','--json'],env=ENV,text=True))
    tested={x['command'] for x in results if x['success']}
    missing={x['command'] for x in caps['commands']}-tested
    assert not missing, missing
    print('PASS',len(results),'recorded cases;',len(caps['commands']),'of',len(caps['commands']),'registered commands covered')
finally:
    (WORK/'acceptance.json').write_text(json.dumps(results,indent=2)+'\n')
