module cli.registry;
version (InochiCLI):
import cli.context;
import cli.nodes;
import cli.meshes;
import cli.rig;
import cli.assets;
import cli.animations;
import cli.render;
import inochi2d;
import creator.ext;
import creator.core.actionstack;
import std.algorithm;
import std.array;
import std.conv;
import std.exception;
import std.json;
import std.string;

struct Command {string group,action,options;bool edits;string description;}
Command[] commands(){Command[] out_;
 void add(string g,string acts,bool edit,string options,string desc){foreach(a;acts.split(','))out_~=Command(g,a,options,edit,desc);}
 add("project","inspect,check",false,"","SDK model inspection and validation");
 add("project","new,save",true,"","Save Creator project");
 add("project","meta",true,"name artist rigger copyright license contact reference thumbnail preserve-pixels","Model metadata");
 add("project","import-session",true,"file","Copy Inochi Session model extension data");
 add("project","import",true,"file keep-structure","Import PSD, KRA, INX, INP, image or image folder");
 add("project","merge-plan",false,"file layer-filter node-filter unmapped-only mapping","Inspect native PSD/KRA layer mappings and available targets");
 add("project","merge",true,"file parent rename retranslate resort unmapped-only mapping","Merge PSD, KRA, project or image");
 add("project","repair,regenerate-ids,layer-names",true,"","Creator repair tools");
 add("node","hit",false,"point sort space reference tile param physics time animation frame loop snap-to-frames","Viewport overlapping parts in draw-order or size order");add("node","list",false,"filter","Node tree and UUIDs");add("node","get",false,"node runtime","Inspect node");
 add("node","add",true,"type name parent","Create node");add("node","delete,origin",true,"node","Remove node or recalculate origin");add("node","reparent",true,"node parent index local","Creator reparent preserving world position and draw order; --local keeps local properties");
 add("node","set",true,"node name enabled recursive position rotation scale zsort lock-to-root pixel-snap origin opacity blend threshold tint screen-tint emission layer-path dynamic translate-children propagate viewport space reference tile","Edit node properties");
 add("camera","list,get",false,"node","Inspect cameras");add("camera","add,set",true,"node name parent position rotation scale viewport","Create or edit camera");
 add("mesh","copy",true,"node source uv-policy","Copy native mesh data to a target");add("mesh","layout",true,"node","Creator vertex-editor UV layout");add("mesh","get",false,"node","Inspect vertices, UVs and triangles");add("mesh","select",false,"node vertices rect polygon param at space reference tile mirror-x mirror-y mirror-origin","Return selected vertex indices");
 add("mesh","set",true,"node data","Replace mesh with explicit vertices, UVs and triangles");
 add("mesh","vertex-set",true,"node index position uv uv-policy space reference tile param at mirror-x mirror-y mirror-origin","Edit vertex and UV");add("mesh","vertex-add",true,"node position connect-to uv-policy space reference tile mirror-x mirror-y mirror-origin","Add vertex");add("mesh","vertex-remove",true,"node vertices uv-policy mirror-x mirror-y mirror-origin","Remove vertices");add("mesh","connect,disconnect",true,"node a b uv-policy mirror-x mirror-y mirror-origin","Edit edge connections");add("mesh","triangulate",true,"node uv-policy","Creator triangulation");add("mesh","grid",true,"node x y uv-policy","Create mesh grid");add("mesh","automesh",true,"node uv-policy mode preset x y x-segments y-segments margin threshold sampling distance max-distance rings mirror-x mirror-y mirror-origin","Creator grid or contour automesh");add("mesh","transform,mirror,brush",true,"node param at uv-policy vertices move scale angle center axis radius strength brush inner-radius height inner-ratio stroke flow space reference tile mirror-x mirror-y mirror-origin","Transform selected vertices");
 add("mesh","path",true,"node param at uv-policy vertices from to pivot dragged angle shift-point shift-to space reference tile mirror-x mirror-y mirror-origin","Creator spline path deformation");
 add("param","list",false,"filter","List parameters");add("param","group-list",false,"","List groups");add("param","get",false,"param","Inspect parameter");add("param","add",true,"name vec2 min max defaults","Create parameter");add("param","mouth-shape",true,"name","Creator mouth-shape preset");add("param","set",true,"param name min max defaults merge group","Edit parameter");add("param","delete,to-2d",true,"param","Delete or convert parameter");add("param","duplicate",true,"param name","Duplicate parameter and bindings");add("param","split",true,"param name nodes","Move selected bindings into new parameter");add("param","axis-add",true,"param axis value","Add axis point in model units");add("param","axis-move",true,"param axis index value","Move axis point");add("param","axis-remove",true,"param axis index","Remove axis point");add("param","flip,mirror",true,"param axis","SDK axis flips and value mirrors");add("param","autofill",true,"param axis from to direction","Creator directional mirrored key autofill");add("param","group-add",true,"name color","Create group");add("param","group-set",true,"group name color","Edit group");add("param","group-delete",true,"group","Remove group keeping parameters");
 add("param","paste",true,"param source axis","Creator paste with optional mirrored pairing");
 add("param","order",true,"param index","Reorder parameters");
 add("param","pair-auto",true,"first-pattern second-pattern","Creator automatic mirror pairing");add("param","pair-list",false,"","List mirror pairs");add("param","pair-add",true,"first second","Configure mirror pair");add("param","pair-set",true,"node first second","Assign or unassign mirror pair members");add("param","pair-remove",true,"node","Remove mirror pair");
 add("binding","list",false,"param","List parameter bindings");add("binding","get",false,"param node property","Inspect binding");add("binding","add,remove",true,"param node property","Create or remove binding");add("binding","set",true,"param node property interpolation","Set interpolation");add("binding","copy,swap",true,"param node property target","Copy or swap compatible bindings");
 add("key","from-mirror",true,"param node property at axis source-node vertices","Creator set-from-mirror for a selected key");add("key","get",false,"param node property at","Inspect key forms");add("key","set",true,"param node property at offsets value","Set mesh deformation or scalar binding");add("key","unset,reset,invert,current,flip-deform",true,"param node property at vertices","Unset, reset or invert key");add("key","mirror,extrapolate",true,"param node property at axis","Mirror or extrapolate key");add("key","copy",true,"param node property at to target-node target-param","Copy key form");
 add("texture","list",false,"runtime","List texture slots");add("texture","load",true,"node slot file","Replace texture");add("texture","remove,emissive",true,"node slot","Remove or make emissive");add("texture","export",false,"node slot","Export straight-alpha image");add("texture","bleed",true,"radius","Bleed textures");add("texture","premultiply,mipmaps",true,"","Texture processing");
 add("mask","list",false,"node","List masks");add("mask","add,remove,set",true,"node source mode","Mask and dodge bindings");
 add("mask","order",true,"node source index","Reorder masks");
 add("physics","get",false,"node","Inspect puppet or physics node");add("physics","set",true,"node model mapping gravity pixels-per-meter length frequency angle-damping length-damping output-scale local-only","Edit physical properties");add("physics","map",true,"node param","Map physics output parameter");add("physics","unmap",true,"node","Unmap physics output");
 add("automation","list",false,"","List automations");add("automation","get",false,"name","Inspect automation");add("automation","add",true,"name type","Create SDK automation");add("automation","delete",true,"name","Delete automation");add("automation","set",true,"name enabled speed phase wave damping bounciness gravity","Edit automation");add("automation","unbind",true,"name index","Remove automation binding");add("automation","bind",true,"name param axis range distance position","Bind automation output");
 add("animation","list",false,"","List animations");add("animation","get",false,"name","Inspect animation");add("animation","add",true,"name length fps","Create animation");add("animation","set",true,"name new-name length fps additive weight lead-in lead-out","Edit animation");add("animation","delete",true,"name","Remove animation");add("animation","rename",true,"name target","Rename animation");add("animation","duplicate",true,"name target","Duplicate animation");add("animation","lane-add,lane-remove",true,"name param axis","Add or remove lane");add("animation","lane-set",true,"name param axis interpolation merge","Edit lane");add("animation","key-set",true,"name param axis frame value tension","Set animation key");add("animation","key-remove",true,"name param axis frame","Remove animation key");
 string rendering="param focus isolate bounds padding size max-size camera zoom view-center background time frame animation playback loop snap-to-frames physics postprocess ambient-light mesh vertices triangulate overlay-bounds orientation mirror-view creator-reference";
 add("render","image,grid",false,rendering~" values","SDK render and parameter grid");add("export","image",false,rendering,"SDK image export");add("export","inp,atlas-preview",false,"resolution scale padding nonlinear keep-unused watermark watermark-opacity watermark-loops watermark-blend","Creator INP atlas export");add("export","video",false,rendering~" fps frames loops codec transparent ffmpeg-options","SDK frames and Creator FFmpeg encoding");
 add("scene","get",false,"","Inspect scene preview state");add("scene","set",true,"ambient-light","Set scene ambient light");add("history","list",false,"details","List batch undo history");add("history","seek",true,"index","Restore a history position");add("history","clear",true,"","Clear batch undo history");add("history","undo,redo,begin,end",true,"","Batch history and edit groups");return out_;}
JSONValue batchSchema() {
 JSONValue[] alternatives;
 foreach(cmd;commands()) {
  JSONValue[string] options;
  foreach(option;cmd.options.split(' '))if(option.length)options[option]=JSONValue(cast(JSONValue[string])null);
  options["output"]=JSONValue(cast(JSONValue[string])null);
  alternatives~=JSONValue([
   "type":JSONValue("object"),
   "required":JSONValue([JSONValue("command")]),
   "additionalProperties":JSONValue(false),
   "properties":JSONValue([
    "command":JSONValue(["const":JSONValue(cmd.group~" "~cmd.action)]),
    "options":JSONValue(["type":JSONValue("object"),"properties":JSONValue(options),"additionalProperties":JSONValue(false)])
   ])
  ]);
 }
 return JSONValue(["$schema":JSONValue("https://json-schema.org/draft/2020-12/schema"),
  "title":JSONValue("Inochi CLI batch"),"type":JSONValue("array"),
  "items":JSONValue(["oneOf":JSONValue(alternatives)])]);
}
Command command(string group,string action){foreach(c;commands())if(c.group==group&&c.action==action)return c;throw new Exception("Unknown command: "~group~" "~action);}
JSONValue execute(Context c,Command cmd,Options o){foreach(k,v;o)enforce(cmd.options.split(' ').canFind(k)||["output","in-place","json","software"].canFind(k),"Unknown option for "~cmd.group~" "~cmd.action~": --"~k);
 ModelSnapshot before;if(cmd.edits&&cmd.group!="history"&&c.groupDepth==0)before=c.snapshot();JSONValue result;
 bool temporaryStack=cmd.group!="history";
 if(temporaryStack)incActionPushStack();
 scope(exit)if(temporaryStack)incActionPopStack();
 switch(cmd.group){case "node":result=nodeOps(c,cmd.action,o);break;case "camera":if(cmd.action=="list"){JSONValue[] a;foreach(n;nodes(c.puppet))if(cast(ExCamera)n)a~=json(n);result=JSONValue(a);}else{auto opts=o.dup;opts["type"]="Camera";if(cmd.action!="add")enforce(cast(ExCamera)node(c.puppet,need(o,"node")) !is null,"Expected Camera node");result=nodeOps(c,cmd.action,opts);}break;
 case "project":result=projectOps(c,cmd.action,o);break;case "mesh":result=meshOps(c,cmd.action,o);break;case "param":result=paramOps(c,cmd.action,o);break;case "binding":result=bindingOps(c,cmd.action,o);break;case "key":result=keyOps(c,cmd.action,o);break;case "texture":result=textureOps(c,cmd.action,o);break;case "mask":result=maskOps(c,cmd.action,o);break;case "physics":result=physicsOps(c,cmd.action,o);break;case "automation":result=automationOps(c,cmd.action,o);break;case "animation":result=animationOps(c,cmd.action,o);break;case "render":result=render(c,cmd.action,o);break;case "export":result=exportOps(c,cmd.action,o);break;
 case "scene":if(cmd.action=="set")inSceneAmbientLight=triple(need(o,"ambient-light"));result=JSONValue(["ambientLight":json(inSceneAmbientLight.vector)]);break;
 case "history":switch(cmd.action){
 case "list":result=JSONValue(["index":JSONValue(c.cursor),"count":JSONValue(incActionHistory().length)]);if(flag(o,"details")){JSONValue[] entries;foreach(i,action;incActionHistory())entries~=JSONValue(["index":JSONValue(i+1),"description":JSONValue(action.describe()),"applied":JSONValue(i<c.cursor)]);result["actions"]=JSONValue(entries);}break;
 case "clear":enforce(c.groupDepth==0,"Cannot clear history inside an edit group");incActionClearHistory(ActionStackClear.CurrentLevel);break;
 case "seek":enforce(c.groupDepth==0,"Cannot seek history inside an edit group");auto index=to!size_t(need(o,"index"));enforce(index<=incActionHistory().length,"History index out of range");incActionSetIndex(index);break;
 case "undo":enforce(c.groupDepth==0,"Cannot undo inside an edit group");enforce(incActionCanUndo(),"Nothing to undo");incActionUndo();break;
 case "redo":enforce(c.groupDepth==0,"Cannot redo inside an edit group");enforce(incActionCanRedo(),"Nothing to redo");incActionRedo();break;
 case "begin":if(c.groupDepth++==0){c.groupBefore=c.snapshot();incActionPushGroup();}break;
 case "end":enforce(c.groupDepth>0,"No history group");if(--c.groupDepth==0){c.record(c.groupBefore);incActionPopGroup();}break;
 default:assert(0);}if(cmd.action!="list")result=JSONValue(c.cursor);break;default:assert(0);}
 if(temporaryStack){incActionPopStack();temporaryStack=false;}
 if(before.length){validate(c.puppet);c.record(before,cmd.group~" "~cmd.action);}return result;}
