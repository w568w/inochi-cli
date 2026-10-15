module cli.main;
version (InochiCLI) {
import cli.context;
import cli.cancellation;
import cli.registry;
import cli.outputs;
import std.stdio;
import std.json;
import std.string;
import std.array;
import std.algorithm;
import std.conv;
import std.exception;
import std.path;
import std.process;
import std.file : thisExePath;
import creator.core.actionstack;
int main(string[] args){try{
 auto all=commands();
 if(args.length==1||args[1]=="--help"||args[1]=="help"){writeln("inochi MODEL GROUP ACTION [--option=value] [-o FILE]\ninochi MODEL render [-o IMAGE]\ninochi MODEL batch edits.json [-o FILE]\ninochi capabilities --json\nUse MODEL=new to create a project.");foreach(c;all)writeln(c.group," ",c.action,"  ",c.description,"\n  ",c.options);return 0;}
 if(args[1]=="capabilities"){JSONValue[] list;foreach(c;all)list~=JSONValue(["command":JSONValue(c.group~" "~c.action),"edits":JSONValue(c.edits),"options":JSONValue(c.options.split(' ')),"description":JSONValue(c.description)]);writeln(JSONValue(["creator":JSONValue("v0.8.6"),"sdk":JSONValue("v0.8.6"),"commands":JSONValue(list),"batchSchema":batchSchema()]).toPrettyString);return 0;}
 enforce(args.length>=3,"Expected model and command");string model=args[1],group=args[2],action;size_t index=3;
 if(group=="render") {action="image";if(index<args.length&&!args[index].startsWith('-'))action=args[index++];}
 else if(group=="batch"){enforce(index<args.length,"Expected batch file");action=args[index++];}
 else {enforce(index<args.length,"Expected operation");action=args[index++];}
 Options o;
 while(index<args.length){auto token=args[index++];if(token=="-o")token="--output";enforce(token.startsWith("--"),"Unexpected argument: "~token);token=token[2..$];auto eq=token.indexOf('=');string k,v;if(eq>=0){k=token[0..eq];v=token[eq+1..$];}else{k=token;v=index<args.length&&!args[index].startsWith("--")&&args[index]!="-o"?args[index++]:"true";}if(k=="param"&&k in o)o[k]~=";"~v;else o[k]=v;}
 if(flag(o,"help")){if(group=="batch"){writeln("Batch is a JSON array of {command: 'group action', options: {...}}. Options match the command catalog; values may be strings, numbers, booleans or arrays. Use '-' to read stdin. Operations run in order, with one model load. Failure reports a zero-based operation index and publishes no outputs. See capabilities --json for the generated JSON Schema.");return 0;}command(group,action);foreach(c;all)if(c.group==group&&c.action==action)writeln(c.description,"\nOptions: ",c.options);return 0;}
 version(linux) if(environment.get("DISPLAY").length==0||flag(o,"software")) {
  auto child=["xvfb-run","-a",thisExePath(),model,group,action];
  o["software"]="false";foreach(key,value;o)child~="--"~key~"="~value;
  auto env=environment.toAA();env["SDL_VIDEODRIVER"]="x11";env["LIBGL_ALWAYS_SOFTWARE"]="1";
  return wait(spawnProcess(child,env));
 }
 if("output" in o && model!="new" && !flag(o,"in-place"))enforce(absolutePath(o["output"])!=absolutePath(model),"Overwriting input requires --in-place");
 JSONValue operations;bool recovery=group=="project"&&(action=="repair"||action=="regenerate-ids");
 if(group=="batch"){
  operations=data(action=="-"?"-":"@"~action);
  if(operations.array.length){auto first=operations.array[0];if(first.type==JSONType.object&&"command" in first&&first["command"].type==JSONType.string)recovery=first["command"].str=="project repair"||first["command"].str=="project regenerate-ids";}
 }
 initCancellation();
 initGL();scope(exit)closeGL();incActionInit();auto c=new Context(model,!recovery);JSONValue result;bool edited;
 auto outputs=new OutputTransaction(model,flag(o,"in-place"));scope(exit)outputs.cleanup();
 Options prepare(Command cmd,Options source){
  auto options=source.dup;
  foreach(ref value;options){
   if(value.startsWith("@"))value="@"~outputs.readPath(value[1..$]);
  }
  foreach(key;["file","reference"])if(key in options)options[key]=outputs.readPath(options[key]);
  if(cmd.group=="render"||cmd.group=="export"||(cmd.group=="texture"&&cmd.action=="export"))options["output"]=outputs.stage(need(options,"output"));
  return options;
 }
 if(group=="batch"){
  auto batch=operations;JSONValue[] results;
  foreach(i,item;batch.array){try{
   foreach(key,value;item.object)enforce(key=="command"||key=="options","Unknown batch field: "~key);
   auto parts=item["command"].str.split(' ');enforce(parts.length==2,"Batch command must be 'group action'");auto cmd=command(parts[0],parts[1]);Options options;
   if("options" in item)foreach(k,v;item["options"].object)options[k]=v.type==JSONType.string?v.str:v.type==JSONType.array&&(["offsets","data","from","mapping","stroke","polygon","nodes","vertices","connect-to"].canFind(k)||(k=="to"&&parts[0]=="mesh"))?v.toString:v.type==JSONType.array?v.array.map!(x=>x.type==JSONType.string?x.str:x.toString).join(','):v.toString;
   checkCancellation();auto prepared=prepare(cmd,options);results~=execute(c,cmd,prepared);edited|=cmd.edits;
   if(cmd.group=="project"&&cmd.action=="save"&&"output" in options)c.save(outputs.stage(options["output"]));
  }catch(Throwable e){throw new Exception("Batch operation "~i.to!string~": "~e.msg);}}
  enforce(c.groupDepth==0,"Unclosed history group");result=JSONValue(results);
 }else{auto cmd=command(group,action);result=execute(c,cmd,prepare(cmd,o));edited=cmd.edits;}
 checkCancellation();
 if(edited)c.save(outputs.stage(flag(o,"in-place")?model:opt(o,"output")));
 checkCancellation();
 outputs.commit(result);
 if(flag(o,"json"))writeln(result.toPrettyString);
 else if(edited)writeln("Saved ",absolutePath(flag(o,"in-place")?model:opt(o,"output")));
 else if(group=="node"&&action=="list")foreach(n;result.array)writeln(n["uuid"].toString,"  ",n["type"].str,"  ",n["path"].str);
 else if(group=="param"&&action=="list")foreach(p;result.array)writeln(p["uuid"].toString,"  ",p["name"].str,"  ",p["is_vec2"].get!bool?"2D":"1D");
 else writeln(result.toPrettyString);
 return 0;
 }catch(Throwable e){stderr.writeln("inochi: ",e.msg);return cancellationSignal()?128+cancellationSignal():1;}}
}
