# Where IES and HQDM diverge

This is the part of the crosswalk that is not engineering but scholarship. IES and HQDM are cousins: both are 4D upper ontologies descended from the BORO method and ISO 15926, so most of the backbone maps cleanly (see `crosswalk/ies-hqdm.sssom.tsv`). The value is in the pairs that look like they should map and do not, because those are where an implementer aligning a system to both models will silently get it wrong.

Each divergence below is grounded in the published ontologies: IES from `IES-Org/ont-ies` (`docs/specification/ies-common.ttl`, namespace `http://informationexchangestandard.org/ont/ies/common/`) and HQDM from `gchq/HQDM` (`hqdm.owl`, namespace `http://www.semanticweb.org/magma-core/ontologies/hqdm#`).

## 1. `ies:Event` is not `hqdm:event` (the headline false friend)

The single most dangerous correspondence in the whole crosswalk is the one a name-matcher makes first and gets exactly backwards.

- **`ies:Event`** is defined as "an Event represents an activity or incident, involving one or more participants." It is a *happening* with extent and participants. In IES it is a subclass of `ies:Element` (a spatio-temporal extent).
- **`hqdm:event`** is an *instantaneous temporal boundary*: a point that marks where a state or individual begins or ends. It has no participants and no duration.

So the true counterpart of `ies:Event` is **`hqdm:activity`**, and the true counterpart of `hqdm:event` is, on the IES side, the boundary machinery around `ies:BoundingState` (divergence 2), not `ies:Event` at all. Any tool that aligns `ies:Event` to `hqdm:event` on the strength of the shared label will map a durative, participant-bearing happening onto a zero-duration point. The crosswalk records the label match as a `skos:relatedMatch` at confidence 0.25 purely to carry this warning.

## 2. Temporal boundaries: a State in IES, an event (point) in HQDM

Both ontologies must say when a 4D extent begins and ends. They use different devices.

- **IES** bounds an extent with **`ies:BoundingState`** (a subclass of `ies:ContinuousState`), linked by `ies:isStartOf` / `ies:isEndOf`. A boundary in IES is itself a *state*.
- **HQDM** bounds an extent with **`hqdm:event`** (a point), linked by `hqdm:beginning` / `hqdm:ending`. A boundary in HQDM is an *event*.

The consequence is that `ies:BoundingState` and `hqdm:event` are functionally equivalent (both are "the boundary") but ontologically different categories (a state versus a point event). A correspondence exists, but it cannot be `skos:exactMatch`; it is a `relatedMatch` that a crosswalk consumer must handle with an EDOAL-style transformation, not a direct class equivalence.

## 3. Where `State` sits in the hierarchy

- **`ies:State`** is declared as a **top-level root class** in `ies-common.ttl`, sibling to `ies:Thing`/`ies:Element` rather than under them.
- **`hqdm:state`** is subsumed under **`hqdm:spatio_temporal_extent`** (the 4D root).

The intended semantics are close (a state is a temporal part of an individual), and the crosswalk maps them at 0.85. But the structural placement differs, so any reasoning that relies on `state ⊑ spatio_temporal_extent` (true in HQDM) will not hold from the IES class graph alone. This is a soundness trap for a reasoner run over a naive union of the two.

## 4. Participation is the clean convergence (worth stating positively)

Not every notable pair is a trap. IES and HQDM independently made the same, non-obvious modelling choice: participation is a *state*, not merely a relation.

- **`ies:EventParticipant`** is a subclass of **`ies:State`**.
- **`hqdm:participant`** is a `state_of_X` (a state of the participating thing).

This is a genuine, deep agreement inherited from the shared BORO commitment, and it is why `ies:isParticipantIn` ↔ `hqdm:participant_in` and `ies:EventParticipant` ↔ `hqdm:participant` are among the strongest correspondences in the set. Recording convergences matters as much as recording traps: it tells an implementer where cross-model reasoning is safe.

## 5. Possible worlds: same word, different scope

Both ontologies carry a `possible_world` notion, but they place it differently.

- **`ies:PossibleWorld`** is a subclass of `ies:Element`: a possible world is itself a spatio-temporal extent you can be a part of (`ies:pluriverse` relates them).
- **`hqdm:possible_world`** is likewise a `spatio_temporal_extent`, but HQDM foregrounds `hqdm:part_of_possible_world` and a `class_of_possible_world` powertype that IES does not mirror one-to-one.

The classes correspond (0.80), but the surrounding apparatus (how membership in a world is asserted, whether worlds are classified) does not, so mappings of the *relations* around possible worlds need case-by-case treatment.

## 6. The powertype stack lines up but is not symmetric

Both models open a class-of hierarchy over 4D individuals (`ies:ClassOfElement` ↔ `hqdm:class_of_spatio_temporal_extent`) and a second order above it (`ies:ClassOfClassOfElement` ↔ `hqdm:class_of_class_of_spatio_temporal_extent`). But IES's domain-specific class-of tree (e.g. `ies:ClassOfPerson`, `ies:ClassOfAsset`) is shaped by its intelligence and security use cases, while HQDM's (e.g. `hqdm:kind_of_physical_object`, `hqdm:class_of_activity`) is shaped by enterprise and engineering use cases. Above the backbone, the powertype hierarchies stop being parallel and become a genuine matching problem, which is where the automated pipeline (candidate generation, fuzzy adjudication) earns its place beyond this hand-curated core.

---

**How to read this file.** A clean crosswalk is not one with no divergences; it is one where the divergences are named. Divergences 1, 2 and 3 are traps a label-matcher falls into. Divergence 4 is a convergence to exploit. Divergences 5 and 6 mark where the backbone ends and the real alignment work begins. Contributions that add a divergence (with evidence from both ontologies) are more valuable than contributions that add another easy match.
