#!/usr/bin/env python3
"""Check explicit path rotation and along-path shift against native deformation output."""
import json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BIN=Path(sys.argv[1]);BASE=ROOT/'tests/results/fixture.inx';WORK=ROOT/'tests/results/path-controls';WORK.mkdir(exist_ok=True)
ENV=os.environ.copy();RESULT=[]
def call(model,cmd,**opts):
    args=[str(BIN),str(model),*cmd.split(),'--json']
    for k,v in opts.items():
        if isinstance(v,(dict,list)):v=json.dumps(v)
        if isinstance(v,bool):v=str(v).lower()
        args.append('--'+k.replace('_','-')+'='+str(v))
    p=subprocess.run(args,cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=90)
    assert p.returncode==0,(cmd,p.stderr);return json.loads(p.stdout)
def record(name):RESULT.append({'case':name,'verified':True});print('PASS',name,flush=True)
try:
    original=[[-32,0],[0,0],[32,0]]
    rotated=WORK/'rotated.inx';explicit=WORK/'explicit.inx'
    call(BASE,'mesh path',node='Part',**{'from':original,'pivot':1,'dragged':2,'angle':1.57079632679},output=rotated)
    call(BASE,'mesh path',node='Part',**{'from':original,'to':[[-32,0],[0,0],[0,32]]},output=explicit)
    a=call(rotated,'mesh get',node='Part');b=call(explicit,'mesh get',node='Part')
    assert max(abs(a-b) for a,b in zip(a['verts'],b['verts']))<1e-4
    record('path rotation uses the selected pivot and rotates the dragged side through the shared native operation')
    shifted=WORK/'shifted.inx';call(BASE,'mesh path',node='Part',**{'from':original,'shift-point':1,'shift-to':'16,10'},output=shifted)
    call(BASE,'mesh path',node='Part',**{'from':original,'to':[[-32,0],[16,0],[32,0]]},output=explicit)
    a=call(shifted,'mesh get',node='Part');b=call(explicit,'mesh get',node='Part')
    assert max(abs(a-b) for a,b in zip(a['verts'],b['verts']))<.02,(a['verts'],b['verts'])
    record('path shift projects the requested point onto the original native spline before deforming vertices')
finally:
    (WORK/'results.json').write_text(json.dumps(RESULT,indent=2)+'\n')
