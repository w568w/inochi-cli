module cli.merge;
version (InochiCLI):
import cli.context;
import creator.ext;
import creator : incSetCLIProject;
import creator.windows.flipconfig;
import inochi2d;
import std.algorithm;
import std.array;
import std.conv;
import std.exception;
import std.path;

private string uniqueName(string original, ref bool[string] names) {
    auto base=clean(original),candidate=base;
    size_t index=2;
    while(candidate in names)candidate=base~" ("~(index++).to!string~")";
    names[candidate]=true;return candidate;
}
void mergeProject(Context context, string file, Node parent) {
    auto target=context.puppet;
    auto incoming=inLoadPuppet!ExPuppet(file);
    auto oldPairs=incGetFlipPairs().dup;
    incSetCLIProject(incoming);incGetFlipPairs();incLoadFlipConfig(incoming);auto newPairs=incGetFlipPairs().dup;
    incSetCLIProject(target);incGetFlipPairs();incSetFlipPairs(oldPairs);
    bool[uint] ids;
    foreach(n;nodes(target))ids[n.uuid]=true;
    foreach(p;target.parameters)ids[p.uuid]=true;
    foreach(g;target.groups)ids[g.uuid]=true;
    uint remap(uint original){if(!(original in ids)){ids[original]=true;return original;}uint next;do next=inCreateUUID();while(next in ids);ids[next]=true;return next;}
    foreach(n;nodes(incoming))n.forceSetUUID(remap(n.uuid));
    bool[string] parameterNames;
    foreach(p;target.parameters)parameterNames[clean(p.name)]=true;
    foreach(p;incoming.parameters){p.uuid=remap(p.uuid);p.name=uniqueName(p.name,parameterNames);p.makeIndexable();}
    bool[string] groupNames;foreach(g;target.groups)groupNames[clean(g.name)]=true;
    foreach(g;incoming.groups){g.uuid=remap(g.uuid);g.name=uniqueName(g.name,groupNames);}
    foreach(n;nodes(incoming))if(auto driver=cast(SimplePhysics)n)driver.param(driver.param);
    bool[string] children;foreach(child;parent.children)children[clean(child.name)]=true;
    incoming.root.name=uniqueName(stripExtension(baseName(file)),children);
    incoming.root.reparent(parent,parent.children.length);
    target.parameters~=incoming.parameters;target.groups~=incoming.groups;
    bool[string] animationNames;foreach(name;target.getAnimations.keys)animationNames[name]=true;
    foreach(name,animation;incoming.getAnimations)target.getAnimations[uniqueName(name,animationNames)]=animation;
    bool[string] automationNames;foreach(a;target.automation)automationNames[a.name]=true;
    foreach(a;incoming.automation){
        a.name=uniqueName(a.name,automationNames);
        if(auto sine=cast(ExSineAutomation)a)foreach(ref binding;sine.projectBindings)binding.paramId=binding.param.name;
        if(auto physics=cast(ExPhysicsAutomation)a)foreach(ref binding;physics.projectBindings)binding.paramId=binding.param.name;
        a.finalize(target);target.automation~=a;
    }
    foreach(key,blob;incoming.extData){
        if(key==FlipConfigPath)continue;
        enforce(!(key in target.extData)||target.extData[key]==blob,"Conflicting vendor section: "~key);
        target.extData[key]=blob.dup;
    }
    incSetCLIProject(target);incSetFlipPairs(oldPairs~newPairs);
    target.rescanNodes();target.populateTextureSlots();target.updateTextureState();
}
