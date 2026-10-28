"""Deterministic, wholly fictional invoices with source-value labels.

120 source pages; one known payment-region crop per page. No customer documents.
"""
from pathlib import Path
import hashlib,io,json,random
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter

ROOT=Path(__file__).resolve().parents[1]
FONTS=Path('C:/Windows/Fonts')
def font(name,size): return ImageFont.truetype(str(FONTS/name),size)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def money(cents): return f'{cents/100:,.2f}'
def capture(im,variant,seed):
    rng=np.random.default_rng(seed); original=im.size
    names=['clean','jpeg','soft_blur','small_capture','strong_blur','skew','sensor_noise','tiny_capture','shadow','faded_scan']
    if variant==1:
        b=io.BytesIO();im.save(b,'JPEG',quality=24);b.seek(0);im=Image.open(b).convert('RGB')
    if variant in [2,4]: im=im.filter(ImageFilter.GaussianBlur(1.1 if variant==2 else 2.4))
    if variant in [3,7]:
        factor=.25 if variant==3 else .13
        im=im.resize((round(im.width*factor),round(im.height*factor)),Image.Resampling.LANCZOS).resize(original,Image.Resampling.BICUBIC)
    if variant==5: im=im.rotate(2.8,resample=Image.Resampling.BICUBIC,expand=False,fillcolor='white')
    if variant==6:
        a=np.asarray(im).astype(float);im=Image.fromarray(np.clip(a+rng.normal(0,24,a.shape),0,255).astype('uint8'))
    if variant==8:
        a=np.asarray(im).astype(float);mask=np.linspace(.42,1.0,im.width)[None,:,None];im=Image.fromarray(np.clip(a*mask,0,255).astype('uint8'))
    if variant==9:
        a=np.asarray(im).astype(float)*.23+196; a[::3,:,:]-=12; im=Image.fromarray(np.clip(a,0,255).astype('uint8')).filter(ImageFilter.GaussianBlur(.8))
    return im,names[variant]

def main():
    out=ROOT/'data/synthetic';out.mkdir(parents=True,exist_ok=True)
    templates=[('arial.ttf','#176B66'),('calibri.ttf','#315C88'),('times.ttf','#8D4B32'),('consola.ttf','#47466B'),('segoeui.ttf','#185D7E'),('georgia.ttf','#67503F'),('verdana.ttf','#48693E'),('tahoma.ttf','#7F475C'),('trebuc.ttf','#375F6C'),('cambria.ttc','#695735'),('arial.ttf','#8C4B30'),('calibri.ttf','#265B61')]
    rows=[]
    for family,(face,accent) in enumerate(templates):
        for variant in range(10):
            ix=family*10+variant;r=random.Random(20261028+ix);case=f'invoice-{ix:03d}'
            currency=['USD','EUR','GBP'][family%3]
            qty=[r.randrange(2,24) for _ in range(3)];unit=[r.randrange(825,32500) for _ in range(3)]
            subtotal=sum(q*u for q,u in zip(qty,unit));shipping=r.randrange(1200,9200);tax=round(subtotal*.075);total=subtotal+shipping+tax
            values=dict(subtotal=subtotal,shipping=shipping,tax=tax,total=total,currency=currency)
            ref='\n'.join(f'{key.title()} {currency} {money(values[key])}' for key in ['subtotal','shipping','tax','total'])
            im=Image.new('RGB',(1500,1900),'#FFFFFF');d=ImageDraw.Draw(im)
            left=100+(family%3)*30
            d.rectangle((0,0,1500,32),fill=accent)
            d.text((left,115),f'FIELDLINE {family+1:02d}',font=font(face,49),fill=accent)
            d.text((left,185),'Industrial supplies · evaluation company',font=font(face,25),fill='#52606C')
            d.text((1080,115),'INVOICE',font=font('arialbd.ttf',42),fill='#1C2935')
            d.text((1080,180),f'DVL-{ix:04d}',font=font(face,30),fill='#394956')
            d.text((left,315),'BILL TO',font=font('arialbd.ttf',21),fill=accent)
            d.text((left,360),'Northfield Operations Lab',font=font(face,34),fill='#1C2935')
            d.text((left,410),'Accounts Payable / Research Example',font=font(face,27),fill='#52606C')
            d.text((960,335),f'PO: LAB-{10000+ix}',font=font(face,28),fill='#1C2935')
            d.text((960,385),'Issued: 28 Oct 2026',font=font(face,27),fill='#52606C')
            d.rectangle((left,560,1400,620),fill=accent)
            for x,t in [(left+15,'ITEM'),(830,'QTY'),(990,'UNIT PRICE'),(1220,'AMOUNT')]:d.text((x,575),t,font=font('arialbd.ttf',22),fill='white')
            for j,desc in enumerate(['Inspection kit','Replacement filter','Cable assembly']):
                y=665+j*94
                for x,t in [(left+15,desc),(840,str(qty[j])),(990,money(unit[j])),(1210,money(qty[j]*unit[j]))]:d.text((x,y),t,font=font(face,28),fill='#263645')
                d.line((left,y+57,1400,y+57),fill='#DCE2E6',width=2)
            cropw=780+(family%2)*80;croph=340+(family%3)*15
            block=Image.new('RGB',(cropw,croph),'white');bd=ImageDraw.Draw(block)
            fsize=34+(family%3)*3
            for j,line in enumerate(ref.splitlines()):
                bd.text((35,32+j*69),line,font=font(face,fsize),fill='#15232D')
            block,condition=capture(block,variant,20261028+ix)
            x=1400-cropw;y=1040+(family%3)*28
            im.paste(block,(x,y))
            d=ImageDraw.Draw(im)
            d.text((left,1570),'Please reference the invoice and purchase order numbers.',font=font(face,25),fill='#52606C')
            d.text((left,1750),'Generated evaluation document · no real transaction',font=font('arial.ttf',22),fill='#76838C')
            pp=out/f'{case}-page.png';bp=out/f'{case}-region.png';im.save(pp,optimize=True);block.save(bp,optimize=True)
            rows.append({'id':case,'template_family':family,'split':'calibration' if family<4 else 'test','condition':condition,'page':pp.relative_to(ROOT).as_posix(),'region':bp.relative_to(ROOT).as_posix(),'region_bbox':[x,y,x+cropw,y+croph],'reference_text':ref,'reference_fields':values,'page_sha256':sha(pp),'region_sha256':sha(bp),'purchase_order':{'currency':currency,'subtotal':subtotal,'quantities':qty},'items':[{'description':desc,'quantity':q,'unit_price':u} for desc,q,u in zip(['Inspection kit','Replacement filter','Cable assembly'],qty,unit)]})
    (ROOT/'data/manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
    print(json.dumps({'pages':len(rows),'calibration':40,'test':80,'templates':12,'root':str(out)}))
if __name__=='__main__':main()
