"""Exact upstream prompt, native Transformers binary head, no answer generation."""
import argparse,json,time,hashlib,sys,platform
from pathlib import Path
import torch,transformers
from PIL import Image
from transformers import AutoProcessor,Qwen3_5ForSequenceClassification
ROOT=Path(__file__).resolve().parents[1]
UP=ROOT/'vendor/MiniCPM-OCR/scripts/minicpm-ocr-jev';sys.path.insert(0,str(UP))
from infer_vllm import build_prompt,PROMPT_TEMPLATE_MD5,load_image

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--probe',action='store_true');args=ap.parse_args()
    torch.set_num_threads(4);torch.manual_seed(42)
    base=ROOT/'models/MiniCPM-OCR-Jev'
    proc=AutoProcessor.from_pretrained(base,local_files_only=True)
    t=time.perf_counter()
    model,info=Qwen3_5ForSequenceClassification.from_pretrained(base,num_labels=2,dtype=torch.bfloat16,device_map='cuda',attn_implementation='sdpa',output_loading_info=True,local_files_only=True)
    model.eval()
    if info.get('missing_keys') or info.get('mismatched_keys'):raise RuntimeError(str(info))
    env={'backend':'Transformers native Qwen3_5ForSequenceClassification, not vLLM','torch':torch.__version__,'transformers':transformers.__version__,'python':platform.python_version(),'gpu':torch.cuda.get_device_name(),'model_load_seconds':time.perf_counter()-t,'loading_info':str(info),'prompt_template_md5':PROMPT_TEMPLATE_MD5,'num_labels':2,'shared_gpu':True,'score_definition':'softmax(logits)[1] at the last nonpadding token; no posthoc calibration','model_revision':json.loads((ROOT/'results/model-lock.json').read_text())['MiniCPM-OCR-Jev']['revision']}
    (ROOT/'results/verifier-environment.json').write_text(json.dumps(env,indent=2))
    if args.probe:
        ex=UP/'examples/01_text_putnam';doc=json.loads((ex/'case.json').read_text());c=doc['candidates'][1]
        rows=[{'case_id':'probe-upstream-inconsistent','image_path':str(ex/'block.png'),'text':c['text'],'render':{'ok':True,'render_image_path':str(ex/'reference_render.png')},'expected_prob_yes':doc['observed_prob_yes']['ocr_output']}]
        out=ROOT/'results/probe.jsonl'
    else:
        rows=json.loads((ROOT/'results/rendered-candidates.json').read_text());out=ROOT/'results/verifier.jsonl'
    done={json.loads(s)['case_id'] for s in out.read_text().splitlines()} if out.exists() else set()
    for i,row in enumerate(rows):
        if row['case_id'] in done:continue
        result={'case_id':row['case_id'],'set':row.get('set','probe')}
        if not row['render']['ok']:
            result.update(prob_yes=None,verdict=row['render']['reason'],error=row['render']['detail'])
        else:
            try:
                t=time.perf_counter();images=[load_image(ROOT/row['image_path']),load_image(ROOT/row['render']['render_image_path'])]
                prompt=build_prompt(row['text']);inputs=proc(text=[prompt],images=images,return_tensors='pt').to('cuda')
                assert inputs['input_ids'][0,-1].item()==271,inputs['input_ids'][0,-15:]
                torch.cuda.synchronize();p=time.perf_counter()
                with torch.inference_mode():logits=model(**inputs,use_cache=False).logits
                torch.cuda.synchronize();end=time.perf_counter();probs=logits.float().softmax(-1)[0].tolist()
                result.update(prob_yes=probs[1],prob_no=probs[0],logits=logits.float()[0].tolist(),verdict='scored',input_tokens=inputs['input_ids'].shape[1],preprocess_ms=(p-t)*1000,forward_ms=(end-p)*1000,total_ms=(end-t)*1000,error=None,expected_prob_yes=row.get('expected_prob_yes'))
            except Exception as e:
                result.update(prob_yes=None,verdict='runtime_error',error=f'{type(e).__name__}: {e}')
        with out.open('a') as f:f.write(json.dumps(result,ensure_ascii=False)+'\n');f.flush()
        print(json.dumps({'n':i+1,**result},ensure_ascii=False),flush=True)
        if result['verdict']=='runtime_error':raise RuntimeError(result['error'])
        time.sleep(.05)
if __name__=='__main__':main()
