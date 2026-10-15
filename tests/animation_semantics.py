#!/usr/bin/env python3
"""Assert Creator animation editing and native playback through pose metadata."""
import json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BIN=Path(sys.argv[1]);BASE=ROOT/'tests/results/fixture.inx';WORK=ROOT/'tests/results/animation';WORK.mkdir(exist_ok=True)
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
def pose(model,label,**opts):
    image=WORK/(label+'.png');call(model,'render',animation='Turn',isolate='Part',max_size=64,output=image,**opts);return json.loads(image.with_suffix('.json').read_text())
def record(name):RESULT.append({'case':name,'verified':True});print('PASS',name,flush=True)
try:
    source=WORK/'source.inx';batch(BASE,[('key set',{'param':'XY','node':'Part','property':'transform.t.x','at':'-1,0','value':-4}),('key set',{'param':'XY','node':'Part','property':'transform.t.x','at':'1,0','value':4}),('animation add',{'name':'Turn','length':12,'fps':60}),('animation lane-add',{'name':'Turn','param':'XY'}),('animation lane-set',{'name':'Turn','param':'XY','merge':'Forced'}),('animation key-set',{'name':'Turn','param':'XY','frame':0,'value':0}),('animation key-set',{'name':'Turn','param':'XY','frame':8,'value':1})],source)
    for mode,values in [('Nearest',[0,1]),('Stepped',[0,0]),('Linear',[.25,.75]),('Cubic',[.203125,.796875])]:
        out=WORK/(mode+'.inx');call(source,'animation lane-set',name='Turn',param='XY',interpolation=mode,output=out)
        for frame,expected in zip([2,6],values):
            meta=pose(out,mode+str(frame),frame=frame)
            assert abs(meta['parameters']['XY'][0]-expected)<1e-5,(mode,frame,meta['parameters']['XY'])
            vertex=next(v for v in meta['vertices'] if v['index']==0);assert abs(vertex['world'][0]-(-16+4*expected))<1e-4
        record('animation '+mode+' interpolates native values and actual vertex positions')
    duplicate=WORK/'duplicate.inx';batch(source,[('animation duplicate',{'name':'Turn','target':'Copy'}),('animation key-set',{'name':'Copy','param':'XY','frame':8,'value':.5}),('animation key-remove',{'name':'Copy','param':'XY','frame':0})],duplicate)
    original=call(duplicate,'animation get',name='Turn');copy=call(duplicate,'animation get',name='Copy')
    assert [k['value'] for k in original['lanes'][0]['keyframes']]==[0,1]
    assert [k['value'] for k in copy['lanes'][0]['keyframes']]==[.5]
    record('animation duplication keeps independent key arrays and key removal changes only its target')
    removed=WORK/'lane-removed.inx';call(duplicate,'animation lane-remove',name='Copy',param='XY',output=removed)
    assert not call(removed,'animation get',name='Copy')['lanes']
    renamed=WORK/'renamed.inx';call(removed,'animation rename',name='Copy',target='Renamed',output=renamed)
    assert set(call(renamed,'animation list'))=={'Turn','Renamed'}
    deleted=WORK/'deleted.inx';call(renamed,'animation delete',name='Renamed',output=deleted)
    assert set(call(deleted,'animation list'))=={'Turn'}
    record('lane deletion, animation rename and animation deletion persist their intended targets')
    meta=pose(source,'paused',frame=2);assert meta['animation']['paused'] and meta['animation']['frame']==2
    meta=pose(source,'playing',time=.05,loop=True);assert meta['animation']['playing'] and not meta['animation']['paused']
    meta=pose(source,'ended',time=1);assert not meta['animation']['playing']
    record('native preview playback supports seek-and-pause, looping play and stopping at the end')
    for fps in [120,60,30,25,48]:
        out=WORK/f'fps-{fps}.inx';call(source,'animation set',name='Turn',fps=fps,output=out)
        assert abs(call(out,'animation get',name='Turn')['timestep']-1/fps)<1e-7
    record('all animation framerate presets and a custom rate survive SDK reload')
    meta=pose(source,'explicit-pause',time=.05,playback='pause');assert meta['animation']['paused'] and meta['animation']['frame']==3
    meta=pose(source,'explicit-resume',frame=2,playback='play',loop=True);assert meta['animation']['playing'] and not meta['animation']['paused'] and meta['animation']['frame']==2
    leadout=WORK/'leadout.inx';call(source,'animation set',name='Turn',lead_out=8,output=leadout)
    meta=pose(leadout,'explicit-stop',time=.05,playback='stop');assert not meta['animation']['playing'] and meta['animation']['stopping'] and meta['animation']['frame']==3
    meta=pose(leadout,'explicit-reset',time=.05,playback='reset');assert not meta['animation']['playing'] and not meta['animation']['stopping'] and meta['animation']['frame']==0
    assert meta['parameters']['XY'][0]==0
    record('explicit pause, resume, lead-out stop and immediate reset invoke native playback actions')

finally:
    (WORK/'results.json').write_text(json.dumps(RESULT,indent=2)+'\n')
