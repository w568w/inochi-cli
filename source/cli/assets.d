module cli.assets;
version (InochiCLI):
import cli.context;
import cli.cancellation;
import cli.merge : mergeProject;
import cli.render;
import creator;
import creator.ext;
import creator.io.psd;
import creator.io.kra;
import creator.windows.psdmerge;
import creator.windows.kramerge;
import creator.io.inpexport;
import creator.io.videoexport;
import creator.core.colorbleed;
import bindbc.opengl;
import creator.panels.inspector : incApplyTextureToSlot;
import creator.utils.repair;
import inochi2d;
import inochi2d.core.animation.player;
import imagefmt;
import std.algorithm;
import std.array;
import std.conv;
import std.exception;
import std.file;
import std.json;
import std.path;
import std.string;
import std.math;

Texture loadTexture(string path){auto texture=ShallowTexture(path);inTexPremultiply(texture.data,texture.channels);return new Texture(texture);}
JSONValue textureOps(Context c,string action,Options o){auto p=c.puppet;
 if(action=="list"){p.populateTextureSlots();JSONValue[] result;foreach(i,t;p.textureSlots)result~=JSONValue(["slot":JSONValue(i),"width":JSONValue(t.width),"height":JSONValue(t.height),"channels":JSONValue(t.channels)]);
 if(flag(o,"runtime"))foreach(i,t;p.textureSlots){t.bind();GLint minFilter,magFilter,mipWidth;glGetTexParameteriv(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,&minFilter);glGetTexParameteriv(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,&magFilter);glGetTexLevelParameteriv(GL_TEXTURE_2D,1,GL_TEXTURE_WIDTH,&mipWidth);result[i]["minFilter"]=JSONValue(minFilter);result[i]["magFilter"]=JSONValue(magFilter);result[i]["mip1Width"]=JSONValue(mipWidth);}
return JSONValue(result);}
 if(action=="mipmaps"){incRegenerateMipmaps();return JSONValue(p.textureSlots.length);}
 if(action=="bleed"||action=="premultiply"){
  auto iterations=to!int(opt(o,"radius","32"));enforce(iterations>=0,"Bleed iterations must be nonnegative");
  foreach(t;p.textureSlots)if(t.channels==4){
   if(action=="bleed")incColorBleedPixels(t,iterations);
   else {auto bytes=t.getTextureData();inTexPremultiply(bytes,t.channels);t.setData(bytes);}
  }
  return JSONValue(p.textureSlots.length);
 }
 auto part=cast(Part)node(p,need(o,"node"));enforce(part!is null,"Texture requires Part");auto slot=to!size_t(opt(o,"slot","0"));enforce(slot<part.textures.length,"Invalid texture slot");
 if(action=="load")incApplyTextureToSlot(part,cast(TextureUsage)slot,need(o,"file"));
 else if(action=="remove")part.textures[slot]=null;
 else if(action=="emissive"){
  enforce(part.textures[slot] !is null,"Empty texture slot");
  auto source=part.textures[slot];part.textures[TextureUsage.Emissive]=new Texture(ShallowTexture(source.getTextureData(true),source.width,source.height,source.channels,3));
 }
 else if(action=="export"){auto t=part.textures[slot];enforce(t!is null,"Empty texture slot");auto bytes=t.getTextureData(true);writePixels(need(o,"output"),t.width,t.height,bytes,t.channels);}
 else throw new Exception("Unknown texture operation");p.populateTextureSlots();p.updateTextureState();return json(part);
}
void configureMerge(T)(Context context,T window,Options options) {
 if(auto mapping="mapping" in options)foreach(row;data(*mapping).array){
  auto layer=row["layer"].str;
  if("unmap" in row&&row["unmap"].get!bool)window.mapCLI(layer,context.puppet.root,false,"ignore" in row&&row["ignore"].get!bool);
  else if("node" in row)window.mapCLI(layer,node(context.puppet,row["node"].str),"replace" in row&&row["replace"].get!bool,"ignore" in row&&row["ignore"].get!bool);
  else {enforce("ignore" in row,"Mapping requires node, unmap or ignore");window.ignoreCLI(layer,row["ignore"].get!bool);}
 }
}
JSONValue projectOps(Context c,string action,Options o){auto p=c.puppet;
 if(action=="inspect")return json(p);
 if(action=="check"){validate(p);return JSONValue(["nodes":JSONValue(nodes(p).length),"parameters":JSONValue(p.parameters.length),"textures":JSONValue(p.textureSlots.length)]);}
 if(action=="save"||action=="new")return JSONValue("Model ready to save");
 if(action=="meta"){if(auto v="name" in o)p.meta.name=*v;if(auto v="artist" in o)p.meta.artist=*v;if(auto v="rigger" in o)p.meta.rigger=*v;if(auto v="copyright" in o)p.meta.copyright=*v;if(auto v="license" in o)p.meta.licenseURL=*v;if(auto v="contact" in o)p.meta.contact=*v;if(auto v="reference" in o)p.meta.reference=*v;if(auto v="thumbnail" in o)p.meta.thumbnailId=to!uint(*v);if(auto v="preserve-pixels" in o)p.meta.preservePixels=to!bool(*v);p.updateTextureState();return json(p.meta);}
 if(action=="repair"){incAttemptRepairPuppet(p);return json(p);}
 if(action=="regenerate-ids"){incRegenerateNodeIDs(p.root);return json(p);}
 if(action=="layer-names"){foreach(n;nodes(p))if(auto part=cast(ExPart)n)part.layerPath="/"~clean(n.name);return json(p);}
 if(action=="import-session"){auto incoming=inLoadPuppet!ExPuppet(need(o,"file"));auto key="com.inochi2d.inochi-session.bindings";enforce(key in incoming.extData,"No Inochi Session bindings in source model");p.extData[key]=incoming.extData[key].dup;return JSONValue(key);}
 if(action=="import"){auto file=need(o,"file");switch(extension(file)){case ".psd":incImportPSD(file,IncPSDImportSettings(flag(o,"keep-structure")));break;case ".kra":incImportKRA(file,IncKRAImportSettings(flag(o,"keep-structure")));break;case ".inx", ".inp":incSetCLIProject(inLoadPuppet!ExPuppet(file));break;default:if(isDir(file))incImportFolder(file);else {auto next=new ExPuppet;incSetCLIProject(next);auto part=incCreateExPart(loadTexture(file),next.root,baseName(file));next.populateTextureSlots();}break;}c.adopt(cast(ExPuppet)incActivePuppet());return json(c.puppet);}
 if(action=="merge-plan"){
  auto file=need(o,"file");
  if(extension(file)==".psd"){auto window=new PSDMergeWindow(file);configureMerge(c,window,o);return window.planCLI(opt(o,"layer-filter"),opt(o,"node-filter"),flag(o,"unmapped-only"));}
  if(extension(file)==".kra"){auto window=new KRAMergeWindow(file);configureMerge(c,window,o);return window.planCLI(opt(o,"layer-filter"),opt(o,"node-filter"),flag(o,"unmapped-only"));}
  throw new Exception("Merge plans require PSD or KRA");
 }
 if(action=="merge"){enforce(!flag(o,"resort"),"Re-sort is unimplemented in Creator v0.8.6");auto file=need(o,"file");if(extension(file)==".psd"){auto merge=new PSDMergeWindow(file);configureMerge(c,merge,o);merge.applyCLI(flag(o,"rename"),flag(o,"retranslate"),flag(o,"resort"),flag(o,"unmapped-only"));return json(p);}if(extension(file)==".kra"){auto merge=new KRAMergeWindow(file);configureMerge(c,merge,o);merge.applyCLI(flag(o,"rename"),flag(o,"retranslate"),flag(o,"resort"),flag(o,"unmapped-only"));return json(p);}if(extension(file)==".inx"||extension(file)==".inp"){auto parent="parent" in o?node(p,o["parent"]):p.root;mergeProject(c,file,parent);return json(p);}auto part=incCreateExPart(loadTexture(file),"parent" in o?node(p,o["parent"]):p.root,baseName(file));p.rescanNodes();p.populateTextureSlots();p.updateTextureState();return json(part);}
 throw new Exception("Unknown project operation");
}
IncINPExportSettings atlasSettings(Options o){
 IncINPExportSettings s;s.atlasResolution=to!size_t(opt(o,"resolution","2048"));s.scale=number(opt(o,"scale","1"));s.padding=to!int(opt(o,"padding","16"));s.nonLinearScaling=flag(o,"nonlinear");s.optimizePruneUnused=!flag(o,"keep-unused");if(auto v="watermark" in o)s.decorateWatermark=loadTexture(*v);s.decorateWatermarkOpacity=number(opt(o,"watermark-opacity","1"));s.decorateWatermarkLoops=to!uint(opt(o,"watermark-loops","10"));s.decorateWatermarkBlendMode=enumValue!BlendMode(opt(o,"watermark-blend","ClipToLower"));enforce(s.atlasResolution>=128&&s.atlasResolution<=16384&&s.scale>0&&s.padding>=0,"Invalid atlas settings");return s;
}
JSONValue exportOps(Context c,string action,Options o){auto path=need(o,"output");
 if(action=="image")return render(c,"image",o);
 if(action=="inp"||action=="atlas-preview"){
 auto s=atlasSettings(o);
 if(action=="atlas-preview"){auto preview=incINPExportGenPreview(c.puppet,s);auto texture=preview.preview;writePixels(path,texture.width,texture.height,texture.getTextureData(true),texture.channels);auto meta=JSONValue(["image":JSONValue(absolutePath(path)),"width":JSONValue(texture.width),"height":JSONValue(texture.height),"outputScale":JSONValue(preview.outputScale)]);write(setExtension(path,".json"),meta.toPrettyString~"\n");return meta;}
 incINPExport(c.puppet,s,path);auto check=inLoadPuppet!ExPuppet(path);validate(check);return JSONValue(path);}
 if(action=="video"){auto original=c.snapshot();scope(exit)c.restore(original);auto fps=opt(o,"fps")=="auto"?0:to!int(opt(o,"fps","60")),frames=to!int(opt(o,"frames","60"));
 if("loops" in o||fps<=0||opt(o,"fps")=="auto"){
  auto player=new AnimationPlayer(c.puppet);auto playback=player.createOrGet(need(o,"animation"));enforce(playback !is null,"Animation not found");
  if(fps<=0)fps=playback.fps;
  if("loops" in o){auto loops=to!int(o["loops"]);enforce(loops>0,"Loop count must be positive");auto factor=cast(float)fps/playback.fps;frames=cast(int)ceil(playback.loopPointBegin*factor)+cast(int)ceil((playback.loopPointEnd-playback.loopPointBegin)*factor)*loops+cast(int)ceil((playback.frames-playback.loopPointEnd)*factor);}
 }
 enforce(fps>0&&fps<=240&&frames>0,"Invalid video rate or frames");auto settings=o.dup;settings["time"]="0";pose(c,settings);auto region=bounds(c,settings);auto first=frame(c,settings,region);VideoExportSettings v;v.codec=opt(o,"codec","libx264");v.framerate=fps;v.frames=frames;v.file=path;v.width=first.width;v.height=first.height;v.transparency=flag(o,"transparent");v.ffmpegOptions=opt(o,"ffmpeg-options","");auto encoder=incVideoExport(v);scope(failure)encoder.cancelCLI();foreach(i;0..frames){checkCancellation();c.restore(original);settings["time"]=(cast(double)i/fps).to!string;pose(c,settings);auto f=frame(c,settings,region);encoder.encodeFrame(f.pixels);}enforce(encoder.finishCLI()==0,"FFmpeg export failed");return JSONValue(path);}
 throw new Exception("Unknown export operation");
}
