#!/usr/bin/env python3
"""Verify PSD/KRA merge selection, unmapping and ignore operations."""
import json,hashlib,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BIN=Path(sys.argv[1]);WORK=ROOT/'tests/results/merge-mapping';WORK.mkdir(exist_ok=True)
FIX=ROOT/'tests/results/import-export';ENV=os.environ.copy();RESULT=[]
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
    for kind in ['psd','kra']:
        source=FIX/(kind+'-True.inx');file=FIX/('group.'+kind)
        digest=hashlib.sha256(source.read_bytes()).hexdigest();child=call(source,'node get',node='Child');plan=call(source,'project merge-plan',file=file)
        assert len(plan['layers'])==1 and plan['layers'][0]['layer']=='/Folder/Child' and plan['layers'][0]['replace'] and plan['layers'][0]['node']==child['uuid']
        assert hashlib.sha256(source.read_bytes()).hexdigest()==digest
        assert not call(source,'project merge-plan',file=file,unmapped_only=True)['layers']
        assert call(source,'project merge-plan',file=file,layer_filter='cHiLd',node_filter='CHILD')==plan
        assert not call(source,'project merge-plan',file=file,layer_filter='missing')['layers']
        assert not call(source,'project merge-plan',file=file,node_filter='missing')['targets']
        record(kind+' merge plan preserves native automatic mappings and filters without editing the model')
        mapping=[{'layer':'/Folder/Child','ignore':True}]
        ignored=WORK/(kind+'-ignored.inx');call(source,'project merge',file=file,mapping=mapping,output=ignored)
        assert call(ignored,'project inspect')==call(source,'project inspect')
        preview=call(source,'project merge-plan',file=file,mapping=mapping);assert preview['layers'][0]['ignore'] and preview['layers'][0]['replace']
        used=WORK/(kind+'-used.inx');call(source,'project merge',file=file,mapping=[{'layer':'/Folder/Child','ignore':False}],output=used)
        assert len(call(used,'node list'))==len(call(source,'node list'))
        skip=WORK/(kind+'-only-unmapped.inx');call(source,'project merge',file=file,unmapped_only=True,output=skip)
        assert call(skip,'project inspect')==call(source,'project inspect')
        record(kind+' ignore and use preserve the mapping target and control whether the layer is applied')
        preview=call(source,'project merge-plan',file=file,mapping=[{'layer':'/Folder/Child','unmap':True}]);assert not preview['layers'][0]['replace']
        unmapped=WORK/(kind+'-unmapped.inx');call(source,'project merge',file=file,mapping=[{'layer':'/Folder/Child','unmap':True}],output=unmapped)
        assert len(call(unmapped,'node list'))==len(call(source,'node list'))+1
        record(kind+' unmapping restores the root add target instead of replacing the existing part')
        destination=WORK/(kind+'-parent.inx');call(source,'node add',type='Node',name='Destination',output=destination)
        added=WORK/(kind+'-added.inx');call(destination,'project merge',file=file,mapping=[{'layer':'/Folder/Child','node':'Destination','replace':False}],output=added)
        assert any('/Destination/Child' in n['path'] for n in call(added,'node list'))
        record(kind+' explicit nonreplacement mapping creates the layer under its selected parent')
    source=FIX/'psd-True.inx';shared_source=WORK/'shared-source.inx'
    ops=WORK/'shared.json';ops.write_text(json.dumps([{'command':'node add','options':{'type':'Part','name':'Other'}},{'command':'texture load','options':{'node':'Other','file':str(ROOT/'tests/fixtures/part.png')}},{'command':'mesh copy','options':{'node':'Other','source':'Child'}}]))
    call(source,'batch '+str(ops),output=shared_source)
    packed=WORK/'shared.inp';call(shared_source,'export inp',resolution=128,padding=2,output=packed)
    assert call(packed,'node get',node='Other')['textures'][0]==call(packed,'node get',node='Child')['textures'][0]
    before=WORK/'atlas-before.png';call(packed,'texture export',node='Other',output=before)
    changed=WORK/'shared-merged.inx';call(packed,'project merge',file=FIX/'group.psd',mapping=[{'layer':'/Folder/Child','node':'Child','replace':True}],output=changed)
    after=WORK/'atlas-after.png';call(changed,'texture export',node='Other',output=after)
    from PIL import Image
    assert Image.open(before).tobytes()==Image.open(after).tobytes()
    assert call(packed,'node get',node='Other')['mesh']==call(changed,'node get',node='Other')['mesh']
    record('replacing a layer preserves shared atlas textures and unrelated mesh data')

finally:
    (WORK/'results.json').write_text(json.dumps(RESULT,indent=2)+'\n')
