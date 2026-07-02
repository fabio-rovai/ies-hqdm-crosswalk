#!/usr/bin/env python3
"""
Reference alignment pipeline for the IES <-> HQDM crosswalk.

This script is the transparent, dependency-light reference implementation of the
FIRST stage (candidate generation) and the VALIDATION stage of the pipeline
described in the README. The heavy adjudication stages (fuzzy-logic scoring,
agentic/structural adjudication, LLM oracle on the uncertain subset) are run by
Tesseract's open-ontologies engine and are described, not reimplemented, here.

Pipeline (README section "Method"):
  1. candidate generation   <- this script (lexical + structure-lite)
  2. fuzzy adjudication      <- open-ontologies `align_flora` (FLORA, arXiv:2510.20467)
  3. LLM oracle on uncertain <- open-ontologies `align_oracle` (arXiv:2508.08500)
  4. symbolic repair         <- open-ontologies `align_repair` (BERTMap-style)
  5. documentation           <- SSSOM (crosswalk/ies-hqdm.sssom.tsv)
  6. validation              <- this script (--validate) + pyshacl over shapes/

Usage:
  python scripts/align.py --candidates          # naive candidates, for triage
  python scripts/align.py --validate            # check curated TSV IRIs resolve in the ontologies
  python scripts/align.py --coverage            # what fraction of backbone classes the curated set covers

Requires: rdflib (pip install rdflib). Ontology files are fetched on first run
if not present in ./vendor/.
"""
from __future__ import annotations
import argparse, csv, os, sys, urllib.request
from pathlib import Path

IES_URL  = "https://raw.githubusercontent.com/IES-Org/ont-ies/main/docs/specification/ies-common.ttl"
HQDM_URL = "https://raw.githubusercontent.com/gchq/HQDM/main/hqdm.owl"
IES_NS   = "http://informationexchangestandard.org/ont/ies/common/"
HQDM_NS  = "http://www.semanticweb.org/magma-core/ontologies/hqdm#"

ROOT = Path(__file__).resolve().parent.parent
VENDOR = ROOT / "vendor"
TSV = ROOT / "crosswalk" / "ies-hqdm.sssom.tsv"


def _fetch(url: str, dest: Path) -> Path:
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        print(f"fetching {url} -> {dest}", file=sys.stderr)
        urllib.request.urlretrieve(url, dest)
    return dest


def _defined_terms(graph, ns):
    """All local names in `ns` that the ontology defines (any rdf:type: class or
    property). IES types classes as rdfs:Class; HQDM as owl:Class; both declare
    object/data properties. We accept any typed subject in the namespace."""
    from rdflib import RDF
    return {str(s)[len(ns):] for s, _, _ in graph.triples((None, RDF.type, None))
            if str(s).startswith(ns)}


def _load_classes():
    """Return (ies_terms, hqdm_terms): all defined local names per ontology."""
    from rdflib import Graph
    ies_g = Graph().parse(_fetch(IES_URL, VENDOR / "ies-common.ttl"), format="turtle")
    hqdm_g = Graph().parse(_fetch(HQDM_URL, VENDOR / "hqdm.owl"))
    return _defined_terms(ies_g, IES_NS), _defined_terms(hqdm_g, HQDM_NS)


def _norm(name: str) -> str:
    return name.replace("_", "").replace(" ", "").lower()


def _read_curated():
    rows = []
    with open(TSV) as fh:
        for line in fh:
            if line.startswith("#") or line.startswith("subject_id"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 5:
                rows.append(parts)
    return rows


def cmd_candidates():
    ies, hqdm = _load_classes()
    hqdm_norm = {_norm(h): h for h in hqdm}
    hits = 0
    for i in sorted(ies):
        key = _norm(i)
        if key in hqdm_norm:
            print(f"LEXICAL\ties:{i}\thqdm:{hqdm_norm[key]}")
            hits += 1
    print(f"\n{hits} lexical candidate pairs. NOTE: lexical matches include FALSE FRIENDS "
          f"(e.g. Event/event), see DIVERGENCES.md. This is candidate generation only; "
          f"real correspondences come from adjudication (stages 2-4).", file=sys.stderr)


def cmd_validate():
    ies, hqdm = _load_classes()
    problems = 0
    for row in _read_curated():
        subj = row[0].split(":", 1)[1]
        obj = row[3].split(":", 1)[1]
        if subj not in ies:
            print(f"UNRESOLVED IES TERM: {row[0]}"); problems += 1
        if obj not in hqdm:
            print(f"UNRESOLVED HQDM TERM: {row[3]}"); problems += 1
    n = len(_read_curated())
    print(f"\n{n} correspondences checked; {problems} unresolved IRIs.", file=sys.stderr)
    sys.exit(1 if problems else 0)


def cmd_coverage():
    ies, _ = _load_classes()
    backbone = {"Thing", "Element", "Entity", "State", "Event", "PeriodOfTime",
                "ParticularPeriod", "BoundingState", "PossibleWorld",
                "EventParticipant", "ClassOfElement"}
    mapped = {r[0].split(":", 1)[1] for r in _read_curated()}
    covered = backbone & mapped
    print(f"backbone classes covered: {len(covered)}/{len(backbone)}")
    for b in sorted(backbone - covered):
        print(f"  UNMAPPED: ies:{b}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidates", action="store_true")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--coverage", action="store_true")
    a = ap.parse_args()
    if a.candidates: cmd_candidates()
    elif a.validate: cmd_validate()
    elif a.coverage: cmd_coverage()
    else: ap.print_help()


if __name__ == "__main__":
    main()
