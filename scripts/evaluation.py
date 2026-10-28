"""Critical-field extraction and transparent rules; no ground truth in routing."""
import re
from decimal import Decimal,InvalidOperation
FIELDS=['subtotal','shipping','tax','total']
def parse_fields(text):
    text=re.sub(r'<[^>]+>',' ',text).replace('**','').replace('\\$','$')
    found={};issues=[];currencies=[]
    for line in text.splitlines():
        m=re.search(r'\b(subtotal|sub\s+total|shipping|freight|tax|total)\b',line,re.I)
        if not m:continue
        key=m.group(1).lower().replace(' ','');key='shipping' if key=='freight' else key
        tail=line[m.end():]
        currency=re.search(r'\b(USD|EUR|GBP|JPY)\b|([$€£])',tail,re.I)
        if currency:currencies.append(currency.group(1).upper() if currency.group(1) else {'$':'USD','€':'EUR','£':'GBP'}[currency.group(2)])
        nums=re.findall(r'(?<!\w)-?\d[\d,]*\.\d{2}(?!\d)',tail)
        if len(nums)!=1:issues.append('ambiguous_or_missing_'+key);continue
        if key in found:issues.append('duplicate_'+key);continue
        try:found[key]=int(Decimal(nums[0].replace(',',''))*100)
        except InvalidOperation:issues.append('invalid_'+key)
    if len(currencies)==4 and len(set(currencies))==1:found['currency']=currencies[0]
    else:issues.append('missing_or_inconsistent_currency')
    for key in FIELDS:
        if key not in found:issues.append('missing_'+key)
    return found,sorted(set(issues))
def rules(text):
    fields,issues=parse_fields(text)
    if all(k in fields for k in FIELDS):
        if abs(fields['subtotal']+fields['shipping']+fields['tax']-fields['total'])>1:issues.append('arithmetic_mismatch')
        if any(fields[k]<0 for k in FIELDS):issues.append('negative_amount')
    return fields,sorted(set(issues))
def label(fields,reference):return all(fields.get(k)==reference[k] for k in FIELDS+['currency'])
