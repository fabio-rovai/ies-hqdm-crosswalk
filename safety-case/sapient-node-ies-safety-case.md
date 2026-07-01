# Worked safety case: grounding a SAPIENT edge node's autonomy in IES

A worked example of the three-layer model from the companion working paper: interface agreement (SAPIENT / BSI Flex 335), assurance-argument structure (a CAE safety case), and a shared world model (IES). The point of the example is narrow and concrete: to show that grounding the safety-case leaves in an IES-typed world model turns them from prose assertions into machine-checkable propositions, and that a CIVeX certificate is the natural evidence node for the leaf that classical safety cases cannot discharge.

This is illustrative, built entirely on public standards and open ontologies. It is not a certified safety case and asserts nothing about any real system.

## The system under assurance

A single **SAPIENT edge node**: an autonomous sensor that detects objects in its field of view, classifies them, and reports detections over the SAPIENT interface (BSI Flex 335) to a fusion node. This is exactly the unit BSI Flex 335 standardises: an autonomous sensor/effector node exchanging messages, including run-time-defined detection taxonomies.

SAPIENT (Layer 1) tells us how the node's messages are structured. It does not tell us whether the autonomy producing those messages is safe, nor whether two nodes mean the same thing by a "detection." That is what the safety case (Layer 2), grounded in IES (Layer 3), supplies.

## The shared world model (Layer 3, IES types)

We commit the node's world model to IES terms, so that "what the node believes" is expressed in the same 4D vocabulary the rest of the force uses. Using the crosswalk in this repository, these terms also carry over to HQDM where the mission touches the built environment.

| World-model element | IES type |
|---|---|
| A detected object (persisting thing) | `ies:Entity` |
| The object's condition at a time (e.g. "moving") | `ies:State` (e.g. `ies:EntityInTransit`) |
| A detection (a happening with participants) | `ies:Event` (an occurrence; see note) |
| The node's role in the detection | `ies:EventParticipant` (via `ies:isParticipantIn`) |
| When the detection holds | `ies:ParticularPeriod` (ISO8601) |
| Where it holds | `ies:Location` / `ies:GeoPoint` |
| The class the object was assigned | `ies:ClassOfEntity` (the SAPIENT run-time taxonomy term) |

Note: a "detection" is a happening with participants, so it is an `ies:Event`, which the crosswalk maps to `hqdm:activity`, not the instantaneous `hqdm:event`. Getting this right is the difference between a coherent shared picture and a subtly corrupt one (see `../DIVERGENCES.md` #1). This is a concrete instance of why the world model has to be typed, not just messaged.

## The safety case (Layer 2, CAE)

Structured as Claims-Argument-Evidence, following the Dstl-sponsored templates for autonomous systems (Bloomfield et al., 2021, arXiv:2102.02625). Each leaf claim is written as a proposition over the IES-typed world model, so it is a query, not an assertion.

**C0 (top claim).** The edge node's autonomous detect-classify-report behaviour is acceptably safe and interoperable within the networked system.

**A0 (argument).** C0 holds if (C1) every report is well-typed against the shared IES world model, (C2) each report action causally achieves its intended effect on the fusion picture, and (C3) the node detects and flags when the world moves outside the operating design domain the case was built on.

### C1 — Reports are well-typed against the shared world model (soundness and interoperability)

*Claim as a query:* every emitted detection is an `ies:Event` with exactly one `ies:EventParticipant` linking to the node, an object typed `ies:Entity`, a classification drawn from an agreed `ies:ClassOfEntity`, an `ies:ParticularPeriod`, and a location; and it does not mis-instantiate `ies:Event` as an HQDM-style instantaneous boundary.

*Evidence:* SHACL validation of each outgoing report against IES report shapes. This is the same class of check this repository already runs over the crosswalk itself (`shapes/`). A report that omits the participation state, or types the detection as a boundary rather than an occurrence, fails validation before it is emitted. This leaf is fully machine-checkable, which the prose version ("detections are correctly formed") is not.

### C2 — Each report causally achieves its intended effect (the leaf classical cases cannot discharge)

*Claim as a query:* issuing report R causes the fusion node's picture to include the intended, correctly-typed detection, and this effect is identifiable rather than confounded (for example by a duplicate track, a spoofed input, or a stale prior).

*Evidence:* a **CIVeX certificate** (Rovai, 2026, arXiv:2605.09168). CIVeX maps the action "emit report R" to a causal query over the node's action-state graph, checks identifiability, and returns EXECUTE / REJECT / EXPERIMENT / ABSTAIN with an assumption-scoped certificate recording the graph commitments, the identification argument, a one-sided lower confidence bound, provenance and risk limits. The certificate is attached as the evidence node for C2. This is the primitive the assurance literature lacks: existing templates check that a report is *valid*, not that emitting it *causally produces the intended fused effect*. The world model the certificate is evaluated over is the IES-typed event graph, which is why C2 and C1 share a substrate.

### C3 — The validity envelope is machine-detectable (operating design domain)

*Claim as a query:* the node continuously checks whether the current situation still satisfies the IES-typed conditions the case assumes (sensor within its stated `ies:State` of health, environment within the assumed `ies:ClassOf...` conditions, time within the mission `ies:ParticularPeriod`), and raises a defeater when it does not.

*Evidence:* the operating design domain expressed as an IES-typed condition, monitored at runtime. Because the domain is a query over the shared world model rather than prose, "the world has moved outside the case's validity" becomes a detectable event, not a post-hoc finding. This closes the gap named across the assurance literature: cases that cannot tell, at runtime, that they no longer apply.

## Why this composes across suppliers

The decisive property is that C1 to C3 are stated over a *shared* world model, not the node's private one. A second supplier's node, assured the same way against the same IES types, produces detections that compose with the first node's, and a fusion node can reason over both without a bespoke per-supplier mapping. Two independently assured nodes are also *jointly* assurable, because their claims quantify over the same referents. This is the coalition-interoperability gap and the safe-reuse gap closed in one substrate, which is the whole argument of the working paper reduced to one node.

## Machine-readable fragment

See `safety-case.ttl` for the CAE structure as RDF, with each leaf's IES type binding and evidence node, validatable with the same tooling as the crosswalk.

## References

- Dstl / BSI (2024). BSI Flex 335 (SAPIENT): Network of autonomous sensors and effectors, Interface control, v2.0.
- Bloomfield, R., et al. (2021). Safety Case Templates for Autonomous Systems. arXiv:2102.02625 (Dstl-sponsored).
- Rovai, F. (2026). CIVeX: Causal Intervention Verification for Language Agents. arXiv:2605.09168.
- IES: `IES-Org/ont-ies`, Open Government Licence. HQDM: `gchq/HQDM`, Apache-2.0.
