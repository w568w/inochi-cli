module cli.outputs;
version (InochiCLI):
import std.algorithm;
import std.array;
import std.conv;
import std.exception;
import std.file;
import std.json;
import std.path;
import std.string;
import std.uuid : randomUUID;

private extern(C) bool inochiSameFile(const char*, const char*);

private string absoluteName(string name) {return buildNormalizedPath(absolutePath(name));}
private bool sameFile(string first,string second) {return inochiSameFile(first.toStringz,second.toStringz);}
private bool present(string name) {if(exists(name))return true;try{return isSymlink(name);}catch(FileException){return false;}}

// Files are produced privately, prepared on each destination filesystem, then
// published together. Existing files remain recoverable until publication ends.
class OutputTransaction {
    private struct Directory {string stage, destination;}
    private struct Publication {string source,destination,prepared,backup;bool backedUp,published;}
    private string root;
    private string protectedInput;
    private bool allowInput;
    private Directory[] directories;
    private string[] temporaryDirectories;
    private Publication[] publications;
    private string[string] aliases;
    this(string input, bool inPlace) {
        protectedInput=input=="new"?"":absoluteName(input);allowInput=inPlace;
        root=buildPath(tempDir(),"inochi-outputs-"~randomUUID().toString());mkdir(root);
    }
    void cleanup() {
        foreach(ref p;publications){if(p.prepared.length&&exists(p.prepared))remove(p.prepared);}
        foreach(dir;temporaryDirectories)if(exists(dir)&&dirEntries(dir,SpanMode.shallow).empty)rmdir(dir);
        if(root.length&&exists(root))rmdirRecurse(root);
    }
    string stage(string destination) {
        enforce(destination.length>0,"Output path cannot be empty");destination=absoluteName(destination);
        enforce(allowInput||protectedInput.length==0||!sameFile(destination,protectedInput),"Overwriting input requires --in-place");
        auto dir=buildPath(root,directories.length.to!string);mkdir(dir);
        directories~=Directory(dir,dirName(destination));
        auto result=buildPath(dir,baseName(destination));aliases[absoluteName(result)]=destination;
        return result;
    }
    string readPath(string name) {
        auto requested=absoluteName(name);
        foreach_reverse(d;directories){auto candidate=buildPath(d.stage,baseName(name));if(absoluteName(buildPath(d.destination,baseName(name)))==requested&&exists(candidate))return candidate;}
        return name;
    }
    void rewrite(ref JSONValue value) {
        switch(value.type){
        case JSONType.string:if(auto destination=value.str in aliases)value=JSONValue(*destination);break;
        case JSONType.array:foreach(ref child;value.array)rewrite(child);break;
        case JSONType.object:foreach(ref child;value.object)rewrite(child);break;
        default:break;
        }
    }
    private string localTemporary(string directory,string label) {
        auto dir=buildPath(directory,".inochi-"~label~"-"~randomUUID().toString());mkdir(dir);temporaryDirectories~=dir;
        auto path=buildPath(dir,"file");write(path,cast(ubyte[])[]);return path;
    }
    void commit(ref JSONValue result) {
        // Later writes to the same output name replace earlier staged writes.
        size_t[string] latest;
        foreach(d;directories)foreach(entry;dirEntries(d.stage,SpanMode.shallow)) {
            if(!entry.isFile)continue;
            auto destination=absoluteName(buildPath(d.destination,entry.name.baseName));
            enforce(allowInput||protectedInput.length==0||!sameFile(destination,protectedInput),"Overwriting input requires --in-place");
            aliases[absoluteName(entry.name)]=destination;
            if(auto existing=destination in latest)publications[*existing].source=entry.name;
            else {latest[destination]=publications.length;publications~=Publication(entry.name,destination);}
        }
        rewrite(result);
        // Metadata sidecars may refer to sibling renders (e.g. Creator reference).
        foreach(ref p;publications)if(extension(p.source)==".json"){
            auto metadata=parseJSON(readText(p.source));rewrite(metadata);write(p.source,metadata.toPrettyString~"\n");
        }
        foreach(ref p;publications){
            enforce(exists(dirName(p.destination))&&isDir(dirName(p.destination)),"Output directory not found: "~dirName(p.destination));
            enforce(!exists(p.destination)||!isDir(p.destination),"Output path is a directory: "~p.destination);
            p.prepared=localTemporary(dirName(p.destination),"new");copy(p.source,p.prepared);
        }
        try {
            foreach(ref p;publications){
                if(present(p.destination)){
                    p.backup=localTemporary(dirName(p.destination),"backup");remove(p.backup);rename(p.destination,p.backup);p.backedUp=true;
                }
                rename(p.prepared,p.destination);p.prepared="";p.published=true;
            }
        }catch(Throwable failure){
            string[] restorationErrors;
            foreach_reverse(ref p;publications){
                try {if(p.published&&exists(p.destination))remove(p.destination);if(p.backedUp){rename(p.backup,p.destination);p.backedUp=false;}}
                catch(Throwable error){restorationErrors~=p.destination~": "~error.msg~"; backup: "~p.backup;}
            }
            enforce(restorationErrors.length==0,"Output publication failed: "~failure.msg~"; restoration errors: "~restorationErrors.join("; "));
            throw failure;
        }
        foreach(ref p;publications)if(p.backedUp){remove(p.backup);p.backedUp=false;}
    }
}
