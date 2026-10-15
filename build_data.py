"""Export an allowlisted, immutable view of saved J++ readouts; no inference."""
import json,gzip,hashlib,collections
from pathlib import Path
from tokenizers import Tokenizer
ROOT=Path(__file__).resolve().parent; STUDY=ROOT.parent/'temporal-jlens-study'; O=STUDY/'outputs'; D=ROOT/'data';D.mkdir(exist_ok=True)
cache=Path.home()/'.cache/huggingface/hub'
models={'q36':'Qwen/Qwen3.6-27B','q35':'Qwen/Qwen3.5-122B-A10B','ds':'deepseek-ai/DeepSeek-V4-Flash'}
toks={k:Tokenizer.from_file(str(next((cache/('models--'+v.replace('/','--'))/'snapshots').glob('*/tokenizer.json')))) for k,v in models.items()}
manifest={'models':models,'groups':[],'missing':[{'model':'ds','trial':'filler12-instrument-calibration-001','reason':'Not run: reservation deadline buffer.'},{'model':'Gemma / OLMo','reason':'No successful lens readouts were collected; setup checks only.'}], 'scope':'Saved J++ experiments in this study, including superseded setup attempts and earlier block selection. Older Qwen3-14B J-lens experiments and activation swaps use a different lens/protocol and are not relabeled as J++.'}
groups={};provenance={};total=0

def read(f):
 return json.load(gzip.open(f,'rt') if str(f).endswith('.gz') else open(f))
def group(gid,model,title,desc):
 if gid not in groups:
  g=dict(id=gid,model=model,title=title,description=desc,trials=[]);groups[gid]=g;manifest['groups'].append(g)
 return groups[gid]
def add(gid,model,title,desc,d,ids,positions,rows,sources,response=None,boundary=None,note=''):
 global total
 g=group(gid,model,title,desc);ident=d['id'];uid=gid+'--'+ident
 assert not any(t['id']==ident for t in g['trials']),uid
 tokens=[toks[model].decode([i],skip_special_tokens=False) for i in ids]
 cells=collections.defaultdict(list)
 for x in rows:
  off=x.get('offset',0);assert off<len(positions)
  y=dict(x);top=y.pop('filtered_top100',y.pop('filtered_top20',[]));y['top']=top
  for s in y.get('scores',[]):
   if 'token_ids' not in s:s['token_ids']=[s['token_id']];s['form_logits']=[s['logit']]
   s['forms']=[toks[model].decode([i],skip_special_tokens=False) for i in s['token_ids']]
  cells[off].append(y)
 for off,rs in cells.items():assert len({x['layer'] for x in rs})==len(rs)
 ps=[]
 for i,pos in enumerate(positions):
  pos=dict(pos);pos['offset']=i;pos['text']=tokens[pos['position']];pos['kind']='generated' if boundary is not None and pos['position']>=boundary else 'supplied';ps.append(pos)
 phase=d.get('phase','preliminary');specified=d.get('specified_word',d.get('specified'))
 titletrial=d.get('setting') or d.get('title') or (specified+' · '+ident.rsplit('-',1)[-1] if specified else d.get('prompt','').split('. Think')[0].removeprefix('Imagine '))
 payload=dict(id=ident,group=gid,model=models[model],prompt=d.get('prompt',''),title=titletrial,category=d.get('category','instrument'),phase=phase,specified=specified,tokens=tokens,token_ids=ids,positions=ps,response=response,boundary=boundary,note=note,rows=rows if False else {str(k):v for k,v in cells.items()})
 raw=json.dumps(payload,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode();path=D/(uid+'.json.gz')
 with open(path,'wb') as f:f.write(gzip.compress(raw,mtime=0))
 hashes={str(f.relative_to(STUDY)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sources}
 provenance[uid]={'source_sha256':hashes,'export_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
 count=sum(len(x) for x in cells.values());total+=count
 g['trials'].append(dict(id=ident,title=titletrial,category=payload['category'],phase=phase,file=path.name,positions=len(ps),readouts=count))

# Existing audited token scan; retains every recorded block and position.
v=read(STUDY/'viewer/data/index.json')
for t in v['trials']:
 f=STUDY/'viewer/data'/(t['id']+'.json');d=read(f);scan=v['positions'][t['id']];rows=[];sources=[f]
 for pos in scan['positions']:
  rp=STUDY/'viewer/data/positions'/t['id']/(str(pos['offset'])+'.json.gz');sources.append(rp)
  rows.extend(dict(x,offset=pos['offset']) for x in read(rp))
 orig=read(next((O/'reporting-v1/positions'/t['phase']/'records').glob(t['id']+'.json')))
 # Initial sequence excludes generated READY1 and closing token (3 tokens).
 add('q36-natural','q36','Natural READY1 · token scan','24 silent situations + 92 known-item trials. All recorded suffix tokens; 63 fitted blocks. Maximum over accepted single-token forms.',d,scan['full_ids'],scan['positions'],rows,sources,d['response'],len(scan['full_ids'])-3)

for folder,label in [('reporting-filler-ws-20261013','Answer prefix'),('reporting-filler-20261013','Early punctuation setup'),('reporting-filler-explicit-20261013','Strict Answer setup')]:
 for f in sorted((O/folder).glob('*/records/*.json')):
  d=read(f);n=d['prefix']['filler_tokens'];gid=f'q36-{folder}-f{n}'
  ids=d['input_ids']+d['prefix']['token_ids'];boundary=len(ids);gen=d['generation'];ids+=gen['token_ids']+([gen['stop_id']] if gen.get('terminated') and gen.get('stop_id') is not None else [])
  note=f"Saved compliance: {d.get('compliant')}. Response preserved verbatim. Only the final prefix token was recorded."
  add(gid,'q36',f'{label} · {n} fillers','Supplied punctuation prefix; readout at the final prefix token. '+('Whitespace-normalized READY1 criterion.' if 'ws-' in folder else 'Superseded setup attempt; includes noncompliant responses.'),d,ids,[{'position':d['measurement_position']}],d['readouts'],[f],gen['text'],boundary,note)

for folder,model,label in [('qwen','q35','Natural READY1'),('deepseek-diagnostic','ds','Natural READY1 · diagnostic'),('deepseek-config-screen','ds','Filler screen')]:
 base=O/'moe-validation-20261013'/folder
 for f in sorted((base/'records').glob('*.json')):
  d=read(f);rp=base/'readouts'/(d['id']+'.json.gz');rows=read(rp);n=d.get('repeats');gid=model+'-'+folder+(f'-f{n}' if n is not None else '')
  desc='All saved token positions and fitted blocks. '+('12-trial exploratory diagnostic, not full validation.' if folder=='deepseek-diagnostic' else 'One known item and one silent situation per category. Supplied period-newline repetitions followed by Answer:. Instrument silent trial at 12 repetitions was not run.' if n is not None else '24 silent situations and 92 known-item trials.')
  add(gid,model,label+(f' · {n} repetitions' if n is not None else ''),desc,d,d['full_ids'],d['positions'],rows,[f,rp],d['response'],len(d['input_ids']),'DeepSeek candidate list replaces accordion with harp.' if model=='ds' else '')

# Earlier J++ data, clearly separated from the current multi-form protocol.
for folder,label in [('redo04','Earlier block selection'),('redo03-calibration-v2','Early calibration smoke'),('redo03-calibration-v2-complete-attempt','Early calibration attempt')]:
 for f in sorted((O/folder).rglob('records/*.json')):
  d=read(f)
  if not d.get('readouts'):continue
  phase=d.get('phase','calibration');gid='q36-'+folder+'-'+phase
  ids=list(d['initial']['ids']);boundary=len(ids);gen=d.get('natural_generation');response=None
  if gen:
   response=gen['text'];ids+=gen['token_ids']+([gen['stop_id']] if gen.get('terminated') and gen.get('stop_id') is not None else [])
  add(gid,'q36',label+' · '+phase,'Historical protocol: one accepted token per candidate, assistant-start readout; only top 20 vocabulary tokens saved. Separate from the current multi-form protocol.',d,ids,[{'position':d['site']}],d['readouts'],[f],response,boundary,'Historical run. Saved status: '+str(d.get('complete',d.get('checks_passed','not recorded'))))

# Successful API probe, preserving its lower top-N limit and reported probabilities.
f=O/'neuronpedia-model-screen/setup/qwen3.6-27b.json';d=read(f);ts=d['response']['tokens'];rows=[]
for off,t in enumerate(ts):
 result=next(x for x in t['results'] if x['type']=='JPP_LENS')
 for j,l in enumerate(d['response']['meta']['layers_by_type']['JPP_LENS']):
  rows.append(dict(offset=off,layer=l,filtered_top100=[dict(text=s,probability=p) for s,p in zip(result['top_tokens'][j],result['top_probs'][j])],scores=[]))
add('q36-api','q36','Neuronpedia API probe','One known-violin probe. API reports 64 layers, top 8 only; probabilities are API-rounded. No fixed-candidate scores were returned.',dict(id='api-violin',prompt=d['request']['chat'][0]['content'],phase='validation',category='instrument',specified_word='violin'),[t['id'] for t in ts],[{'position':i} for i in range(len(ts))],rows,[f],''.join(t['token'] for t in ts if t['is_generated']),d['response']['meta']['prompt_len'])
manifest['readouts']=total;manifest['trials']=sum(len(g['trials']) for g in groups.values())
(D/'index.json').write_text(json.dumps(manifest,ensure_ascii=False,separators=(',',':')))
(D/'provenance.json').write_text(json.dumps(provenance,separators=(',',':')))
print('EXPORTED',manifest['trials'],'trials',total,'readouts',len(groups),'groups')
