"""Build the full, word-aligned USD evidence walkthrough from frozen results."""
import html,json,re,math,subprocess,wave,struct
from pathlib import Path
import imageio_ffmpeg

R=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
write=lambda p,s:p.write_text(s,encoding='utf-8')
words=read(R/'assets/audio/words.json')
script=(R/'narration.txt').read_text(encoding='utf-8').strip()
norm=lambda s:re.sub('[^a-z0-9]','',s.lower())
stream=''.join(norm(w['text']) for w in words)
positions=[];n=0
for w in words:positions.append(n);n+=len(norm(w['text']))
def at(phrase):
    p=stream.index(norm(phrase));i=max(i for i,x in enumerate(positions) if x<=p)
    return words[i]['start']+.4

anchors={
 'upload':'I upload a dollar invoice','read':'Mini CPM OCR reads',
 'inject':'Now I deliberately','rules':'Subtotal shipping and tax','pass':'The rules pass',
 'verify':'OCR Jev checks','source':'the source image','text':'the candidate text',
 'render':'and an image rendered','renderwhy':'That rendered copy',
 'head':'Inside the model','classifier':'A small classification head','outcomes':'consistent and inconsistent',
 'direct':'It returns a consistency','score':'Higher scores mean','goodscore':'The correct candidate',
 'badscore':'Our altered candidate','threshold':'We compare that score','calibration':'separate calibration examples',
 'queue':'This invoice enters','review':'The reviewer opens','restore':'restores the correct amounts',
 'confirm':'and confirms the correction','use':'For accounts payable',
 'po':'purchase order matching','approval':'and approval',
 'evaluate':'I also tested','natural':'On eighty held out','naturalrules':'rules caught all three',
 'overhead':'The verifier added thirteen','stress':'In a separate stress test',
 'stressflag':'it flagged all twenty four','takeaway':'The useful measure','lab':'The online lab lets'
}
T={k:at(v) for k,v in anchors.items()}
D=math.ceil(words[-1]['start']+words[-1]['duration']+.4+2)
write(R/'timing.json',json.dumps({'duration':D,**T},indent=2))
cases={c['case_id']:c for c in read(R/'evidence.json')}
good=cases['invoice-090-reference'];bad=cases['invoice-090-consistent_amounts']
assert abs(bad['score']-.004264634568244219)<1e-12
F=good['reference_fields'];keys=['subtotal','shipping','tax','total'];B={k:F[k]*10 for k in keys}
money=lambda n:f'${n/100:,.2f}'
img=lambda c,k:'assets/evidence/'+Path(c[k]).name
base=(R/'assets/workflow-base.css').read_text(encoding='utf-8')
extra='''#root{background:transparent}.state{height:594px}.source-shell{height:594px}.action-title h1{font-size:36px}.panel-toolbar{font-size:20px}.doc-window{bottom:26px}.source-footer{bottom:22px}.source-highlight-label{top:370px}.eyebrow{font-size:17px}.explain{font-size:25px}.state-note{font-size:23px}.big-question{font-size:43px;line-height:1.2;letter-spacing:-1.6px;margin:25px 0}.gate-pair{display:flex;gap:18px;margin:35px 0}.gate{flex:1;border:1px solid #aac7b8;padding:22px 18px;border-radius:5px;font-size:24px;line-height:1.4;background:#f1f6f2}.gate b{display:block;font-size:30px;margin-top:12px}.intro-byline{font-size:22px;color:#546b68}.candidate-block pre{font-size:25px}.render-reveal,.rendered img{height:150px}.classifier{top:871px;height:55px;font-size:23px}.classifier b{font-size:24px}.concept-note{font-size:23px;line-height:1.5;color:#546b68;margin-top:16px}.input-pills{display:flex;gap:10px;margin:8px 0 13px}.input-pills span{flex:1;font-size:21px;text-align:center;background:#f0f5f1;border:1px solid #aac7b8;padding:12px 8px;border-radius:4px}.down{height:30px;text-align:center;color:#096b5b;font-size:27px}.representation{height:85px;border:1px solid #9cbcae;border-radius:5px;background:#e5eee9;padding:12px 20px;text-align:center}.representation b{font-size:25px;font-weight:600}.rep-cells{display:flex;justify-content:center;gap:10px;margin-top:10px}.rep-cells i{display:block;width:48px;height:13px;background:#7aa38f;border-radius:2px}.head-box{padding:18px;border:2px solid #096b5b;border-radius:5px;text-align:center;color:#096b5b;font-size:27px;font-weight:650}.output-row{display:grid;grid-template-columns:165px 1fr 100px;gap:16px;align-items:center;margin-top:16px;font-size:23px}.output-row strong{text-align:right;font-size:29px;font-variant-numeric:tabular-nums}.output-track{height:14px;background:#e6ece5;border-radius:2px;overflow:hidden}.output-track i{display:block;width:100%;height:100%;transform-origin:left;background:#096b5b}.output-row.bad .output-track i{background:#a52d24}.one-result{font-size:22px;color:#546b68;margin-top:18px}.score-definition{font-size:26px;line-height:1.4}.score-row{margin:27px 0}.old-score{font-size:59px}.score-meter{margin-top:38px}.score-context{margin-top:23px;font-size:23px;color:#546b68}.policy-flow{margin-top:28px}.threshold-number{font-size:60px;color:#096b5b;letter-spacing:-2px}.policy-line{display:flex;align-items:center;justify-content:space-between;border:1px solid #d6dfd5;border-radius:5px;padding:18px;margin-top:16px;font-size:24px}.policy-line strong{font-size:32px}.policy-line.flag{background:#fff4e5;border-color:#bb8b4b}.calibration-note{background:#edf3ef;border-radius:5px;padding:16px;font-size:23px;color:#546b68;line-height:1.4}.queue-card{padding:24px}.review-switch{height:224px}#review-panel .button{position:relative;height:56px;padding:12px 20px;margin-top:13px}.done-amount{margin:23px 0}.handoff-record{display:flex;align-items:center;justify-content:space-between;padding:20px;background:#edf3ef;border:1px solid #aac7b8;border-radius:5px;margin:22px 0;font-size:25px}.handoff-record strong{font-size:39px;color:#096b5b}.handoff-step{display:flex;justify-content:space-between;align-items:center;padding:17px 20px;border:1px solid #d6dfd5;border-radius:5px;font-size:26px;margin-top:16px}.handoff-step small{font-size:20px;color:#546b68}.handoff-evidence{font-size:23px;color:#096b5b;line-height:1.6;margin:20px 0}.eval-grid{display:grid;grid-template-columns:repeat(16,1fr);gap:7px;margin:22px 0 16px}.eval-cell{height:23px;border:1px solid #a8bdb0;border-radius:3px;background:#edf3ef}.eval-legend{display:flex;gap:24px;font-size:20px;color:#546b68}.eval-legend i{display:inline-block;width:13px;height:13px;margin-right:8px;border-radius:2px}.metrics{display:flex;gap:18px;margin-top:25px}.metric{flex:1;padding:18px;background:#f4f6f1;border:1px solid #d6dfd5;border-radius:5px}.metric strong{display:block;font-size:51px;color:#096b5b}.metric span{font-size:22px;line-height:1.4}.eval-verdict{font-size:25px;font-weight:600;margin-top:24px;color:#a52d24}.stress-grid{grid-template-columns:repeat(8,1fr);gap:10px}.stress-grid .eval-cell{height:48px}.stress-facts{display:flex;gap:20px;margin:28px 0}.stress-facts>div{flex:1;padding:20px;background:#f4f6f1;border:1px solid #d6dfd5}.stress-facts b{font-size:42px;display:block}.stress-facts span{font-size:23px}.takeaway{font-size:39px;line-height:1.25;letter-spacing:-1px;margin:22px 0}.lab-actions{font-size:25px;line-height:1.8;margin:20px 0;color:#096b5b}.project-link{background:#edf3ef;border:1px solid #aac7b8;padding:17px 20px;margin-top:13px;font-size:20px;border-radius:5px;line-height:1.5}.project-link b{font-size:23px;display:block}.small-note{font-size:20px}.cursor-label{font-size:17px}.source-caption{position:absolute;left:190px;top:880px;color:#546b68;font-size:23px;line-height:1.5;width:680px}.lower-callout{position:absolute;left:930px;top:882px;font-size:23px;color:#096b5b;width:830px}.state-inner{width:100%}'''
CSS=base+extra
(R/'compositions').mkdir(exist_ok=True)
def comp(name,body,js,css=''):
    write(R/f'compositions/{name}.html',f'<template><style>{CSS}{css}</style><div id="root" data-composition-id="{name}" data-width="1920" data-height="1080">{body}</div><script>const t={json.dumps(T)};const tl=gsap.timeline({{paused:true}});{js}\nwindow.__timelines["{name}"]=tl;</script></template>')
def fields(prefix,v):
    return ''.join(f'<div id="{prefix}-{k}" class="field {"total" if k=="total" else ""}"><span>{k.title()}</span><strong>{money(v[k])}</strong></div>' for k in keys)
def panel(id,start,end,body):
    return f'<section id="{id}" class="clip state" data-start="{start:.6f}" data-duration="{end-start:.6f}" data-track-index="2"><div class="state-inner">{body}</div></section>'
def title(id,start,end,text):
    return f'<div id="title-{id}" class="clip action-title" data-start="{start:.6f}" data-duration="{end-start:.6f}" data-track-index="1"><h1>{text}</h1></div>'
def tag(text):return f'<p class="eyebrow">{text}</p>'

# Persistent source workspace: the same source pixels survive every step.
steps=''.join(f'<div id="step-{i}" class="step"><span>{i+1:02d}</span>{name}<i id="step-line-{i}"></i></div>' for i,name in enumerate(['Upload','Read','Check','Verify','Review']))
shell=f'''<div class="mast"><div class="brand">DVL / Document Verification Lab</div><small>GUILIN ZHANG · USD INVOICE WORKFLOW</small></div><div class="steps">{steps}</div><div class="source-shell"><div class="panel-toolbar"><b>DVL-0090.png</b><span>Original invoice · USD</span></div><div class="doc-window" data-layout-allow-overflow><div id="page-camera" class="page-camera" data-layout-allow-overflow><img id="source-page" src="{img(good,'page')}" alt="Original USD invoice" data-layout-allow-overflow><div id="payment-roi" class="roi"></div><div id="source-total-marker" class="source-total-marker"></div></div><div id="source-input-badge" class="source-badge">1 · Original source image</div><div id="source-total-label" class="source-highlight-label">Printed total · {money(F['total'])}</div><div id="source-footer" class="source-footer">Original document total <strong>{money(F['total'])}</strong></div></div><div id="upload-stamp" class="upload-stamp">✓ Uploaded</div></div><div id="source-caption" class="source-caption">Source evidence remains attached to the corrected fields.</div>'''
shelljs='''gsap.set('.step i',{scaleX:0});gsap.set('#page-camera',{x:154,y:4,scale:.265});gsap.set('#payment-roi,#source-total-marker,#source-input-badge,#source-total-label,#source-footer,#upload-stamp,#source-caption',{opacity:0});
for(const [i,s] of [[0,t.upload],[1,t.read],[2,t.rules],[3,t.verify],[4,t.queue]]){tl.to('#step-line-'+i,{scaleX:1,duration:.45},s);tl.to('#step-'+i,{color:'#096b5b',duration:.3},s);}
tl.to('#upload-stamp',{opacity:1,duration:.3},t.upload+1.4);
tl.to('#payment-roi',{opacity:1,duration:.35},t.read+.5);
tl.to('#page-camera',{x:-349.6,y:-659.6,scale:.74,duration:1.4,ease:'power2.inOut'},t.read+.65);
tl.to('#upload-stamp',{opacity:0,duration:.2},t.read+.5);
tl.to('#source-footer',{opacity:1,duration:.4},t.read+2.2);
tl.to('#source-total-marker',{opacity:1,duration:.3},t.inject+2.3);
tl.to('#source-input-badge',{opacity:1,duration:.3},t.source);
tl.to('#payment-roi',{borderWidth:7,duration:.3},t.source);
tl.to('#source-input-badge',{opacity:0,duration:.25},t.queue);
tl.to('#source-total-label',{opacity:1,duration:.3},t.review+.6);
tl.to('#source-total-marker',{borderColor:'#096b5b',backgroundColor:'rgba(9,107,91,.06)',duration:.4},t.confirm+1.2);
tl.to('#source-total-label',{color:'#096b5b',backgroundColor:'#e1eee5',duration:.4},t.confirm+1.2);
tl.to('#source-caption',{opacity:1,duration:.4},t.use);
'''
comp('workspace',shell,shelljs)

# Intake, extraction and the explicitly authored stress intervention.
intake=title('hook',0,T['upload'],'The numbers add up. Do they match the page?')
intake+=panel('hook-panel',0,T['upload'],tag('TWO DIFFERENT CHECKS')+'<h2 class="big-question">A valid sum can hide<br>a wrong reading.</h2><div class="gate-pair"><div id="hook-rule" class="gate">Do the amounts add up?<b class="good">Arithmetic</b></div><div id="hook-visual" class="gate">Do they match the source?<b>Visual evidence</b></div></div><p class="intro-byline">Follow one invoice through recognition, verification and review.</p>')
intake+=title('upload',T['upload'],T['read'],'Upload the source document')
intake+=panel('upload-panel',T['upload'],T['read'],tag('INVOICE INTAKE')+'<h2>Start with the supplier invoice.</h2><p class="explain">Keep the original document alongside every extracted value.</p><div class="file-card"><span class="file-icon">USD</span><div><b>DVL-0090.png</b><p>Supplier invoice · 1 page</p></div></div><div id="upload-button" class="button">Upload invoice <span>↑</span></div>')
intake+=title('read',T['read'],T['inject'],'Read the payment region into editable fields')
intake+=panel('read-panel',T['read'],T['inject'],tag('MINICPM-OCR / IMAGE → TEXT')+f'<h2>Four amounts, linked to their source.</h2><div id="read-progress"><span>Reading payment details</span><div class="thin"><i id="ocr-progress"></i></div></div><div class="fields read-fields">{fields("read",F)}</div><div id="ocr-done" class="state-note good">✓ Region read · currency USD</div>')
intake+=title('inject',T['inject'],T['rules'],'Deliberately introduce a consistent amount error')
intake+=panel('inject-panel',T['inject'],T['rules'],tag('CONTROLLED STRESS TEST')+f'<h2>Multiply all four amounts by ten.</h2><div id="inject-button" class="button amber-button">Test: apply ×10 to every amount</div><div class="field-switch"><div id="before-injection" class="fields">{fields("before",F)}</div><div id="after-injection" class="fields">{fields("after",B)}</div></div><div id="injected-label" class="state-note amber">Original image preserved. Test candidate changed.</div>')
intake+=title('rules',T['rules'],T['verify'],'Run the rules already in the workflow')
intake+=panel('rules-panel',T['rules'],T['verify'],tag('REQUIRED FIELDS · CURRENCY · ARITHMETIC')+f'<h2>Every amount changed together.</h2><div class="equation"><span>{money(B["subtotal"])}</span><b>+</b><span>{money(B["shipping"])}</span><b>+</b><span>{money(B["tax"])}</span><b>=</b><strong>{money(B["total"])}</strong></div><div class="check-list"><p id="rule-1">✓ Required fields present</p><p id="rule-2">✓ Currency consistent: USD</p><p id="rule-3">✓ Subtotal + shipping + tax = total</p></div><div id="rules-pass" class="verdict good">RULES PASS</div><p class="explain">Source total: <b>{money(F["total"])}</b></p>')
intakejs='''gsap.set('#hook-rule,#hook-visual',{opacity:0,y:12});gsap.set('#ocr-progress',{scaleX:0});gsap.set('.read-fields .field,#ocr-done',{opacity:0});gsap.set('#after-injection,#injected-label,#rule-1,#rule-2,#rule-3,#rules-pass',{opacity:0});
tl.to('#hook-rule',{opacity:1,y:0,duration:.4},1);tl.to('#hook-visual',{opacity:1,y:0,duration:.4},3.1);
tl.to('#upload-button',{scale:.985,duration:.1},t.upload+.7).to('#upload-button',{scale:1,duration:.25,ease:'back.out(1.2)'},t.upload+.8);
tl.to('#ocr-progress',{scaleX:1,duration:3.6,ease:'none'},t.read+.6);tl.to('.read-fields .field',{opacity:1,duration:.35,stagger:.65},t.read+2.1);tl.to('#ocr-done',{opacity:1,duration:.3},t.inject-1.1);
tl.to('#before-injection',{opacity:0,duration:.18},t.inject+1.6);tl.to('#after-injection',{opacity:1,duration:.25},t.inject+1.8);tl.fromTo('#after-total',{backgroundColor:'#f5dca4'},{backgroundColor:'#fff2dc',duration:.6},t.inject+1.8);tl.to('#injected-label',{opacity:1,duration:.3},t.inject+2.2);
tl.to('#rule-1',{opacity:1,duration:.25},t.rules+.2);tl.to('#rule-2',{opacity:1,duration:.25},t.rules+.9);tl.to('#rule-3',{opacity:1,duration:.25},t.rules+1.6);tl.to('#rules-pass',{opacity:1,duration:.3},t.pass);
'''
comp('intake',intake,intakejs)

# Actual verifier inputs, then a conceptual view of the binary head.
mechanism=title('inputs',T['verify'],T['head'],'Compare the OCR claim with the source pixels')
mechanism+=panel('verify-panel',T['verify'],T['head'],tag('MINICPM-OCR JEV / THREE INPUTS')+f'<h2>Make the candidate visible.</h2><div id="candidate-text" class="candidate-block"><p class="small-label">2 · Candidate text</p><pre>{html.escape(bad["text"])}</pre></div><div id="render-arrow" class="render-arrow">↓ <span>Render text as an image</span></div><div id="candidate-render" class="candidate-block rendered"><p class="small-label">3 · Rendered candidate</p><div class="render-reveal"><img src="{img(bad,"render_image")}" alt="Actual candidate render"></div></div>')
mechanism+=f'<div id="classifier-inputs" class="classifier"><span>Source image + candidate text + rendered image</span><b>→ OCR Jev</b></div>'
mechanism+=title('head',T['head'],T['score'],'How the model produces a consistency score')
mechanism+=panel('head-panel',T['head'],T['score'],tag('2B MULTIMODAL VERIFIER / BINARY CLASSIFICATION')+'<h2>Three inputs. One scored comparison.</h2><div id="head-inputs" class="input-pills"><span>Source image</span><span>Candidate text</span><span>Rendered image</span></div><div class="down" id="head-arrow-1">↓</div><div id="representation" class="representation"><b>Shared internal representation</b><div class="rep-cells">'+''.join('<i></i>' for _ in range(8))+'</div></div><div class="down" id="head-arrow-2">↓</div><div id="head-box" class="head-box">Classification head</div><div id="outputs"><div class="output-row bad"><span>Inconsistent</span><div class="output-track"><i id="no-bar"></i></div><strong>0.9957</strong></div><div class="output-row"><span>Consistent</span><div class="output-track"><i id="yes-bar"></i></div><strong>0.0043</strong></div></div><p id="one-result" class="one-result">Direct classifier output · no generated explanation</p>')
mechanismjs='''gsap.set('#candidate-text,#render-arrow,#candidate-render,#classifier-inputs',{opacity:0});gsap.set('#representation,#head-arrow-1,#head-arrow-2,#head-box,#outputs,#one-result',{opacity:0,y:8});gsap.set('#no-bar,#yes-bar',{scaleX:0});
tl.to('#candidate-text',{opacity:1,duration:.35},t.text);tl.to('#render-arrow',{opacity:1,duration:.3},t.render-.2);tl.to('#candidate-render',{opacity:1,duration:.35},t.render+.25);tl.fromTo('.render-reveal',{clipPath:'inset(0 0 100% 0)'},{clipPath:'inset(0 0 0% 0)',duration:1.2,ease:'none'},t.render+.4);tl.to('#classifier-inputs',{opacity:1,duration:.4},t.renderwhy);tl.to('#candidate-text,#candidate-render',{borderColor:'#096b5b',duration:.4},t.renderwhy+.7);tl.to('#classifier-inputs',{opacity:0,duration:.25},t.head-.25);
tl.to('#head-arrow-1,#representation',{opacity:1,y:0,duration:.4,stagger:.2},t.head+1.3);tl.to('#head-arrow-2,#head-box',{opacity:1,y:0,duration:.4,stagger:.2},t.classifier);tl.to('#outputs',{opacity:1,y:0,duration:.35},t.outcomes);tl.to('#no-bar',{scaleX:.995735,duration:.8,ease:'power2.out'},t.outcomes+.2);tl.to('#yes-bar',{scaleX:.004265,duration:.8,ease:'power2.out'},t.outcomes+.2);tl.to('#one-result',{opacity:1,y:0,duration:.35},t.direct);
'''
comp('mechanism',mechanism,mechanismjs)

# Scores are evidence; the threshold is a separately chosen routing policy.
routing=title('score',T['score'],T['threshold'],'Read the score as agreement with the source')
routing+=panel('score-panel',T['score'],T['threshold'],tag('RECORDED RESULTS / SAME USD SOURCE')+f'<h2>Higher means stronger agreement.</h2><p class="score-definition">A score from 0 to 1 measures visual consistency between the source and candidate.</p><div class="score-row"><div id="good-result"><p>Correct candidate</p><strong class="old-score">{good["score"]:.4f}</strong></div><span>→</span><div id="bad-result"><p>Altered candidate</p><strong class="bad-score">{bad["score"]:.4f}</strong></div></div><div class="score-meter"><i id="score-dot"></i></div><div class="meter-labels"><span>0 · disagreement</span><span>1 · agreement</span></div><p id="score-context" class="score-context">Candidate total: {money(B["total"])}<br>Source total: {money(F["total"])}</p>')
routing+=title('threshold',T['threshold'],T['queue'],'Use a separate policy to decide what needs review')
routing+=panel('threshold-panel',T['threshold'],T['queue'],tag('ROUTING POLICY / FROZEN BEFORE TESTING')+'<h2>Review below the selected threshold.</h2><div class="policy-flow"><p class="threshold-number">0.980</p><div id="calibration-note" class="calibration-note">Selected using 40 separate calibration cases.</div><div id="policy-low" class="policy-line flag"><span>This candidate</span><strong class="bad">0.0043 &lt; 0.980</strong></div><div id="policy-review" class="policy-line"><span>Next action</span><strong>Human review →</strong></div></div>')
routing+=title('queue',T['queue'],T['review'],'Send this invoice to the review queue')
routing+=panel('queue-panel',T['queue'],T['review'],tag('REVIEW QUEUE')+f'<h2>Open the evidence behind the field.</h2><div id="queue-card" class="queue-card"><div><b>DVL-0090</b><span class="pill bad">Needs review</span></div><p>Candidate total</p><strong>{money(B["total"])}</strong><div class="line"></div><p class="bad">Low visual consistency · {bad["score"]:.4f}</p><div id="open-evidence" class="button">Open source evidence →</div></div>')
routing+=title('review',T['review'],T['use'],'Compare the source, restore the fields, confirm')
routing+=panel('review-panel',T['review'],T['use'],tag('REVIEWER / SOURCE-TO-FIELD CHECK')+f'<h2>Restore the amounts from the document.</h2><div class="field-switch review-switch"><div id="review-wrong" class="fields">{fields("wrong",B)}</div><div id="review-correct" class="fields">{fields("correct",F)}</div></div><div id="restore-button" class="button secondary">Restore source amounts</div><div id="confirm-button" class="button"><span id="confirm-label">Confirm correction ✓</span><span id="confirmed-label" style="position:absolute;left:20px">Correction confirmed ✓</span></div><p id="review-status" class="small-note">Source evidence stays attached to DVL-0090.</p>')
routing+=title('use',T['use'],T['evaluate'],'Carry corrected fields into the invoice workflow')
routing+=panel('use-panel',T['use'],T['evaluate'],tag('ACCOUNTS PAYABLE / DOWNSTREAM WORKFLOW')+f'<h2>From document review to business checks.</h2><div class="handoff-record"><div>DVL-0090<br><span class="small-note">Corrected invoice total</span></div><strong>{money(F["total"])}</strong></div><div id="po-step" class="handoff-step"><span>Purchase order matching</span><small>Next check →</small></div><div id="approval-step" class="handoff-step"><span>Approval workflow</span><small>Pending</small></div><p id="handoff-evidence" class="handoff-evidence">✓ Original document<br>✓ Extracted and corrected values<br>✓ Review history</p>')
routingjs='''gsap.set('#good-result,#bad-result,#score-context',{opacity:0});gsap.set('#score-dot',{opacity:0,x:0});gsap.set('#calibration-note,#policy-low,#policy-review',{opacity:0,y:8});gsap.set('#review-correct',{opacity:0});gsap.set('#confirm-button',{opacity:.3});gsap.set('#confirmed-label',{opacity:0});gsap.set('#po-step,#approval-step,#handoff-evidence',{opacity:0,y:8});
tl.to('#good-result',{opacity:1,duration:.4},t.goodscore);tl.to('#score-dot',{opacity:1,x:710,duration:.9,ease:'power2.inOut'},t.goodscore+.2);tl.to('#bad-result',{opacity:1,duration:.4},t.badscore);tl.to('#score-dot',{x:3,duration:1,ease:'power2.inOut'},t.badscore+.3);tl.to('#score-context',{opacity:1,duration:.4},t.badscore+1.2);
tl.to('#calibration-note',{opacity:1,y:0,duration:.4},t.calibration-.2);tl.to('#policy-low',{opacity:1,y:0,duration:.4},t.threshold+1);tl.to('#policy-review',{opacity:1,y:0,duration:.4},t.queue-1.2);
tl.to('#review-wrong',{opacity:0,duration:.2},t.restore+.5);tl.to('#review-correct',{opacity:1,duration:.25},t.restore+.6);tl.fromTo('#correct-total',{backgroundColor:'#bdddc7'},{backgroundColor:'#e7f2e8',duration:.6},t.restore+.6);tl.to('#confirm-button',{opacity:1,duration:.3},t.restore+.8);tl.to('#confirm-button',{backgroundColor:'#064b40',scale:.985,duration:.1},t.confirm+.5).to('#confirm-button',{scale:1,duration:.25},t.confirm+.6);tl.to('#review-status',{color:'#096b5b',duration:.3},t.confirm+.7);tl.to('#confirm-label',{opacity:0,duration:.15},t.confirm+.7);tl.to('#confirmed-label',{opacity:1,duration:.2},t.confirm+.8);
tl.to('#po-step',{opacity:1,y:0,duration:.4},t.po-.3);tl.to('#approval-step',{opacity:1,y:0,duration:.4},t.approval);tl.to('#handoff-evidence',{opacity:1,y:0,duration:.4},t.approval+.8);
'''
comp('routing',routing,routingjs)

# Evaluation is kept separate from the single constructed stress demonstration.
evaluation=title('natural',T['evaluate'],T['stress'],'Measure what the extra model adds')
evaluation+=panel('natural-panel',T['evaluate'],T['stress'],tag('80 HELD-OUT SYNTHETIC INVOICE REGIONS')+'<h2>Start with the existing rules baseline.</h2><div class="eval-grid">'+''.join(f'<i id="case-{i}" class="eval-cell"></i>' for i in range(80))+'</div><div class="eval-legend"><span><i style="background:#a52d24"></i>3 natural errors</span><span id="extra-legend"><i style="background:#bb7d20"></i>13 extra reviews</span></div><div class="metrics"><div id="rules-metric" class="metric"><strong>3 / 3</strong><span>Errors already caught<br>by the rules</span></div><div id="extra-metric" class="metric"><strong>+13</strong><span>Correct cases sent<br>to extra review</span></div></div><div id="natural-verdict" class="eval-verdict">Additional natural errors caught: 0</div>')
evaluation+=title('stress',T['stress'],T['takeaway'],'Test a different failure mode separately')
evaluation+=panel('stress-panel',T['stress'],T['takeaway'],tag('SEPARATE DESIGNED STRESS TEST / 24 CANDIDATES')+'<h2>Consistent changes can evade arithmetic.</h2><div class="eval-grid stress-grid">'+''.join(f'<i id="stress-{i}" class="eval-cell"></i>' for i in range(24))+'</div><div class="stress-facts"><div><b>24 passed</b><span>Existing rules</span></div><div id="stress-result"><b class="amber">24 flagged</b><span>Visual verification</span></div></div><p class="explain">12 currency substitutions<br>12 tenfold amount changes</p>')
evaluation+=title('lab',T['takeaway'],D,'Inspect the evidence. Measure the review workload.')
evaluation+=panel('lab-panel',T['takeaway'],D,tag('DOCUMENT VERIFICATION LAB / GUILIN ZHANG')+'<h2 class="takeaway">Errors caught per unit<br>of review work.</h2><div id="lab-actions" class="lab-actions">Inspect source images and candidates<br>Compare recorded scores<br>Explore the review threshold</div><div id="hf-link" class="project-link"><b>Interactive evidence lab</b>huggingface.co/spaces/guilindev/document-verification-lab</div><div id="github-link" class="project-link"><b>Reproduce the experiment</b>github.com/GuilinDev/document-verification-lab</div>')
evaljs='''gsap.set('#rules-metric,#extra-metric,#extra-legend,#natural-verdict,#stress-result,#lab-actions,#hf-link,#github-link',{opacity:0,y:8});
tl.to('#case-3,#case-37,#case-65',{backgroundColor:'#a52d24',borderColor:'#a52d24',duration:.3,stagger:.12},t.naturalrules);tl.to('#rules-metric',{opacity:1,y:0,duration:.4},t.naturalrules);
tl.to('#case-4,#case-8,#case-12,#case-17,#case-24,#case-28,#case-32,#case-41,#case-49,#case-54,#case-62,#case-70,#case-77',{backgroundColor:'#bb7d20',borderColor:'#bb7d20',duration:.3,stagger:.03},t.overhead);tl.to('#extra-metric,#extra-legend',{opacity:1,y:0,duration:.4},t.overhead);tl.to('#natural-verdict',{opacity:1,y:0,duration:.4},t.stress-2);
tl.to('.stress-grid .eval-cell',{backgroundColor:'#e6b464',borderColor:'#9b5b10',duration:.35,stagger:.02},t.stressflag);tl.to('#stress-result',{opacity:1,y:0,duration:.4},t.stressflag+.5);
tl.to('#lab-actions',{opacity:1,y:0,duration:.4},t.lab);tl.to('#hf-link',{opacity:1,y:0,duration:.4},t.lab+.8);tl.to('#github-link',{opacity:1,y:0,duration:.4},t.lab+1.5);
'''
summary=read(R.parent/'results/summary.json')
rule_ids=summary['test_rules']['review_ids']
extra_ids=[x for x in summary['test_hybrid']['review_ids'] if x not in rule_ids]
selector=lambda ids:','.join('#case-'+str(int(x.split('-')[1])-40) for x in ids)
evaljs=evaljs.replace('#case-3,#case-37,#case-65',selector(rule_ids))
evaljs=evaljs.replace('#case-4,#case-8,#case-12,#case-17,#case-24,#case-28,#case-32,#case-41,#case-49,#case-54,#case-62,#case-70,#case-77',selector(extra_ids))
comp('evaluation',evaluation,evaljs)

# Registry cursor adapted from the approved preview, with real button coordinates.
pointer='<div id="ui-pointer" class="cursor" data-layout-allow-overflow><span id="pointer-ring" class="click-ring"></span><svg viewBox="0 0 24 30"><path d="M5 3 L5 19 L9 15 L12 22 L15 20.5 L11.5 14 L18 14 Z"/></svg><span id="pointer-label" class="cursor-label" data-layout-allow-overflow>Reviewer</span></div>'
pointerjs='''gsap.set('#ui-pointer',{x:1430,y:600,opacity:0});gsap.set('#pointer-label',{opacity:0});
function cursor(x,y,s,click=true){tl.to('#ui-pointer',{opacity:1,x,y,duration:.4,ease:'power2.inOut'},s);if(click){tl.fromTo('#pointer-ring',{scale:.4,opacity:.85},{scale:1.65,opacity:0,duration:.45,immediateRender:false},s+.4);tl.to('#ui-pointer',{scale:.88,duration:.09},s+.39).to('#ui-pointer',{scale:1,duration:.15},s+.48);}}
cursor(1500,609,t.upload+.3);tl.to('#ui-pointer',{opacity:0,duration:.2},t.upload+1.5);
cursor(1460,405,t.inject+.9);tl.to('#ui-pointer',{opacity:0,duration:.25},t.rules-.3);
cursor(1450,716,t.review-.6);tl.to('#pointer-label',{opacity:1,duration:.2},t.review+.3);cursor(520,623,t.review+.4,false);cursor(1425,642,t.restore+.1);cursor(1450,712,t.confirm+.1);tl.to('#ui-pointer',{opacity:0,duration:.3},t.confirm+1.2);
'''
comp('pointer',pointer,pointerjs)

# Semantic captions: split at punctuation/meaningful clauses, never orphan a word.
sentences=re.split(r'(?<=[.!?])\s+',script)
overrides={
'An invoice can pass every arithmetic check and still contain the wrong amounts.':['An invoice can pass every arithmetic check','and still contain the wrong amounts.'],
'Mini CPM OCR reads its payment region into editable fields, keeping the source beside them.':['Mini CPM OCR reads its payment region into editable fields,','keeping the source beside them.'],
'The rules pass, although the original total is clearly different.':['The rules pass,','although the original total is clearly different.'],
'It receives the source image, the candidate text, and an image rendered from that text.':['It receives the source image, the candidate text,','and an image rendered from that text.'],
'That rendered copy makes the claimed content visible for comparison.':['That rendered copy makes the claimed content','visible for comparison.'],
'A small classification head scores two outcomes: consistent and inconsistent.':['A small classification head scores two outcomes:','consistent and inconsistent.'],
'We compare that score with a threshold chosen on separate calibration examples.':['We compare that score with a threshold','chosen on separate calibration examples.'],
'The reviewer opens its source, restores the correct amounts, and confirms the correction.':['The reviewer opens its source,','restores the correct amounts,','and confirms the correction.'],
'For accounts payable, the corrected fields can continue to purchase order matching and approval, with their evidence attached.':['For accounts payable, the corrected fields can continue','to purchase order matching and approval,','with their evidence attached.'],
'On eighty held out synthetic invoices, rules caught all three natural errors.':['On eighty held out synthetic invoices,','rules caught all three natural errors.'],
'The verifier added thirteen reviews and caught no extra errors.':['The verifier added thirteen reviews','and caught no extra errors.'],
'In a separate stress test, it flagged all twenty four deliberately altered candidates that passed the rules.':['In a separate stress test,','it flagged all twenty four deliberately altered candidates','that passed the rules.'],
'The online lab lets you inspect every case and explore that tradeoff yourself.':['The online lab lets you inspect every case','and explore that tradeoff yourself.']}
phrases=[]
for s in sentences:phrases.extend(overrides.get(s,[s]))
assert norm(' '.join(phrases))==norm(script)
groups=[];p=0
for phrase in phrases:
    start=at(phrase);endpos=p+len(norm(phrase));idx=max(i for i,x in enumerate(positions) if x<endpos)
    end=words[idx]['start']+words[idx]['duration']+.4
    display=phrase.replace('Mini CPM OCR','MiniCPM-OCR').replace('zero point nine nine','0.99').replace('zero point zero zero four','0.004')
    groups.append([start,end,display]);p=endpos
def stamp(t):
    x=round(t*1000);return f'{x//3600000:02d}:{x//60000%60:02d}:{x//1000%60:02d},{x%1000:03d}'
caps=[];srt=[]
for i,(start,end,text) in enumerate(groups):
    end=min(groups[i+1][0]-.04,end+.3) if i+1<len(groups) else end+.25
    caps.append(f'<div id="cap-{i}" class="clip caption" data-start="{start:.6f}" data-duration="{end-start:.6f}" data-track-index="3"><p>{html.escape(text)}</p></div>')
    srt.append(f'{i+1}\n{stamp(start)} --> {stamp(end)}\n{text}\n')
write(R.parent/'deliverables/document-verification-usd-full-en.srt','\n'.join(srt))
capcss=".caption{position:absolute;left:220px;right:220px;top:956px;height:76px;display:flex;align-items:center;justify-content:center}.caption p{background:#163431;color:white;font:29px/1.4 Inter,sans-serif;padding:12px 22px;border-radius:4px;text-align:center;margin:0}"
comp('captions',''.join(caps),'',capcss)
hosts=[]
for z,name in enumerate(['workspace','intake','mechanism','routing','evaluation','pointer','captions']):
    kind='captions' if name=='captions' else 'graphics'
    hosts.append(f'<div id="{name}" class="clip" style="position:absolute;inset:0;z-index:{z}" data-composition-id="{name}" data-composition-src="compositions/{name}.html" data-start="0" data-duration="{D}" data-track-index="{z}" data-track-kind="{kind}" data-width="1920" data-height="1080"></div>')
write(R/'index.html',f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><script src="assets/gsap.min.js"></script><style>*{{box-sizing:border-box;margin:0}}html,body{{width:1920px;height:1080px;overflow:hidden;background:#f3f5f2}}#root{{position:relative;width:100%;height:100%}}</style></head><body><div id="root" data-composition-id="main" data-width="1920" data-height="1080" data-duration="{D}">{''.join(hosts)}<audio id="narration-music" src="assets/audio/mix.wav" data-start="0" data-duration="{D}" data-track-index="7" data-track-kind="audio"></audio></div><script>const tl=gsap.timeline({{paused:true}});window.__timelines['main']=tl;</script></body></html>''')

# Preserve continuous speech. Lower the music in speech bands and under the voice.
rate=48000;clicks=[T['upload']+.7,T['inject']+1.3,T['review']-.2,T['restore']+.5,T['confirm']+.5]
samples=[0.0]*(D*rate)
for when in clicks:
    for j in range(3600):
        k=round(when*rate)+j
        if k<len(samples):samples[k]+=.018*math.sin(2*math.pi*820*j/rate)*math.exp(-j/(rate*.012))
with wave.open(str(R/'assets/audio/clicks.wav'),'wb') as w:
    w.setparams((1,2,rate,0,'NONE','not compressed'));w.writeframes(b''.join(struct.pack('<h',round(x*32767)) for x in samples))
ff=imageio_ffmpeg.get_ffmpeg_exe()
music=R/'assets/audio/ambient-piano.mp3'
inputs=['-i',str(R/'assets/audio/voice.mp3')]
filters=f'[0:a]adelay=400|400,volume=1.4,apad,atrim=0:{D}[v];'
if music.exists():
    inputs+=['-stream_loop','-1','-i',str(music),'-i',str(R/'assets/audio/clicks.wav')]
    filters+=f'[1:a]equalizer=f=2200:t=q:w=0.8:g=-5,volume=0.025,afade=t=in:d=1,afade=t=out:st={D-3}:d=3,atrim=0:{D}[m];[v][m][2:a]amix=inputs=3:normalize=0,alimiter=limit=0.89:level=0[out]'
else:
    inputs+=['-i',str(R/'assets/audio/clicks.wav')]
    filters+='[v][1:a]amix=inputs=2:normalize=0,alimiter=limit=0.89:level=0[out]'
    print('Background music absent: building with continuous narration and clicks.',flush=True)
subprocess.run([ff,'-hide_banner','-loglevel','error','-y',*inputs,'-filter_complex',filters,'-map','[out]','-ar','48000','-ac','2',str(R/'assets/audio/mix.wav')],check=True)
write(R/'audio_meta.json',json.dumps({'duration':D,'voice_end':words[-1]['start']+words[-1]['duration']+.4,'delay':.4,'music_included':music.exists(),'music_gain':.025 if music.exists() else 0,'music_speech_band_cut':{'frequency':2200,'q':.8,'gain_db':-5} if music.exists() else None,'click_times':clicks},indent=2))
print(json.dumps({'duration':D,'words':len(words),'timings':T},indent=2),flush=True)
