import asyncio,json
from pathlib import Path
import edge_tts
ROOT=Path(__file__).resolve().parent
async def main():
    text=(ROOT/'narration.txt').read_text(encoding='utf-8').strip();words=[]
    voice=edge_tts.Communicate(text,'en-US-AndrewNeural',rate='+3%',boundary='WordBoundary')
    with (ROOT/'assets/audio/voice.mp3').open('wb') as f:
        async for c in voice.stream():
            if c['type']=='audio':f.write(c['data'])
            elif c['type']=='WordBoundary':words.append({'text':c['text'],'start':c['offset']/1e7,'duration':c['duration']/1e7})
    (ROOT/'assets/audio/words.json').write_text(json.dumps(words,indent=2),encoding='utf-8')
    print('VOICE_END',words[-1]['start']+words[-1]['duration'],flush=True)
asyncio.run(main())
