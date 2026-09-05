# Legacy MATLAB scripts

These are the original MATLAB scripts this project started from. They are
kept for reference and still run in base MATLAB (no toolboxes needed), but
they are no longer maintained — the Python tool in the parent folder
replaces them and adds the interactive menu, the GUI, and the schematic /
numbered plot modes.

| Script | What it draws |
|---|---|
| `tresca.m` | Tresca hexagonal prism in principal stress space |
| `von_mises.m` | von Mises cylinder |
| `drucker.m` | Drucker-Prager cone (set `eta` to 0.5 or 1 inside the file) |
| `tresca_and_von_mises.m` | both surfaces together |
| `deviatoric_tresca.m` | Tresca hexagon in the π-plane |
| `deviatoric_von.m` | von Mises circle in the π-plane |

Each script is self-contained: open it, change the yield stress `y` (or
`Y`) or `eta` near the top, and run it. The surfaces are built around the
z-axis and rotated 54.7356° about [-1, 1, 0] onto the hydrostatic axis.
