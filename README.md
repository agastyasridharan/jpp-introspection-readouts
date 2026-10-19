# Introspection · J++ Lens

Static viewer for saved J++ experiments: 1,235 trial records, 209,938 block–token readouts, 19 configurations, three models. The layout and typography are adapted from [Assistant Privilegeness](https://agastyasridharan.github.io/assistant-privilegeness/), with only the J++ lens shown.

The dataset includes current natural-READY1 and filler experiments, the earlier Qwen3.6 block-selection study, superseded setup attempts, and the successful Neuronpedia probe. Older Qwen3-14B J-lens experiments and swapping experiments are outside this J++ archive. Historical protocols and limited top-N exports are labeled separately. One DeepSeek instrument trial was not run because of the deadline buffer. These are readouts, not evidence that introspective reporting succeeded.

No inference is performed by the viewer. Saved logits and rankings are preserved; API probabilities are labeled separately. Each trial is gzip-compressed and loaded on demand. Modern browsers with `DecompressionStream` are required.

`data/index.json` lists all trial files. `data/provenance.json` records SHA-256 hashes of the source artifacts and exports. `build_data.py` rebuilds from the local study directory and tokenizer caches; `audit_data.py` checks the exports. The published site contains only allowlisted experiment data and these source files, not GPU launchers, credentials, or environment logs.

Local preview: `python3 -m http.server 8771`.

## Natural recommendations and reporting

The separate [natural section](https://agastyasridharan.github.io/jpp-introspection-readouts/natural/) contains four tabs: the 24-situation natural-recommendation pilot, the 40-situation instrument replication, the 11-situation two-option reporting pilot, and the 27-situation free-naming/four-option reporting experiment. Its 102 trial records and 11,154 block–token readouts cover 64 distinct situations; reporting tabs reuse their original-state readouts. The earlier archive remains at the root URL.

Reporting tabs include exact questions, answers, option orders, and saved scores for 422 responses, plus downloadable reports and scored results. Their target is the final prompt token at block 53 regardless of the viewer selection. There are no reporting-answer activation readouts. The original generated recommendation was not supplied to reporting branches. These exploratory comparisons do not establish introspective access.

`build_natural.py` exports allowlisted source data to `natural/data/`; `audit_natural.py` verifies source hashes, token positions, vocabulary readouts, candidate scores, and reporting responses. Candidate scores are reconstructed only where an accepted token form occurs in the saved top 100. Missing candidates have unknown scores, not zero.
