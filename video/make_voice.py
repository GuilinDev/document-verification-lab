import asyncio,json,re
from pathlib import Path
import edge_tts
ROOT=Path(__file__).resolve().parent
async def main():
    segments=json.loads((ROOT/'narration.json').read_text());text='\n\n'.join(segments)
    out=ROOT/'assets/audio';out.mkdir(parents=True,exist_ok=True);words=[]
    voice=edge_tts.Communicate(text,'en-US-AndrewNeural',rate='+8%',boundary='WordBoundary')
    with (out/'voice.mp3').open('wb') as f:
        async for c in voice.stream():
            if c['type']=='audio':f.write(c['data'])
            elif c['type']=='WordBoundary':words.append({'text':c['text'],'start':c['offset']/1e7,'duration':c['duration']/1e7})
    (out/'words.json').write_text(json.dumps(words,indent=2));(ROOT/'narration.txt').write_text(text)
    print('WORDS',len(words),'LAST_END',words[-1]['start']+words[-1]['duration'])
asyncio.run(main())
