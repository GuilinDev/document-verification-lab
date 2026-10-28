"""Integrity and routing checks against committed experiment artifacts."""
import hashlib,json
from pathlib import Path
from evaluation import rules,label
ROOT=Path(__file__).resolve().parents[1]
read=lambda p:json.loads((ROOT/p).read_text(encoding='utf-8'))
m=read('data/manifest.json');d=read('site/evidence.json');s=read('results/summary.json')
assert len(m)==120 and len({r['id'] for r in m})==120
assert {r['template_family'] for r in m if r['split']=='test'}.isdisjoint({r['template_family'] for r in m if r['split']=='calibration'})
for r in m:
    for k in ['page','region']:
        assert hashlib.sha256((ROOT/r[k]).read_bytes()).hexdigest()==r[k+'_sha256']
    f,issues=rules(r['reference_text']);assert not issues and label(f,r['reference_fields'])
assert len(d['cases'])==168
for c in d['cases']:
    assert 0<=c['score']<=1
    for k in ['page','region','render_image']:assert (ROOT/'site'/c[k]).is_file(),c[k]
    f,issues=rules(c['text']);assert issues==c['rule_issues'] and label(f,c['reference_fields'])==c['correct']
t=s['operating_point']['threshold'];rows=[c for c in d['cases'] if c['set']=='natural' and c['split']=='test']
review=[c for c in rows if c['rule_issues'] or c['score']<t]
assert len(review)==s['test_hybrid']['reviewed']==16
assert sum(not c['correct'] for c in review)==s['test_hybrid']['errors_caught']==3
assert s['test_rules']['reviewed']==3 and s['test_rules']['errors_caught']==3
for mutation in ['currency','consistent_amounts']:
    rows=[c for c in d['cases'] if c.get('mutation')==mutation]
    assert len(rows)==12 and all(not c['correct'] and not c['rule_issues'] and c['score']<t for c in rows)
assert all(c['correct'] and c['score']>=t for c in d['cases'] if c.get('mutation')=='reference')
print('PASS: 120 input hashes, disjoint templates, 168 media bundles, labels and policy totals.')
