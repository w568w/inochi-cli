module cli.nodes;
version (InochiCLI):
import cli.context;
import cli.render : pose;
import creator;
import creator.actions;
import creator.core.actionstack;
import creator.ext;
import creator.utils.transform;
import creator.panels.nodes;
import inochi2d;
import std.algorithm;
import std.array;
import std.conv;
import std.exception;
import std.json;
import std.string;

JSONValue nodeOps(Context c,string action,Options o){auto p=c.puppet;
 if(action=="list") {JSONValue[] a;auto filter=opt(o,"filter").toLower;foreach(n;nodes(p)){if(filter.length&&!clean(n.name).toLower.canFind(filter)&&!nodePath(n).toLower.canFind(filter))continue;a~=JSONValue(["uuid":JSONValue(n.uuid),"name":JSONValue(clean(n.name)),"path":JSONValue(nodePath(n)),"type":json(n)["type"],"enabled":JSONValue(n.enabled)]);}return JSONValue(a);}
 if(action=="hit") {
  auto snapshot=c.snapshot();scope(exit)c.restore(snapshot);pose(c,o);
  auto space=opt(o,"space","world");enforce(space=="world"||space=="image","Hit testing uses world or image coordinates");
  auto point=worldPoint(pair(need(o,"point")),o);Part[] matches;
  foreach(part;p.getAllParts){auto b=part.bounds;if(point.x>=b.x&&point.x<=b.z&&point.y>=b.y&&point.y<=b.w)matches~=part;}
  auto mode=opt(o,"sort","z");enforce(mode=="z"||mode=="size","Sort must be z or size");
  if(mode=="z")sort!((a,b)=>a.zSortNoOffset<b.zSortNoOffset,SwapStrategy.stable)(matches);
  else sort!((a,b)=>(a.bounds.z-a.bounds.x)*(a.bounds.w-a.bounds.y)<(b.bounds.z-b.bounds.x)*(b.bounds.w-b.bounds.y),SwapStrategy.stable)(matches);
  JSONValue[] result;foreach(part;matches)result~=JSONValue(["uuid":JSONValue(part.uuid),"name":JSONValue(clean(part.name)),"path":JSONValue(nodePath(part)),"bounds":json(part.bounds.vector)]);
  return JSONValue(result);
 }
 if(action=="add"){auto parent="parent" in o?node(p,o["parent"]):p.root;Node n;switch(opt(o,"type","Node")){case "Node":n=new Node(parent);break;case "Part":n=new ExPart(parent);break;case "Mask":n=new Mask(parent);break;case "Composite":n=new Composite(parent);break;case "SimplePhysics":n=new SimplePhysics(parent);break;case "Camera":n=new ExCamera(parent);break;case "MeshGroup":n=new MeshGroup(parent);break;default:throw new Exception("Unknown node type");}n.name=need(o,"name");p.rescanNodes();if("position" in o||"rotation" in o||"scale" in o||"viewport" in o){auto options=o.dup;options["node"]=n.uuid.to!string;nodeOps(c,"set",options);}return json(n);}
 auto n=node(p,need(o,"node"));
 if(action=="get"){auto result=json(n);if(flag(o,"runtime"))result["runtime"]=JSONValue(["pixelSnap":JSONValue(n.localTransform.pixelSnap)]);return result;}
 if(action=="delete"){enforce(n!is p.root,"Cannot delete root");incDeleteChildWithHistory(n);return JSONValue(n.uuid);}
 if(action=="reparent"){auto parent=node(p,need(o,"parent"));auto t=parent;while(t){enforce(t!is n,"Reparent would create cycle");t=t.parent;}auto original=n.localTransform;auto originalSort=n.relZSort;n.reparent(parent,to!size_t(opt(o,"index","0")));if(flag(o,"local")){n.localTransform=original;n.relZSort=originalSort;n.transformChanged();}p.rescanNodes();return json(n);}
 if(action=="origin"){(new NodesPanel).recalculateNodeOrigin(n,true);return json(n);}
 enforce(action=="set","Unknown node operation: "~action);
 foreach(key; ["opacity","blend","threshold","tint","screen-tint"]) if(key in o)enforce(cast(Part)n !is null || cast(Composite)n !is null,"--"~key~" requires Part or Composite");
 foreach(key; ["emission","layer-path"]) if(key in o)enforce(cast(Part)n !is null,"--"~key~" requires Part");
 if("origin" in o)enforce(cast(Drawable)n !is null,"--origin requires a mesh");
 foreach(key; ["dynamic","translate-children"]) if(key in o)enforce(cast(MeshGroup)n !is null,"--"~key~" requires MeshGroup");
 if("propagate" in o)enforce(cast(Composite)n !is null,"--propagate requires Composite");
 if("viewport" in o)enforce(cast(ExCamera)n !is null,"--viewport requires Camera");

 if(auto v="name" in o)n.name=*v;
 if(auto v="enabled" in o){n.enabled=to!bool(*v);if(flag(o,"recursive"))foreach(child;nodes(p)){auto t=child.parent;while(t){if(t is n)child.enabled=n.enabled;t=t.parent;}}}
 if(auto v="position" in o){auto value=triple(*v);auto space=opt(o,"space","local");enforce(["local","world","image"].canFind(space),"Invalid coordinate space");if(space=="image")value=vec3(worldPoint(value.xy,o),value.z);if(space!="local"){
  mat4 parentMatrix=mat4.identity;
  if(n.lockToRoot){p.root.localTransform.update();parentMatrix=p.root.localTransform.matrix;}
  else if(n.parent)parentMatrix=n.parent.transform.matrix;
  value=(parentMatrix.inverse*vec4(value,1)).xyz;
 }n.localTransform.translation=value;}
 if(auto v="rotation" in o)n.localTransform.rotation=triple(*v);
 if(auto v="scale" in o)n.localTransform.scale=pair(*v);
 if(auto v="zsort" in o)n.zSort=number(*v);
 if(auto v="lock-to-root" in o)n.lockToRoot=to!bool(*v);
 if(auto v="pixel-snap" in o)n.localTransform.pixelSnap=to!bool(*v);
 if(auto d=cast(Drawable)n)if(auto v="origin" in o){d.getMesh.origin=pair(*v);d.refresh();}
 if(auto part=cast(Part)n) {
  if(auto v="opacity" in o)part.opacity=number(*v);if(auto v="blend" in o)part.blendingMode=enumValue!BlendMode(*v);if(auto v="threshold" in o)part.maskAlphaThreshold=number(*v);
  if(auto v="tint" in o)part.tint=triple(*v);if(auto v="screen-tint" in o)part.screenTint=triple(*v);if(auto v="emission" in o)part.emissionStrength=number(*v);
  if(auto ex=cast(ExPart)part)if(auto v="layer-path" in o)ex.layerPath=*v;
 }
 if(auto a=cast(Composite)n) {if(auto v="threshold" in o)a.threshold=number(*v);if(auto v="propagate" in o){a.propagateMeshGroup=to!bool(*v);if(a.parent)a.reparent(a.parent,0);}if(auto v="opacity" in o)a.opacity=number(*v);if(auto v="blend" in o)a.blendingMode=enumValue!BlendMode(*v);if(auto v="tint" in o)a.tint=triple(*v);if(auto v="screen-tint" in o)a.screenTint=triple(*v);}
 if(auto a=cast(MeshGroup)n){if(auto v="dynamic" in o)a.dynamic=to!bool(*v);if(auto v="translate-children" in o)a.setTranslateChildren(to!bool(*v));}
 if(auto a=cast(ExCamera)n)if(auto v="viewport" in o)a.getViewport=pair(*v);
 n.transformChanged();return json(n);
}
JSONValue physicsOps(Context c,string action,Options o){auto p=c.puppet;
 if(action=="get"&&!("node" in o))return json(p.physics);
 if(action=="set"&&!("node" in o)){if(auto v="gravity" in o)p.physics.gravity=number(*v);if(auto v="pixels-per-meter" in o)p.physics.pixelsPerMeter=number(*v);return json(p.physics);}
 auto a=cast(SimplePhysics)node(p,need(o,"node"));enforce(a!is null,"Expected SimplePhysics node");if(action=="get")return json(a);
 if(action=="map"){a.param(parameter(p,need(o,"param")));p.rescanNodes();return json(a);}
 if(action=="unmap"){a.param(null);p.rescanNodes();return json(a);}
 enforce(action=="set","Unknown physics operation");
 if(auto v="model" in o)a.modelType(enumValue!PhysicsModel(*v));if(auto v="mapping" in o)a.mapMode=enumValue!ParamMapMode(*v);
 if(auto v="gravity" in o)a.gravity=number(*v);if(auto v="length" in o)a.length=number(*v);if(auto v="frequency" in o)a.frequency=number(*v);if(auto v="angle-damping" in o)a.angleDamping=number(*v);if(auto v="length-damping" in o)a.lengthDamping=number(*v);if(auto v="output-scale" in o)a.outputScale=pair(*v);if(auto v="local-only" in o)a.localOnly=to!bool(*v);a.reset();return json(a);
}
JSONValue maskOps(Context c,string action,Options o){auto n=node(c.puppet,need(o,"node"));MaskBinding[]* masks;if(auto p=cast(Part)n)masks=&p.masks;else if(auto a=cast(Composite)n)masks=&a.masks;enforce(masks!is null,"Masks require Part or Composite");if(action=="list")return json(*masks);
 auto source=drawable(c.puppet,need(o,"source"));enforce(source!is n,"Cannot mask against self");auto mode=opt(o,"mode","Mask");
 if(action=="order"){auto index=to!size_t(need(o,"index"));enforce(index<(*masks).length,"Invalid mask index");auto oldIndex=(*masks).countUntil!(m=>m.maskSrcUUID==source.uuid);enforce(oldIndex>=0,"Mask not found");auto entry=(*masks)[oldIndex];(*masks)=(*masks).remove(oldIndex);(*masks).insertInPlace(index,entry);return json(*masks);}
 if(action=="add"){enforce(!(*masks).any!(m=>m.maskSrcUUID==source.uuid),"Mask already exists");MaskBinding b;b.maskSrcUUID=source.uuid;b.maskSrc=source;b.mode=enumValue!MaskingMode(mode);(*masks)~=b;}
 else if(action=="remove")(*masks)=(*masks).filter!(m=>m.maskSrcUUID!=source.uuid).array;
 else if(action=="set"){bool found;foreach(ref m;*masks)if(m.maskSrcUUID==source.uuid){m.mode=enumValue!MaskingMode(mode);found=true;}enforce(found,"Mask binding not found");}
 else throw new Exception("Unknown mask operation");return json(*masks);
}
