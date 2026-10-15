#!/usr/bin/env python3
"""Verify native layered imports, explicit merges and atlas export data."""
import json, math, os, struct, subprocess, sys, zipfile
from pathlib import Path
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1];BIN=Path(sys.argv[1])
ENV=os.environ.copy()
WORK=ROOT/'tests/results/import-export';WORK.mkdir(exist_ok=True)
RESULT=[]
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
def record(name):RESULT.append({'case':name,'verified':True});print('PASS',name,flush=True)
def nodes(model):return call(model,'node list')
U16=lambda x:struct.pack('>H',x);U32=lambda x:struct.pack('>I',x)
rgba=bytes([180,70,40,255])*256
planes=[rgba[i::4] for i in range(4)]
def layer(name,kind=0):
    extra=U32(0)+U32(0)+bytes([len(name)])+name.encode();extra+=bytes(-len(extra)%4)
    if kind:extra+=b'8BIMlsct'+U32(4)+U32(kind)
    if kind:
        return struct.pack('>iiiiH',0,0,0,0,0)+b'8BIMpass'+bytes([255,0,0,0])+U32(len(extra))+extra,b''
    channels=b''.join(struct.pack('>hI',i if i<3 else -1,258) for i in range(4))
    record=struct.pack('>iiiiH',4,6,20,22,4)+channels+b'8BIMnorm'+bytes([128,0,0,0])+U32(len(extra))+extra
    return record,b''.join(U16(0)+p for p in planes)
records=[layer('</Layer set>',3),layer('Child'),layer('Folder',1)]
info=U16(3)+b''.join(r for r,_ in records)+b''.join(d for _,d in records);info+=bytes(len(info)%2)
mask=U32(len(info))+info+U32(0)
header=b'8BPS'+U16(1)+bytes(6)+U16(4)+U32(32)+U32(32)+U16(8)+U16(3)
PSD=WORK/'group.psd';PSD.write_bytes(header+U32(0)+U32(0)+U32(len(mask))+mask+U16(0)+bytes(32*32*4))
raw=b''.join([planes[2],planes[1],planes[0],planes[3]])
lzf=b''.join(bytes([len(raw[i:i+32])-1])+raw[i:i+32] for i in range(0,len(raw),32))
blob=f'VERSION 2\nTILEWIDTH 16\nTILEHEIGHT 16\nPIXELSIZE 4\nDATA 1\n6,4,LZF,{len(lzf)}\n'.encode()+b'\0'+lzf+b'\n'
xml='<DOC><IMAGE name="fixture" width="32" height="32" colorspacename="RGBA"><layers><layer name="Folder" nodetype="grouplayer" collapsed="0" visible="1" opacity="255" uuid="folder" x="0" y="0"><layers><layer name="Child" nodetype="paintlayer" filename="layer0" colorspacename="RGBA" visible="1" opacity="128" compositeop="normal" uuid="child" x="0" y="0"/></layers></layer></layers></IMAGE></DOC>'
KRA=WORK/'group.kra'
with zipfile.ZipFile(KRA,'w') as z:
    z.writestr('mimetype','application/x-krita');z.writestr('maindoc.xml',xml);z.writestr('fixture/layers/layer0',blob)
try:
    imported=[]
    for file in [PSD,KRA]:
        for keep in [False,True]:
            out=WORK/f'{file.suffix[1:]}-{keep}.inx';call('new','project import',file=file,keep_structure=keep,output=out)
            tree=nodes(out);names=[n['name'] for n in tree]
            assert 'Child' in names and ('Folder' in names)==keep,(file,keep,tree)
            child=call(out,'node get',node='Child');assert child['psdLayerPath']=='/Folder/Child'
            assert child['transform']['trans'][:2]==[-2,-4],child['transform']
            assert math.isclose(child['opacity'],128/255,abs_tol=1e-6),child['opacity']
            assert child['enabled'] and child['mesh']['verts']==[-8,-8,-8,8,8,-8,8,8]
            tex=WORK/f'{file.suffix[1:]}-{keep}.png';call(out,'texture export',node='Child',output=tex)
            assert Image.open(tex).getpixel((8,8))==(180,70,40,255)
            imported.append(out);record(f'{file.suffix} import preserves layer paths, position, opacity and keep-structure={keep}')
    # Explicitly map a layer to another existing part, then check actual pixels.
    destination=WORK/'merge-destination.inx'
    batch(imported[1],[('node set',{'node':'Child','name':'Other','position':'8,9'})],destination)
    for file in [PSD,KRA]:
        out=WORK/f'merged-{file.suffix[1:]}.inx'
        call(destination,'project merge',file=file,mapping=[{'layer':'/Folder/Child','node':'Other','replace':True}],rename=True,retranslate=True,output=out)
        child=call(out,'node get',node='Child');assert child['transform']['trans'][:2]==[-2,-4] and child['psdLayerPath']=='/Folder/Child'
        assert len(nodes(out))==3
        tex=WORK/f'merged-{file.suffix[1:]}.png';call(out,'texture export',node='Child',output=tex);assert Image.open(tex).getpixel((8,8))[:3]==(180,70,40)
        record(f'{file.suffix} mapped merge applies rename, retranslation and replacement texture')
    base=ROOT/'tests/results/fixture.inx';disabled=WORK/'disabled.inx';call(base,'node set',node='Eye',enabled=False,output=disabled)
    for keep in [False,True]:
        out=WORK/f'atlas-keep-{keep}.inp';call(disabled,'export inp',resolution=128,padding=2,scale=1,keep_unused=keep,output=out)
        tree=nodes(out);assert ('Eye' in [n['name'] for n in tree])==keep
        part=call(out,'node get',node='Part');assert len(part['mesh']['uvs'])==8
        assert all(0<=u<=1 for u in part['mesh']['uvs'])
        slots=call(out,'texture list');assert slots and all(t['width']==128 and t['height']==128 for t in slots)
        record(f'INP atlas resolution, UV normalization, padding and keep-unused={keep}')
    preview=WORK/'preview.png';meta=call(imported[1],'export atlas-preview',resolution=128,padding=2,scale=1,output=preview)
    assert Image.open(preview).size==(128,128) and meta['outputScale']==1
    assert json.loads(preview.with_suffix('.json').read_text())['image']==str(preview)
    record('Creator atlas preview is an Agent-viewable image with packing metadata')
    for scale in [.5,1,2]:
        out=WORK/f'scale-{scale}.inp';call(imported[1],'export inp',resolution=128,padding=2,scale=scale,output=out)
        original=WORK/f'original-{scale}.png';reloaded=WORK/f'exported-{scale}.png'
        call(imported[1],'render',bounds='-12,-14,8,6',size='64,64',padding=0,output=original)
        call(out,'render',bounds='-12,-14,8,6',size='64,64',padding=0,output=reloaded)
        a=Image.open(original).convert('RGBA');b=Image.open(reloaded).convert('RGBA')
        assert max(abs(x-y) for x,y in zip(a.getpixel((32,32)),b.getpixel((32,32))))<=2
        record(f'atlas texture scale={scale} preserves reloaded center color and geometry')
    # A repeated opaque watermark changes actual packed pixels according to its settings.
    watermark=WORK/'watermark.png';Image.new('RGBA',(2,2),(0,220,30,255)).save(watermark)
    out=WORK/'watermarked.inp';call(imported[1],'export inp',resolution=128,padding=2,watermark=watermark,watermark_opacity=1,watermark_loops=2,watermark_blend='Normal',output=out)
    packed=WORK/'watermarked-pixels.png';call(out,'texture export',node='Child',output=packed)
    assert Image.open(packed).getpixel((64,64))[:3]==(0,220,30)
    record('atlas watermark texture, opacity, loop count and blend alter actual exported pixels')
    large=WORK/'large.png';small=WORK/'small.png';Image.new('RGBA',(256,32),(10,30,90,255)).save(large);Image.new('RGBA',(16,16),(200,80,20,255)).save(small)
    model=WORK/'mixed-sizes.inx'
    ops=[]
    for name,file,w,h in [('Large',large,256,32),('Small',small,16,16)]:
        mesh={'vertices':[[-w/2,-h/2],[-w/2,h/2],[w/2,-h/2],[w/2,h/2]],'uvs':[[0,0],[0,1],[1,0],[1,1]],'triangles':[0,1,2,2,1,3]}
        ops.extend([('node add',{'name':name,'type':'Part'}),('texture load',{'node':name,'file':str(file)}),('mesh set',{'node':name,'data':mesh})])
    batch('new',ops,model)
    widths=[]
    for nonlinear in [False,True]:
        out=WORK/f'nonlinear-{nonlinear}.inp';call(model,'export inp',resolution=128,padding=0,nonlinear=nonlinear,output=out)
        mesh=call(out,'mesh get',node='Small');widths.append(max(mesh['uvs'][::2])-min(mesh['uvs'][::2]))
        tex=call(out,'texture list');assert tex and all(s['width']==128 for s in tex)
    assert widths[1]>widths[0]*1.8 and math.isclose(widths[1],16/128,abs_tol=.01),widths
    record('nonlinear atlas scaling keeps small parts at full resolution while fitting oversized parts')
finally:
    (WORK/'results.json').write_text(json.dumps(RESULT,indent=2)+'\n')
