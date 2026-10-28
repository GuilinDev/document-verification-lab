"""Run the upstream pinned renderer in its own Python environment."""
import dataclasses,json,sys,time,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
UP=ROOT/'vendor/MiniCPM-OCR/scripts/minicpm-ocr-jev';sys.path.insert(0,str(UP))
from rm_render import Candidate,render_candidates
def main():
    manifest=json.loads((ROOT/'data/manifest.json').read_text());ocr={r['id']:r for r in map(json.loads,(ROOT/'results/ocr.jsonl').read_text().splitlines())}
    assert len(ocr)==120,'Wait for all OCR outputs before rendering'
    items=[]
    for row in manifest:
        o=ocr[row['id']]
        items.append({'case_id':row['id'],'source_id':row['id'],'set':'natural','category':'text','image_path':row['region'],'text':o['text'],'ocr_error':o.get('error')})
    # Predeclared clean example from every family; changes do not enter natural metrics.
    for row in manifest[::10]:
        ref=row['reference_text'];f=row['reference_fields'];old=f"{f['total']/100:,.2f}"
        variants={'reference':ref,'total_digit':ref.replace(old,f"{(f['total']+10000)/100:,.2f}"),'currency':ref.replace(f['currency'],'JPY'),'consistent_amounts':'\n'.join(f"{k.title()} {f['currency']} {f[k]*10/100:,.2f}" for k in ['subtotal','shipping','tax','total'])}
        for name,text in variants.items():items.append({'case_id':row['id']+'-'+name,'source_id':row['id'],'set':'stress','category':'text','image_path':row['region'],'text':text,'injected_error':name!='reference','mutation':name})
    # Upstream smoke cases preserve their original candidate/reference pairing.
    for ex in sorted((UP/'examples').glob('*/case.json')):
        doc=json.loads(ex.read_text());base=ex.parent
        for i,c in enumerate(doc['candidates']):
            items.append({'case_id':'upstream-'+base.name+'-'+str(i),'set':'upstream','category':doc['category'],'image_path':str(base/doc['block_image']),'text':c['text'],'expected_prob_yes':doc.get('observed_prob_yes',{}).get(c['role'])})
    (ROOT/'results/candidates.json').write_text(json.dumps(items,ensure_ascii=False,indent=2))
    candidates=[Candidate(case_id=r['case_id'],image_path=str(ROOT/r['image_path']),text=r['text'],category=r['category']) for r in items]
    t=time.perf_counter();rendered=render_candidates(candidates,work_dir=ROOT/'results/rendered',browser_concurrency=3,python_bin=sys.executable);elapsed=time.perf_counter()-t
    results=[]
    for row,render in zip(items,rendered):
        d=dataclasses.asdict(render)
        if d['render_image_path']:
            path=Path(d['render_image_path']);d['render_sha256']=hashlib.sha256(path.read_bytes()).hexdigest();d['render_image_path']=path.relative_to(ROOT).as_posix()
        results.append({**row,'render':d})
    (ROOT/'results/rendered-candidates.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
    (ROOT/'results/render-environment.json').write_text(json.dumps({'upstream_revision':'b33b474136088dc43a2341e94590c804ec0c16a5','batch_seconds':elapsed,'candidate_count':len(items),'success':sum(r.ok for r in rendered),'pinned_packages':{'playwright':'1.62.0','Pillow':'12.3.0','Markdown':'3.10.3'},'font_environment':'DGX host fonts; not the exact reference Docker font set','parallelism':3},indent=2))
    print('RENDERED',len(results),'seconds',elapsed,flush=True)
if __name__=='__main__':main()
