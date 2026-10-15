module cli.context;
version (InochiCLI):
import inochi2d;
import creator;
import creator.ext;
import creator.actions : Action;
import creator.core.actionstack;
import creator.windows.flipconfig;
import creator.atlas.atlas : incInitAtlassing;
import bindbc.sdl;
import bindbc.opengl;
import std.algorithm;
import std.array;
import std.conv;
import std.exception;
import std.file;
import std.json;
import std.math;
import std.path;
import std.string;
import std.traits : OriginalType;

alias Options = string[string];
string opt(Options o, string name, string fallback="") { auto v=name in o; return v ? *v : fallback; }
bool flag(Options o,string name) { return name in o && opt(o,name)!="false"; }
string need(Options o,string name) { enforce(name in o,"Missing --"~name); return o[name]; }
float number(string s) { float v=to!float(s); enforce(isFinite(v),"Expected finite number: "~s); return v; }
string[] items(string text) {
 if(text.startsWith("@")||text=="-"||text.startsWith("["))return data(text).array.map!(v=>v.type==JSONType.string?v.str:v.toString).array;
 return text.split(',');
}
float[] numbers(string s) { return items(s).map!number.array; }
vec2 pair(string s) { auto a=numbers(s); enforce(a.length==1||a.length==2,"Expected x,y: "~s); return vec2(a[0],a.length==2?a[1]:0); }
vec3 triple(string s) { auto a=numbers(s); enforce(a.length==2||a.length==3,"Expected x,y[,z]"); return vec3(a[0],a[1],a.length==3?a[2]:0); }
JSONValue data(string s) { if(s=="-") { import std.stdio; s=stdin.byLineCopy.join("\n"); } else if(s.startsWith("@"))s=readText(s[1..$]); return parseJSON(s); }
string clean(string s) { return s.stripRight("\0"); }
JSONValue json(ParameterBinding binding) {
    auto buffer=appender!(char[]);auto serializer=inCreateSerializer(buffer);
    binding.serializeSelf(serializer);serializer.flush();return parseJSON(cast(string)buffer.data);
}
JSONValue json(ParameterBinding[] bindings) {JSONValue[] out_;foreach(binding;bindings)out_~=json(binding);return JSONValue(out_);}
JSONValue json(T)(T value) { return parseJSON(inToJson(value)); }
string nodePath(Node n) { return n.parent ? nodePath(n.parent)~"/"~clean(n.name) : clean(n.name); }
Node[] nodes(ExPuppet p) { Node[] a; void visit(Node n) {a~=n;foreach(c;n.children)visit(c);} visit(p.root);return a; }
Node node(ExPuppet p,string ref_) { Node[] found; foreach(n;nodes(p)) if(clean(n.name)==ref_||nodePath(n)==ref_.stripLeft('/')||n.uuid.to!string==ref_)found~=n;
 enforce(found.length>0,"Node not found: "~ref_); enforce(found.length==1,"Ambiguous node: "~ref_~"; candidates: "~found.map!(n=>nodePath(n)~" ("~n.uuid.to!string~")").join(", "));return found[0]; }
string parameterPath(Parameter a){if(auto ex=cast(ExParameter)a)if(ex.parent)return clean(ex.parent.name)~"/"~clean(a.name);return clean(a.name);}
Parameter parameter(ExPuppet p,string ref_) { Parameter[] found;foreach(a;p.parameters)if(clean(a.name)==ref_||parameterPath(a)==ref_.stripLeft('/')||a.uuid.to!string==ref_)found~=a;enforce(found.length>0,"Parameter not found: "~ref_);enforce(found.length==1,"Ambiguous parameter: "~ref_~"; candidates: "~found.map!(a=>parameterPath(a)~" ("~a.uuid.to!string~")").join(", "));return found[0]; }
Drawable drawable(ExPuppet p,string ref_) {auto d=cast(Drawable)node(p,ref_);enforce(d!is null,"Node has no mesh: "~ref_);return d;}
void validate(ExPuppet p) {
 bool[uint] ids;
 foreach(n;nodes(p)) {enforce(!(n.uuid in ids),"Duplicate node UUID"); ids[n.uuid]=true;
  if(auto d=cast(Drawable)n) {auto m=d.getMesh;enforce(m.vertices.length==m.uvs.length,"UV count mismatch: "~clean(n.name));enforce(m.indices.length%3==0,"Invalid triangle list");foreach(i;m.indices)enforce(i<m.vertices.length,"Invalid vertex index");}
 }
 foreach(a;p.parameters) foreach(b;a.bindings) { enforce(b.getNode!is null,"Binding target missing"); if(auto d=cast(DeformationParameterBinding)b) foreach(x;d.values)foreach(v;x)enforce(v.vertexOffsets.size()==(cast(Drawable)b.getNode).vertices.length,"Deformation vertex count mismatch"); }
}
struct ModelSnapshot {
 size_t[2][][uint] meshEdges;
 ubyte[] model;
 bool[uint] pixelSnap;
 vec2[uint] parameterValues;
 bool[uint] parameterActive;
 bool enableDrivers,renderParameters;
 vec3 ambientLight;
 JSONValue previewAnimation;
 double clock;
 @property size_t length(){return model.length;}
}
class Context {
 ExPuppet puppet;
 string input;
 JSONValue previewAnimation;
 size_t[2][][uint] meshEdges;
 @property size_t cursor(){return incActionIndex();}
 size_t groupDepth;
 ModelSnapshot groupBefore;
 this(string path,bool strict=true) {input=path;incInitExt();puppet=path=="new"?new ExPuppet:inLoadPuppet!ExPuppet(path);incSetCLIProject(puppet);incGetFlipPairs();incLoadFlipConfig(puppet);if(strict)validate(puppet);}
 ModelSnapshot snapshot() {
  ModelSnapshot state;foreach(id,edges;meshEdges)state.meshEdges[id]=edges.dup;incDumpFlipConfig(puppet);puppet.populateTextureSlots();state.model=inWriteINPPuppetMemory(puppet);
  foreach(n;nodes(puppet))state.pixelSnap[n.uuid]=n.localTransform.pixelSnap;
  foreach(p;puppet.parameters){state.parameterValues[p.uuid]=p.value;state.parameterActive[p.uuid]=p.active;}
  state.ambientLight=inSceneAmbientLight;state.enableDrivers=puppet.enableDrivers;state.renderParameters=puppet.renderParameters;state.previewAnimation=previewAnimation;state.clock=clockTime;return state;
 }
 void adopt(ExPuppet model) {meshEdges=null;puppet=model;incSetCLIProject(puppet);incGetFlipPairs();incLoadFlipConfig(puppet);}
 void restore(ModelSnapshot state) {
  adopt(inLoadINPPuppet!ExPuppet(state.model));
  foreach(id,edges;state.meshEdges)meshEdges[id]=edges.dup;
  foreach(n;nodes(puppet))if(auto value=n.uuid in state.pixelSnap)n.localTransform.pixelSnap=*value;
  foreach(p;puppet.parameters){if(auto value=p.uuid in state.parameterValues)p.value=*value;if(auto value=p.uuid in state.parameterActive)p.active=*value;}
  inSceneAmbientLight=state.ambientLight;puppet.enableDrivers=state.enableDrivers;puppet.renderParameters=state.renderParameters;previewAnimation=state.previewAnimation;clockTime=state.clock;
 }
 void record(ModelSnapshot before,string name="Edit group") {if(groupDepth)return;incActionPush(new SnapshotAction(this,before,snapshot(),name));}
 void save(string path) {enforce(path.length>0,"Editing requires -o FILE or --in-place");enforce(extension(path)==".inx"||extension(path)==".inp","Output must be .inx or .inp");validate(puppet);auto bytes=snapshot().model;auto temp=path~".tmp-"~to!string(thisProcessID)~".inx";scope(exit)if(exists(temp))remove(temp);write(temp,bytes);auto check=inLoadPuppet!ExPuppet(temp);validate(check);enforce(inToJson(check)==inToJson(puppet),"Saved model did not round-trip");enforce(check.extData.length==puppet.extData.length,"Vendor section count changed");foreach(name,blob;puppet.extData)enforce(name in check.extData && check.extData[name]==blob,"Vendor section changed: "~name);rename(temp,path);}
}
// Native ActionStack owns traversal, redo truncation, grouping and history selection.
// A snapshot action retains fields that the runtime does not serialize into INX.
class SnapshotAction : Action {
 Context context;ModelSnapshot before,after;string name;
 this(Context context,ModelSnapshot before,ModelSnapshot after,string name){this.context=context;this.before=before;this.after=after;this.name=name;}
 void rollback(){context.restore(before);}
 void redo(){context.restore(after);}
 string describe(){return name;}
 string describeUndo(){return name;}
 string getName(){return name;}
 bool merge(Action other){return false;}
 bool canMerge(Action other){return false;}
}

import std.process : thisProcessID;
__gshared double clockTime;
SDL_Window* window;
SDL_GLContext glContext;
void initGL() {
 enforce(loadSDL()!=sdlSupport.noLibrary,"SDL2 unavailable");
 enforce(SDL_Init(SDL_INIT_VIDEO)==0,"SDL init: "~fromStringz(SDL_GetError()).idup);
 // macOS exposes 3.3 features through its forward-compatible 4.1 context.
 version(OSX){enum glMajor=4;enum glMinor=1;}else{enum glMajor=3;enum glMinor=3;}
 SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION,glMajor);SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION,glMinor);SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK,SDL_GL_CONTEXT_PROFILE_CORE);
 version(OSX) SDL_GL_SetAttribute(SDL_GL_CONTEXT_FLAGS,SDL_GL_CONTEXT_FORWARD_COMPATIBLE_FLAG);
 window=SDL_CreateWindow("inochi CLI",0,0,64,64,SDL_WINDOW_OPENGL|SDL_WINDOW_HIDDEN);
 enforce(window!is null,"Cannot create OpenGL window: "~fromStringz(SDL_GetError()).idup);
 glContext=SDL_GL_CreateContext(window);enforce(glContext!is null,"Cannot create OpenGL context: "~fromStringz(SDL_GetError()).idup);
 enforce(loadOpenGL()>=GLSupport.gl33,"OpenGL 3.3 required");
 inInit(&time);incInitAtlassing();inPostProcessingAddBasicLighting();inSetUpdateBounds(true);
}
double time() {return clockTime;}
void closeGL() {if(glContext)SDL_GL_DeleteContext(glContext);if(window)SDL_DestroyWindow(window);SDL_Quit();}
JSONValue referenceMetadata(Options o) {
 auto meta=data("@"~need(o,"reference"));
 if("tiles" in meta){auto tile=pair(need(o,"tile"));foreach(entry;meta["tiles"].array)if(entry["tileX"].get!int==tile.x&&entry["tileY"].get!int==tile.y)return entry;throw new Exception("Render grid tile not found");}
 return meta;
}
vec2 worldPoint(vec2 point,Options o) {
 if(opt(o,"space","local")!="image")return point;
 auto meta=referenceMetadata(o);auto m=meta["sheetPixelToWorld" in meta?"sheetPixelToWorld":"pixelToWorld"].array;
 return vec2(cast(float)(m[0].array[0].get!double*point.x+m[0].array[1].get!double*point.y+m[0].array[2].get!double),cast(float)(m[1].array[0].get!double*point.x+m[1].array[1].get!double*point.y+m[1].array[2].get!double));
}
// Evaluate the coordinate reference pose without persisting preview state.
class CoordinatePose {
 Context context;vec2[] values;bool[] automationEnabled;bool drivers;bool active;
 this(Context context,Options options,Parameter selected=null,vec2u at=vec2u(0)) {
  if(opt(options,"space","local")=="local")return;
  this.context=context;active=true;auto p=context.puppet;drivers=p.enableDrivers;
  foreach(parameter;p.parameters)values~=parameter.value;
  foreach(automation;p.automation){automationEnabled~=automation.enabled;automation.enabled=false;}
  p.enableDrivers=false;
  if(opt(options,"space")=="image"){
   auto metadata=referenceMetadata(options);
   if("parameterStates" in metadata)foreach(row;metadata["parameterStates"].array){auto id=row["uuid"].get!uint;foreach(parameter;p.parameters)if(parameter.uuid==id)parameter.value=pair(row["effective"].toString);}
   else if("parameters" in metadata)foreach(name,value;metadata["parameters"].object)parameter(p,name).value=pair(value.toString);
  }
  if(selected !is null)selected.value=selected.getKeypointValue(at);
  p.update();
 }
 void restore(){if(!active)return;auto p=context.puppet;foreach(i,parameter;p.parameters)parameter.value=values[i];p.update();foreach(i,automation;p.automation)automation.enabled=automationEnabled[i];p.enableDrivers=drivers;active=false;}
}

vec2 localPoint(Drawable d,vec2 p,Options o) {
    auto space=opt(o,"space","local");if(space=="local")return p;
    enforce(space=="world"||space=="image","--space must be local, world or image");
    return (d.transform.matrix.inverse*vec4(worldPoint(p,o),0,1)).xy+d.getMesh.origin;
}

T enumValue(T)(string value) {
    static foreach (name; __traits(allMembers, T)) {
        if (value.toLower==name.toLower || value.toLower==to!string(cast(OriginalType!T)__traits(getMember,T,name)).toLower)
            return __traits(getMember,T,name);
    }
    throw new Exception("Invalid "~T.stringof~": "~value);
}
