module cli.cancellation;
version (InochiCLI):
import core.stdc.signal;
import core.volatile;
import std.exception;
private __gshared uint requestedSignal;
private extern(C) void cancelled(int value) nothrow @nogc {volatileStore(&requestedSignal,cast(uint)value);}
void initCancellation(){signal(SIGINT,&cancelled);signal(SIGTERM,&cancelled);version(Posix){import core.sys.posix.signal : SIGPIPE;signal(SIGPIPE,SIG_IGN);}}
int cancellationSignal(){return cast(int)volatileLoad(&requestedSignal);}
void checkCancellation(){enforce(cancellationSignal()==0,"Cancelled");}
