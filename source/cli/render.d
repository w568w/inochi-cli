module cli.render;
version (InochiCLI):
import cli.context;
import cli.cancellation;
import creator.viewport.common.mesh : IncMesh;
import inochi2d;
import inochi2d.core.animation.player;
import creator.ext;
import creator.windows.imgexport;
import imagefmt;
import std.algorithm;
import std.array;
import std.conv;
import std.exception;
import std.file;
import std.json;
import std.math;
import std.path;
import std.string;
import std.process;

struct Frame {ubyte[] pixels;int width,height;JSONValue meta;}
void pose(Context c,Options o) {
 auto p=c.puppet;
 p.enableDrivers=flag(o,"physics");if("ambient-light" in o)inSceneAmbientLight=triple(o["ambient-light"]);clockTime=0;inUpdate();inUpdate();p.resetDrivers();
 c.previewAnimation=JSONValue(null);
 foreach(a;p.parameters)a.value=a.defaults;
 auto player=new AnimationPlayer(p);
 player.snapToFramerate=flag(o,"snap-to-frames");
 AnimationPlaybackRef playback;
 if(auto name="animation" in o){playback=player.createOrGet(*name);enforce(playback !is null,"Animation not found: "~*name);playback.play(flag(o,"loop")||("loops" in o),true);}
 if("frame" in o){enforce(playback !is null,"--frame requires --animation");auto selected=to!int(o["frame"]);enforce(selected>=0&&selected<playback.frames,"Frame outside animation");playback.seek(selected);playback.pause();}
 void parameters() {
  if(auto settings="param" in o) foreach(s;(*settings).split(';')) {auto i=s.indexOf('=');enforce(i>0,"--param NAME=x,y");auto a=parameter(p,s[0..i]);auto v=pair(s[i+1..$]);enforce(v.x>=a.min.x&&v.x<=a.max.x&&(!a.isVec2||(v.y>=a.min.y&&v.y<=a.max.y)),"Parameter outside range: "~a.name);a.value=v;}
 }
 double seconds=number(opt(o,"time","0"));enforce(seconds>=0,"Time must be nonnegative");
 auto steps=cast(size_t)ceil(seconds*60);enforce(steps<=216000,"Time exceeds one hour");
 parameters();player.prerenderAll();p.update();
 double previous=0;
 foreach(i;0..steps) {checkCancellation();clockTime=min((i+1)/60.0,seconds);inUpdate();parameters();player.update(cast(float)(clockTime-previous));p.update();previous=clockTime;if(playback && "loops" in o && playback.looped>=to!int(o["loops"]))playback.stop(false);}
 if("playback" in o){
  enforce(playback !is null,"--playback requires --animation");
  switch(o["playback"]){
   case "play":if(!playback.playing||playback.paused)playback.play(flag(o,"loop"),true);break;
   case "pause":playback.pause();break;
   case "stop":playback.stop(false);break;
   case "reset":playback.stop(true);break;
   default:throw new Exception("Playback must be play, pause, stop or reset");
  }
  foreach(parameter;p.parameters)parameter.value=parameter.defaults;
  parameters();player.prerenderAll();p.update();
 }
 if(playback)c.previewAnimation=JSONValue(["name":JSONValue(playback.name),"frame":JSONValue(playback.frame),"subframe":JSONValue(playback.hframe),"looped":JSONValue(playback.looped),"looping":JSONValue(playback.looping),"paused":JSONValue(playback.paused),"playing":JSONValue(playback.playing),"stopping":JSONValue(!playback.playing&&playback.isPlayingLeadOut),"leadOut":JSONValue(playback.isPlayingLeadOut)]);
}
vec4 bounds(Context c,Options o) {
 auto root="focus" in o?node(c.puppet,o["focus"]):c.puppet.root;
 auto isolated="isolate" in o?node(c.puppet,o["isolate"]):null;
 vec4 result=vec4(float.max,float.max,-float.max,-float.max);bool found;
 foreach(n;nodes(c.puppet)) if(auto part=cast(Part)n){
  bool inside=n is root,visible=n.enabled;auto parent=n.parent;
  while(parent){inside|=parent is root;visible&=parent.enabled;parent=parent.parent;}
  if(!inside||!visible)continue;
  if(isolated !is null){bool included=n is isolated;auto ancestor=n.parent;while(ancestor){included|=ancestor is isolated;ancestor=ancestor.parent;}if(!included)continue;}
  foreach(i,v;part.vertices){auto point=(part.getDynamicMatrix*vec4(v+part.deformation[i]-part.getMesh.origin,0,1)).xy;result.x=min(result.x,point.x);result.y=min(result.y,point.y);result.z=max(result.z,point.x);result.w=max(result.w,point.y);found=true;}
 }
 if(!found)result=root.getCombinedBounds;
 enforce(result.z>result.x&&result.w>result.y,"Empty render bounds");return result;
}
Frame frame(Context c,Options o,vec4 area=vec4(float.nan)) {
 auto p=c.puppet;
 bool[] original;
 if(auto s="isolate" in o) {auto n=node(p,*s);foreach(v;nodes(p)){original~=v.enabled;bool within=v is n;auto t=v;while(t.parent){t=t.parent;within|=t is n;}bool ancestor=false;t=n;while(t.parent){t=t.parent;ancestor|=v is t;}v.enabled&=within||ancestor;}}
 scope(exit)if(original.length)foreach(i,n;nodes(p))n.enabled=original[i];
 if(isNaN(area.x))area=bounds(c,o);
 if(auto custom="bounds" in o){auto a=numbers(*custom);enforce(a.length==4,"--bounds x0,y0,x1,y1");area=vec4(a[0],a[1],a[2],a[3]);}
 auto padding=number(opt(o,"padding","0.05"));enforce(padding>=0,"Padding must be nonnegative");
 auto center=(area.xy+area.zw)/2;auto size=area.zw-area.xy;size*=1+2*padding;
 int width,height;float scale;
 if(auto requested="size" in o){auto v=pair(*requested);width=cast(int)v.x;height=cast(int)v.y;scale=min(width/size.x,height/size.y);}
 else {auto edge=to!int(opt(o,"max-size","1024"));scale=edge/max(size.x,size.y);width=max(1,cast(int)round(size.x*scale));height=max(1,cast(int)round(size.y*scale));}
 enforce(width>0&&height>0&&width<=16384&&height<=16384,"Image size must be 1..16384");
 Camera cam;
 if(auto ref_="camera" in o){auto camera=cast(ExCamera)node(p,*ref_);enforce(camera!is null,"Expected Camera node");cam=camera.getCamera;auto vp=camera.getViewport;width=cast(int)vp.x;height=cast(int)vp.y;}
 else {cam=new Camera;cam.position=-center;cam.scale=vec2(scale);}
 enforce(width>0&&height>0&&width<=16384&&height<=16384,"Camera viewport must be 1..16384");
 if(auto value="zoom" in o){auto zoom=number(*value);enforce(zoom>0,"Zoom must be positive");cam.scale=vec2(zoom);}
 if(auto value="view-center" in o)cam.position=-pair(*value);
 if(flag(o,"mirror-view"))cam.scale.x=-cam.scale.x;
 inSetCamera(cam);inSetViewport(width,height);vec4 bg=vec4(0);if(auto color="background" in o){auto a=numbers(*color);enforce(a.length==4,"Background requires r,g,b,a");bg=vec4(a[0],a[1],a[2],a[3]);}inSetClearColor(bg.r,bg.g,bg.b,bg.a);
 inBeginScene();p.draw();inEndScene();if(flag(o,"postprocess"))inPostProcessScene();
 Frame f;f.width=width;f.height=height;f.pixels=new ubyte[inViewportDataLength()];inDumpViewport(f.pixels);
 // SDK texture dumps are premultiplied; PNG consumers expect straight alpha.
 foreach(i;0..f.pixels.length/4){auto a=f.pixels[4*i+3];if(a&&a<255)foreach(j;0..3)f.pixels[4*i+j]=cast(ubyte)min(255u,(cast(uint)f.pixels[4*i+j]*255+a/2)/a);}
 auto matrix=cam.matrix;
 double ax=cast(double)matrix[0][0]*width/2, bx=cast(double)matrix[0][1]*width/2, zx=(cast(double)matrix[0][3]+1)*width/2;
 double ay=-cast(double)matrix[1][0]*height/2, by=-cast(double)matrix[1][1]*height/2, zy=(1-cast(double)matrix[1][3])*height/2;
 vec2 project(vec2 w){return vec2(cast(float)(ax*w.x+bx*w.y+zx),cast(float)(ay*w.x+by*w.y+zy));}
 JSONValue[] rows=[JSONValue([JSONValue(ax),JSONValue(bx),JSONValue(zx)]),JSONValue([JSONValue(ay),JSONValue(by),JSONValue(zy)]),JSONValue([JSONValue(0),JSONValue(0),JSONValue(1)])];
 auto det=ax*by-ay*bx;enforce(std.math.abs(det)>1e-10,"Singular render camera");
 JSONValue[] inverse=[JSONValue([JSONValue(by/det),JSONValue(-bx/det),JSONValue((bx*zy-by*zx)/det)]),JSONValue([JSONValue(-ay/det),JSONValue(ax/det),JSONValue((ay*zx-ax*zy)/det)]),JSONValue([JSONValue(0),JSONValue(0),JSONValue(1)])];
 f.meta=JSONValue(["width":JSONValue(width),"height":JSONValue(height),"worldToPixel":JSONValue(rows),"pixelToWorld":JSONValue(inverse),"parameters":JSONValue(string[string].init),"vertices":JSONValue(JSONValue[].init)]);
 JSONValue[] parameterStates;
 foreach(a;p.parameters){f.meta["parameters"][clean(a.name)]=json(a.value.vector);parameterStates~=JSONValue(["uuid":JSONValue(a.uuid),"name":JSONValue(clean(a.name)),"value":json(a.value.vector),"effective":json(a.lastInternal.vector)]);}
 f.meta["parameterStates"]=JSONValue(parameterStates);
 f.meta["animation"]=c.previewAnimation;
 f.meta["advancedBlending"]=JSONValue(inIsAdvancedBlendMode(BlendMode.Multiply));
 JSONValue[] corners;
 foreach(q;[vec2(0,0),vec2(width,0),vec2(width,height),vec2(0,height)]){auto world=vec2(cast(float)((by*q.x-bx*q.y+bx*zy-by*zx)/det),cast(float)((-ay*q.x+ax*q.y+ay*zx-ax*zy)/det));corners~=json(world.vector);}
 f.meta["viewportCornersWorld"]=JSONValue(corners);f.meta["bounds"]=json(area.vector);
 void dot(int px,int py,ubyte r,ubyte g,ubyte b) {if(px>=0&&py>=0&&px<width&&py<height){auto i=(py*width+px)*4;f.pixels[i..i+4]=[r,g,b,cast(ubyte)255];}}
 void label(int px,int py,string text){
  immutable glyphs=["111101101101111","010110010010111","111001111100111","111001111001111","101101111001001","111100111001111","111100111101111","111001001001001","111101111101111","111101111001111"];
  foreach(ch;text){if(ch>='0'&&ch<='9')foreach(y;0..5)foreach(x;0..3)if(glyphs[ch-'0'][y*3+x]=='1')dot(px+x,py+y,255,30,100);px+=4;}
 }
 void line(vec2 a,vec2 b,ubyte r=0,ubyte g=220,ubyte blue=255){int count=cast(int)max(std.math.abs(b.x-a.x),std.math.abs(b.y-a.y))+1;foreach(i;0..count){auto q=a+(b-a)*(cast(float)i/count);dot(cast(int)q.x,cast(int)q.y,r,g,blue);}}
 JSONValue[] verts;
 auto target="isolate" in o?node(p,o["isolate"]):"focus" in o?node(p,o["focus"]):p.root;
 foreach(n;nodes(p))if(auto d=cast(Drawable)n){bool inside=d is target;auto t=cast(Node)d;while(t.parent){t=t.parent;inside|=t is target;}bool visible=n.enabled;auto ancestor=n.parent;while(ancestor){visible&=ancestor.enabled;ancestor=ancestor.parent;}if(!inside||!visible)continue;vec2[] positions;
  foreach(i,v;d.vertices){auto world=(d.getDynamicMatrix*vec4(v+d.deformation[i]-d.getMesh.origin,0,1)).xy;auto pixel=project(world);positions~=pixel;verts~=JSONValue(["node":JSONValue(d.uuid),"index":JSONValue(i),"world":json(world.vector),"pixel":json(pixel.vector)]);if(flag(o,"vertices")){label(cast(int)pixel.x+4,cast(int)pixel.y-2,i.to!string);}if(flag(o,"vertices"))foreach(dx;-2..3)foreach(dy;-2..3)dot(cast(int)pixel.x+dx,cast(int)pixel.y+dy,255,30,100);}
  if(flag(o,"mesh")){
   auto edges=d.uuid in c.meshEdges;
   if(edges&&!flag(o,"triangulate")){foreach(edge;*edges)line(positions[edge[0]],positions[edge[1]]);}
   else {auto indices=flag(o,"triangulate")?(new IncMesh(d.getMesh)).autoTriangulate().export_().indices:d.getMesh.indices;foreach(i;0..indices.length/3)foreach(j;0..3)line(positions[indices[3*i+j]],positions[indices[3*i+(j+1)%3]]);}
  }
 }
 JSONValue[] guides;
 if(flag(o,"overlay-bounds")||flag(o,"orientation"))foreach(n;nodes(p)){
  bool included=n is target;auto parent=n.parent;while(parent){included|=parent is target;parent=parent.parent;}if(!included)continue;
  if(flag(o,"overlay-bounds")){auto box=n.getCombinedBounds;auto a=project(box.xy),b=project(vec2(box.z,box.y)),d=project(box.zw),e=project(vec2(box.x,box.w));line(a,b,240,200,30);line(b,d,240,200,30);line(d,e,240,200,30);line(e,a,240,200,30);guides~=JSONValue(["node":JSONValue(n.uuid),"boundsWorld":json(box.vector)]);}
  if(flag(o,"orientation")){auto nodeMatrix=n.transform.matrix;auto origin=project((nodeMatrix*vec4(0,0,0,1)).xy),x=project((nodeMatrix*vec4(32,0,0,1)).xy),y=project((nodeMatrix*vec4(0,-32,0,1)).xy),z=project((nodeMatrix*vec4(0,0,32,1)).xy);line(origin,x,255,60,60);line(origin,y,60,255,60);line(origin,z,60,60,255);guides~=JSONValue(["node":JSONValue(n.uuid),"originPixel":json(origin.vector),"xAxisPixel":json(x.vector),"yAxisPixel":json(y.vector),"zAxisPixel":json(z.vector)]);}
 }
 f.meta["guides"]=JSONValue(guides);
 f.meta["triangulationPreview"]=JSONValue(flag(o,"triangulate"));
 f.meta["vertices"]=JSONValue(verts);
 if(flag(o,"creator-reference")){
  auto reference=new ExCamera(vec2(width,height));reference.name="CLI reference camera";reference.localTransform.translation=vec3(-cam.position,0);reference.localTransform.rotation.z=-cam.rotation;reference.localTransform.scale=vec2(1/cam.scale.x,1/cam.scale.y);reference.reparent(p.root,0);p.rescanNodes();
  auto path=stripExtension(need(o,"output"))~".creator.png";auto exporter=new ImageExportWindow(path);exporter.exportCLI(reference,bg.a==0,flag(o,"postprocess"));reference.reparent(null,0);p.rescanNodes();f.meta["creatorReference"]=JSONValue(path);
 }
 return f;
}
void writePixels(string path,int width,int height,ubyte[] pixels,int channels=4){
 if(extension(path).toLower==".jpg"||extension(path).toLower==".jpeg"){
  auto rgba=new ubyte[width*height*4];foreach(i;0..width*height){auto a=channels==4?pixels[i*4+3]:255;foreach(j;0..3){auto v=pixels[i*channels+(channels<3?0:j)];rgba[i*4+j]=cast(ubyte)((cast(uint)v*a+255u*(255-a))/255);}rgba[i*4+3]=255;}
  auto encoder=pipeProcess(["ffmpeg","-loglevel","error","-y","-f","rawvideo","-pixel_format","rgba","-video_size",width.to!string~"x"~height.to!string,"-i","pipe:0","-frames:v","1","-q:v","2",path],Redirect.stdin);
  encoder.stdin.rawWrite(rgba);encoder.stdin.close();enforce(wait(encoder.pid)==0,"JPEG encoding failed");
 }else enforce(write_image(path,width,height,pixels,channels)==0,"Image export failed: "~path);
}
void writeFrame(Frame f,string path){enforce(path.length>0,"Rendering requires -o FILE");writePixels(path,f.width,f.height,f.pixels);write(setExtension(path,".json"),f.meta.toPrettyString~"\n");}
JSONValue render(Context c,string action,Options o){auto original=c.snapshot();scope(exit)c.restore(original);
 if(action!="grid"){pose(c,o);auto f=frame(c,o);writeFrame(f,need(o,"output"));return JSONValue(["image":JSONValue(absolutePath(o["output"])),"metadata":JSONValue(absolutePath(setExtension(o["output"],".json")))]);}
 auto p=parameter(c.puppet,need(o,"param"));enforce(p.isVec2,"Grid requires 2D parameter");auto values=numbers(opt(o,"values","-1,0,1"));enforce(values.length>0&&values.length<=16,"Grid needs 1..16 values");auto name=p.name;
 vec4 combined=vec4(float.max,float.max,-float.max,-float.max);
 foreach(y;values)foreach(x;values){c.restore(original);auto options=o.dup;options["param"]=name~"="~x.to!string~","~y.to!string;pose(c,options);auto b=bounds(c,options);combined=vec4(min(combined.x,b.x),min(combined.y,b.y),max(combined.z,b.z),max(combined.w,b.w));}
 Frame sheet;JSONValue[] tiles;
 foreach(iy,y;values)foreach(ix,x;values){c.restore(original);auto options=o.dup;options["param"]=name~"="~x.to!string~","~y.to!string;pose(c,options);auto f=frame(c,options,combined);
  if(!sheet.pixels.length){sheet.width=f.width*cast(int)values.length;sheet.height=f.height*cast(int)values.length;sheet.pixels=new ubyte[sheet.width*sheet.height*4];}
  foreach(row;0..f.height){auto start=((iy*f.height+row)*sheet.width+ix*f.width)*4;sheet.pixels[start..start+f.width*4]=f.pixels[row*f.width*4..(row+1)*f.width*4];}
  f.meta["tileX"]=JSONValue(ix);f.meta["tileY"]=JSONValue(iy);
  auto offsetX=ix*f.width,offsetY=iy*f.height;
  auto forward=parseJSON(f.meta["worldToPixel"].toString),inverse=parseJSON(f.meta["pixelToWorld"].toString);
  forward[0][2]=JSONValue(forward[0][2].get!double+offsetX);forward[1][2]=JSONValue(forward[1][2].get!double+offsetY);
  inverse[0][2]=JSONValue(inverse[0][2].get!double-inverse[0][0].get!double*offsetX-inverse[0][1].get!double*offsetY);inverse[1][2]=JSONValue(inverse[1][2].get!double-inverse[1][0].get!double*offsetX-inverse[1][1].get!double*offsetY);
  f.meta["sheetWorldToPixel"]=forward;f.meta["sheetPixelToWorld"]=inverse;
  tiles~=f.meta;
 }
 sheet.meta=JSONValue(["width":JSONValue(sheet.width),"height":JSONValue(sheet.height),"tiles":JSONValue(tiles)]);writeFrame(sheet,need(o,"output"));return JSONValue(["image":JSONValue(absolutePath(o["output"])),"tiles":JSONValue(tiles.length)]);
}
