#!/usr/bin/env python3
"""Verify remaining import/export choices and native cancellation publication behavior."""
import json,os,struct,subprocess,sys,signal,time,tempfile
import psutil
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];BIN=Path(sys.argv[1]);BASE=ROOT/'tests/results/fixture.inx';WORK=ROOT/'tests/results/import-export-edges';WORK.mkdir(exist_ok=True)
ENV=os.environ.copy();RESULT=[]
def call(model,cmd,**opts):
    args=[str(BIN),str(model),*cmd.split(),'--json']
    for k,v in opts.items():
        if isinstance(v,bool):v=str(v).lower()
        args.append('--'+k.replace('_','-')+'='+str(v))
    p=subprocess.run(args,cwd=ROOT,env=ENV,text=True,capture_output=True,timeout=120)
    assert p.returncode==0,(cmd,p.stderr);return json.loads(p.stdout)
def record(name):RESULT.append({'case':name,'verified':True});print('PASS',name,flush=True)
try:
    folder=WORK/'images';folder.mkdir(exist_ok=True)
    for name,color in [('One.png',(100,20,30,255)),('Two.png',(20,100,30,255))]:Image.new('RGBA',(16,16),color).save(folder/name)
    model=WORK/'folder.inx';call('new','project import',file=folder,output=model)
    nodes=call(model,'node list');assert len([n for n in nodes if n['type']=='Part'])==2
    record('image folder import creates every native image part and reloads them')
    key=b'com.inochi2d.inochi-session.bindings';payload=b'{"fixture":"session"}'
    source=WORK/'session.inp';source.write_bytes(BASE.read_bytes()+b'EXT_SECT'+struct.pack('>I',1)+struct.pack('>I',len(key))+key+struct.pack('>I',len(payload))+payload)
    copied=WORK/'session-copy.inx';call(BASE,'project import-session',file=source,output=copied);assert key in copied.read_bytes() and payload in copied.read_bytes()
    saved=WORK/'session-resaved.inx';call(copied,'project save',output=saved);assert payload in saved.read_bytes()
    record('Inochi Session import retains its exact vendor payload across native save and reload')
    source=ROOT/'tests/results/render-effects/layers.inx';camera=WORK/'camera.inx';call(source,'camera add',name='Output',viewport='64,48',position='0,0',scale='1,1',output=camera)
    for post in [False,True]:
        movie=WORK/f'post-{post}.mp4';call(camera,'export video',camera='Output',postprocess=post,ambient_light='.25,.5,.75',frames=2,fps=24,output=movie)
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','stream=width,height','-of','json',str(movie)],text=True))['streams'][0]
        assert (probe['width'],probe['height'])==(64,48)
        data=subprocess.check_output(['ffmpeg','-v','error','-i',str(movie),'-frames:v','1','-f','rawvideo','-pix_fmt','rgb24','pipe:1'])
        im=Image.frombytes('RGB',(64,48),data)
        expected=[192,64,128] if not post else [48,32,96]
        assert max(abs(a-b) for a,b in zip(im.getpixel((32,24)),expected))<=8,(post,im.getpixel((32,24)),expected)
    record('video camera selection and postprocessing affect decoded dimensions and pixels')
    # Python's Windows terminate() bypasses C signal handlers.
    if os.name != 'nt':
        for sig in [signal.SIGINT,signal.SIGTERM]:
            movie=WORK/f'cancel-{sig}.mp4';movie.write_bytes(b'old output');before=set(Path(tempfile.gettempdir()).glob('inochi-outputs-*'))
            p=subprocess.Popen([str(BIN),str(BASE),'export','video','--frames=100000','--size=128,128','-o',str(movie)],cwd=ROOT,env=ENV,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            children=[]
            try:
                deadline=time.monotonic()+15
                while time.monotonic()<deadline:
                    children=psutil.Process(p.pid).children()
                    if children:break
                    assert p.poll() is None
                    time.sleep(.02)
                assert children,'encoder never started'
                p.send_signal(sig);stdout,stderr=p.communicate(timeout=30)
                assert p.returncode==128+sig and 'Cancelled' in stderr,(p.returncode,stderr)
                assert movie.read_bytes()==b'old output'
                assert not (set(Path(tempfile.gettempdir()).glob('inochi-outputs-*'))-before)
                assert all(not child.is_running() for child in children)
            finally:
                if p.poll() is None:p.kill();p.communicate()
        record('SIGINT and SIGTERM cancel video, reap FFmpeg and preserve prior output without staging leaks')
finally:
    (WORK/'results.json').write_text(json.dumps(RESULT,indent=2)+'\n')
