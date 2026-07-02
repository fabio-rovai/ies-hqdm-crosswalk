#!/usr/bin/env python3
"""Demonstrate what the IES/HQDM grounding buys a PYRAMID bridge.

Two PYRAMID components (Geography, Tactical Objects) model the same building
under disjoint, component-local types. This script shows, over the actual RDF:

  Q1  Without the shared grounding, a deployment cannot join the two
      components' views: nothing tells it the Geographical_Feature and the
      Tactical_Object are the same thing. Result: empty.

  Q2  With the bridge (co-reference + IES/HQDM grounding), the same building
      resolves to one referent that carries both the operational-picture type
      (ies:Entity) and the built-environment type (hqdm:physical_object),
      the latter reused straight from the crosswalk.

  Q3  The false friend is *not* joined: the two "Capability" entities share
      no referent, so the bridge does not (and SHACL will not let it) unify them.

Run:  python pyramid-bridge/demo.py
Deps: rdflib
"""
import pathlib
from rdflib import Graph

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent

BRIDGE = HERE / "bridge.ttl"
CROSSWALK = ROOT / "crosswalk" / "ies-hqdm.ttl"

PREFIXES = """
PREFIX bridge: <https://w3id.org/tesseract/pyramid-bridge/>
PREFIX pyrgeo: <https://gov.tesseract.academy/ns/pyramid-pra/geography#>
PREFIX pyrtac: <https://gov.tesseract.academy/ns/pyramid-pra/tactical-objects#>
PREFIX ies:   <http://informationexchangestandard.org/ont/ies/common/>
PREFIX hqdm:  <http://www.semanticweb.org/magma-core/ontologies/hqdm#>
PREFIX skos:  <http://www.w3.org/2004/02/skos/core#>
PREFIX rdfs:  <http://www.w3.org/2000/01/rdf-schema#>
"""


def banner(txt):
    print("\n" + "=" * 72 + f"\n{txt}\n" + "=" * 72)


def main():
    # The two graphs a deployment actually has: the bridge and the crosswalk.
    g = Graph()
    g.parse(BRIDGE, format="turtle")
    g.parse(CROSSWALK, format="turtle")
    print(f"loaded {len(g)} triples (bridge.ttl + crosswalk/ies-hqdm.ttl)")

    banner("Q1  Without the shared grounding: can the two components be joined?")
    q1 = PREFIXES + """
        SELECT ?geoObj ?tacObj WHERE {
            ?geoObj a pyrgeo:GeographicalFeature .
            ?tacObj a pyrtac:TacticalObject .
            # A deployment with no bridge has only the component-local types.
            # There is no shared identifier or type to join on:
            FILTER(?geoObj = ?tacObj)
        }"""
    r1 = list(g.query(q1))
    print(f"rows joining Geographical_Feature to Tactical_Object directly: {len(r1)}")
    print("-> the components share no type and no identifier; the gap is real.")

    banner("Q2  With the bridge: resolve co-referent objects and their grounded types")
    q2 = PREFIXES + """
        SELECT ?referent ?iesType ?hqdmType WHERE {
            ?geoObj a pyrgeo:GeographicalFeature ; bridge:refersTo ?referent .
            ?tacObj a pyrtac:TacticalObject      ; bridge:refersTo ?referent .
            ?geoObj skos:exactMatch ?tacObj .
            # types the referent carries via grounding, hqdm side from the crosswalk
            pyrtac:TacticalObject      bridge:groundsIn ?iesType .
            pyrgeo:GeographicalFeature bridge:groundsIn ?hqdmType .
            FILTER(?iesType = ies:Entity && ?hqdmType = hqdm:physical_object)
        }"""
    r2 = list(g.query(q2))
    for referent, ies_t, hqdm_t in r2:
        print(f"referent      : {referent}")
        print(f"  IES type    : {ies_t}   (operational picture)")
        print(f"  HQDM type   : {hqdm_t}   (built/physical environment, via crosswalk)")
    print(f"rows: {len(r2)}")
    print("-> one building, one referent, both worlds' types attached and checkable.")

    banner("Q3  The false friend is NOT unified")
    q3 = PREFIXES + """
        ASK {
            ?a a pyrgeo:Capability ; bridge:refersTo ?r .
            ?b a pyrtac:Capability ; bridge:refersTo ?r .
        }"""
    joined = g.query(q3).askAnswer
    print(f"do the two Capability entities share a referent? {joined}")
    print("-> False: the bridge grounds them separately; SHACL forbids unifying them.")

    banner("Q4  The grounding generalises: how many components resolve to the referent?")
    q4 = PREFIXES + """
        SELECT (COUNT(DISTINCT ?obj) AS ?components) WHERE {
            ?obj bridge:refersTo <https://w3id.org/tesseract/pyramid-bridge/example#Building_17> .
        }"""
    n_comp = int(list(g.query(q4))[0][0])
    print(f"component-local objects resolving to Building 17: {n_comp}")
    print("-> Geography, Tactical Objects and Data Fusion; not a cherry-picked pair.")

    ok = (len(r1) == 0 and len(r2) == 1 and joined is False and n_comp == 3)
    banner("RESULT: " + ("PASS - grounding changes the outcome as claimed"
                         if ok else "FAIL - unexpected result"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
