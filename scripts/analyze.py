"""Freeze a calibration threshold, then evaluate the untouched test families."""
import json,math,statistics,random,shutil
from pathlib import Path
from evaluation import rules,label
ROOT=Path(__file__).resolve().parents[1]
def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8'))
def lines(name):return [json.loads(s) for s in (ROOT/name).read_text().splitlines() if s]
def wilson(k,n):
    if not n:return None
    z=1.96;p=k/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [max(0,c-h),min(1,c+h)]
def policy(rows,t=None):
    reviewed=[r for r in rows if r['rule_issues'] or r['score'] is None or (t is not None and r['score']<t)]
    ids={r['case_id'] for r in reviewed};accepted=[r for r in rows if r['case_id'] not in ids]
    wrong=sum(not r['correct'] for r in rows);caught=sum(not r['correct'] for r in reviewed);escaped=wrong-caught
    return dict(n=len(rows),errors=wrong,reviewed=len(reviewed),accepted=len(accepted),errors_caught=caught,errors_accepted=escaped,correct_reviewed=len(reviewed)-caught,accepted_error_rate=escaped/len(accepted) if accepted else None,accepted_error_wilson95=wilson(escaped,len(accepted)),review_ids=sorted(ids))
def main():
    manifest={r['id']:r for r in read('data/manifest.json')}
    ocr={r['id']:r for r in lines('results/ocr.jsonl')};scores={r['case_id']:r for r in lines('results/verifier.jsonl')}
    candidates=read('results/rendered-candidates.json');rows=[]
    for c in candidates:
        if c['set']=='upstream':continue
        m=manifest[c['source_id']];s=scores[c['case_id']];f,issues=rules(c['text'])
        rows.append({**m,**{k:v for k,v in c.items() if k not in ['render']},'extracted':f,'rule_issues':issues,'correct':label(f,m['reference_fields']),'score':s['prob_yes'],'verifier_ms':s.get('forward_ms'),'verifier_total_ms':s.get('total_ms'),'render_image':c['render'].get('render_image_path'),'ocr_ms':ocr[c['source_id']]['total_ms']})
    cal=[r for r in rows if r['set']=='natural' and r['split']=='calibration']
    # Floor budget, include all forced failures. Ties cannot be split by id.
    budget=math.floor(.20*len(cal));base=policy(cal);threshold=0.0
    for v in sorted({r['score'] for r in cal if r['score'] is not None}):
        t=math.nextafter(v,1.0)
        if policy(cal,t)['reviewed']<=budget:threshold=t
    frozen={'threshold':threshold,'review_when':'rule failure OR score unavailable OR score < threshold','calibration_n':len(cal),'target_review_fraction':.20,'actual_calibration_reviewed':policy(cal,threshold)['reviewed'],'source_ids':[r['case_id'] for r in cal],'selection':'largest observed score boundary within floor(20% * n), keeping ties together; no test labels used'}
    (ROOT/'results/operating-point.json').write_text(json.dumps(frozen,indent=2))
    test=[r for r in rows if r['set']=='natural' and r['split']=='test'];stress=[r for r in rows if r['set']=='stress'];hybrid=policy(test,threshold)
    rng=random.Random(20261028);counts=[]
    for _ in range(10000):counts.append(sum(not r['correct'] for r in rng.sample(test,hybrid['reviewed'])))
    counts.sort();up=[s for s in scores.values() if s['set']=='upstream']
    timings={}
    for key,values in [('ocr_total_ms',[r['total_ms'] for r in ocr.values()]),('verifier_forward_ms',[s['forward_ms'] for s in list(scores.values())[1:] if s.get('forward_ms') is not None]),('verifier_total_ms',[s['total_ms'] for s in list(scores.values())[1:] if s.get('total_ms') is not None])]:
        a=sorted(values);timings[key]={'n':len(a),'median':statistics.median(a),'p95':a[math.ceil(.95*len(a))-1]}
    summary={'operating_point':frozen,'natural_all':policy([r for r in rows if r['set']=='natural']),'calibration_rules':base,'calibration_hybrid':policy(cal,threshold),'test_rules':policy(test),'test_hybrid':hybrid,'test_random_same_review_budget':{'reviewed':hybrid['reviewed'],'expected_errors_caught':hybrid['reviewed']*hybrid['errors']/len(test),'simulation95_errors_caught':[counts[249],counts[9749]],'draws':10000,'seed':20261028},'stress_by_mutation':{name:{'n':len(a:=[r for r in stress if r['mutation']==name]),'min_score':min(r['score'] for r in a),'max_score':max(r['score'] for r in a),'median_score':statistics.median(r['score'] for r in a),'rules':policy(a),'hybrid':policy(a,threshold)} for name in ['reference','total_digit','currency','consistent_amounts']},'timing':timings,'upstream_smoke':up,'rendering':read('results/render-environment.json'),'limitations':['Synthetic payment-region crops, not whole-invoice or production accuracy.','No fine-tuning or production calibration. Score is a model output, not a guarantee.','Region pixels degraded; source page outside the region remains crisp.','Shared GPU with PyTorch fallback kernels; timing excludes candidate rendering in verifier_total_ms.','Host fonts differ from upstream reference Docker renderer.','Error labels cover four amounts and currency, not all possible visual or layout defects.']}
    (ROOT/'results/summary.json').write_text(json.dumps(summary,indent=2))
    (ROOT/'site/evidence.json').write_text(json.dumps({'summary':summary,'cases':rows},ensure_ascii=False))
    print(json.dumps({k:summary[k] for k in ['operating_point','test_rules','test_hybrid','test_random_same_review_budget','timing']},indent=2))
if __name__=='__main__':main()
