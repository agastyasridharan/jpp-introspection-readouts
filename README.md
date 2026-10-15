# Introspection · J++ Lens

Static viewer for saved J++ experiments: 1,235 trial records, 209,938 block–token readouts, 19 configurations, three models. The layout and typography are adapted from [Assistant Privilegeness](https://agastyasridharan.github.io/assistant-privilegeness/), with only the J++ lens shown.

The dataset includes current natural-READY1 and filler experiments, the earlier Qwen3.6 block-selection study, superseded setup attempts, and the successful Neuronpedia probe. Older Qwen3-14B J-lens experiments and swapping experiments are outside this J++ archive. Historical protocols and limited top-N exports are labeled separately. One DeepSeek instrument trial was not run because of the deadline buffer. These are readouts, not evidence that introspective reporting succeeded.

No inference is performed by the viewer. Saved logits and rankings are preserved; API probabilities are labeled separately. Each trial is gzip-compressed and loaded on demand. Modern browsers with `DecompressionStream` are required.

`data/index.json` lists all trial files. `data/provenance.json` records SHA-256 hashes of the source artifacts and exports. `build_data.py` rebuilds from the local study directory and tokenizer caches; `audit_data.py` checks the exports. The published site contains only allowlisted experiment data and these source files, not GPU launchers, credentials, or environment logs.

Local preview: `python3 -m http.server 8771`.
