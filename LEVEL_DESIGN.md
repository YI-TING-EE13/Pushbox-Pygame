# PushBox Level Design Guidelines

This document defines the core principles, structural rules, difficulty progression standards, and validation checklists for designing, reviewing, and extending default Sokoban levels in PushBox. Following these guidelines prevents repetitive grid designs, ensures predictable difficulty progression, and maintains high code and design quality.

---

## 1. Purpose

Default levels serve as the core progression experience for the player. These guidelines prevent common level design pitfalls, such as:
* **Overly Similar Levels:** Puzzles that look slightly different but share identical mechanical paths and solutions.
* **Unclear Difficulty Progression:** Severe difficulty spikes or sudden, unearned drops in complexity.
* **Invalid Board Layouts:** Levels with mismatched box-target counts, unreachable spaces, or missing players.
* **Cramped Map Layouts:** Board boundaries that collide with UI indicators at standard `800x720` resolution.
* **Undocumented Design Intent:** Grid modifications without clear pedagogical goals (e.g. teaching a specific push, turn, or ordering route).

---

## 2. Level Data Format

All default levels are stored statically within the codebase and are loaded at runtime.

* **File Location:** [constants.py](file:///c:/Users/LAB-606/Desktop/Software%20Side%20Project/PushBox_v1/src/pushbox/utils/constants.py)
* **Default Grid Map:** Loaded from the dictionary `DEFAULT_LEVELS`. Grids are stored as 2D lists (rows containing integer cell values).
* **Grid Cell Key:**
  ```text
  0 = Empty floor
  1 = Wall
  2 = Target
  3 = Box
  4 = Player
  5 = Box on target (Avoid starting layouts with this cell type)
  ```
* **Default Metadata Map:** Stored in the dictionary `DEFAULT_LEVEL_METADATA`, mapping each level (e.g. `"Level 1"`) to its type-safe `LevelMetadata` structure:
  ```python
  class LevelMetadata(TypedDict):
      difficulty: str  # E.g., "Intro", "Intermediate", "Advanced"
      theme: str       # High-level puzzle theme (e.g., "Split Warehouse")
      boxes: int       # Programmatic count of starting boxes
      note: str        # Brief description of layout and intended strategy
  ```

---

## 3. Structural Validity Rules

To be eligible for inclusion in the default level catalog, every grid must adhere to these strict structural rules:
1. **Exactly One Player:** The starting grid must contain precisely one player cell (`4`).
2. **At Least One Box:** Puzzles must have a box count (`3`) greater than or equal to `1`.
3. **Mismatched Counts Blocked:** The number of starting boxes (`3`) must exactly equal the number of starting targets (`2`).
4. **Rectangular Boundaries:** The grid layout must be a uniform rectangular list-of-lists. Empty padding regions should be filled with `0` or `1` appropriately.
5. **Closed Outer Walls:** The playable area must be fully enclosed by outer walls (`1`) to prevent the player or boxes from exiting the grid borders.
6. **Dimension Limits:** Grids must stay within the range of **5x5** (minimum) to **20x20** (maximum) to scale beautifully inside the standard window viewport.
7. **No Pre-placed Solved States:** Do not place solved boxes (`5` / `BOX_ON_TARGET`) in starting default levels unless explicitly teaching a specialized mechanic.
8. **No Unreachable Segments:** All floor cells and target paths must be accessible by the player unless unreachable zones are explicitly documented for decorative symmetry.
9. **No Early Stalemates:** Starting positions must not place boxes in immediate deadlocks (e.g. in corners or flush against double-corner walls) unless specifically demonstrating deadlock recovery.

---

## 4. Difficulty Labels

We classify levels using six lightweight difficulty labels. These labels act as player guidance only and do not constitute formal mathematical proofs of complexity or solvability.

| Difficulty | Description / Characteristics | Expected Puzzle Scope |
| --- | --- | --- |
| **Intro** | Introduces raw mechanics (moving, single box pushes, target alignments). Large, open floors with negligible deadlock risks. | 1–3 simple boxes, wide spaces |
| **Intro+** | Practices target row packing or distant target regions. Irreversible mistakes are minimal, but requires minor movement adjustments. | 2–3 boxes, simple straight corridors |
| **Intermediate**| Introduces simple interior wall obstacles. Minor order dependencies appear, requiring the player to plan out the sequence of pushes. | 2–3 boxes, offset target lines |
| **Intermediate+**| Tighter rooms. Multiple boxes are placed in close clusters, necessitating careful repositioning before a push can occur. | 3–4 boxes, tight corners, blockages |
| **Advanced** | Constrained routing. Puzzles involve narrow lanes, turnings (L-corridors), obstacle islands, or split target regions. High deadlock risk. | 2–4 boxes, narrow corridors, islands |
| **Advanced+** | Highest complexity. Separated multi-room complexes connected by narrow paths. Precise sequencing and careful step planning required. | 4–5 boxes, multi-room structures |

---

## 5. Level Design Dimensions

Rather than merely shifting boxes and walls around, new default levels should vary across multiple design dimensions to ensure a diverse playing experience:

* **Wall Topology:** Differentiating open spaces from narrow, maze-like corridor lattices.
* **Corridor Width:** Limiting the width of corridors to 1 cell (highly restrictive) or 2+ cells (allowing player recovery and turnaround).
* **Target Distribution:** Aligning targets in a neat line/cluster, separating them across the map, or placing them as islands.
* **Ordering Constraints:** Structuring the puzzle so box A *must* be pushed to target B before box C can be moved (sequencing locks).
* **Deadlock Risk:** Placing targets in positions that require pushing a box flush against walls, creating high stalemate possibilities if done out of order.
* **Visual Identity:** Emphasizing symmetry, room subdivisions, or central landmark islands to keep maps memorable.

---

## 6. Common Puzzle Patterns

Leverage these classic Sokoban puzzle patterns to achieve specific learning goals:

### Straight Push Lanes
* **Concept:** A straight path leading directly to a target.
* **Purpose:** Teaches basic pushing and alignment mechanics.
* **Deadlock Risk:** Extremely low.
* **When to Use:** Levels 1–5 to onboard new players.

### L-Shaped Corridors
* **Concept:** A corridor containing a 90-degree turn.
* **Purpose:** Teaches players that a box cannot be pulled out of a corner once pushed flush against the inner walls.
* **Deadlock Risk:** High (if pushed into the corner without access).
* **When to Use:** Intermediate to Advanced levels.

### Obstacle Islands
* **Concept:** A wall pillar or segment placed in the center of a wide room.
* **Purpose:** Requires the player to circle around the island to push a box from the opposite direction.
* **Deadlock Risk:** Moderate.
* **When to Use:** Intermediate to Advanced levels to encourage spatial planning.

### Split Warehouse
* **Concept:** Two separate rooms connected by a single narrow doorway.
* **Purpose:** Restricts box transfer and forces the player to plan which box enters the doorway first.
* **Deadlock Risk:** Very High.
* **When to Use:** Advanced and Advanced+ levels.

---

## 7. Anti-Patterns to Avoid

Avoid these design mistakes when adding or refining levels:
* **"Reskinned Clones":** Creating a level that looks cosmetically distinct but plays exactly like a previous one (same moves, same paths).
* **Empty Spacing Bloat:** Designing massive empty spaces that serve no purpose except to increase walking distance.
* **Obvious Line-of-Sight Targets:** Always placing targets in straight lines directly in front of boxes, eliminating the need to steer.
* **Excessive Early Box Bloat:** Throwing 5+ boxes at a player before they have mastered basic 2-box and 3-box routing mechanics.
* **Unpreventable Deadlocks:** Starting positions that force a deadlock on the very first push, leaving zero choice.
* **Subjective Number-Based Difficulty:** Labeling a level as "Advanced" simply because it is numbered later in the progression list, without actually introducing complex design traits.
* **Single-Cell Chokepoints Without Recovery:** Creating 1-cell narrow corridors or doorways without adjacent turnaround pockets or loop routes, preventing player repositioning.
* **Pull-Only Targets:** Placing targets in pockets or corners that would require a box to be pulled (which is mechanically impossible).
* **Inaccessible Push Faces:** Enclosing starting boxes with walls such that the player cannot reach the required push position behind the box.

---

## 8. Current Level 1–30 Design Intent Table

The following table summarizes the design themes and intent for the 30 built-in default levels, acting as the pedagogical blueprint of the game.

| Level | Difficulty | Theme | Boxes | Design Intent |
| :---: | :---: | :---: | :---: | :--- |
| **1** | Intro | Basic Route | 3 | Introduces basic movement, pushing, and 1-to-1 target matching. |
| **2** | Intro | Cluster Pushes | 4 | Teaches player to push clustered boxes to nearby target slots. |
| **3** | Intro+ | Target Row | 6 | Practices organizing a large number of boxes towards a single row of targets. |
| **4** | Intermediate | Blocked Center | 5 | Introduces wall-separated columns requiring sequencing and path-finding. |
| **5** | Intermediate | Compact Cluster | 5 | Introduces tight, compact rooms with high proximity box groupings. |
| **6** | Intro | Twin Push | 2 | Simple two-box alignment exercise with wide spaces and easy recovery. |
| **7** | Intro+ | Split Targets | 2 | Forces the player to separate boxes to opposite ends of the room. |
| **8** | Intro+ | Three Columns | 3 | Teaches repeated vertical pushing and parallel lane routing. |
| **9** | Intermediate | Obstacle Spacing | 3 | Adds simple interior wall pillars to affect player repositioning routes. |
| **10** | Intermediate | Four-Box Grid | 4 | Combines vertical column push lanes with open movement areas. |
| **11** | Intermediate | Offset Goals | 2 | Uses separated boxes and targets separated by a central divider block. |
| **12** | Intermediate | Staggered Paths | 2 | Requires navigating boxes around staggered wall configurations. |
| **13** | Intermediate+ | Tight Cluster | 3 | Places boxes close together in restricted spaces near blocked corridors. |
| **14** | Advanced | Lane Control | 3 | Restricts player movement via interior wall columns and long lanes. |
| **15** | Advanced | Mixed Columns | 4 | Combines multiple vertical corridors with central blocking segments. |
| **16** | Advanced | L-Corridor | 2 | Focuses on 90-degree turning pushes and angled player access routes. |
| **17** | Advanced | Split Warehouse | 3 | Connects distinct left and right rooms via a tight center corridor. |
| **18** | Advanced | Central Island | 4 | Uses a central wall island to shape approach routes and force loops. |
| **19** | Advanced+ | Small Rooms | 4 | Restricts progress by isolating targets behind narrow door frames. |
| **20** | Advanced+ | Mixed Warehouse | 5 | Final challenge combining multiple boxes, wall partitions, and target slots. |
| **21** | Advanced | Long Reposition Route | 3 | Forces the player to walk long loops around outer paths to reposition behind boxes. |
| **22** | Advanced | Two-Box Ordering Lock | 2 | Requires pushing box A completely out of the way before box B can navigate a tight bottleneck. |
| **23** | Advanced+ | Three-Zone Warehouse | 4 | Connects three distinct chambers in a linear sequence, forcing multi-stage box transfers. |
| **24** | Advanced+ | Narrow Door Recovery | 3 | Focuses on pulling/pushing boxes out of tight doors without wedging them in the corner. |
| **25** | Advanced+ | Mixed Final Challenge | 5 | Grand finale. Large scale, multiple room islands, high sequencing dependencies, and 5 boxes. |
| **26** | Advanced | Switchback Hall | 3 | Uses inner partitions to require route switching and player repositioning. |
| **27** | Advanced+ | Twin Courtyards | 4 | Connects two open courtyards with moderate box ordering requirements. |
| **28** | Advanced+ | Central Spine | 4 | Uses a central wall spine to force side-to-side box routing and loop maneuvers. |
| **29** | Advanced+ | Offset Storage | 5 | Staggered storage chambers demanding mixed horizontal/vertical push orientations. |
| **30** | Advanced+ | Final Warehouse | 6 | Absolute grand finale. Connects six boxes, complex target slots, and internal wall islands. |

---

## 9. Guidelines for Future Level Expansion (31+)

When the default level catalog is extended beyond 30 levels in future releases, designers should:
1. Maintain the progressive difficulty curve, introducing new mechanics (e.g. multi-box locks, tight corridors, visual symmetry) with limited box counts first.
2. Avoid early box bloat, keeping the starting box count under 6 for gameplay performance and clarity.
3. Validate all new draft grids against the [Review Checklist for New Levels](#10-review-checklist-for-new-levels) prior to implementation.

---

## 10. Review Checklist for New Levels

Future developers and agents must check all new levels against this checklist before committing:

### Structural Checks
* [ ] **Single Player:** Verify the grid contains exactly one player starting cell (`4`).
* [ ] **Valid Boxes:** Starting box count is at least `1`.
* [ ] **Box-Target Equality:** Starting box count exactly equals starting target count.
* [ ] **Closed Map:** Outer borders are fully sealed by wall cells (`1`) to prevent escape.
* [ ] **Grid Dimensions:** Grid scale is between **5x5** and **20x20**.
* [ ] **Clean Starting Cells:** Starting layout contains no solved `BOX_ON_TARGET` (`5`) cells.

### Design Checks
* [ ] **Clear Theme:** The level has a defined mechanical or spatial layout theme.
* [ ] **Pedagogical Intent:** The level teaches a specific pathing, loop, or order skill.
* [ ] **Low Repetitiveness:** The layout is distinct from adjacent levels.
* [ ] **Recovery Space:** There is enough space to navigate around boxes without immediate deadlocks.
* [ ] **Difficulty Accuracy:** The assigned difficulty label matches the actual design dimensions.
* [ ] **Metadata Consistency:** The `DEFAULT_LEVEL_METADATA` box count matches the exact box count in the grid.

### Verification Checks
* [ ] **Tests Pass:** `uv run pytest -v` runs with 100% success.
* [ ] **Linter Clean:** `uv run ruff check .` returns zero warnings or errors.
* [ ] **Formatter Compliant:** `uv run ruff format --check .` passes.
* [ ] **Mypy Clean:** `uv run mypy src/` returns zero type issues.
* [ ] **Visual Launch:** The level launches safely and centers perfectly on the screen at `800x720`.
* [ ] **Manual Playtest:** The level has been manually completed to guarantee it is solvable.

---

## 11. Relationship to Automated Tests

While automated tests are highly robust, developers must understand their scope:
* **What Automated Tests Can Verify:** Grid dimension limits, presence of exactly one player, matched box/target counts, type-safe metadata formatting, and successful level selector rendering.
* **What Automated Tests Cannot Verify:** **Puzzle solvability.** The test suite does not include a mathematical Sokoban pathfinding solver. Therefore, manual playtesting is **mandatory** to prove that a level is actually winnable and has high aesthetic quality.

---

## 12. Future Improvements

Future iterations on the level design system could explore:
1. **Lightweight Path Solver:** Integrating a simple BFS/DFS pathfinding engine into tests to mathematically check solvability.
2. **Skill Tag Metadata:** Adding a `"skills"` field to `LevelMetadata` (e.g. `["turns", "looping", "sequencing"]`).
3. **Draft Directory workflow:** Establishing a `levels/design_drafts/` directory for proposed puzzles prior to code inclusion.
4. **Visual Review Tooling:** Developing a command-line script to output ASCII level layouts for quick markdown review.
