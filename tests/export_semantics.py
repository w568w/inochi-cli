#!/usr/bin/env python3
"""Verify actual image/video alpha, format, camera and frame-count output."""
import json, os, subprocess, sys
from pathlib import Path
from PIL import Image, ImageChops
ROOT=Path(__file__).resolve().parents[1];BIN=Path(sys.argv[1])
BASE=ROOT/'tests/results/fixture.inx';WORK=ROOT/'tests/results/exports';WORK.mkdir(exist_ok=True)
ENV=os.environ.copy();RESULT=[]
def call(model,cmd,**opts):
    args=[str(BIN),str(model),*cmd.split(),'--json']
    for key,value in opts.items():
        if isinstance(value,bool):value=str(value).lower()
        args.append('--'+key.replace('_','-')+'='+str(value))
    p=subprocess.run(args,cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=120)
    assert p.returncode==0,(cmd,p.stderr);return json.loads(p.stdout)
def record(name):RESULT.append({'case':name,'verified':True});print('PASS',name,flush=True)
try:
    texture=WORK/'alpha.png';Image.new('RGBA',(32,32),(120,80,40,128)).save(texture)
    model=WORK/'alpha.inx';call(BASE,'texture load',node='Part',file=texture,output=model)
    png=WORK/'alpha-render.png';opts={'isolate':'Part','size':'64,64','padding':.1}
    call(model,'export image',**opts,output=png)
    im=Image.open(png);assert im.mode=='RGBA' and im.getpixel((0,0))[3]==0
    assert abs(im.getpixel((32,32))[3]-128)<=1,im.getpixel((32,32))
    record('transparent PNG preserves zero-alpha margins and partial-alpha interior')
    opaque=WORK/'background.png';call(model,'export image',**opts,background='.1,.2,.3,1',output=opaque)
    pixel=Image.open(opaque).getpixel((0,0))
    assert all(abs(a-b)<=1 for a,b in zip(pixel,(26,51,76,255))),pixel
    tga=WORK/'alpha-render.tga';call(model,'export image',**opts,output=tga)
    assert Image.open(tga).convert('RGBA').tobytes()==im.tobytes()
    jpeg=WORK/'alpha-render.jpg';call(model,'export image',**opts,output=jpeg)
    assert Image.open(jpeg).mode=='RGB' and min(Image.open(jpeg).getpixel((0,0)))>=245
    record('background compositing, TGA pixel orientation and JPEG white alpha flattening match output contracts')
    camera=WORK/'camera.inx';call(model,'camera set',node='View',position='0,0',scale='1,1',viewport='80,48',output=camera)
    image=WORK/'camera.png';call(camera,'export image',isolate='Part',camera='View',output=image)
    assert Image.open(image).size==(80,48)
    meta=json.loads(image.with_suffix('.json').read_text());assert meta['width']==80 and meta['height']==48
    record('image export honors native camera viewport dimensions and coordinate metadata')
    sequence=WORK/'sequence.png'
    for file in WORK.glob('sequence-*.png'):file.unlink()
    call(model,'export video',**opts,frames=3,fps=24,codec='png',transparent=True,output=sequence)
    frames=sorted(WORK.glob('sequence-*.png'));assert len(frames)==3
    for file in frames:
        image=Image.open(file).convert('RGBA');assert image.size==(64,64)
        assert image.getpixel((0,0))[3]==0 and abs(image.getpixel((32,32))[3]-128)<=2
    record('Creator PNG video sequence publishes all frames with preserved transparency')
    movie=WORK/'auto.mp4';call(model,'export video',**opts,frames=3,fps=24,codec='auto',output=movie)
    probe=subprocess.run(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=nb_read_frames,r_frame_rate,width,height','-of','json',str(movie)],capture_output=True,text=True,check=True)
    stream=json.loads(probe.stdout)['streams'][0];assert stream['nb_read_frames']=='3' and stream['r_frame_rate']=='24/1' and stream['width']==stream['height']==64
    record('automatic video codec produces the requested dimensions, framerate and frame count')
    movie=WORK/'alpha.webm';call(model,'export video',**opts,frames=2,fps=24,codec='libvpx-vp9',transparent=True,output=movie)
    decoded=subprocess.run(['ffmpeg','-v','error','-c:v','libvpx-vp9','-i',str(movie),'-frames:v','1','-f','rawvideo','-pix_fmt','rgba','pipe:1'],capture_output=True,check=True)
    image=Image.frombytes('RGBA',(64,64),decoded.stdout)
    assert image.getpixel((0,0))[3]==0 and abs(image.getpixel((32,32))[3]-128)<=3,image.getpixel((32,32))
    record('transparent VP9 output retains alpha through actual video decoding')
finally:
    (WORK/'results.json').write_text(json.dumps(RESULT,indent=2)+'\n')
