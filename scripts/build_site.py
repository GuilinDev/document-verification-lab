import json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
doc=json.loads((ROOT/'site/evidence.json').read_text())
assets=ROOT/'site/assets';assets.mkdir(exist_ok=True)
for c in doc['cases']:
    for key in ['page','region','render_image']:
        src=ROOT/c[key];dst=assets/src.name
        shutil.copyfile(src,dst);c[key]='assets/'+dst.name
    c.pop('image_path',None)
(ROOT/'site/evidence.json').write_text(json.dumps(doc,ensure_ascii=False))
print('Static evidence:',len(doc['cases']),'cases',len(list(assets.iterdir())),'assets')
