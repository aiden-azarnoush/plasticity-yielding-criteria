# Plasticity Yield Criteria Visualizer

**[Open the visualizer in your browser →](https://aiden-azarnoush.github.io/plasticity-yielding-criteria/)**

The classical yield criteria in plasticity — **Tresca**, **von Mises**, and
**Drucker-Prager** — drawn in 3D principal stress space (drag to rotate),
in 2D plane stress, and in the deviatoric π-plane. Pick a criterion or
Tresca + von Mises together, set the yield stress or the Drucker-Prager
constants, and switch views. Nothing to install. A Python version with the
same views, a small graphical interface, and a question-and-answer mode is
in [`python/`](python/), with the original MATLAB scripts in
[`matlab/`](matlab/).

<p align="center">
<img src="figures/rotating.gif" width="400" alt="Tresca hexagonal prism inside the von Mises cylinder, rotating">
</p>

## The web page

1. **Criterion:** Tresca, von Mises, both together, or Drucker-Prager.
2. **View:** 3D principal stress space, plane stress (σ₃ = 0), or the
   π-plane.
3. **Constants:** σ<sub>y</sub> for Tresca and von Mises; η and c̄ for
   Drucker-Prager. A "schematic" checkbox hides the axis numbers for a
   clean figure to drop into a report or a slide.

> [!TIP]
> In the 3D view, drag to rotate, scroll to zoom, and use the camera icon
> in the plot toolbar to download a PNG of exactly what you see.

> [!NOTE]
> Drucker-Prager is drawn on its own: a pressure-sensitive cone next to the
> pressure-independent prisms makes for a cluttered picture, so the
> combination option is Tresca + von Mises. Try η = 0.5 and η = 1 to watch
> the cone open and close.

## The criteria

**Tresca** (maximum shear stress): yield when
$\tau_{max} = \tfrac12\max|\sigma_i - \sigma_j| = \sigma_y/2$ — a hexagonal
prism along the hydrostatic axis.

**von Mises** (distortion energy):

```math
\sqrt{\tfrac12\left[(\sigma_1-\sigma_2)^2 + (\sigma_2-\sigma_3)^2 + (\sigma_3-\sigma_1)^2\right]} = \sigma_y
\qquad\Longleftrightarrow\qquad \sqrt{3J_2} = \sigma_y
```

a circular cylinder that circumscribes the Tresca prism; the two touch only
on the six uniaxial-stress lines, which is why Tresca is the conservative
criterion.

**Drucker-Prager** (pressure-sensitive; soils, rock, concrete, granular
media):

```math
\sqrt{J_2} = k - \alpha\, I_1
```

drawn as a cone with deviatoric radius $\bar c$ at $I_1 = 0$ and apex on
the hydrostatic axis at $\xi = \sqrt{3}\,\bar c/\eta$ (hydrostatic tension,
tension-positive convention), i.e. $k = \bar c/\sqrt2$ and
$\alpha = \eta/(3\sqrt2)$.

| Tresca + von Mises, 3D | Plane stress | π-plane |
|---|---|---|
| ![](figures/both_3d.png) | ![](figures/both_2d.png) | ![](figures/both_pi.png) |

## Run it locally (Python)

```bash
cd python
pip install numpy matplotlib
python yield_criteria.py          # graphical interface
python yield_criteria.py --cli    # question-and-answer mode
```

Both ask three things — criterion, view, constant — and press Enter on the
constant for a schematic plot. The code is one small function per
criterion and view (`tresca_3d`, `mises_pi`, `drucker_2d`, …), so it is
easy to read and extend.

> [!WARNING]
> The Python GUI uses `tkinter`, which ships with the standard Python
> installers on macOS and Windows; on some Linux distributions it is a
> separate package (`sudo apt install python3-tk`).

## Repository layout

```
index.html          the web page (GitHub Pages serves this)
python/             yield_criteria.py
matlab/             the original MATLAB scripts (2010s), kept for reference
figures/
```

## Author

**Aiden Azarnoush**

## License

MIT — see [LICENSE](LICENSE).

## References

- Hill, R. (1998). *The Mathematical Theory of Plasticity*
- Lubliner, J. (1990). *Plasticity Theory*
- Chen, W.F. & Han, D.J. (1988). *Plasticity for Structural Engineers*

---

## Dedication

*This work is dedicated to my beloved mother, **Simin Nematpour**, who
passed away. I love her and miss her deeply. Her memory continues to
inspire my academic pursuits and passion for engineering.*
