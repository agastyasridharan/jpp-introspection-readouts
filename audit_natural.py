"""Check published natural readouts against immutable saved experiment artifacts."""
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT.parent / 'temporal-jlens-study/outputs'
DATA = ROOT / 'natural/data'
load = lambda p: json.loads(p.read_text())
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
manifest = load(DATA / 'index.json')
provenance = load(DATA / 'provenance.json')
records = readouts = reports = 0
for group in manifest['groups']:
    for trial in group['trials']:
        path = DATA / trial['file']
        data = json.loads(gzip.decompress(path.read_bytes()))
        evidence = provenance[group['id'] + '--' + trial['id']]
        assert sha(path) == evidence['export_sha256']
        sources = [OUT / p for p in evidence['source_sha256']]
        for p in sources:
            assert sha(p) == evidence['source_sha256'][str(p.relative_to(OUT))]
        source = load(next(p for p in sources if p.parent.name in ('readouts', 'gpu-readouts')))
        generation = load(sources[0])
        tokens = generation.get('tokens', generation.get('response', {}).get('tokens'))
        assert data['tokens'] == [t['token'] for t in tokens]
        assert data['token_ids'] == [t['id'] for t in tokens]
        assert data['boundary'] == next(t['position'] for t in tokens if t['is_generated'])
        for position in data['positions']:
            assert position['text'] == data['tokens'][position['position']]
            for row in data['rows'][str(position['offset'])]:
                original = next(r for r in source['rows'] if r['position'] == position['position'] and r['block'] == row['layer'])
                assert [t['token_id'] for t in row['top']] == original['ids']
                assert [t['logit'] for t in row['top']] == original['logits']
                assert [t['text'] for t in row['top']] == original['tokens']
                for score in row['scores']:
                    assert score['logit'] == max(score['form_logits'])
                    assert score['word'] not in row['absent_candidates']
                for k in (20, 50, 100):
                    ids = {t['token_id'] for t in row['top'][:k]}
                    assert row['distinct_items_top_k'][str(k)] == sum(bool(ids.intersection(s['token_ids'])) for s in row['scores'])
                readouts += 1
        if data['reporting']:
            original = load(next(p for p in sources if p.parent.name == 'outputs'))['responses']
            assert len(original) == len(data['reporting'])
            for saved, exported in zip(original, data['reporting']):
                for key in ('condition', 'order', 'options', 'text', 'prompt_ids'):
                    assert saved[key] == exported[key]
                reports += 1
        records += 1
assert records == manifest['trials'] == 102
assert readouts == manifest['readouts'] == 11154
assert reports == 422
print(f'PASS: {records} records, {readouts} exact readouts, {reports} reporting responses')
