#!/usr/bin/env python3
"""Verify native inspector texture-slot conversion and replacement effects."""
import json, os, subprocess, sys
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];BIN=Path(sys.argv[1])
BASE=ROOT/'tests/results/fixture.inx';WORK=ROOT/'tests/results/textures';WORK.mkdir(exist_ok=True)
ENV=os.environ.copy();RESULT=[]
def call(model,cmd,ok=True,**opts):
    args=[str(BIN),str(model),*cmd.split(),'--json']
    for key,value in opts.items():args.append('--'+key.replace('_','-')+'='+str(value))
    p=subprocess.run(args,cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=90)
    assert (p.returncode==0)==ok,(cmd,p.stderr)
    return json.loads(p.stdout) if ok else p

def record(name):RESULT.append({'case':name,'verified':True});print('PASS',name,flush=True)
try:
    source=WORK/'source.png';Image.new('RGBA',(32,32),(120,80,40,128)).save(source)
    for slot in range(3):
        model=WORK/f'slot-{slot}.inx';image=WORK/f'slot-{slot}.png'
        call(BASE,'texture load',node='Part',slot=slot,file=source,output=model)
        call(model,'texture export',node='Part',slot=slot,output=image)
        im=Image.open(image)
        assert im.size==(32,32)
        if slot==0:
            assert im.mode=='RGBA';expected=(120,80,40,128)
        else:
            assert im.mode=='RGB';expected=(120,80,40)
        assert all(abs(a-b)<=1 for a,b in zip(im.getpixel((16,16)),expected))
        record(f'inspector slot {slot} uses native channel conversion and preserves exported pixels')
    emissive=WORK/'emissive.inx';call(WORK/'slot-0.inx','texture emissive',node='Part',output=emissive)
    image=WORK/'emissive.png';call(emissive,'texture export',node='Part',slot=1,output=image)
    assert Image.open(image).mode=='RGB'
    assert all(abs(a-b)<=1 for a,b in zip(Image.open(image).getpixel((16,16)),(120,80,40)))
    record('Make Emissive converts straight Albedo RGB into the emission slot')
    mismatch=WORK/'mismatch.png';Image.new('RGBA',(16,16),(1,2,3,255)).save(mismatch)
    fail=WORK/'bad.inx';fail.unlink(missing_ok=True)
    p=call(BASE,'texture load',ok=False,node='Part',slot=1,file=mismatch,output=fail)
    assert 'does not match' in p.stderr and not fail.exists()
    record('mismatched auxiliary texture fails without publishing a model')
    both=WORK/'both.inx';call(WORK/'slot-1.inx','texture load',node='Part',slot=2,file=source,output=both)
    smaller=WORK/'smaller.inx';call(both,'texture load',node='Part',slot=0,file=mismatch,output=smaller)
    part=call(smaller,'node get',node='Part')
    assert part['textures'][1:]==[4294967295,4294967295],part['textures']
    record('Albedo size replacement clears both incompatible auxiliary slots')
    removed=WORK/'removed.inx';call(WORK/'slot-1.inx','texture remove',node='Part',slot=1,output=removed)
    assert call(removed,'node get',node='Part')['textures'][1]==4294967295
    record('texture removal clears the persisted slot reference')
    pixel=WORK/'bleed-source.png';im=Image.new('RGBA',(32,32),(0,0,0,0));im.putpixel((16,16),(120,80,40,255));im.save(pixel)
    source_model=WORK/'bleed-source.inx';call(BASE,'texture load',node='Part',file=pixel,output=source_model)
    bleed=WORK/'bled.inx';call(source_model,'texture bleed',radius=1,output=bleed)
    image=WORK/'bled.png';call(bleed,'texture export',node='Part',output=image);im=Image.open(image)
    assert im.getpixel((15,16))==(120,80,40,0),im.getpixel((15,16))
    assert im.getpixel((13,16))==(0,0,0,0) and im.getpixel((16,16))==(120,80,40,255)
    record('native texture bleeding fills nearby transparent RGB while retaining all alpha values')
    premult=WORK/'premult.inx';call(WORK/'slot-0.inx','texture premultiply',output=premult)
    image=WORK/'premult.png';call(premult,'texture export',node='Part',output=image);value=Image.open(image).getpixel((16,16))
    assert abs(value[0]-60)<=2 and value[3]==128,value
    record('premultiply repair applies alpha to existing texture RGB without changing alpha')
    batch=WORK/'mipmaps.json';batch.write_text(json.dumps([
        {'command':'project meta','options':{'preserve-pixels':True}},
        {'command':'texture list','options':{'runtime':True}},
        {'command':'texture mipmaps'},
        {'command':'texture list','options':{'runtime':True}}]))
    p=subprocess.run([str(BIN),str(BASE),'batch',str(batch),'-o',str(WORK/'mipmaps.inx'),'--json'],capture_output=True,text=True,env=ENV,timeout=90)
    assert p.returncode==0,p.stderr;values=json.loads(p.stdout)
    assert all(v['mip1Width']==v['width']//2 for v in values[3])
    assert all(v['magFilter']==9729 for v in values[3]),values[3]
    record('native mipmap regeneration creates half-resolution GPU levels and selects linear filtering')

finally:
    (WORK/'results.json').write_text(json.dumps(RESULT,indent=2)+'\n')
