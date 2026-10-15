#!/usr/bin/env python3
"""Exercise every typed model inspector field and scalar binding property."""
import json, math, os, re, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BIN=Path(sys.argv[1])
ENV=os.environ.copy()
WORK=ROOT/'tests/results/properties';WORK.mkdir(exist_ok=True);RESULT=[]
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
def near(a,b):
    if isinstance(a,list):assert len(a)==len(b);assert all(math.isclose(x,y,abs_tol=1e-5) for x,y in zip(a,b)),(a,b)
    else:assert math.isclose(a,b,abs_tol=1e-5),(a,b)
def record(name):RESULT.append({'case':name,'verified':True});print('PASS',name,flush=True)
BASE=ROOT/'tests/results/fixture.inx'
try:
    model=WORK/'node-fields.inx';batch(BASE,[('node set',{'node':'Part','name':'Renamed','position':'2,3,4','rotation':'.1,.2,.3','scale':'1.2,.8','zsort':5,'origin':'1,2','tint':'.2,.3,.4','screen-tint':'.1,.2,.3','opacity':.7,'emission':2,'threshold':.6,'blend':'Multiply','layer-path':'/Folder/Renamed'}),('node set',{'node':'Head','enabled':False,'recursive':True}),('camera set',{'node':'View','viewport':'320,240','position':'1,2,3','rotation':'0,0,.25','scale':'2,3'}),('node set',{'node':'Face','dynamic':False,'translate-children':False})],model)
    node=call(model,'node get',node='Renamed');near(node['transform']['trans'],[2,3,4]);near(node['transform']['rot'],[.1,.2,.3]);near(node['transform']['scale'],[1.2,.8]);near(node['zsort'],5);near(node['mesh']['origin'],[1,2]);near(node['tint'],[.2,.3,.4]);near(node['screenTint'],[.1,.2,.3]);near(node['opacity'],.7);near(node['emissionStrength'],2);near(node['mask_threshold'],.6);assert node['blend_mode']=='Multiply' and node['psdLayerPath']=='/Folder/Renamed' and node['enabled'] is False
    assert call(model,'node get',node='Eye')['enabled'] is False
    camera=call(model,'camera get',node='View');near(camera['viewport'],[320,240]);near(camera['transform']['scale'],[2,3]);near(camera['transform']['rot'],[0,0,.25])
    group=call(model,'node get',node='Face');assert not group['dynamic_deformation'] and not group['translate_children']
    record('all typed transform, material, mesh-origin, visibility, camera and MeshGroup inspector fields survive SDK reload')
    model=WORK/'metadata.inx';call(BASE,'project meta',name='Model',artist='Artist',rigger='Rigger',copyright='Copyright',license='https://example.org/license',contact='Contact',reference='Reference',thumbnail=0,preserve_pixels=True,output=model)
    meta=call(model,'project inspect')['meta'];expected={'name':'Model','artist':'Artist','rigger':'Rigger','copyright':'Copyright','licenseURL':'https://example.org/license','contact':'Contact','reference':'Reference','thumbnailId':0,'preservePixels':True}
    assert all(meta[k]==v for k,v in expected.items()),meta;record('all model information and texture-filtering inspector fields survive SDK reload')
    model=WORK/'physics-fields.inx';batch(BASE,[('physics set',{'gravity':3,'pixels-per-meter':750}),('physics set',{'node':'Pendulum','model':'spring_pendulum','mapping':'yx','gravity':.4,'length':25,'frequency':3,'angle-damping':.2,'length-damping':.3,'output-scale':'2,3','local-only':True})],model)
    globals=call(model,'physics get');near(globals['gravity'],3);near(globals['pixelsPerMeter'],750)
    driver=call(model,'physics get',node='Pendulum');assert driver['model_type']=='SpringPendulum' and driver['map_mode']=='YX' and driver['local_only'];near(driver['gravity'],.4);near(driver['length'],25);near(driver['frequency'],3);near(driver['angle_damping'],.2);near(driver['length_damping'],.3);near(driver['output_scale'],[2,3]);record('all SimplePhysics and global physics inspector fields survive SDK reload')
    common=['zSort','transform.t.x','transform.t.y','transform.t.z','transform.r.x','transform.r.y','transform.r.z','transform.s.x','transform.s.y']
    properties={
        'Part':common+['alphaThreshold','opacity','tint.r','tint.g','tint.b','screenTint.r','screenTint.g','screenTint.b','emissionStrength'],
        'Group':common+['opacity','tint.r','tint.g','tint.b','screenTint.r','screenTint.g','screenTint.b'],
        'Pendulum':common+['gravity','length','frequency','angleDamping','lengthDamping','outputScale.x','outputScale.y'],
    }
    ops=[('node add',{'name':'Group','type':'Composite'})]
    for name,keys in properties.items():
        for index,key in enumerate(keys):ops.append(('key set',{'param':'XY','node':name,'property':key,'at':'1,0','value':.1+index*.02}))
    model=WORK/'scalar-fields.inx';batch(BASE,ops,model)
    for name,keys in properties.items():
        bindings=call(model,'binding list',param='XY');node=call(model,'node get',node=name)
        for index,key in enumerate(keys):
            b=next(b for b in bindings if b['node']==node['uuid'] and b['param_name']==key)
            near(b['values'][2][1],.1+index*.02);assert b['isSet'][2][1]
        record(name+' every scalar property available to deformation inspector stores the explicit selected key value')
    model=WORK/'animation-fields.inx';batch(BASE,[('animation add',{'name':'A','length':20,'fps':24}),('animation set',{'name':'A','new-name':'B','length':40,'fps':30,'additive':True,'weight':.4,'lead-in':3,'lead-out':30}),('animation lane-add',{'name':'B','param':'XY','axis':1}),('animation lane-set',{'name':'B','param':'XY','axis':1,'interpolation':'Cubic','merge':'Multiplicative'}),('animation key-set',{'name':'B','param':'XY','axis':1,'frame':10,'value':.6,'tension':.7})],model)
    a=call(model,'animation get',name='B');assert a['length']==40 and a['additive'] and a['leadIn']==3 and a['leadOut']==30;near(a['timestep'],1/30);near(a['animationWeight'],.4);lane=a['lanes'][0];assert lane['target']==1 and lane['interpolation']=='Cubic' and lane['merge_mode']=='Multiplicative';assert lane['keyframes'][0]['frame']==10;near(lane['keyframes'][0]['value'],.6);near(lane['keyframes'][0]['tension'],.7);record('all animation and lane inspector properties survive SDK reload')
    hit=WORK/'hit.inx'
    batch(BASE,[('node set',{'node':'Part','zsort':2}),('node set',{'node':'Eye','zsort':1,'scale':'0.5,0.5'})],hit)
    assert [r['name'] for r in call(hit,'node hit',point='0,0',sort='z')]==['Eye','Part']
    assert [r['name'] for r in call(hit,'node hit',point='0,0',sort='size')]==['Eye','Part']
    assert call(hit,'node hit',point='1000,1000')==[]
    record('viewport overlap query returns matching parts in native draw-order and size sorting')

finally:
    (WORK/'results.json').write_text(json.dumps(RESULT,indent=2)+'\n')
