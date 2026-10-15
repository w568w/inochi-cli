module cli.animations;
version (InochiCLI):
import cli.context;
import inochi2d;
import creator.ext;
import inochi2d.core.automation.phys;
import inochi2d.core.automation.sine;
import std.algorithm;
import std.array;
import std.conv;
import std.exception;
import std.json;
import std.string;
JSONValue animationOps(Context c,string action,Options o){auto p=c.puppet;auto animations=&p.getAnimations();
 if(action=="list")return json(*animations);
 auto name=need(o,"name");
 if(action=="add"){enforce(!(name in *animations),"Animation exists");Animation a;a.length=to!int(opt(o,"length","60"));auto fps=number(opt(o,"fps","60"));enforce(a.length>0&&fps>0,"Invalid animation timing");a.timestep=1.0f/fps;a.animationWeight=1;(*animations)[name]=a;return json(a);}
 auto a=name in *animations;enforce(a!is null,"Animation not found: "~name);
 if(action=="get")return json(*a);
 if(action=="delete"){(*animations).remove(name);return JSONValue(name);}
 if(action=="rename"){auto target=need(o,"target");enforce(target.strip.length>0,"Animation name cannot be empty");enforce(target==name||!(target in *animations),"Animation name already exists");auto value=*a;(*animations).remove(name);(*animations)[target]=value;return json(value);}
 if(action=="duplicate"){auto target=need(o,"target");enforce(!(target in *animations),"Animation already exists: "~target);auto copy=*a;copy.lanes=a.lanes.dup;foreach(ref l;copy.lanes)l.frames=l.frames.dup;(*animations)[target]=copy;return json(copy);}
 if(action=="set"){if(auto v="length" in o){a.length=to!int(*v);a.leadOut=a.length;}if(auto v="fps" in o)a.timestep=1.0f/number(*v);if(auto v="additive" in o)a.additive=to!bool(*v);if(auto v="weight" in o)a.animationWeight=number(*v);if(auto v="lead-in" in o)a.leadIn=to!int(*v);if(auto v="lead-out" in o)a.leadOut=to!int(*v);enforce(a.length>0&&a.timestep>0,"Invalid animation timing");if(auto target="new-name" in o){enforce((*target).strip.length>0,"Animation name cannot be empty");enforce(*target==name||!(*target in *animations),"Animation name already exists");auto value=*a;(*animations).remove(name);(*animations)[*target]=value;return json(value);}return json(*a);}
 auto param=parameter(p,need(o,"param"));auto axis=to!int(opt(o,"axis","0"));enforce(axis==0||(axis==1&&param.isVec2),"Invalid axis");ptrdiff_t index=-1;foreach(i,l;a.lanes)if(l.paramRef.targetParam is param&&l.paramRef.targetAxis==axis)index=i;
 if(action=="lane-add"){enforce(index==-1,"Lane already exists");AnimationLane lane;lane.paramRef=new AnimationParameterRef(param,axis);lane.interpolation=InterpolateMode.Linear;a.lanes~=lane;return json(*a);}
 enforce(index>=0,"Lane not found");auto lane=&a.lanes[index];
 if(action=="lane-remove"){a.lanes=a.lanes.remove(index);return json(*a);}
 if(action=="lane-set"){if(auto v="interpolation" in o)lane.interpolation=enumValue!InterpolateMode(*v);if(auto v="merge" in o)lane.mergeMode=enumValue!ParamMergeMode(*v);return json(*a);}
 auto frame=to!int(need(o,"frame"));enforce(frame>=0&&frame<a.length,"Frame outside animation");
 if(action=="key-remove")lane.frames=lane.frames.filter!(v=>v.frame!=frame).array;
 else if(action=="key-set"){auto value=number(need(o,"value"));auto tension=number(opt(o,"tension","0.5"));bool found;foreach(ref v;lane.frames)if(v.frame==frame){v.value=value;v.tension=tension;found=true;}if(!found)lane.frames~=Keyframe(frame,value,tension);lane.updateFrames();}
 else throw new Exception("Unknown animation operation");return json(*a);
}
JSONValue automationOps(Context c,string action,Options o){auto p=c.puppet;
 if(action=="list")return json(p.automation);
 auto name=need(o,"name");
 if(action=="add"){auto type=opt(o,"type","sine");enforce(inHasAutomationType(type),"Unknown automation type: "~type);auto a=inInstantiateAutomation(type,p);a.name=name;p.automation~=a;return json(a);}
 Automation[] found;foreach(a;p.automation)if(a.name==name)found~=a;enforce(found.length==1,"Automation not found or ambiguous");auto a=found[0];
 if(action=="delete")p.automation=p.automation.filter!(v=>v!is a).array;
 else if(action=="bind"){auto param=parameter(p,need(o,"param"));auto axis=to!int(opt(o,"axis","0"));enforce(axis==0||(axis==1&&param.isVec2),"Invalid automation axis");AutomationBinding b;b.param=param;b.paramId=param.name;b.axis=axis;b.range=pair(opt(o,"range","0,1"));a.bind(b);if(auto physics=cast(PhysicsAutomation)a){auto position=pair(opt(o,"position","0,0"));auto n=VerletNode(position);n.distance=number(opt(o,"distance","1"));physics.nodes[$-1]=n;}}
 else if(action=="unbind"){auto index=to!size_t(need(o,"index"));if(auto sine=cast(ExSineAutomation)a){enforce(index<sine.projectBindings.length,"Binding index outside range");sine.projectBindings=sine.projectBindings.remove(index);}else if(auto physics=cast(ExPhysicsAutomation)a){enforce(index<physics.projectBindings.length,"Binding index outside range");physics.projectBindings=physics.projectBindings.remove(index);physics.nodes=physics.nodes.remove(index);}else throw new Exception("Unsupported automation binding editor");}
 else if(action=="set"){foreach(key;["speed","phase","wave"])if(key in o)enforce(cast(SineAutomation)a !is null,"--"~key~" requires sine automation");foreach(key;["damping","bounciness","gravity"])if(key in o)enforce(cast(PhysicsAutomation)a !is null,"--"~key~" requires physics automation");if(auto v="enabled" in o)a.enabled=to!bool(*v);if(auto sine=cast(SineAutomation)a){if(auto v="speed" in o)sine.speed=number(*v);if(auto v="phase" in o)sine.phase=number(*v);if(auto v="wave" in o)sine.sineType=enumValue!SineType(*v);}if(auto physics=cast(PhysicsAutomation)a){if(auto v="damping" in o)physics.damping=number(*v);if(auto v="bounciness" in o)physics.bounciness=number(*v);if(auto v="gravity" in o)physics.gravity=number(*v);}}
 else enforce(action=="get","Unknown automation operation");return json(a);
}
