# IES ↔ HQDM crosswalk

**The first public crosswalk between the UK Information Exchange Standard (IES) and the Higher Quality Data Model (HQDM).** Two 4D upper ontologies from the same BORO / ISO 15926 tradition, one grown for defence and national-security data, one underpinning the National Digital Twin. Nobody had published a machine-readable alignment between them. This repository is a candidate-for-review crosswalk, released so that people building across the two can start from something concrete rather than from scratch.

Maintained by [Tesseract Academy](https://gov.tesseract.academy). Companion to the working paper *Trusted, Interoperable Autonomy for UK Defence Data: Grounding Assurance in a Shared 4D Ontology* (Rovai, 2026).

## Why this exists

The UK Defence Investment Plan (June 2026) commits over £5bn to autonomous systems and £7.5bn to a Digital Backbone and Digital Targeting Web that only work if heterogeneous systems, and coalition partners, share data a machine can reason over. On the UK side that shared vocabulary is IES. Alongside it, the built-and-physical-environment world runs on HQDM and the National Digital Twin Foundation Data Model. An autonomous system reasoning about a mission in a real place has to connect what IES says about the operational picture to what HQDM says about the terrain and infrastructure. Today that join is manual, because no published crosswalk exists. This repository is a first, open, honest attempt at it.

The two ontologies are cousins (shared BORO and ISO 15926 heritage), so most of the 4D backbone maps cleanly. The interesting content is where they do not: see **[DIVERGENCES.md](DIVERGENCES.md)**.

## What is here

| Path | What it is |
|---|---|
| `crosswalk/ies-hqdm.sssom.tsv` | The crosswalk in [SSSOM](https://mapping-commons.github.io/sssom/) format: subject, predicate, object, justification, confidence, comment. The canonical artifact. |
| `crosswalk/ies-hqdm.ttl` | The same correspondences as SKOS mapping triples with PROV-O provenance, plus two worked reified correspondences. |
| `DIVERGENCES.md` | The scholarship: the pairs that look like they map and do not. Read this first. |
| `shapes/crosswalk-shapes.ttl` | SHACL shapes validating the reified correspondences (every mapping has a subject, object, SKOS predicate, confidence in [0,1], and provenance). |
| `scripts/align.py` | The reference candidate-generation and validation pipeline (rdflib). |
| `safety-case/` | A worked example: grounding the autonomy of a SAPIENT (BSI Flex 335) sensor node in an IES-typed world model. |
| `pyramid-bridge/` | A worked example: grounding a PYRAMID (Def Stan 00-134) inter-component bridge in IES/HQDM, so two PRA components that model the same object resolve to one referent. |

## Sources (both open)

- **IES**: `IES-Org/ont-ies`, `docs/specification/ies-common.ttl`, namespace `http://informationexchangestandard.org/ont/ies/common/`. Open Government Licence v3. Custodian: the cross-government IES Working Group (DBT).
- **HQDM**: `gchq/HQDM`, `hqdm.owl`, namespace `http://www.semanticweb.org/magma-core/ontologies/hqdm#`. Apache-2.0, Crown Copyright.

This repository references those ontologies by IRI and does not redistribute them. The crosswalk asserts correspondences between their terms.

## Method

The curated backbone in v0.1.0 was hand-authored from the two published ontologies and grounded in their shared 4D commitments. It is the seed. The pipeline that extends it beyond the backbone, and that the wider `class-of` hierarchies genuinely need, is:

1. **Candidate generation**, embedding retrieval over class and relation representations (after LLMs4OM, arXiv:2404.10317), with HNSW as the nearest-neighbour primitive. `scripts/align.py --candidates` gives the naive lexical baseline for triage.
2. **Fuzzy adjudication**, interpretable, convergent fuzzy-logic scoring over classes and relations (FLORA, arXiv:2510.20467), with structural adjudication (KROMA, arXiv:2507.14032) for the cases where temporal-part structure, not lexical similarity, decides.
3. **LLM oracle on the uncertain subset**, an LLM used only to validate high-uncertainty correspondences (arXiv:2508.08500), never to generate them blind.
4. **Symbolic repair**, consistency checking of accepted correspondences (BERTMap-style, arXiv:2112.02682).
5. **Documentation**, every correspondence recorded in SSSOM with predicate, confidence, and justification; complex non-1:1 correspondences expressed in EDOAL rather than forced into SKOS.
6. **Validation**, SHACL over `shapes/`, following the published PROV-O→BFO mapping (Scientific Data, 2025) as the methodological template.

Stages 2 to 4 run in Tesseract's [open-ontologies](https://github.com/fabio-rovai/open-ontologies) engine. This repository ships the seed, the documentation, the validation, and the reference candidate generator, so the whole method is inspectable.

## Validate it yourself

```bash
pip install rdflib pyshacl
python scripts/align.py --validate      # curated IRIs resolve in both ontologies
python scripts/align.py --coverage      # backbone coverage report
pyshacl -s shapes/crosswalk-shapes.ttl -df turtle crosswalk/ies-hqdm.ttl
```

## Status and honesty

- This is **v0.1.0, candidate-for-review**. It is not an endorsed mapping, and it is not affiliated with Dstl, GCHQ, the IES Working Group, or the NDTP.
- The "first public crosswalk" claim is bounded by the visibility of public artifacts; a non-public government mapping cannot be excluded. A final check with the IES Working Group and the primary IES implementers is invited, and issues correcting or extending any correspondence are the most welcome kind of contribution.
- Every correspondence carries a confidence that is the curator's subjective strength, not a measured score. The pipeline above is how those become measured.

## How to contribute

The highest-value contribution is a **new divergence** (a pair that looks like it maps and does not, with evidence from both ontologies), or a **correction** to a correspondence. Adding another easy backbone match is worth less. Open an issue or a PR against the SSSOM file and DIVERGENCES.md.

## Licence

The crosswalk data and documentation in this repository are released under **CC-BY-4.0** (see `LICENSE`). The upstream ontologies keep their own licences (IES: OGL v3; HQDM: Apache-2.0), noted in `NOTICE`.

## Cite

See `CITATION.cff`. Contact: [gov.tesseract.academy](https://gov.tesseract.academy).
