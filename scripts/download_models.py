import json,time
from pathlib import Path
from huggingface_hub import snapshot_download
root=Path(__file__).resolve().parents[1]
lock=json.loads((root/'results/model-lock.json').read_text())
for name,entry in lock.items():
    repo=entry['repo_id'];revision=entry['revision']
    print(repo,revision,flush=True)
    dst=root/'models'/name
    snapshot_download(repo,revision=revision,local_dir=dst,max_workers=3)
    print('READY',name,flush=True)
