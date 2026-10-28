import inspect,json,struct
from pathlib import Path
import transformers
print('TRANSFORMERS',transformers.__version__)
print('OCR CLASS',hasattr(transformers,'MiniCPMOcrForConditionalGeneration'))
print('CLASSIFIER',inspect.getsource(transformers.Qwen3_5ForSequenceClassification))
root=Path(__file__).resolve().parents[1]
for name in ['MiniCPM-OCR-1.0','MiniCPM-OCR-Jev']:
    base=root/'models'/name
    print(name,(base/'config.json').read_text())
    path=base/'model.safetensors'
    if path.exists():
        with path.open('rb') as f:
            n=struct.unpack('<Q',f.read(8))[0];h=json.loads(f.read(n))
        print('KEYS',list(h)[:6],list(h)[-6:])
        print('HEADS',[(k,v) for k,v in h.items() if k.endswith('score.weight') or k.endswith('lm_head.weight')])
print('OCR TEMPLATE',(root/'models/MiniCPM-OCR-1.0/chat_template.jinja').read_text())
