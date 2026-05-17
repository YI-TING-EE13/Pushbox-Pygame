# Level 21–25 Design Plan

This document details the design plan and architectural specifications for the next five default levels: `Level 21` through `Level 25`. 

> [!IMPORTANT]
> This plan has been successfully implemented, integrated, and verified in Phase 21C. All default levels from Level 21 through Level 25 are now active in the game codebase, complete with dynamic selector classification, metadata badges, and regression tests.

---

## 1. Overview

The primary goal of this planning document is to establish a graduated difficulty framework for the final set of default levels. Expanding our default levels from 20 to 25 will complete the built-in default level catalog. 

By detailing themes, skill goals, grid shapes, and deadlocks in advance, we ensure that every new level is structurally distinct, enjoyable, and structurally valid, designed to reduce the risk of sudden difficulty spikes or layout collisions.

---

## 2. Design Goals

All planned levels strictly follow the standards defined in [LEVEL_DESIGN.md](file:///c:/Users/LAB-606/Desktop/Software%20Side%20Project/PushBox_v1/LEVEL_DESIGN.md):
* **Graduated Complexity:** Create a smooth curve from Level 20's Advanced+ difficulty into high-tier spatial challenges.
* **Aesthetic & Structural Uniqueness:** Avoid reskinned clones of prior levels by utilizing diverse wall topologies and room layouts.
* **Clear Pedagogical Skills:** Each level is engineered to teach or test a specific spatial reasoning skill (e.g. routing, ordering locks, zone transferring).
* **Grid Safety Limits:** All draft grids are expected to fit within `800x720` resolution after verification and satisfy all structural checks.

---

## 3. Proposed Level Table

The following table summarizes the proposed specifications for the next five levels:

| Level | Proposed Difficulty | Theme | Boxes | Main Skill | Difference from Earlier Levels |
| :---: | :---: | :---: | :---: | :--- | :--- |
| **21** | Advanced | Long Reposition Route | 3 | Looping & spatial routing | Requires traveling long loops around outer paths to steer boxes from behind. |
| **22** | Advanced | Two-Box Ordering Lock | 2 | Sequence lock planning | Uses a single-column corridor exit where Box A *must* clear a path before Box B is moved. |
| **23** | Advanced+ | Three-Zone Warehouse | 4 | Zone transfer navigation | Connects three rooms in a sequential chain, forcing multi-stage box transfers. |
| **24** | Advanced+ | Narrow Door Recovery | 3 | Constrained space recovery | Focuses on pushing boxes through tight 1-cell door frames without wedging them in corners. |
| **25** | Advanced+ | Mixed Final Challenge | 5 | Multi-box spatial planning | Grand finale. Large scale, multiple room islands, high sequencing, and 5 starting boxes. |

---

## 4. Per-Level Design Notes & Draft Grids

*Note: These visual ASCII drafts have been successfully implemented and integrated in the active [constants.py](file:///c:/Users/LAB-606/Desktop/Software%20Side%20Project/PushBox_v1/src/pushbox/utils/constants.py) file.*

### Level 21: Long Reposition Route
* **Intended Mechanic:** Repositioning loops.
* **Target Box Count:** 3
* **Map Topology:** A large 9x9 room subdivided by a long center vertical wall segment.
* **Player Learning Goal:** Steer boxes around obstructions by recognizing that the player must walk all the way around the central divider to push a box from its other side.
* **Deadlock Risk:** Moderate. Pushing a box flush against the central vertical divider blocks access unless pushed carefully.
* **Difference from Earlier Levels:** Earlier column levels (e.g. Level 8 and 10) have short, open columns. Level 21 has an elongated wall partition that makes repositioning walks much longer.
* **Suggested Metadata:**
  * Theme: "Long Reposition Route"
  * Difficulty: "Advanced"
  * Note: "Requires traveling long loops around outer paths to steer boxes from behind."
* **Layout Concept (Draft Only):**
  ```text
  1 1 1 1 1 1 1 1 1
  1 4 0 0 1 0 0 2 1
  1 0 3 0 1 0 0 0 1
  1 0 0 0 1 0 0 0 1
  1 1 0 1 1 1 0 1 1
  1 0 0 0 1 0 0 0 1
  1 0 3 0 1 0 3 0 1
  1 2 0 0 0 0 0 2 1
  1 1 1 1 1 1 1 1 1
  ```

---

### Level 22: Two-Box Ordering Lock
* **Intended Mechanic:** Sequential ordering lock.
* **Target Box Count:** 2
* **Map Topology:** Compact 7x7 grid with a single narrow exit lane leading to offset target slots.
* **Player Learning Goal:** Identify that Box A must be pushed into a temporary holding corridor to clear the lane before Box B can navigate through, otherwise Box B gets permanently wedged.
* **Deadlock Risk:** Very High. A single incorrect push locks the narrow exit lane.
* **Difference from Earlier Levels:** Unlike previous offset puzzles (e.g. Level 11) which had spacious bypasses, Level 22 has no bypass lane, enforcing a strict sequential order.
* **Suggested Metadata:**
  * Theme: "Two-Box Ordering Lock"
  * Difficulty: "Advanced"
  * Note: "Uses a single-column corridor exit where Box A must clear a path before Box B is moved."
* **Layout Concept (Draft Only):**
  ```text
  1 1 1 1 1 1 1
  1 4 0 1 0 2 1
  1 0 3 1 3 2 1
  1 0 0 0 0 0 1
  1 0 1 1 1 0 1
  1 0 0 0 0 0 1
  1 1 1 1 1 1 1
  ```

---

### Level 23: Three-Zone Warehouse
* **Intended Mechanic:** Multi-room box transfers.
* **Target Box Count:** 4
* **Map Topology:** A wide 9x11 grid split into three linear chambers (Left, Center, Right) connected by single-cell door openings.
* **Player Learning Goal:** Plan multi-stage transfers by moving boxes from the Left Room, through the Center Room, and into the Right Room targets without clogging the narrow doors.
* **Deadlock Risk:** Very High. Moving a box into the Center Room too early blocks the player from accessing the other rooms.
* **Difference from Earlier Levels:** Unlike Level 17 (Split Warehouse) which connects only two chambers with a simple horizontal connection, Level 23 connects three separate zones, creating double-congested bottlenecks.
* **Suggested Metadata:**
  * Theme: "Three-Zone Warehouse"
  * Difficulty: "Advanced+"
  * Note: "Connects three distinct chambers in a linear sequence, forcing multi-stage box transfers."
* **Layout Concept (Draft Only):**
  ```text
  1 1 1 1 1 1 1 1 1 1 1
  1 4 0 0 1 2 2 1 0 0 1
  1 0 3 0 1 2 2 1 0 0 1
  1 0 3 0 0 0 0 0 0 0 1
  1 1 1 0 1 1 1 1 0 1 1
  1 0 3 0 0 0 0 0 3 0 1
  1 0 0 0 1 0 0 1 0 0 1
  1 0 0 0 1 0 0 1 0 0 1
  1 1 1 1 1 1 1 1 1 1 1
  ```

---

### Level 24: Narrow Door Recovery
* **Intended Mechanic:** Offset corner pushing.
* **Target Box Count:** 3
* **Map Topology:** Compact 9x9 layout featuring multiple partitioned 2x2 alcoves with offset doorways.
* **Player Learning Goal:** Learn to push boxes into small rooms and align them against offset targets, managing tight space where the player has minimal room to loop behind a box.
* **Deadlock Risk:** Extremely High. Pushing a box directly flush against the inner walls of the small rooms makes it impossible to reposition or steer.
* **Difference from Earlier Levels:** Unlike Level 19 (Small Rooms) which has direct linear doors, Level 24 uses offset doorways, requiring turning maneuvers *during* entry.
* **Suggested Metadata:**
  * Theme: "Narrow Door Recovery"
  * Difficulty: "Advanced+"
  * Note: "Focuses on pushing boxes through tight 1-cell door frames without wedging them in corners."
* **Layout Concept (Draft Only):**
  ```text
  1 1 1 1 1 1 1 1 1
  1 4 0 1 2 0 1 0 1
  1 0 3 0 0 0 0 3 1
  1 0 0 1 1 1 1 0 1
  1 1 0 1 0 0 1 0 1
  1 2 0 0 3 0 0 2 1
  1 0 0 1 0 0 1 0 1
  1 0 0 1 0 0 1 0 1
  1 1 1 1 1 1 1 1 1
  ```

---

### Level 25: Mixed Final Challenge
* **Intended Mechanic:** Combined sequencing, routing, and multi-box management.
* **Target Box Count:** 5
* **Map Topology:** Medium-scale 11x11 layout containing multiple obstacle pillars, split target blocks, and restricted hallways.
* **Player Learning Goal:** Synthesize all previous skills: navigate loop routes, manage multi-box bottlenecks, separate targets, and plan precise order strategies with 5 starting boxes.
* **Deadlock Risk:** High. Multiple potential corners and wall segments exist.
* **Difference from Earlier Levels:** The ultimate test. Combines the routing loops of Level 21, the sequencing locks of Level 22, and the narrow doorways of Level 24.
* **Suggested Metadata:**
  * Theme: "Mixed Final Challenge"
  * Difficulty: "Advanced+"
  * Note: "Grand final challenge combining routing loops, ordering locks, and narrow doorways."
* **Layout Concept (Draft Only):**
  ```text
  1 1 1 1 1 1 1 1 1 1 1
  1 4 0 0 1 2 2 2 1 0 1
  1 0 3 0 1 0 0 0 1 0 1
  1 0 3 0 0 0 1 0 0 3 1
  1 1 0 1 1 0 1 1 0 1 1
  1 2 0 0 1 0 1 0 0 2 1
  1 1 0 1 1 0 1 1 0 1 1
  1 0 3 0 0 0 1 0 0 3 1
  1 0 0 0 1 0 0 0 1 0 1
  1 0 0 0 1 0 0 0 1 0 1
  1 1 1 1 1 1 1 1 1 1 1
  ```

---

## 5. Review Checklist for Future Implementation

Before committing these levels to code in the next phase, they must pass this strict verification checklist:
* [ ] **One Player Starting Point:** Confirm every starting grid contains exactly one `4` cell.
* [ ] **Target-Box Balance:** Count the `3`s and `2`s in each map configuration; ensure they are exactly equal.
* [ ] **Sealed Boundaries:** Ensure outer borders are completely made of `1`s.
* [ ] **Clean Startup:** Verify that the starting grid utilizes only `0-4` (no resolved `5`s).
* [ ] **Type-Safe Metadata:** The new `DEFAULT_LEVEL_METADATA` structures must exactly compile with `LevelMetadata`.
* [ ] **Uniqueness Check:** Compare the new grids against Levels 1–20 to ensure no accidental duplication.
* [ ] **Dynamic Centering:** Launch each level in the game screen. Verify that the grid scales and centers safely at `800x720` without clipping the status bar or timer.
* [ ] **Manual Playtest Check:** Complete every new level manually; manual completion provides practical confidence of solvability and actual quality.
* [ ] **Selector Pagination Stability:** Ensure that the newly added cards display their metadata badges, corner stars, and detail panels legibly across all selector pages.

---

## 6. Implementation Risks & Mitigation Strategies

1. **Window Viewport Clipping (Level 25 Scaling):**
   * *Risk:* Large grids (like 11x11) might clip or overlap with game UI controls (timer, step counts, pause button) in the game view.
   * *Mitigation:* The existing renderer dynamically scales cell sizes based on viewport dimensions. We must verify that the cell size is auto-calculated correctly during playtesting.
2. **Page 3 and Page 4 Selector Layout Pagination:**
   * *Risk:* Adding 5 default levels brings total default levels to 25. The selector lists 9 levels per page. Page 1 has 9 (Levels 1–9). Page 2 has 9 (Levels 10–18). Page 3 will now hold 7 default levels (Levels 19–25). If a custom level is created, it will be the 8th item on Page 3. If a second custom level is created, it becomes the 9th item. A third custom level will now automatically trigger a **Page 4** transition.
   * *Mitigation:* We must ensure that selector pagination and keyboard index wrapping gracefully support Page 4 boundaries and clamp without index errors.
3. **Severe Difficulty Spikes:**
   * *Risk:* Levels 23–25 might be excessively frustrating if corridors are too narrow with zero recovery space.
   * *Mitigation:* Integrate short 2-cell wide bypass loops where players can undo mistakes or reposition.

---

## 7. Plan Status

* **Status:** Fully Implemented & Verified in Phase 21C.
* **Release Target:** Included in default catalog.
