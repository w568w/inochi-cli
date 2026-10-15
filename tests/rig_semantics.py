#!/usr/bin/env python3
"""Assert parameter, binding and key operations against native Creator behavior."""
import json, os, subprocess, sys, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BIN=Path(sys.argv[1])
ENV=os.environ.copy()
WORK=ROOT/'tests/results/rig-semantics';WORK.mkdir(exist_ok=True)
BASE=ROOT/'tests/results/fixture.inx';RESULT=[]
def call(model,cmd,**opts):
    args=[str(BIN),str(model),*cmd.split(),'--json']
    for k,v in opts.items():
        if isinstance(v,(dict,list)):v=json.dumps(v)
        if isinstance(v,bool):v=str(v).lower()
        args.append('--'+k.replace('_','-')+'='+str(v))
    p=subprocess.run(args,cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=60)
    assert p.returncode==0,(cmd,p.stderr);return json.loads(p.stdout)
def batch(model,ops,out):
    file=WORK/'ops.json';file.write_text(json.dumps([{'command':c,'options':o} for c,o in ops]));return call(model,'batch '+str(file),output=out)
def near(a,b):
    assert len(a)==len(b),(a,b);assert max((abs(x-y) for x,y in zip(a,b)),default=0)<1e-4,(a,b)
def record(name):RESULT.append({'case':name,'verified':True});print('PASS',name,flush=True)
try:
    model=WORK/'duplicate.inx';batch(BASE,[('param set',{'param':'XY','group':'Expressions'}),('param duplicate',{'param':'XY','name':'Copy'}),('param axis-move',{'param':'Copy','axis':0,'index':1,'value':.2})],model)
    original=call(model,'param get',param='XY');copy=call(model,'param get',param='Copy');near(original['axis_points'][0],[0,.5,1]);near(copy['axis_points'][0],[0,.6,1]);assert copy['parentUUID']==original['parentUUID'];assert copy['uuid']!=original['uuid'];record('parameter duplicate retains its group and edits independent axis storage')
    model=WORK/'scalar.inx';batch(BASE,[('key set',{'param':'XY','node':'Part','property':'transform.t.x','at':'-1,0','value':-3}),('key set',{'param':'XY','node':'Part','property':'transform.t.x','at':'1,0','value':5})],model)
    mirrored=WORK/'from-mirror.inx';call(model,'key from-mirror',param='XY',node='Part',property='transform.t.x',at='1,0',axis=0,output=mirrored)
    key=call(mirrored,'key get',param='XY',node='Part',property='transform.t.x',at='1,0');assert key['selectedValue']==3 and key['selectedIsSet'];record('set-from-mirror overwrites an already-set selected scalar key')
    pair=WORK/'paired.inx';batch(BASE,[('param pair-add',{'first':'Part','second':'Eye'}),('key set',{'param':'XY','node':'Part','property':'transform.t.x','at':'-1,0','value':-7}),('key from-mirror',{'param':'XY','node':'Eye','property':'transform.t.x','at':'1,0','axis':0})],pair)
    key=call(pair,'key get',param='XY',node='Eye',property='transform.t.x',at='1,0');assert key['selectedValue']==7;record('set-from-mirror resolves configured counterpart nodes')
    changed=WORK/'flipped.inx';call(model,'param flip',param='XY',axis=0,output=changed)
    assert call(changed,'key get',param='XY',node='Part',property='transform.t.x',at='-1,0')['selectedValue']==5
    assert call(changed,'key get',param='XY',node='Part',property='transform.t.x',at='1,0')['selectedValue']==-3;record('parameter flip swaps axis key locations without mirroring their values')
    changed=WORK/'mirrored-values.inx';call(model,'param mirror',param='XY',axis=0,output=changed)
    assert call(changed,'key get',param='XY',node='Part',property='transform.t.x',at='-1,0')['selectedValue']==3
    assert call(changed,'key get',param='XY',node='Part',property='transform.t.x',at='1,0')['selectedValue']==-5;record('parameter mirror transforms values without swapping key locations')
    field=[[1,2],[3,4],[5,6],[7,8]];deform=WORK/'deform.inx';call(BASE,'key set',param='XY',node='Part',at='1,0',offsets=field,output=deform)
    changed=WORK/'inverse.inx';call(deform,'key invert',param='XY',node='Part',at='1,0',output=changed)
    key=call(changed,'key get',param='XY',node='Part',at='1,0');assert key['selectedValue']==[[-x,-y] for x,y in field];record('key invert negates both deformation components')
    changed=WORK/'horizontal.inx';call(deform,'key mirror',param='XY',node='Part',at='1,0',axis=0,output=changed)
    key=call(changed,'key get',param='XY',node='Part',at='1,0');assert key['selectedValue']==[[-x,y] for x,y in field];record('key horizontal mirror only negates horizontal deformation components')
    changed=WORK/'copied.inx';call(deform,'key copy',param='XY',node='Part',at='1,0',to='-1,0',target_node='Eye',output=changed)
    key=call(changed,'key get',param='XY',node='Eye',at='-1,0');assert key['selectedValue']==field;record('key clipboard-equivalent copy preserves component order on a compatible target')
    batch(deform,[('binding copy',{'param':'XY','node':'Part','property':'deform','target':'Eye'}),('key set',{'param':'XY','node':'Eye','at':'1,0','offsets':[[9,10]]*4}),('binding swap',{'param':'XY','node':'Part','property':'deform','target':'Eye'})],changed)
    assert call(changed,'key get',param='XY',node='Eye',at='1,0')['selectedValue']==field
    assert call(changed,'key get',param='XY',node='Part',at='1,0')['selectedValue']==[[9,10]]*4;record('binding swap exchanges complete forms while retaining independent sources')
    reset=WORK/'reset.inx';call(model,'key reset',param='XY',node='Part',property='transform.t.x',at='1,0',output=reset)
    key=call(reset,'key get',param='XY',node='Part',property='transform.t.x',at='1,0');assert key['selectedValue']==0 and key['selectedIsSet'];record('key reset preserves the explicitly-set flag')
    unset=WORK/'unset.inx';call(model,'key unset',param='XY',node='Part',property='transform.t.x',at='1,0',output=unset)
    assert not call(unset,'key get',param='XY',node='Part',property='transform.t.x',at='1,0')['selectedIsSet'];record('key unset clears the explicitly-set flag')
    changed=WORK/'partial-pair.inx';call(pair,'param pair-set',node='Part',second='none',output=changed)
    entries=call(changed,'param pair-list');assert len(entries)==1 and entries[0]['uuid2']==4294967295
    changed2=WORK/'reassigned-pair.inx';call(changed,'param pair-set',node='Part',second='Eye',output=changed2)
    entries=call(changed2,'param pair-list');eye=call(changed2,'node get',node='Eye')['uuid'];assert entries[0]['uuid2']==eye
    record('mirror pairing supports unassigned slots and explicit reassignment as in the UI table')
    for color,expected in [('red',[.25,.15,.15]),('green',[.15,.25,.15]),('blue',[.15,.15,.25]),('purple',[.25,.15,.25]),('cyan',[.15,.25,.25]),('yellow',[.25,.25,.15]),('white',[.25,.25,.25])]:
        changed=WORK/f'group-{color}.inx';call(BASE,'param group-set',group='Expressions',color=color,output=changed)
        group=call(changed,'param group-list')[0];near(group['color'],expected)
    changed=WORK/'group-none.inx';call(BASE,'param group-set',group='Expressions',color='none',output=changed)
    assert call(changed,'param group-list')[0]['color']==['nan','nan','nan']
    record('all group color palette presets and no-color state survive native reload')
    selected=WORK/'selected-reset.inx'
    offsets=[[1,2],[3,4],[5,6],[7,8]]
    call(BASE,'key set',param='XY',node='Part',at='1,0',offsets=offsets,output=selected)
    reset=WORK/'reset-subset.inx';call(selected,'key reset',param='XY',node='Part',at='1,0',vertices='1,3',output=reset)
    value=call(reset,'key get',param='XY',node='Part',at='1,0')
    assert value['selectedValue']==[[1,2],[0,0],[5,6],[0,0]] and value['selectedIsSet']
    record('viewport reset selected changes only the specified vertex offsets and marks the key set')
    mirror=WORK/'mirror-subset.inx'
    call(selected,'key from-mirror',param='XY',node='Part',at='1,0',axis=0,vertices='1',output=mirror)
    value=call(mirror,'key get',param='XY',node='Part',at='1,0')['selectedValue']
    assert value[0]==offsets[0] and value[2:]==offsets[2:]
    assert value[1]!=offsets[1]
    record('viewport flip selected from mirror preserves all unselected key offsets')

    configured=WORK/'configured.inx'
    batch(BASE,[('param set',{'param':'XY','name':'Angle','min':'-30,-10','max':'30,10','defaults':'3,2','merge':'Weighted','group':'Expressions'}),('param axis-add',{'param':'Angle','axis':0,'value':15}),('param axis-move',{'param':'Angle','axis':0,'index':2,'value':12})],configured)
    param=call(configured,'param get',param='Angle')
    near(param['min'],[-30,-10]);near(param['max'],[30,10]);near(param['defaults'],[3,2]);near(param['axis_points'][0],[0,.5,.7,1]);assert param['merge_mode']=='Weighted'
    record('parameter properties and axis add/move use original model units and survive reload')
    reduced=WORK/'axis-removed.inx';call(configured,'param axis-remove',param='Angle',axis=0,index=2,output=reduced)
    near(call(reduced,'param get',param='Angle')['axis_points'][0],[0,.5,1])
    record('axis deletion removes the selected breakpoint while preserving endpoints')
    duplicate=WORK/'duplicate-properties.inx';call(configured,'param duplicate',param='Angle',name='CopyAngle',output=duplicate)
    original=call(duplicate,'param get',param='Angle');copy=call(duplicate,'param get',param='CopyAngle')
    for key in ['min','max','defaults','merge_mode','axis_points','parentUUID']:assert original[key]==copy[key],key
    record('parameter duplication preserves range, defaults, merge mode and grouping')
    split_source=WORK/'split-source.inx'
    batch(configured,[('key set',{'param':'Angle','node':'Part','property':'transform.t.x','at':'30,0','value':7}),('key set',{'param':'Angle','node':'Eye','property':'transform.t.x','at':'30,0','value':9}),('binding set',{'param':'Angle','node':'Eye','property':'transform.t.x','interpolation':'Cubic'})],split_source)
    split=WORK/'split.inx';call(split_source,'param split',param='Angle',name='EyeAngle',nodes='Eye',output=split)
    original=call(split,'param get',param='Angle');copy=call(split,'param get',param='EyeAngle')
    for key in ['min','max','defaults','merge_mode','axis_points','parentUUID']:assert original[key]==copy[key],key
    part=call(split,'node get',node='Part')['uuid'];eye=call(split,'node get',node='Eye')['uuid']
    assert [b['node'] for b in original['bindings']]==[part] and [b['node'] for b in copy['bindings']]==[eye]
    assert copy['bindings'][0]['interpolate_mode']=='Cubic'
    assert call(split,'key get',param='EyeAngle',node='Eye',property='transform.t.x',at='30,0')['selectedValue']==9
    order=[v['name'] for v in call(split,'param list')];assert order.index('EyeAngle')==order.index('Angle')+1
    record('shared parameter split moves selected node bindings, retains metadata and inserts after the source')
    for direction,source,target,property in [('left','30,0','-30,0','transform.t.x'),('right','-30,0','30,0','transform.t.x'),('up','0,-10','0,10','transform.t.y'),('down','0,10','0,-10','transform.t.y')]:
        source_model=WORK/f'autofill-{direction}-source.inx'
        call(reduced,'key set',param='Angle',node='Part',property=property,at=source,value=7,output=source_model)
        filled=WORK/f'autofill-{direction}.inx';call(source_model,'param autofill',param='Angle',direction=direction,output=filled)
        key=call(filled,'key get',param='Angle',node='Part',property=property,at=target)
        assert key['selectedIsSet'] and key['selectedValue']==-7,key
        assert call(filled,'key get',param='Angle',node='Part',property=property,at=source)['selectedValue']==7
    record('all four directional autofill actions mirror only the destination half of a nonstandard range')
    filled=WORK/'autofill-range.inx';call(source_model,'param autofill',param='Angle',axis=1,**{'from':-10,'to':-0.1},output=filled)
    key=call(filled,'key get',param='Angle',node='Part',property='transform.t.y',at='0,-10')
    assert key['selectedIsSet'] and key['selectedValue']==-7
    record('autofill range bounds are converted from model units before native evaluation')

    current=WORK/'current-source.inx';batch(BASE,[('key set',{'param':'XY','node':'Part','property':'transform.t.x','at':'-1,0','value':2}),('key set',{'param':'XY','node':'Part','property':'transform.t.x','at':'1,0','value':8}),('key unset',{'param':'XY','node':'Part','property':'transform.t.x','at':'0,0'})],current)
    prior=call(current,'key get',param='XY',node='Part',property='transform.t.x',at='0,0')
    changed=WORK/'current.inx';call(current,'key current',param='XY',node='Part',property='transform.t.x',at='0,0',output=changed)
    key=call(changed,'key get',param='XY',node='Part',property='transform.t.x',at='0,0')
    assert not prior['selectedIsSet'] and key['selectedIsSet'] and prior['selectedValue']==key['selectedValue']==5
    record('Set to current marks the interpolated key explicit without changing its value')
    uniform=WORK/'flip-deform-source.inx';batch(BASE,[('key set',{'param':'XY','node':'Part','at':'1,0','offsets':[[2,3]]*4}),('key unset',{'param':'XY','node':'Part','at':'0,0'})],uniform)
    changed=WORK/'flip-deform.inx';call(uniform,'key flip-deform',param='XY',node='Part',at='1,0',output=changed)
    for value in call(changed,'key get',param='XY',node='Part',at='1,0')['selectedValue']:near(value,[-2,3])
    changed=WORK/'flip-unset.inx';call(uniform,'key flip-deform',param='XY',node='Part',at='0,0',output=changed)
    assert not call(changed,'key get',param='XY',node='Part',at='0,0')['selectedIsSet']
    record('Flip Deform remaps set forms across the mesh and leaves unset forms unset')
    interp=WORK/'interpolation-source.inx';batch(BASE,[('key set',{'param':'Blink','node':'Part','property':'transform.t.x','at':-1,'value':0}),('key set',{'param':'Blink','node':'Part','property':'transform.t.x','at':0,'value':10}),('key set',{'param':'Blink','node':'Part','property':'transform.t.x','at':1,'value':0})],interp)
    for mode,expected in [('Nearest',10),('Linear',7.5),('Cubic',8.671875)]:
        changed=WORK/f'interpolation-{mode}.inx';call(interp,'binding set',param='Blink',node='Part',property='transform.t.x',interpolation=mode,output=changed)
        image=WORK/f'interpolation-{mode}.png';call(changed,'render',param='Blink=.25',isolate='Part',max_size=64,output=image)
        meta=json.loads(image.with_suffix('.json').read_text());vertex=next(v for v in meta['vertices'] if v['index']==0)
        assert abs(vertex['world'][0]-(-16+expected))<1e-4,(mode,vertex,expected)
    record('Nearest, Linear and Cubic binding interpolation produce their actual native vertex displacement')

    groups=WORK/'group-renamed.inx';batch(BASE,[('param set',{'param':'XY','group':'Expressions'}),('param set',{'param':'Blink','group':'Expressions'}),('param group-set',{'group':'Expressions','name':'Faces'})],groups)
    assert call(groups,'param get',param='Faces/XY')['name']=='XY'
    original=call(groups,'param list');ungrouped=WORK/'group-deleted.inx';call(groups,'param group-delete',group='Faces',output=ungrouped)
    assert not call(ungrouped,'param group-list')
    for a,b in zip(original,call(ungrouped,'param list')):
        a.pop('parentUUID',None);b.pop('parentUUID',None);assert a==b
    record('group rename updates parameter paths and group deletion keeps all parameter data')
    paste_source=WORK/'paste-source.inx'
    batch(interp,[('param add',{'name':'Destination','vec2':True}),('param axis-add',{'param':'Destination','axis':0,'value':-.5}),('param axis-add',{'param':'Destination','axis':1,'value':.5})],paste_source)
    pasted=WORK/'pasted-grid.inx';call(paste_source,'param paste',param='Destination',source='Blink',output=pasted)
    for at,expected in [('-1,-1',0),('-.5,.5',5),('0,1',10),('1,0',0)]:
        value=call(pasted,'key get',param='Destination',node='Part',property='transform.t.x',at=at)
        assert value['selectedIsSet'] and value['selectedValue']==expected,(at,value)
    record('parameter paste samples the source curve at destination axis points of different counts')
    mirrored_paste=WORK/'paste-mirror.inx'
    batch(paste_source,[('param pair-add',{'first':'Part','second':'Eye'}),('param paste',{'param':'Destination','source':'Blink','axis':0})],mirrored_paste)
    assert call(mirrored_paste,'key get',param='Destination',node='Eye',property='transform.t.x',at='0,0')['selectedValue']==-10
    record('parameter horizontal paste resolves mirror pairs and reflects scalar values')

    vertical=WORK/'vertical-source.inx';call(BASE,'key set',param='XY',node='Part',property='transform.t.y',at='0,-1',value=-7,output=vertical)
    reflected=WORK/'vertical-reflected.inx';call(vertical,'key from-mirror',param='XY',node='Part',property='transform.t.y',at='0,1',axis=1,output=reflected)
    assert call(reflected,'key get',param='XY',node='Part',property='transform.t.y',at='0,1')['selectedValue']==7
    flipped=WORK/'vertical-flipped.inx';call(vertical,'param flip',param='XY',axis=1,output=flipped)
    assert call(flipped,'key get',param='XY',node='Part',property='transform.t.y',at='0,1')['selectedValue']==-7
    mirrored=WORK/'vertical-values.inx';call(vertical,'param mirror',param='XY',axis=1,output=mirrored)
    assert call(mirrored,'key get',param='XY',node='Part',property='transform.t.y',at='0,-1')['selectedValue']==7
    record('vertical from-mirror, axis flip and value mirror preserve their distinct native semantics')
    diagonal=WORK/'diagonal.inx';call(BASE,'key set',param='XY',node='Part',property='transform.t.y',at='-1,-1',value=-7,output=diagonal)
    changed=WORK/'diagonal-mirror.inx';call(diagonal,'key from-mirror',param='XY',node='Part',property='transform.t.y',at='1,1',axis=-1,output=changed)
    assert call(changed,'key get',param='XY',node='Part',property='transform.t.y',at='1,1')['selectedValue']==-7
    record('diagonal set-from-mirror samples both mirrored axes with v0.8.6 scalar behavior')
    changed=WORK/'vertical-deform.inx';call(deform,'key mirror',param='XY',node='Part',at='1,0',axis=1,output=changed)
    assert call(changed,'key get',param='XY',node='Part',at='1,0')['selectedValue']==[[x,-y] for x,y in field]
    removed=WORK/'binding-removed.inx';call(deform,'binding remove',param='XY',node='Part',output=removed)
    assert not call(removed,'binding list',param='XY')
    record('vertical deformation mirror and binding deletion update the selected native data')

    custom=WORK/'custom-color.inx';call(BASE,'param group-set',group='Expressions',color='.2,.3,.4',output=custom)
    near(call(custom,'param group-list')[0]['color'],[.2,.3,.4])
    record('custom parameter group color survives the native editor extension round trip')

finally:
    (WORK/'results.json').write_text(json.dumps(RESULT,indent=2)+'\n')
