"""Run integration suites against explicit built or installed executables."""
import os
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
cli, native = map(lambda p: str(Path(p).resolve()), sys.argv[1:])
env = os.environ.copy()
if sys.platform == 'linux':
    env.update(SDL_VIDEODRIVER='x11', LIBGL_ALWAYS_SOFTWARE='1')
if sys.platform == 'linux' and not env.get('DISPLAY'):
    sys.exit(subprocess.call(['xvfb-run', '-a', sys.executable, *sys.argv], env=env))

# These suites create the base, layered and render-effect fixtures used below.
suites = ['acceptance', 'import_export_semantics', 'render_effects']
suites += sorted(p.stem for p in (root / 'tests').glob('*.py')
                 if p.stem not in {*suites, 'run'})
for suite in suites:
    subprocess.run([sys.executable, str(root / 'tests' / (suite + '.py')), cli],
                   cwd=root, env=env, check=True)
subprocess.run([native, str(root / 'tests/results/fixture.inx')],
               cwd=root, env=env, check=True)
