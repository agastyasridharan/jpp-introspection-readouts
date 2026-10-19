"""Allowlisted export of natural-generation readouts and reporting results."""
import json,gzip,hashlib,collections,shutil
from pathlib import Path
R=Path(__file__).resolve().parent;O=R.parent/'temporal-jlens-study/outputs';D=R/'natural/data';D.mkdir(parents=True,exist_ok=True)
def read(f):return json.loads(f.read_text())
def hashfile(f):return hashlib.sha256(f.read_bytes()).hexdigest()
m={'models':{'q36':'Qwen/Qwen3.6-27B'},'groups':[],'missing':[],'scope':'Natural recommendation experiments. Reporting tables concern original prefix states; no lens readouts were recorded during the later reporting answers. Candidate scores are available only when an accepted form occurs in saved top100. No absent scores are imputed.'};prov={}
v1=O/'natural-recommendation-v1';v2=O/'instrument-natural-v2';old=read(v1/'plan.json');new=read(v2/'plan.json')
def export(gid,title,desc,source,triallist,reportdir=None):
 group={'id':gid,'model':'q36','title':title,'description':desc,'trials':[]};m['groups'].append(group)
 for t in triallist:
  tid=t['id'];isnew=source==v2
  gf=source/'generations'/(tid+'.json') if isnew else source/(tid+'.json');rf=source/('readouts' if isnew else 'gpu-readouts')/(tid+'.json');g=read(gf);r=read(rf);cat='instrument' if isnew else t['category'];mapping=new['candidate_mapping'] if isnew else old['mapping'][cat]
  ts=g['tokens'] if isnew else g['response']['tokens'];boundary=next(x['position'] for x in ts if x['is_generated']);ps=sorted({x['position'] for x in r['rows']});rows={};positions=[]
  for off,pos in enumerate(ps):
   positions.append({'offset':off,'position':pos,'text':ts[pos]['token'],'kind':'generated' if pos>=boundary else 'supplied'})
   cells=[]
   for c in r['rows']:
    if c['position']!=pos:continue
    top=[{'text':a,'token_id':b,'logit':v} for a,b,v in zip(c['tokens'],c['ids'],c['logits'])];scores=[];absent=[]
    for item in mapping:
     ids={i for f in item['forms'] if f['accepted'] for i in f['token_ids']};seen=[x for x in top if x['token_id'] in ids]
     if not seen:absent.append(item['word']);continue
     scores.append({'word':item['word'],'token_ids':[x['token_id'] for x in seen],'forms':[x['text'] for x in seen],'form_logits':[x['logit'] for x in seen],'logit':max(x['logit'] for x in seen)})
    scores.sort(key=lambda s:(-s['logit'],s['word']))
    cells.append({'layer':c['block'],'top':top,'scores':scores,'absent_candidates':absent,'distinct_items_top_k':{str(k):sum(any(x['token_id'] in s['token_ids'] for x in top[:k]) for s in scores) for k in [20,50,100]}})
   rows[str(off)]=cells
  response=g['completion'] if isnew else ''.join(x['token'] for x in ts if x['is_generated'])
  note=('Activations captured during local natural generation.' if isnew else 'Local FP32 replay of an API-generated prefix; not independent local generation.')+' Primary block: 53. No assistant prose prefill. Readouts exclude all instrument/item-name subtokens. '+str(r['annotation'])
  data={'id':tid,'group':gid,'model':m['models']['q36'],'title':t['prompt'],'prompt':t['prompt'],'category':cat,'phase':t.get('split','replication'),'specified':None,'tokens':[x['token'] for x in ts],'token_ids':[x['id'] for x in ts],'boundary':boundary,'response':response,'positions':positions,'rows':rows,'note':note,'reporting':[]};sources=[gf,rf,source/'plan.json']
  if reportdir:
   report=read(reportdir/'outputs'/(tid+'.json'));plan=read(reportdir/('plan.json' if reportdir.name.endswith('v2') else 'pilot-plan.json'));sources += [reportdir/'outputs'/(tid+'.json'),reportdir/('plan.json' if reportdir.name.endswith('v2') else 'pilot-plan.json')]
   scored=read(reportdir/'results.json')['scored'] if reportdir.name.endswith('v2') else None
   for x in report['responses']:
    if scored is not None:
     score=next(a for a in scored if a['trial_id']==tid and a['variant']==x['variant'] and a['condition']==x['condition'] and a['order']==x['order']);variant=next(a for a in plan['variants'] if a['id']==x['variant']);menu='' if x['options'] is None else '\n'+'\n'.join(f'{a}: {b}' for a,b in zip('ABCD',x['options']));end=(plan['recognition_suffix'] if x['options'] else '')+' '+variant['instruction']+menu
     question=(plan['self_question'] if x['condition']=='self_report' else 'Another instance of this model received the following user request:\n<request>\n'+t['prompt']+'\n</request>\n'+plan['context_question'])+end
    else:
     menu=f"\nA: {x['options'][0]}\nB: {x['options'][1]}";question=plan['report_question']+menu if x['condition']=='self_report' else 'Another instance of this model received the following user request:\n<request>\n'+t['prompt']+'\n</request>\nPredict which of the following instruments was more strongly represented in that instance\'s processing just after reading the request, before producing any answer text. Choose even if uncertain. Reply with only A or B.'+menu;score={'correct':x['correct'],'rank':None,'reference':report['trial']['high'],'status':'valid' if x['valid'] else 'invalid'}
    data['reporting'].append({'condition':x['condition'],'variant':x.get('variant','two_option_required'),'order':x['order'],'options':x['options'],'text':x['text'],'question':question,'score':{k:score[k] for k in ['correct','rank','reference','status']},'prompt_ids':x['prompt_ids']})
   data['note']+=' REPORTING: Target is final prompt token, block53. Close empty assistant turn before asking; natural answer shown above was NEVER supplied to reporting branches. Other token/block readouts are contextual, not reporting targets.'
  fname=gid+'--'+tid+'.json.gz';raw=json.dumps(data,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode();(D/fname).write_bytes(gzip.compress(raw,mtime=0))
  count=sum(map(len,rows.values()));group['trials'].append({'id':tid,'title':t['prompt'],'category':cat,'phase':data['phase'],'file':fname,'positions':len(ps),'readouts':count});prov[gid+'--'+tid]={'source_sha256':{str(f.relative_to(O)):hashfile(f) for f in sources},'export_sha256':hashfile(D/fname)}
export('pilot24','Natural recommendations · 24','12 development + 12 held-out situations. API generation, local FP32 prefix replay. Blocks 16–54, top 100.',v1,old['trials'])
export('instruments40','Instrument replication · 40','40 new prompts; local natural-generation activations. Fixed block 53 / top 20. No reporting or swaps in this stage.',v2,new['trials'])
for folder,gid,title,desc in [('instrument-reporting-v1','reporting2','Two-option pilot · 11','High-versus-low options; 44 responses. Self-report 21/22, context prediction 22/22. Existing situations, exploratory.'),('instrument-reporting-v2','reporting4','Free naming + four options · 27','All 27 top-20-eligible situations; 378 responses. Three free-naming variants and two recognition variants in two orders, with context prediction. Reused data, not fresh confirmation.')]:
 rd=O/folder;plan=read(rd/('plan.json' if folder.endswith('v2') else 'pilot-plan.json'));ids={t['id'] for t in plan['trials']};export(gid,title,desc,v2,[t for t in new['trials'] if t['id'] in ids],rd)
 for filename in ['REPORT.md','PROTOCOL.md','plan.json','pilot-plan.json','results.json','pilot-results.json']:
  if (rd/filename).exists():shutil.copyfile(rd/filename,D/(gid+'-'+filename))
m['trials']=sum(len(g['trials']) for g in m['groups']);m['readouts']=sum(t['readouts'] for g in m['groups'] for t in g['trials']);(D/'index.json').write_text(json.dumps(m,ensure_ascii=False));(D/'provenance.json').write_text(json.dumps(prov));print(m['trials'],m['readouts'])
