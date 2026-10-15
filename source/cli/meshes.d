module cli.meshes;
version (InochiCLI):
import cli.context;
import cli.rig : keypoint;
import creator.viewport.common.mesh;
import creator.viewport.common.mesheditor.tools.brush : incApplyBrushDelta;
import creator.viewport.common.spline;
import creator.viewport.common.mesheditor.tools.pathdeform : incRotatePath, incShiftPathPoint;
import creator.viewport.common.mesheditor.tools.lasso : LassoTool;
import creator.viewport.common.mesheditor.operations.base : incMirrorPoint, incMirrorDelta;
import creator.viewport.common.automesh.grid;
import creator.viewport.common.automesh.contours;
import creator.viewport.common.mesheditor.brushes;
import inochi2d;
import std.algorithm;
import std.array;
import std.conv;
import std.exception;
import std.json;
import std.math;
import std.string;
vec2[] vectors(JSONValue value){vec2[] out_;foreach(v;value.array){enforce(v.array.length==2,"Expected coordinate pair");out_~=vec2(number(v.array[0].toString),number(v.array[1].toString));}return out_;}
ushort[] indices(JSONValue v){ushort[] result;foreach(i;v.array){auto n=i.get!long;enforce(n>=0&&n<=65535,"Vertex index outside uint16 range");result~=cast(ushort)n;}return result;}
void applyMesh(Context c,Drawable d,MeshData next){enforce(next.vertices.length<=65535&&next.vertices.length==next.uvs.length,"Invalid vertex/UV count");enforce(next.indices.length%3==0,"Triangles require multiples of three");foreach(i;next.indices)enforce(i<next.vertices.length,"Invalid vertex index");
 auto candidate=new IncMesh(next);DeformationParameterBinding[] bindings;
 foreach(a;c.puppet.parameters)if(auto b=cast(DeformationParameterBinding)a.getBinding(d,"deform")){foreach(x;0..a.axisPointCount(0))foreach(y;0..a.axisPointCount(1)){auto at=vec2u(x,y);if(b.isSet(at)){auto remapped=candidate.deformByDeformationBinding(b,at);enforce(remapped!is null,"Cannot remap bound deformation");b.values[x][y]=*remapped;}else b.values[x][y].clear(next.vertices.length);}bindings~=b;}
 if(auto group=cast(MeshGroup)d)group.clearCache();d.rebuffer(next);foreach(b;bindings)b.reInterpolate();
}
void preserveUV(ref MeshData next,MeshData old){foreach(i,v;next.vertices){bool done;foreach(j,u;old.vertices)if((v-u).lengthSquared<1e-6){next.uvs[i]=old.uvs[j];done=true;break;}if(done)continue;
  bool inside;float best=float.max;vec2 bestUV;
  foreach(t;0..old.indices.length/3){auto ia=old.indices[t*3],ib=old.indices[t*3+1],ic=old.indices[t*3+2];auto a=old.vertices[ia],b=old.vertices[ib],cc=old.vertices[ic];auto ab=b-a,ac=cc-a,ap=v-a;auto det=ab.x*ac.y-ab.y*ac.x;if(std.math.abs(det)<1e-6)continue;auto u=(ap.x*ac.y-ap.y*ac.x)/det;auto w=(ab.x*ap.y-ab.y*ap.x)/det;auto penalty=max(0f,-u)+max(0f,-w)+max(0f,u+w-1);auto uv=old.uvs[ia]*(1-u-w)+old.uvs[ib]*u+old.uvs[ic]*w;if(penalty<best){best=penalty;bestUV=uv;inside=true;}}
  if(inside)next.uvs[i]=bestUV;
 }}
vec2 invertVertex(vec2 delegate(vec2) evaluate,vec2 local,vec2 desired) {
 foreach(step;0..16){
  auto current=evaluate(local),error=desired-current;
  if(error.length<.0005)return local;
  auto dx=(evaluate(local+vec2(.05,0))-current)/.05;
  auto dy=(evaluate(local+vec2(0,.05))-current)/.05;
  auto determinant=dx.x*dy.y-dx.y*dy.x;
  enforce(std.math.abs(determinant)>1e-7,"Singular vertex coordinate mapping");
  local+=vec2((error.x*dy.y-error.y*dy.x)/determinant,(dx.x*error.y-dx.y*error.x)/determinant);
 }
 enforce((evaluate(local)-desired).length<.001,"Vertex coordinate mapping did not converge");
 return local;
}
vec2 solveKeyVertex(Context context,Drawable drawable,DeformationParameterBinding binding,vec2u at,size_t index,vec2 desired) {
 Deformation shape;shape.clear(drawable.vertices.length);
 foreach(i;0..drawable.vertices.length)shape.vertexOffsets[i]=binding.getValue(at).vertexOffsets[i];
 auto local=drawable.vertices[index]+shape.vertexOffsets[index];
 vec2 evaluate(vec2 candidate){
  shape.vertexOffsets[index]=candidate-drawable.vertices[index];binding.setValue(at,shape);context.puppet.update();
  return (drawable.getDynamicMatrix*vec4(drawable.vertices[index]+drawable.deformation[index]-drawable.getMesh.origin,0,1)).xy;
 }
 return invertVertex(&evaluate,local,desired);
}
class BaseCoordinates {
 Context context;Drawable drawable;MeshData original;
 DeformationParameterBinding[] bindings;vec2[][][][] forms;
 this(Context context,Drawable drawable){this.context=context;this.drawable=drawable;original=drawable.getMesh;original.vertices=original.vertices.dup;original.uvs=original.uvs.dup;original.indices=original.indices.dup;
  foreach(parameter;context.puppet.parameters)if(auto binding=cast(DeformationParameterBinding)parameter.getBinding(drawable,"deform")){bindings~=binding;vec2[][][] saved;foreach(ref row;binding.values){vec2[][] savedRow;foreach(ref value;row){vec2[] points;foreach(point;value.vertexOffsets)points~=point;savedRow~=points;}saved~=savedRow;}forms~=saved;}
 }
 void restore(){drawable.rebuffer(original);if(auto group=cast(MeshGroup)drawable)group.clearCache();foreach(i,binding;bindings)foreach(x,ref row;binding.values)foreach(y,ref value;row)value.update(forms[i][x][y]);}
 vec2 solve(ref MeshData mesh,size_t index,vec2 desired){
  scope(exit)restore();
  auto candidate=mesh;candidate.vertices=mesh.vertices.dup;
  vec2 evaluate(vec2 local){restore();candidate.vertices[index]=local;applyMesh(context,drawable,candidate);context.puppet.update();return (drawable.getDynamicMatrix*vec4(drawable.vertices[index]+drawable.deformation[index]-drawable.getMesh.origin,0,1)).xy;}
  return invertVertex(&evaluate,mesh.vertices[index],desired);
 }
}

IncMesh editableMesh(Context context,Drawable drawable,MeshData data) {
 auto mesh=new IncMesh(data);
 if(auto edges=drawable.uuid in context.meshEdges){
  foreach(vertex;mesh.vertices)vertex.disconnectAll();
  foreach(edge;*edges){enforce(edge[0]<mesh.vertices.length&&edge[1]<mesh.vertices.length,"Invalid cached mesh edge");mesh.vertices[edge[0]].connect(mesh.vertices[edge[1]]);}
 }
 return mesh;
}
size_t[2][] meshConnections(IncMesh mesh) {
 size_t[2][] edges;
 foreach(i,vertex;mesh.vertices)foreach(connection;vertex.connections){auto j=mesh.vertices.countUntil(connection);if(j>cast(ptrdiff_t)i)edges~=[i,cast(size_t)j];}
 return edges;
}
JSONValue meshOps(Context c,string action,Options o){auto d=drawable(c.puppet,need(o,"node"));auto old=d.getMesh;auto next=old;next.vertices=old.vertices.dup;next.uvs=old.uvs.dup;next.indices=old.indices.dup;
 if(action=="get"){auto result=json(old);if(auto edges=d.uuid in c.meshEdges)result["edges"]=json(*edges);return result;}
 if(action=="copy"){c.meshEdges.remove(d.uuid);auto source=drawable(c.puppet,need(o,"source"));auto data=source.getMesh;data.vertices=data.vertices.dup;data.uvs=data.uvs.dup;data.indices=data.indices.dup;if(opt(o,"uv-policy","preserve")=="creator")incLayoutMeshUV(d,data);else enforce(opt(o,"uv-policy","preserve")=="preserve","UV policy must be preserve or creator");applyMesh(c,d,data);return json(data);}
 auto uvPolicy=opt(o,"uv-policy","preserve");enforce(uvPolicy=="preserve"||uvPolicy=="creator","UV policy must be preserve or creator");
 if(action=="layout"){incLayoutMeshUV(d,next);applyMesh(c,d,next);return json(next);}
 if(action=="set"){c.meshEdges.remove(d.uuid);auto value=data(need(o,"data"));next.vertices=vectors(value["vertices"]);next.uvs=vectors(value["uvs"]);next.indices=indices(value["triangles"]);if("origin" in value)next.origin=pair(value["origin"].array.map!(v=>v.toString).join(","));applyMesh(c,d,next);return json(next);}
 DeformationParameterBinding keyBinding;vec2u keyAt;Parameter selectedParameter;
 if ("param" in o) {
  enforce(["transform","mirror","brush","path","vertex-set","select"].canFind(action),"This operation cannot edit a key form");
  enforce(uvPolicy=="preserve","UV layout applies to the base mesh only");
  enforce(!("uv" in o),"UV editing requires base mesh mode");
  auto param=parameter(c.puppet,o["param"]);selectedParameter=param;keyAt=keypoint(param,o);if(action=="select")keyBinding=cast(DeformationParameterBinding)param.getBinding(d,"deform");else keyBinding=cast(DeformationParameterBinding)param.getOrAddBinding(d,"deform");enforce(keyBinding !is null,"Deformation binding not found");
  auto current=keyBinding.getValue(keyAt);foreach(i,ref v;next.vertices)v+=current.vertexOffsets[i];
 }
 enforce(["local","world","image"].canFind(opt(o,"space","local")),"Coordinate space must be local, world or image");
 auto coordinatePose=new CoordinatePose(c,o,selectedParameter,keyAt);scope(exit)coordinatePose.restore();
 bool external=opt(o,"space","local")!="local"&&["transform","mirror","brush","path","select","vertex-set"].canFind(action);
 JSONValue coordinateMetadata;
 vec2 toWorking(vec2 world){if(opt(o,"space")!="image")return world;auto m=coordinateMetadata["sheetWorldToPixel" in coordinateMetadata?"sheetWorldToPixel":"worldToPixel"].array;return vec2(cast(float)(m[0].array[0].get!double*world.x+m[0].array[1].get!double*world.y+m[0].array[2].get!double),cast(float)(m[1].array[0].get!double*world.x+m[1].array[1].get!double*world.y+m[1].array[2].get!double));}
 if(external){if(opt(o,"space")=="image")coordinateMetadata=referenceMetadata(o);foreach(i;0..next.vertices.length)next.vertices[i]=toWorking((d.getDynamicMatrix*vec4(d.vertices[i]+d.deformation[i]-d.getMesh.origin,0,1)).xy);}
 auto mirrorOrigin=pair(opt(o,"mirror-origin","0,0"));
 uint[] mirrorAxes=[0];
 if(flag(o,"mirror-x"))mirrorAxes~=1;
 if(flag(o,"mirror-y"))mirrorAxes~=2;
 if(flag(o,"mirror-x")&&flag(o,"mirror-y"))mirrorAxes~=3;
 size_t counterpart(size_t index,uint axis) {
  auto point=incMirrorPoint(axis,next.vertices[index],mirrorOrigin);
  foreach(j,v;next.vertices)if((v-point).lengthSquared<1e-6)return j;
  return size_t.max;
 }
 size_t[] selected;if(auto v="vertices" in o)foreach(s;items(*v)){auto idx=to!size_t(s);enforce(idx<old.vertices.length,"Invalid vertex index");selected~=idx;}else foreach(i;0..old.vertices.length)selected~=i;
 if(action=="select"){if(auto v="rect" in o){auto r=numbers(*v);enforce(r.length==4,"Rectangle needs x0,y0,x1,y1");auto a=vec2(r[0],r[1]),b=vec2(r[2],r[3]);selected=selected.filter!(i=>next.vertices[i].x>=min(a.x,b.x)&&next.vertices[i].x<=max(a.x,b.x)&&next.vertices[i].y>=min(a.y,b.y)&&next.vertices[i].y<=max(a.y,b.y)).array;}if(auto polygon="polygon" in o){auto points=vectors(data(*polygon));enforce(points.length>=3,"Lasso needs at least three points");vec3[] edges;foreach(i,point;points)edges~=[vec3(point,0),vec3(points[(i+1)%points.length],0)];auto lasso=new LassoTool;selected=selected.filter!(i=>lasso.pointInPolygon(vec3(next.vertices[i],0),edges)).array;}
 auto result=selected.dup;foreach(i;selected)foreach(axis;mirrorAxes){auto j=counterpart(i,axis);if(j!=size_t.max&&!result.canFind(j))result~=j;}return json(result);}
 // Freeze counterpart indices before any vertices move.
 size_t[][] peers;foreach(i;selected){size_t[] row;foreach(axis;mirrorAxes)row~=counterpart(i,axis);peers~=row;}
 auto before=next.vertices.dup;size_t[2][] pendingEdges;bool topologyChanged;size_t[] insertedIndices;vec2[] insertedDesired;
 if(action=="vertex-set"){auto i=to!size_t(need(o,"index"));enforce(i<next.vertices.length,"Invalid vertex index");if(auto v="position" in o){
  next.vertices[i]=pair(*v);
 }if(auto v="uv" in o)next.uvs[i]=pair(*v);}
 else if(action=="path"){auto original=vectors(data(need(o,"from")));auto deformed="to" in o?vectors(data(o["to"])):original.dup;enforce("to" in o||"pivot" in o||"shift-point" in o,"Path requires target controls, rotation or shift");enforce(original.length>=2&&original.length==deformed.length,"Path control point counts must match");auto work=editableMesh(c,d,next);auto path=new CatmullSpline;foreach(v;original)path.points~=SplinePoint(v,1,1);path.interpolate();path.createTarget(work,mat4.identity);foreach(i,v;deformed)path.target.points[i].position=v;if("pivot" in o)incRotatePath(path.target,to!int(o["pivot"]),to!int(need(o,"dragged")),number(need(o,"angle")));
 if("shift-point" in o)incShiftPathPoint(path,path.target,to!int(o["shift-point"]),pair(need(o,"shift-to")));
 path.target.interpolate();path.updateTarget(work,selected);next=work.export_();next.uvs=old.uvs.dup;}
 else if(action=="brush"&&"stroke" in o){
  auto path=vectors(data(o["stroke"]));enforce(path.length>=2,"Brush stroke needs at least two positions");
  Brush brush;auto radius=number(opt(o,"radius","32"));enforce(radius>0,"Radius must be positive");
  switch(opt(o,"brush","circle")){case "circle":brush=new CircleBrush("CLI",radius);break;case "soft":brush=new DoubleThreshBrush("CLI",radius,number(opt(o,"inner-radius","0")));break;case "rectangle":brush=new RectangleBrush("CLI",radius,number(opt(o,"height",radius.to!string)),number(opt(o,"inner-ratio","0")));break;default:throw new Exception("Unknown brush shape");}
  auto work=new IncMesh(next);float[] weights;auto strength=number(opt(o,"strength","1"));
  vec2[] positions;foreach(vertex;work.vertices)positions~=vertex.position;weights=brush.weightsAt(path[0],positions);
  foreach(step;1..path.length){if(flag(o,"flow")){positions.length=0;foreach(vertex;work.vertices)positions~=vertex.position;weights=brush.weightsAt(path[step],positions);}incApplyBrushDelta(work.vertices,selected,weights,(path[step]-path[step-1])*strength);}
  foreach(i,vertex;work.vertices)next.vertices[i]=vertex.position;
 }
 else if(action=="transform"||action=="mirror"||action=="brush"){auto delta=pair(opt(o,"move","0,0"));auto scale=pair(opt(o,"scale","1,1"));auto origin=pair(opt(o,"center","0,0"));auto angle=number(opt(o,"angle","0"));if(action=="mirror"){auto axis=to!int(opt(o,"axis","0"));enforce(axis==0||axis==1,"Mirror axis must be 0 or 1");scale.vector[axis]=-1;}auto radius=number(opt(o,"radius","32"));enforce(radius>0,"Radius must be positive");auto strength=number(opt(o,"strength","1"));Brush brush;switch(opt(o,"brush","circle")){case "circle":brush=new CircleBrush("CLI",radius);break;case "soft":brush=new DoubleThreshBrush("CLI",radius,number(opt(o,"inner-radius","0")));break;case "rectangle":brush=new RectangleBrush("CLI",radius,number(opt(o,"height",radius.to!string)),number(opt(o,"inner-ratio","0")));break;default:throw new Exception("Unknown brush shape");}foreach(i;selected){auto value=next.vertices[i];auto transformed=(value-origin)*scale;transformed=vec2(transformed.x*cos(angle)-transformed.y*sin(angle),transformed.x*sin(angle)+transformed.y*cos(angle))+origin+delta;auto weight=action=="brush"?brush.weightAt(origin,value)*strength:1;next.vertices[i]=value+(transformed-value)*weight;}}
 else if(action=="grid"){auto x=numbers(need(o,"x")),y=numbers(need(o,"y"));enforce(x.length>=2&&y.length>=2,"Grid needs at least two values on each axis");enforce(x.isSorted&&y.isSorted,"Grid axes must be sorted");next.gridAxes=[y,x];next.regenerateGrid();preserveUV(next,old);}
 else {
  auto work=editableMesh(c,d,old);topologyChanged=true;
  if(action=="automesh"){auto mode=opt(o,"mode","contour");if(mode=="grid"){enforce(!flag(o,"mirror-x")&&!flag(o,"mirror-y"),"Grid automesh mirroring is unimplemented in Creator v0.8.6");enforce(!("preset" in o),"Contour presets require contour mode");auto proc=new GridAutoMeshProcessor;if("x-segments" in o||"y-segments" in o||"margin" in o){enforce(!("x" in o)&&!("y" in o),"Choose grid segments or explicit axes");proc.configureSegments(number(opt(o,"x-segments","2")),number(opt(o,"y-segments","2")),number(opt(o,"margin","0.1")));}else proc.configureCLI(numbers(opt(o,"x","-0.1,0,0.5,1,1.1")),numbers(opt(o,"y","-0.1,0,0.5,1,1.1")),number(opt(o,"threshold","15")));if("threshold" in o)proc.maskThreshold=number(o["threshold"]);work=proc.autoMesh(d,work);}else{enforce(mode=="contour","Automesh mode must be grid or contour");enforce(!flag(o,"mirror-y"),"Vertical contour mirroring is unimplemented in Creator v0.8.6");auto proc=new ContourAutoMeshProcessor;if("preset" in o)proc.setPreset(o["preset"]);proc.configureCLI(number(opt(o,"sampling",proc.SAMPLING_STEP.to!string)),number(opt(o,"threshold",proc.maskThreshold.to!string)),number(opt(o,"distance",proc.MIN_DISTANCE.to!string)),"rings" in o?numbers(o["rings"]):proc.SCALES,number(opt(o,"max-distance",proc.MAX_DISTANCE.to!string)));auto center=pair(opt(o,"mirror-origin","0,0"));work=proc.autoMesh(d,work,flag(o,"mirror-x"),center.x,flag(o,"mirror-y"),center.y);}}
  else if(action=="vertex-add"){
   auto position=pair(need(o,"position"));
   foreach(axis;mirrorAxes){auto requested=incMirrorPoint(axis,position,mirrorOrigin);auto point=localPoint(d,requested,o);bool exists;
    foreach(j,v;work.vertices){
     if(opt(o,"space","local")=="local"){if((v.position-point).lengthSquared<1e-6){exists=true;break;}}
     else {auto desired=worldPoint(requested,o);vec2 existing;if(j<old.vertices.length)existing=(d.getDynamicMatrix*vec4(d.vertices[j]+d.deformation[j]-d.getMesh.origin,0,1)).xy;else existing=insertedDesired[j-old.vertices.length];if((existing-desired).lengthSquared<1e-6){exists=true;break;}}
    }
    if(exists)continue;
    auto vertex=new MeshVertex(point,[]);
    if(auto links="connect-to" in o)foreach(item;items(*links)){auto index=to!size_t(item);enforce(index<old.vertices.length,"Invalid auto-connect vertex");auto peer=counterpart(index,axis);if(peer!=size_t.max)work.vertices[peer].connect(vertex);}
    if(opt(o,"space","local")!="local"){insertedIndices~=work.vertices.length;insertedDesired~=worldPoint(requested,o);}
    work.vertices~=vertex;
   }
  }
  else if(action=="vertex-remove"){size_t[] removals;foreach(row;peers)foreach(i;row)if(i!=size_t.max&&!removals.canFind(i))removals~=i;
   sort(removals);foreach_reverse(i;removals)work.remove(work.vertices[i]);}
  else if(action=="connect"||action=="disconnect"){auto a=to!size_t(need(o,"a")),b=to!size_t(need(o,"b"));enforce(a<work.vertices.length&&b<work.vertices.length&&a!=b,"Invalid edge");foreach(axis;mirrorAxes){auto aa=counterpart(a,axis),bb=counterpart(b,axis);if(aa==size_t.max||bb==size_t.max||aa==bb)continue;if(action=="connect")work.vertices[aa].connect(work.vertices[bb]);else work.vertices[aa].disconnect(work.vertices[bb]);}}
  else enforce(action=="triangulate","Unknown mesh operation: "~action);
  if(action=="triangulate"||action=="automesh")work=work.autoTriangulate();pendingEdges=meshConnections(work);next=work.export_();preserveUV(next,old);
 }
 if(mirrorAxes.length>1&&["transform","brush","path","vertex-set","select"].canFind(action)) {
  size_t[] sources=action=="vertex-set"?[to!size_t(need(o,"index"))]:selected;
  auto edited=next.vertices.dup;bool[size_t] visited;
  foreach(i;sources){if(i in visited)continue;visited[i]=true;
   foreach(axis;mirrorAxes[1..$]){auto point=incMirrorPoint(axis,before[i],mirrorOrigin);
    foreach(j,v;before)if((v-point).lengthSquared<1e-6){if(!(j in visited)){next.vertices[j]=before[j]+incMirrorDelta(axis,edited[i]-before[i]);visited[j]=true;}break;}
   }
  }
 }
 if(insertedIndices.length){auto coordinates=new BaseCoordinates(c,d);foreach(i,index;insertedIndices)next.vertices[index]=coordinates.solve(next,index,insertedDesired[i]);}
 if(external){
  auto desired=next.vertices.dup;
  if(keyBinding !is null){foreach(i;0..next.vertices.length)if((desired[i]-before[i]).lengthSquared>1e-10)next.vertices[i]=solveKeyVertex(c,d,keyBinding,keyAt,i,worldPoint(desired[i],o));else next.vertices[i]=old.vertices[i]+keyBinding.getValue(keyAt).vertexOffsets[i];}
  else {auto coordinates=new BaseCoordinates(c,d);next.vertices=old.vertices.dup;foreach(i;0..next.vertices.length)if((desired[i]-before[i]).lengthSquared>1e-10)next.vertices[i]=coordinates.solve(next,i,worldPoint(desired[i],o));}
 }
 if(keyBinding !is null){Deformation value;value.clear(old.vertices.length);foreach(i,v;next.vertices)value.vertexOffsets[i]=v-old.vertices[i];keyBinding.setValue(keyAt,value);return json(keyBinding);}
 if(uvPolicy=="creator"){enforce(!("uv" in o),"Choose explicit UV or Creator UV layout");incLayoutMeshUV(d,next);}
 applyMesh(c,d,next);if(topologyChanged)c.meshEdges[d.uuid]=pendingEdges;else if(action=="grid")c.meshEdges.remove(d.uuid);return json(next);
}
