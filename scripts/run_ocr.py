import argparse,json,time,hashlib,platform,subprocess,traceback
from pathlib import Path
import torch,transformers
from PIL import Image
from transformers import AutoProcessor,MiniCPMOcrForConditionalGeneration
ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,default=120);args=ap.parse_args()
    torch.set_num_threads(4);torch.manual_seed(42)
    modelpath=ROOT/'models/MiniCPM-OCR-1.0'
    proc=AutoProcessor.from_pretrained(modelpath,local_files_only=True)
    start=time.perf_counter()
    model,info=MiniCPMOcrForConditionalGeneration.from_pretrained(modelpath,dtype=torch.bfloat16,device_map='cuda',attn_implementation='sdpa',output_loading_info=True,local_files_only=True)
    model.eval();loadsecs=time.perf_counter()-start
    assert not info.get('missing_keys') and not info.get('mismatched_keys'),info
    (ROOT/'results/ocr-environment.json').write_text(json.dumps({'torch':torch.__version__,'transformers':transformers.__version__,'python':platform.python_version(),'gpu':torch.cuda.get_device_name(),'model_load_seconds':loadsecs,'loading_info':str(info),'shared_gpu':True,'decoding':'greedy; max_new_tokens=256; no DSpark','model_revision':json.loads((ROOT/'results/model-lock.json').read_text())['MiniCPM-OCR-1.0']['revision']},indent=2))
    rows=json.loads((ROOT/'data/manifest.json').read_text())[:args.limit]
    out=ROOT/'results/ocr.jsonl';done={json.loads(s)['id'] for s in out.read_text().splitlines()} if out.exists() else set()
    for i,row in enumerate(rows):
        if row['id'] in done:continue
        result={'id':row['id'],'source_sha256':row['region_sha256'],'prompt':'Text Recognition:'}
        try:
            im=Image.open(ROOT/row['region']).convert('RGB')
            messages=[{'role':'user','content':[{'type':'image'},{'type':'text','text':'Text Recognition:'}]}]
            prompt=proc.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=False)
            t=time.perf_counter();inputs=proc(text=[prompt],images=[im],return_tensors='pt').to('cuda')
            torch.cuda.synchronize();p=time.perf_counter()
            with torch.inference_mode(): gen=model.generate(**inputs,max_new_tokens=256,do_sample=False,use_cache=True)
            torch.cuda.synchronize();end=time.perf_counter()
            tail=gen[0,inputs['input_ids'].shape[1]:];text=proc.decode(tail,skip_special_tokens=True)
            result.update(text=text,input_tokens=inputs['input_ids'].shape[1],output_tokens=len(tail),preprocess_ms=(p-t)*1000,generation_ms=(end-p)*1000,total_ms=(end-t)*1000,truncated=len(tail)>=256,error=None)
        except Exception as e:
            result.update(text='',error=f'{type(e).__name__}: {e}');traceback.print_exc()
        with out.open('a') as f:f.write(json.dumps(result,ensure_ascii=False)+'\n');f.flush()
        print(json.dumps({'n':i+1,**result},ensure_ascii=False),flush=True)
        if result.get('error'):raise RuntimeError(result['error'])
        time.sleep(.05)
if __name__=='__main__':main()
