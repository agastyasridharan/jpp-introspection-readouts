import gzip,json,hashlib,math,re
from pathlib import Path
r=Path(__file__).parent;d=r/'data';m=json.loads((d/'index.json').read_text());prov=json.loads((d/'provenance.json').read_text());count=0
for g in m['groups']:
 for t in g['trials']:
  f=d/t['file'];raw=f.read_bytes();p=json.loads(gzip.decompress(raw));assert hashlib.sha256(raw).hexdigest()==prov[g['id']+'--'+t['id']]['export_sha256']
  assert len(p['token_ids'])==len(p['tokens']);assert len(p['positions'])==t['positions'];assert len({x['position'] for x in p['positions']})==len(p['positions'])
  for pos in p['positions']:assert p['tokens'][pos['position']]==pos['text']
  for off,rows in p['rows'].items():
   assert 0<=int(off)<len(p['positions']);assert len({x['layer'] for x in rows})==len(rows)
   for x in rows:
    count+=1;assert len(x['top']) in [8,20,100]
    for v in x['top']:assert math.isfinite(v.get('logit',v.get('probability')))
    for s in x['scores']:
     assert math.isfinite(s['logit']);assert s['logit']==max(s['form_logits']);assert len(s['forms'])==len(s['token_ids'])==len(s['form_logits'])
    for k,value in x.get('distinct_items_top_k',{}).items():
     ids={v['token_id'] for v in x['top'][:int(k)]};assert value==sum(bool(ids&set(s['token_ids'])) for s in x['scores'])
  # Structured export contains prompts and scores only, never runtime credentials.
  text=gzip.decompress(raw).decode();assert not re.search(r'sk-or-v1-[a-zA-Z0-9]{20,}|hf_[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{20,}|BEGIN (?:RSA |OPENSSH )?PRIVATE KEY',text)
assert count==m['readouts'];print('PASS',m['trials'],'trials;',count,'readouts; hashes, token positions, finite scores, form maxima, candidate counts and secret scan')
