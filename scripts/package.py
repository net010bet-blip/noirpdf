"""Create a source distribution without user files, secrets or installed dependencies."""
from pathlib import Path
import zipfile,hashlib
root=Path(__file__).resolve().parents[1]
output=root/'NoirPDF.zip'
excluded={'node_modules','out','.next','__pycache__','.pytest_cache','.git','.venv'}
files=[]
for folder in ['apps','services','packages','infra','tests','docs','scripts','.github']:
    for p in (root/folder).rglob('*'):
        if p.is_file() and not excluded.intersection(p.relative_to(root).parts) and p.suffix not in ('.pyc','.tsbuildinfo'):
            files.append((p,p.relative_to(root).as_posix()))
for name in ['README.md','iniciar-noirpdf.cmd','ARCHITECTURE.md','FEATURE_MATRIX.md','SECURITY.md','DEPLOYMENT.md','TEST_PLAN.md','LICENSE','.env.example','.gitignore','.dockerignore','package.json','package-lock.json','compose.yaml','pytest.ini','render.yaml','playwright.config.ts','playwright.pages.config.ts','playwright.advanced.config.ts','playwright.ai.config.ts']:
    files.append((root/name,name))
for p in (root/'artifacts').glob('catalog-*.png'):
    files.append((p,'docs/evidence/'+p.name))
if (root/'artifacts/e2e-merged.pdf').exists():files.append((root/'artifacts/e2e-merged.pdf','docs/evidence/e2e-merged.pdf'))
with zipfile.ZipFile(output,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
    for p,name in sorted(files,key=lambda x:x[1]):archive.write(p,'NoirPDF/'+name)
with zipfile.ZipFile(output) as archive:
    assert archive.testzip() is None
    assert all('/.env' not in name or name.endswith('.env.example') for name in archive.namelist())
    assert 'NoirPDF/README.md' in archive.namelist()
sha=hashlib.sha256(output.read_bytes()).hexdigest()
(root/'NoirPDF.zip.sha256').write_text(sha+'  NoirPDF.zip\n')
print(f'{output}: {len(files)} files, {output.stat().st_size} bytes; CRC verified; SHA256 {sha}')
