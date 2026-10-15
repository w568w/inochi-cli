module cli.rig;
version (InochiCLI):
import cli.context;
import creator.ext;
import creator.utils.transform : incBindingAutoFlip;
import creator.windows.flipconfig;
import creator.windows.paramsplit : incSplitParameter;
import creator.viewport.common.mesh;
import creator.panels.parameters;
import inochi2d;
import std.algorithm;
import std.array;
import std.conv;
import std.exception;
import std.json;
import std.math;
import std.string;

vec3 groupColor(string value){
 switch(value.toLower){case "none":return vec3(float.nan);case "red":return vec3(.25,.15,.15);case "green":return vec3(.15,.25,.15);case "blue":return vec3(.15,.15,.25);case "purple":return vec3(.25,.15,.25);case "cyan":return vec3(.15,.25,.25);case "yellow":return vec3(.25,.25,.15);case "white":return vec3(.25);default:return triple(value);}
}
vec2u keypoint(Parameter p,Options o){auto v=pair(opt(o,"at","0,0"));auto k=p.findClosestKeypoint(v);auto exact=p.getKeypointValue(k);enforce(std.math.abs(exact.x-v.x)<1e-5&&(!p.isVec2||std.math.abs(exact.y-v.y)<1e-5),"Key not on axis points; use param axis-add first");return k;}
ParameterBinding binding(Context c,Options o,bool create=false){auto p=parameter(c.puppet,need(o,"param"));auto n=node(c.puppet,need(o,"node"));auto name=opt(o,"property","deform");enforce(n.hasParam(name)||(name=="deform"&&cast(Drawable)n!is null),"Node cannot bind property: "~name);auto b=create?p.getOrAddBinding(n,name):p.getBinding(n,name);enforce(b!is null,"Binding not found");return b;}
JSONValue paramOps(Context c,string action,Options o){auto p=c.puppet;
 if(action=="list"){auto filter=opt(o,"filter").toLower;return json(p.parameters.filter!(a=>!filter.length||clean(a.name).toLower.canFind(filter)||parameterPath(a).toLower.canFind(filter)).array); }
 if(action=="pair-auto"){auto window=new FlipPairWindow;window.autoPair(need(o,"first-pattern"),need(o,"second-pattern"));window.apply();return json(incGetFlipPairs());}
 if(action=="pair-list")return json(incGetFlipPairs());
 if(action=="pair-add"){auto first=node(p,need(o,"first")),second=node(p,need(o,"second"));enforce(first!is second,"Pair nodes must differ");auto pairs=incGetFlipPairs();enforce(!pairs.any!(v=>v.parts[].canFind(first)||v.parts[].canFind(second)),"Node already paired");pairs~=new FlipPair([first,second],"");incSetFlipPairs(pairs);return json(pairs);}
 if(action=="pair-set"){
  auto selected=node(p,need(o,"node"));auto pairs=incGetFlipPairs().dup;auto index=pairs.countUntil!(v=>v.parts[].canFind(selected));enforce(index>=0,"Mirror pair not found");
  auto first="first" in o?(o["first"]=="none"?null:node(p,o["first"])):pairs[index].parts[0];
  auto second="second" in o?(o["second"]=="none"?null:node(p,o["second"])):pairs[index].parts[1];
  enforce(first is null||second is null||first !is second,"Pair nodes must differ");
  foreach(i,pair;pairs)if(i!=index)foreach(ref part;pair.parts)if(part !is null&&(part is first||part is second))part=null;
  pairs[index]=new FlipPair([first,second],"");
  pairs=pairs.filter!(v=>v.parts[0] !is null||v.parts[1] !is null).array;
  foreach(pair;pairs)if(pair.parts[0] is null){pair.parts[0]=pair.parts[1];pair.parts[1]=null;}
  incSetFlipPairs(pairs);return json(pairs);
 }
 if(action=="pair-remove"){auto n=node(p,need(o,"node"));auto pairs=incGetFlipPairs().filter!(v=>!v.parts[].canFind(n)).array;incSetFlipPairs(pairs);return json(pairs);}
 if(action=="group-list")return json(p.groups);
 if(action=="group-add"){auto g=new ExParameterGroup(need(o,"name"));if(auto color="color" in o)g.color=groupColor(*color);p.addGroup(g);return json(g);}
 if(action=="group-set"||action=="group-delete"){auto g=p.findGroup(need(o,"group"));enforce(g!is null,"Group not found");if(action=="group-delete"){foreach(a;g.children.dup)(cast(ExParameter)a).setParent(null);p.removeGroup(g);}else{if(auto name="name" in o)g.name=*name;if(auto color="color" in o)g.color=groupColor(*color);}return json(g);}
 if(action=="mouth-shape"){auto a=incCreateMouthShape(need(o,"name"));p.parameters~=a;return json(a);}
 if(action=="add"){auto a=new ExParameter(need(o,"name"),flag(o,"vec2"));a.min=pair(opt(o,"min","-1,-1"));a.max=pair(opt(o,"max","1,1"));if(!a.isVec2){a.min.y=0;a.max.y=1;}a.defaults=pair(opt(o,"defaults","0,0"));if(a.min.x<0&&a.max.x>0)a.insertAxisPoint(0,(0-a.min.x)/(a.max.x-a.min.x));if(a.isVec2&&a.min.y<0&&a.max.y>0)a.insertAxisPoint(1,(0-a.min.y)/(a.max.y-a.min.y));p.parameters~=a;return json(a);}
 auto a=parameter(p,need(o,"param"));
 if(action=="get")return json(a);
 if(action=="delete"){p.removeParameter(a);return JSONValue(a.uuid);}
 if(action=="duplicate"){auto b=a.dup; b.name=opt(o,"name",clean(a.name)~" (Copy)");if(auto source=cast(ExParameter)a)if(auto copy=cast(ExParameter)b)copy.setParent(source.parent);p.parameters~=b;return json(b);}
 if(action=="split"){
  Node[] selected;foreach(ref_;items(need(o,"nodes")))selected~=node(p,ref_);
  auto result=incSplitParameter(a,selected,need(o,"name"));enforce(result !is null,"Split selected no bindings");return json(result);
 }
 if(action=="axis-add"||action=="axis-move"||action=="axis-remove"){auto axis=to!uint(opt(o,"axis","0"));enforce(axis<2&&(a.isVec2||axis==0),"Invalid parameter axis");if(action=="axis-remove"){auto idx=to!uint(need(o,"index"));enforce(idx>0&&idx+1<a.axisPointCount(axis),"Invalid axis point removal");a.deleteAxisPoint(axis,idx);}else{auto value=number(need(o,"value"));auto normalized=(value-a.min.vector[axis])/(a.max.vector[axis]-a.min.vector[axis]);enforce(normalized>0&&normalized<1,"Axis point outside range");if(action=="axis-add"){enforce(!a.axisPoints[axis].canFind(normalized),"Axis point already exists");a.insertAxisPoint(axis,normalized);}else {auto idx=to!uint(need(o,"index"));enforce(idx>0&&idx+1<a.axisPointCount(axis),"Cannot move endpoint");enforce(normalized>a.axisPoints[axis][idx-1]&&normalized<a.axisPoints[axis][idx+1],"Axis points cannot cross");a.axisPoints[axis][idx]=normalized;foreach(b;a.bindings)b.reInterpolate();}}return json(a);}
 if(action=="flip"){auto axis=to!uint(opt(o,"axis","0"));enforce(axis<2,"Invalid axis");a.reverseAxis(axis);return json(a);}
 if(action=="mirror"||action=="autofill"){
  auto axis=to!uint(opt(o,"axis","0"));float from=0,to=1;
  if("direction" in o){
   enforce(action=="autofill"&&!("from" in o)&&!("to" in o)&&!("axis" in o),"Use either direction or axis/from/to");
   switch(o["direction"]){case "left":axis=0;to=.4999;break;case "right":axis=0;from=.5001;break;case "up":axis=1;from=.5001;break;case "down":axis=1;to=.4999;break;default:throw new Exception("Direction must be left, right, up or down");}
  }
  enforce(axis<2&&(a.isVec2||axis==0),"Invalid axis");
  if(action=="mirror")mirrorAll(a,axis);
  else {
   if("from" in o)from=(number(o["from"])-a.min.vector[axis])/(a.max.vector[axis]-a.min.vector[axis]);
   if("to" in o)to=(number(o["to"])-a.min.vector[axis])/(a.max.vector[axis]-a.min.vector[axis]);
   enforce(from>=0&&to<=1&&from<=to,"Autofill range is outside parameter limits");
   mirroredAutofill(a,axis,from,to);
  }
  return json(a);
 }
 if(action=="paste"){incCLIPasteParameter(a,parameter(p,need(o,"source")),to!uint(opt(o,"axis","2")));return json(a);}
 if(action=="order"){auto index=to!size_t(need(o,"index"));enforce(index<p.parameters.length,"Invalid parameter index");auto old=p.parameters.countUntil(a);p.parameters=p.parameters.remove(old);p.parameters.insertInPlace(index,a);return json(p.parameters);}
 if(action=="to-2d"){convertTo2D(a);return json(parameter(p,a.uuid.to!string));}
 enforce(action=="set","Unknown parameter operation: "~action);
 if(auto v="name" in o)a.name=*v;if(auto v="min" in o)a.min=pair(*v);if(auto v="max" in o)a.max=pair(*v);if(auto v="defaults" in o)a.defaults=pair(*v);if(auto v="merge" in o)a.mergeMode=enumValue!ParamMergeMode(*v);
 if(auto v="group" in o){auto ex=cast(ExParameter)a;enforce(ex!is null,"Requires extended parameter");auto g=*v=="none"?null:p.findGroup(*v);enforce(*v=="none"||g!is null,"Group not found");ex.setParent(g);}
 enforce(a.min.x<a.max.x&&(!a.isVec2||a.min.y<a.max.y),"Invalid parameter range");return json(a);
}
JSONValue bindingOps(Context c,string action,Options o){auto p=parameter(c.puppet,need(o,"param"));if(action=="list")return json(p.bindings);auto b=binding(c,o,action=="add");
 if(action=="remove")p.removeBinding(b);
 else if(action=="set"){
  auto mode=enumValue!InterpolateMode(need(o,"interpolation"));
  enforce([InterpolateMode.Nearest,InterpolateMode.Linear,InterpolateMode.Cubic].canFind(mode),"Binding interpolation supports Nearest, Linear or Cubic");
  b.interpolateMode=mode;
 }
 else if(action=="copy"||action=="swap"){auto n=node(c.puppet,need(o,"target"));enforce(b.isCompatibleWithNode(n),"Incompatible target");auto target=p.getOrAddBinding(n,b.getName);foreach(x;0..p.axisPointCount(0))foreach(y;0..p.axisPointCount(1)){auto at=vec2u(x,y);if(action=="swap"){if(auto source=cast(ValueParameterBinding)b){auto dest=cast(ValueParameterBinding)target;auto value=source.getValue(at);auto set=source.isSet(at);target.copyKeypointToBinding(at,b,at);if(set)dest.setValue(at,value);else dest.unset(at);}else{auto source=cast(DeformationParameterBinding)b;auto dest=cast(DeformationParameterBinding)target;enforce(source.getValue(at).vertexOffsets.size()==dest.getValue(at).vertexOffsets.size(),"Mesh vertex counts differ");auto value=source.getValue(at);auto set=source.isSet(at);target.copyKeypointToBinding(at,b,at);if(set)dest.setValue(at,value);else dest.unset(at);}}else b.copyKeypointToBinding(at,target,at);}target.reInterpolate();b.reInterpolate();}
 else enforce(action=="get"||action=="add","Unknown binding operation");return json(b);
}
JSONValue keyOps(Context c,string action,Options o){auto a=parameter(c.puppet,need(o,"param"));auto b=binding(c,o,action=="set"||action=="from-mirror"||(action=="reset"&&"vertices" in o));auto at=keypoint(a,o);
 ulong[] selected;
 if("vertices" in o){
  auto deform=cast(DeformationParameterBinding)b;enforce(deform !is null,"Vertex selection requires a deformation binding");
  enforce(action=="reset"||action=="from-mirror","Vertex selection requires reset or from-mirror");
  auto mesh=cast(Drawable)b.getNode;
  foreach(item;items(o["vertices"])){auto i=to!ulong(item);enforce(i<mesh.vertices.length,"Invalid vertex index");selected~=i;}
 }
 if(action=="get"){auto result=json(b);result["selectedIndex"]=json(at.vector);result["selectedValue"]=result["values"][at.x][at.y];result["selectedIsSet"]=JSONValue(b.isSet(at));return result;}
 if(action=="from-mirror"){
  auto axis=to!int(opt(o,"axis","0"));enforce(axis==-1||axis==0||axis==1,"Mirror axis must be -1, 0 or 1");
  auto sourceNode=b.getNode;
  if("source-node" in o)sourceNode=node(c.puppet,o["source-node"]);
  else if(auto pair=incGetFlipPairFor(sourceNode))sourceNode=pair.parts[0] is sourceNode?pair.parts[1]:pair.parts[0];
  auto source=a.getBinding(sourceNode,b.getName);enforce(source !is null,"Mirrored source binding not found");
  incBindingAutoFlip(b,source,at,cast(uint)axis,true,"vertices" in o?&selected:null);
 }
 else if(action=="current")b.setCurrent(at);
 else if(action=="flip-deform"){if(!b.isSet(at))return json(b);auto d=cast(DeformationParameterBinding)b;enforce(d!is null,"Flip deform requires deformation binding");auto drawable=cast(Drawable)b.getNode;auto mesh=new IncMesh(drawable.getMesh);auto remapped=mesh.deformByDeformationBinding(drawable,d.getValue(at),true);enforce(remapped!is null,"Could not flip deformation");d.setValue(at,*remapped);}
 else if(action=="unset")b.unset(at);else if(action=="reset"){
  if("vertices" in o){auto deform=cast(DeformationParameterBinding)b;auto value=deform.getValue(at);foreach(i;selected)value.vertexOffsets[i]=vec2(0);deform.setValue(at,value);}
  else b.reset(at);
 }
 else if(action=="set"){
  if(auto d=cast(DeformationParameterBinding)b){auto mesh=cast(Drawable)b.getNode;auto parsed=data(need(o,"offsets"));vec2[] values;foreach(v;parsed.array){enforce(v.array.length==2,"Offsets must be pairs");values~=vec2(number(v.array[0].toString),number(v.array[1].toString));}enforce(values.length==mesh.vertices.length,"Offset count must equal vertex count");Deformation delta;delta.clear(values.length);delta.vertexOffsets.data[0..values.length]=values;d.setValue(at,delta);}
  else (cast(ValueParameterBinding)b).setValue(at,number(need(o,"value")));
 }
 else if(action=="invert"||action=="mirror"){b.scaleValueAt(at,action=="mirror"?to!int(opt(o,"axis","0")):-1,-1);}
 else if(action=="copy"){auto targetParam="target-param" in o?parameter(c.puppet,o["target-param"]):a;auto targetNode="target-node" in o?node(c.puppet,o["target-node"]):b.getNode;auto target=targetParam.getOrAddBinding(targetNode,b.getName);enforce(target.isCompatibleWithNode(b.getNode),"Incompatible key target");auto dest=keypoint(targetParam,["at":need(o,"to")]);b.copyKeypointToBinding(at,target,dest);target.reInterpolate();}
 else if(action=="extrapolate")b.extrapolateValueAt(at,to!int(opt(o,"axis","0")));
 else throw new Exception("Unknown key operation");b.reInterpolate();return json(b);
}
