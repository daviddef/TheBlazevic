# Reach: nothing left a menu without being linked from a hub (23 November 2026, the estate clean-up)

Proved against the built site (`site/dist`) of the branch `estate-cleanup-2026-11-23`: each address below left a menu, and the page named in the last column is in the menu and links it in its body. `tools/familycheck.py` (`check:familypages`) asks the family rule on every build; the rest was checked once, here.

Menu links before and after (counted from the built home page's header menu, the drawer excluded): Start 4 -> 4, Our line 13 -> 13, People 9 -> 5, Places & families 16 -> 14, The name 3 -> 3, Research 23 -> 12; 68 -> 51 in all. The `menu_inventory.py compare` against the build of origin/main is in the pull request.

| address | why it left | linked from (hub in the menu) |
|---|---|---|
| `/tree/` | Our line, drawn / The trees / Blood relatives / The Timeline left People > Drawn for the one link "Drawn" (The Spine and The Lines of a Name were never in that group; they are listed there as well) | `/drawn/` yes |
| `/trees/` | Our line, drawn / The trees / Blood relatives / The Timeline left People > Drawn for the one link "Drawn" (The Spine and The Lines of a Name were never in that group; they are listed there as well) | `/drawn/` yes |
| `/bloodline/` | Our line, drawn / The trees / Blood relatives / The Timeline left People > Drawn for the one link "Drawn" (The Spine and The Lines of a Name were never in that group; they are listed there as well) | `/drawn/` yes |
| `/timeline/` | Our line, drawn / The trees / Blood relatives / The Timeline left People > Drawn for the one link "Drawn" (The Spine and The Lines of a Name were never in that group; they are listed there as well) | `/drawn/` yes |
| `/direct-line/` | Our line, drawn / The trees / Blood relatives / The Timeline left People > Drawn for the one link "Drawn" (The Spine and The Lines of a Name were never in that group; they are listed there as well) | `/drawn/` yes |
| `/lines/` | Our line, drawn / The trees / Blood relatives / The Timeline left People > Drawn for the one link "Drawn" (The Spine and The Lines of a Name were never in that group; they are listed there as well) | `/drawn/` yes |
| `/prpic/` | a family page left the "All the families" dropdown (own line first, then A to Z, four named) | `/families/` yes (the menu's own heading link) |
| `/zubrinic/` | a family page left the "All the families" dropdown (own line first, then A to Z, four named) | `/families/` yes (the menu's own heading link) |
| `/harvest/` | left the Research menu | `/research/deep-dives/` yes; also still on its group page and on `/research/` |
| `/readings/` | left the Research menu | `/research/deep-dives/` yes; also still on its group page and on `/research/` |
| `/snapshots/` | left the Research menu | `/research/deep-dives/` yes; also still on its group page and on `/research/` |
| `/indexed/` | left the Research menu | `/research/deep-dives/` yes; also still on its group page and on `/research/` |
| `/stones/` | left the Research menu | `/research/deep-dives/` yes; also still on its group page and on `/research/` |
| `/hungarian-press/` | left the Research menu | `/research/deep-dives/` yes; also still on its group page and on `/research/` |
| `/found/` | left the Research menu | `/research/deep-dives/` yes; also still on its group page and on `/research/` |
| `/coverage/` | left the Research menu | `/research/deep-dives/` yes; also still on its group page and on `/research/` |
| `/impossible/` | left the Research menu | `/research/deep-dives/` yes; also still on its group page and on `/research/` |
| `/duplicates/` | left the Research menu | `/research/deep-dives/` yes; also still on its group page and on `/research/` |
| `/buckets/` | left the Research menu | `/research/deep-dives/` yes; also still on its group page and on `/research/` |

`/roots/` (Roots & Routes) left People > Drawn because the page is retired: it is an Astro redirect stub to `/trees/`, which is in the menu through "Drawn" and `/drawn/`. `/roots/view.html` (the bare viewer for the frames on a person's page) is unchanged.
