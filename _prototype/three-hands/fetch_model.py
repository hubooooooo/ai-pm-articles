"""Fetch the Apache-2.0 Shadow Hand meshes via GitHub's authenticated API."""
from pathlib import Path
import subprocess,json,base64,shutil
from concurrent.futures import ThreadPoolExecutor

ROOT=Path(__file__).parent
DEST=ROOT/'vendor/shadow_hand'
DEST.mkdir(parents=True,exist_ok=True)
SOURCE=Path('/tmp/ai-pm-visual-review/shadow-source')
for name in ['README.md','LICENSE','right_hand.xml','left_hand.xml']:
    shutil.copyfile(SOURCE/name,DEST/name)

def api(path):
    result=subprocess.run(['gh','api',path],check=True,capture_output=True,text=True)
    return json.loads(result.stdout)

assets=api('repos/google-deepmind/mujoco_menagerie/contents/shadow_hand/assets')
excluded={'forearm_collision.obj','mounting_plate.obj'}

def download(item):
    if item['name'] in excluded: return
    path=DEST/item['name']
    if path.exists() and path.stat().st_size==item['size']:return
    data=api('repos/google-deepmind/mujoco_menagerie/git/blobs/'+item['sha'])
    raw=base64.b64decode(data['content'])
    assert len(raw)==item['size']
    path.write_bytes(raw)
    return item['name']

with ThreadPoolExecutor(max_workers=4) as pool:
    for name in pool.map(download,assets):
        if name:print(name,flush=True)
