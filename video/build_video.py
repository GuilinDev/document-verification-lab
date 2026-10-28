"""Build a deterministic narrated film from recorded experimental evidence."""
import html,json,re,shutil,subprocess,wave,math,struct
from pathlib import Path
import imageio_ffmpeg
ROOT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def write(p,s):p.write_text(s,encoding='utf-8')
data=read(ROOT.parent/'site/evidence.json');cases={c['case_id']:c for c in data['cases']}
good=cases['invoice-040-reference'];bad=cases['invoice-040-consistent_amounts'];words=read(ROOT/'assets/audio/words.json');segments=read(ROOT/'narration.json')
norm=lambda s:re.sub('[^a-z0-9]','',s.lower())
stream=''.join(norm(w['text']) for w in words);positions=[];offset=0
for w in words:positions.append(offset);offset+=len(norm(w['text']))
starts=[]
for segment in segments:
    prefix=norm(' '.join(segment.split()[:7]));p=stream.find(prefix)
    assert p>=0,prefix
    i=max(i for i,x in enumerate(positions) if x<=p);starts.append(words[i]['start']+.55)
starts[0]=0
duration=words[-1]['start']+words[-1]['duration']+1.7
ends=starts[1:]+[duration]
assets=ROOT/'assets/evidence';assets.mkdir(parents=True,exist_ok=True)
for c in [good,bad]:
    for key in ['page','region','render_image']:
        src=ROOT.parent/'site'/c[key];shutil.copyfile(src,assets/src.name)
img=lambda c,k:'assets/evidence/'+Path(c[k]).name
e=html.escape
css='''@font-face{font-family:Inter;src:url('assets/fonts/InterVariable.woff2')}*{box-sizing:border-box}#root{position:absolute;inset:0;width:100%;height:100%;background:#f6f6ef;color:#163431;font-family:Inter,sans-serif}.body{position:absolute;inset:104px 192px 176px}.kicker{font-size:21px;font-weight:700;letter-spacing:3px;color:#096b5b;margin:0 0 26px}.title{font-size:60px;line-height:1.12;letter-spacing:-2px;font-weight:620;margin:0 0 35px}.sub{font-size:28px;line-height:1.45;color:#546b68;margin:18px 0}.row{display:flex;align-items:center;gap:48px}.half{flex:1;min-width:0}.sheet{background:#fff;border:1px solid #d6dfd5;border-radius:6px;padding:24px}.label{font-size:20px;font-weight:700;color:#546b68;letter-spacing:1.7px;margin:0 0 18px}.region{display:block;object-fit:contain;width:100%;max-height:300px}.text{white-space:pre-wrap;font-size:30px;line-height:1.8;font-weight:500;margin:0}.big{font-size:82px;letter-spacing:-3px;font-weight:600;margin:10px 0}.good{color:#096b5b}.bad{color:#a52d24}.tag{display:inline-block;padding:12px 20px;border-radius:3px;background:#e5eee9;color:#096b5b;font-size:24px;font-weight:600}.tag.bad{background:#fbe6df;color:#a52d24}.line{height:2px;background:#d6dfd5;margin:24px 0}.note{font-size:23px;color:#546b68;line-height:1.45}.arrow{font-size:42px;color:#096b5b}.topbar{position:absolute;top:38px;left:64px;right:64px;display:flex;justify-content:space-between;font-size:17px;letter-spacing:2px;color:#546b68}.foot{position:absolute;bottom:136px;left:192px;font-size:22px;color:#546b68}'''
bodies=[]
bodies.append(f'''<div class="body"><p class="kicker">DOCUMENT VERIFICATION LAB</p><h1 class="title">Can a valid sum hide bad OCR?</h1><div class="row"><img src="{img(good,'page')}" style="height:555px;width:440px;object-fit:contain" alt="Synthetic invoice DVL0040"><div class="half"><p class="label">FOLLOW ONE INVOICE · DVL-0040</p><div class="sheet"><img class="region" src="{img(good,'region')}" alt="Original payment details"></div><p class="sub">The amount printed on the page</p><div class="big good">€6,416.03</div></div></div></div>''')
bodies.append(f'''<div class="body"><p class="kicker">CONTROLLED STRESS TEST / ALL AMOUNTS ×10</p><h1 class="title">The arithmetic still works.</h1><div class="row"><div class="half"><p class="label">ORIGINAL SOURCE</p><div class="sheet"><img class="region" src="{img(good,'region')}" alt="Original payment region"></div><p class="big good" style="font-size:66px">€6,416.03</p></div><div class="half"><p class="label">ALTERED CANDIDATE</p><div class="sheet"><pre class="text">{e(bad['text'])}</pre></div><p class="big bad" style="font-size:66px">€64,160.30</p></div></div><div class="line"></div><span class="tag">Required fields ✓</span> <span class="tag">Currency consistent ✓</span> <span class="tag">Subtotal + shipping + tax = total ✓</span></div>''')
bodies.append(f'''<div class="body"><p class="kicker">MINICPM-OCR JEV / 2B CLASSIFIER</p><h1 class="title">Compare the result with the pixels.</h1><div class="row" style="gap:22px;align-items:stretch"><div class="sheet half"><p class="label">1 / SOURCE IMAGE</p><img class="region" src="{img(good,'region')}" style="height:180px" alt="Source image"></div><div class="sheet half"><p class="label">2 / CANDIDATE TEXT</p><pre class="text" style="font-size:21px">{e(bad['text'])}</pre></div><div class="sheet half"><p class="label">3 / RENDERED CANDIDATE</p><img class="region" src="{img(bad,'render_image')}" style="height:180px" alt="Actual candidate rendering"></div></div><p class="sub" style="margin:30px 0 12px">Consistency score: higher = stronger predicted agreement</p><div class="row"><div class="half"><p class="label">CORRECT TRANSCRIPTION</p><div class="big good">{good['score']:.4f}</div></div><span class="arrow">→</span><div class="half"><p class="label">AMOUNTS MULTIPLIED BY TEN</p><div class="big bad">{bad['score']:.4f}</div></div></div><p class="note">One score from a classification head. No generated explanation.</p></div>''')
bodies.append('''<div class="body"><p class="kicker">REAL OCR OUTPUTS / HELD-OUT EVALUATION</p><h1 class="title">The extra model added extra review.</h1><p class="sub">120 generated invoices → 40 calibration + 80 held out</p><div class="row" style="margin-top:50px;align-items:flex-start"><div class="half"><p class="label">REGIONS SENT TO REVIEW · OUT OF 80</p><div class="chart-row"><b>Rules</b><div class="rail"><i class="bar" style="--w:18.75%;background:#096b5b"></i></div><strong>3</strong></div><div class="chart-row"><b>Rules + verifier</b><div class="rail"><i class="bar" style="--w:100%;background:#a52d24"></i></div><strong>16</strong></div><p class="note">Both policies caught all 3 natural errors.</p></div><div style="width:400px;padding-left:40px;border-left:2px solid #d6dfd5"><p class="label">ADDITIONAL CORRECT ITEMS REVIEWED</p><div class="big bad" style="font-size:128px">13</div><p class="sub">No additional natural errors caught in this test.</p></div></div></div>''')
bodies.append('''<div class="body"><p class="kicker">SEPARATE STRESS SET / DELIBERATE SUBSTITUTIONS</p><h1 class="title">A useful capability to investigate.</h1><p class="sub">12 complete currency changes + 12 consistent amount changes</p><div class="row" style="margin-top:55px;gap:100px"><div class="half"><p class="label">FLAGGED BY RULES</p><div class="big" style="font-size:140px">0 <span style="font-size:62px;color:#546b68">/ 24</span></div><p class="sub">Each candidate is internally consistent.</p></div><span class="arrow">→</span><div class="half"><p class="label">FLAGGED WITH THE VISUAL VERIFIER</p><div class="big good" style="font-size:140px">24 <span style="font-size:62px;color:#546b68">/ 24</span></div><p class="sub">The source pixels expose the mismatch.</p></div></div><div class="line"></div><p class="note">Designed probes are kept separate from natural OCR errors.</p></div>''')
bodies.append('''<div class="body"><p class="kicker">SUPPLIER-INVOICE WORKFLOWS</p><h1 class="title">Measure what each check adds.</h1><div class="row" style="align-items:stretch;margin:60px 0"><div class="half"><p class="label">01 / EXTRACT</p><h2 style="font-size:40px">Keep the evidence</h2><p class="sub">Attach the source region to the extracted fields.</p></div><span class="arrow">→</span><div class="half"><p class="label">02 / REVIEW</p><h2 style="font-size:40px">Measure the tradeoff</h2><p class="sub">Extra errors caught per extra human review.</p></div><span class="arrow">→</span><div class="half"><p class="label">03 / VALIDATE</p><h2 style="font-size:40px">Check the context</h2><p class="sub">Purchase orders, receipts and business policy.</p></div></div><div class="line"></div><p style="font-size:43px;font-weight:600;margin:25px 0 18px">Explore every case. Change the threshold.</p><p class="good" style="font-size:29px">huggingface.co/spaces/guilindev/document-verification-lab</p><p class="note">Guilin Zhang · Open inputs, code and results</p></div>''')
extra='''.chart-row{display:grid;grid-template-columns:210px 1fr 70px;gap:25px;align-items:center;margin:35px 0;font-size:28px}.chart-row strong{font-size:48px}.rail{height:58px;background:#e5eae2;border-radius:3px}.bar{display:block;width:var(--w);height:100%;transform-origin:left center;border-radius:3px}'''
(ROOT/'compositions').mkdir(exist_ok=True)
hosts=[]
for i,(body,start,end) in enumerate(zip(bodies,starts,ends)):
    name='scene-'+str(i+1);dur=end-start
    animation=f"const tl=gsap.timeline({{paused:true}});tl.fromTo('#{name}-content',{{opacity:0,y:18}},{{opacity:1,y:0,duration:.45,ease:'power2.out'}},0);"
    if i==3:animation+="tl.fromTo('.bar',{scaleX:0},{scaleX:1,duration:1,ease:'power2.out',stagger:.2},1);"
    animation+=f"window.__timelines['{name}']=tl;"
    write(ROOT/'compositions'/f'{name}.html',f'''<template><style>{css}{extra}</style><div id="root" data-composition-id="{name}" data-width="1920" data-height="1080"><div class="topbar"><span>DVL / GUILIN ZHANG</span><span>{i+1:02d} / 06</span></div><div id="{name}-content">{body}</div></div><script>{animation}</script></template>''')
    hosts.append(f'<div id="{name}" class="clip" data-composition-id="{name}" data-composition-src="compositions/{name}.html" data-start="{start:.6f}" data-duration="{dur:.6f}" data-track-index="0" data-track-kind="graphics" data-width="1920" data-height="1080"></div>')
# Phrased captions from one continuous voice stream.
groups=[];group=[]
for w in words:
    if group and (len(' '.join(x['text'] for x in group+[w]))>72 or len(group)>=12):groups.append(group);group=[]
    group.append(w)
    if len(group)>=5 and re.search(r'[.!?]$',w['text']):groups.append(group);group=[]
if group:groups.append(group)
cap=[];srt=[]
def stamp(t):
    ms=round(t*1000);return f'{ms//3600000:02d}:{ms//60000%60:02d}:{ms//1000%60:02d},{ms%1000:03d}'
for j,g in enumerate(groups):
    start=g[0]['start']+.55;end=(groups[j+1][0]['start']+.55-.035) if j+1<len(groups) else g[-1]['start']+g[-1]['duration']+.85
    text=' '.join(w['text'] for w in g)
    cap.append(f'<div id="caption-{j}" class="clip caption" data-start="{start:.6f}" data-duration="{end-start:.6f}" data-track-index="3" data-track-kind="captions"><p>{e(text)}</p></div>')
    srt.append(f'{j+1}\n{stamp(start)} --> {stamp(end)}\n{text}\n')
write(ROOT.parent/'deliverables/walkthrough-en.srt','\n'.join(srt))
rootstyle="@font-face{font-family:Inter;src:url('assets/fonts/InterVariable.woff2')}*{box-sizing:border-box;margin:0}html,body{width:1920px;height:1080px;overflow:hidden;background:#f6f6ef}#root{position:relative;width:100%;height:100%}.caption{position:absolute;left:220px;right:220px;top:938px;height:84px;z-index:50;display:flex;align-items:center;justify-content:center}.caption p{background:#163431;color:white;font:29px/1.35 Inter,sans-serif;text-align:center;padding:12px 22px;border-radius:4px;max-width:1450px}"
captionstyle="@font-face{font-family:Inter;src:url('assets/fonts/InterVariable.woff2')}#root{position:absolute;inset:0;width:100%;height:100%;background:transparent}.caption{position:absolute;left:220px;right:220px;top:938px;height:84px;z-index:50;display:flex;align-items:center;justify-content:center}.caption p{background:#163431;color:white;font:29px/1.35 Inter,sans-serif;text-align:center;padding:12px 22px;border-radius:4px;max-width:1450px}"
write(ROOT/'compositions/captions.html',f'''<template><style>{captionstyle}</style><div id="root" data-composition-id="captions" data-width="1920" data-height="1080">{''.join(cap)}</div><script>const tl=gsap.timeline({{paused:true}});window.__timelines['captions']=tl;</script></template>''')
caption_host=f'<div id="captions" class="clip" style="position:absolute;inset:0;z-index:50;pointer-events:none" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{duration:.6f}" data-track-index="3" data-track-kind="captions" data-width="1920" data-height="1080"></div>'
write(ROOT/'index.html',f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><script src="assets/gsap.min.js"></script><style>{rootstyle}</style></head><body><div id="root" data-composition-id="main" data-width="1920" data-height="1080" data-duration="{duration:.6f}">{''.join(hosts)}{caption_host}<audio id="voice-music" src="assets/audio/mix.wav" data-start="0" data-duration="{duration:.6f}" data-track-index="4" data-track-kind="audio"></audio></div><script>const tl=gsap.timeline({{paused:true}});window.__timelines['main']=tl;</script></body></html>''')
write(ROOT/'timing.json',json.dumps({'starts':starts,'ends':ends,'duration':duration,'voice_offset':.55},indent=2))
# Deterministic quiet taps mark the scene changes. They are synthesized, not stock.
rate=48000;n=round(duration*rate);taps=[0.0]*n
for when in starts[1:]:
    for j in range(round(.09*rate)):
        ix=round(when*rate)+j
        if ix<n:taps[ix]+=.025*math.sin(2*math.pi*740*j/rate)*math.exp(-j/(rate*.016))
with wave.open(str(ROOT/'assets/audio/taps.wav'),'wb') as w:w.setparams((1,2,rate,0,'NONE','not compressed'));w.writeframes(b''.join(struct.pack('<h',round(x*32767)) for x in taps))
ff=imageio_ffmpeg.get_ffmpeg_exe()
filters=f'[0:a]adelay=550|550,apad,atrim=0:{duration},volume=1.4[v];[1:a]volume=0.032,afade=t=in:d=1,afade=t=out:st={duration-2}:d=2,atrim=0:{duration}[m];[2:a]volume=1[t];[v][m][t]amix=inputs=3:normalize=0,alimiter=limit=0.89:level=0[out]'
subprocess.run([ff,'-hide_banner','-loglevel','error','-y','-i',str(ROOT/'assets/audio/voice.mp3'),'-stream_loop','-1','-i',str(ROOT/'assets/audio/ambient-piano.mp3'),'-i',str(ROOT/'assets/audio/taps.wav'),'-filter_complex',filters,'-map','[out]','-ar','48000','-ac','2',str(ROOT/'assets/audio/mix.wav')],check=True)
print('BUILT',duration,'seconds; starts',starts)
