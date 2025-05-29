```markdown
# Plasticity Yield Criteria Visualization

A comprehensive MATLAB implementation for visualizing classical yield criteria in plasticity theory, including both principal stress space and deviatoric stress space representations.

## Table of Contents

- [Overview](#overview)
- [Implemented Yield Criteria](#implemented-yield-criteria)
  - [Tresca Yield Criterion](#1-tresca-yield-criterion)
  - [von Mises Yield Criterion](#2-von-mises-yield-criterion)
  - [Drucker-Prager Yield Criterion](#3-drucker-prager-yield-criterion)
  - [Combined Visualizations](#4-combined-tresca-and-von-mises)
  - [Deviatoric Representations](#5-deviatoric-representations)
- [Theory Background](#theory-background)
- [Usage](#usage)
- [Output](#output)
- [Mathematical Significance](#mathematical-significance)
- [File Structure](#file-structure)
- [Author](#author)
- [License](#license)
- [Contributing](#contributing)
- [References](#references)
- [Dedication](#dedication)

## Overview

This repository contains MATLAB scripts that generate 2D and 3D visualizations of fundamental yield criteria used in plasticity and materials engineering. These criteria define the conditions under which materials transition from elastic to plastic behavior.

> [!NOTE]  
> All scripts are self-contained and require only base MATLAB installation. No additional toolboxes are needed.

## Implemented Yield Criteria

### 1. Tresca Yield Criterion
- **File**: `tresca.m`
- **Description**: Maximum shear stress theory
- **Mathematical Form**: τ_max = σ_y/2
- **Visualization**: Hexagonal prism in principal stress space

### 2. von Mises Yield Criterion  
- **File**: `von_mises.m`
- **Description**: Maximum distortion energy theory
- **Mathematical Form**: √[(σ₁-σ₂)² + (σ₂-σ₃)² + (σ₃-σ₁)²] = √2·σ_y
- **Visualization**: Circular cylinder in principal stress space

### 3. Drucker-Prager Yield Criterion
- **File**: `drucker.m` 
- **Description**: Pressure-dependent yield criterion for granular materials
- **Mathematical Form**: √J₂ + α·I₁ = k
- **Visualization**: Cone in principal stress space
- **Parameters**: η = 0.5 or η = 1.0

> [!TIP]
> For the Drucker-Prager criterion, try both η values (0.5 and 1.0) to see how the cone geometry changes with different material parameters.

### 4. Combined Tresca and von Mises
- **File**: `tresca_and_von_mises.m`
- **Description**: Side-by-side comparison of both criteria
- **Visualization**: Hexagonal prism (Tresca) inscribed in circular cylinder (von Mises)

### 5. Deviatoric Representations

#### Deviatoric Tresca
- **File**: `deviatoric_tresca.m`
- **Description**: Tresca criterion in π-plane (deviatoric stress space)
- **Visualization**: Regular hexagon with principal stress directions

#### Deviatoric von Mises
- **File**: `deviatoric_von.m`
- **Description**: von Mises criterion in π-plane (deviatoric stress space)  
- **Visualization**: Circle with principal stress directions

> [!IMPORTANT]  
> The deviatoric representations show yield surfaces in the π-plane, which is perpendicular to the hydrostatic axis and represents pure deviatoric stress states.

## Theory Background

### Principal Stress Space
The yield surfaces are plotted in a 3D coordinate system where the axes represent the three principal stresses (σ₁, σ₂, σ₃). Key features:

- **Hydrostatic Line**: The line σ₁ = σ₂ = σ₃ (shown in red) represents pure hydrostatic stress states
- **Rotation**: Surfaces are rotated 54.7356° around the [-1,1,0] axis to align with the standard orientation
- **Tresca**: Forms a hexagonal prism with flat faces perpendicular to the deviatoric plane
- **von Mises**: Forms a circular cylinder, always circumscribing the Tresca hexagon

### Deviatoric Stress Space (π-plane)
The π-plane is perpendicular to the hydrostatic line and represents pure deviatoric stress states:

- **Coordinate System**: Uses a 2D projection where principal stress directions are clearly marked
- **Tresca**: Appears as a regular hexagon
- **von Mises**: Appears as a circle
- **Scaling Factor**: r = √(2/3) × σ_y ensures proper geometric relationships

### Drucker-Prager Criterion
Extended yield criterion for pressure-sensitive materials:
- **Cone Shape**: Reflects the material's dependence on hydrostatic pressure
- **Parameters**: Different η values (0.5, 1.0) provide different cone geometries
- **Applications**: Particularly useful for soils, concrete, and granular materials

## Usage

### Requirements
- MATLAB (tested on recent versions)
- No additional toolboxes required

> [!WARNING]  
> Make sure to clear any existing variables and figures before running scripts to avoid conflicts.

### Running the Scripts

1. **Individual Yield Criteria**:
   ```matlab
   run('tresca.m')          % 3D Tresca hexagonal prism
   run('von_mises.m')       % 3D von Mises cylinder
   run('drucker.m')         % 3D Drucker-Prager cone
   ```

2. **Comparison**:
   ```matlab
   run('tresca_and_von_mises.m')  % Both criteria overlaid
   ```

3. **Deviatoric Representations**:
   ```matlab
   run('deviatoric_tresca.m')     % 2D hexagon in π-plane
   run('deviatoric_von.m')        % 2D circle in π-plane
   ```

### Customization

Key parameters that can be modified:

- **Yield Stress**: Change the variable `y` or `Y` in each script
- **Drucker-Prager Parameter**: Modify `eta` (0.5 or 1.0) in `drucker.m`
- **Visualization Range**: Adjust `axis` limits for better viewing
- **Colors and Styling**: Modify `FaceColor`, `LineWidth`, and other graphics properties

> [!CAUTION]
> When modifying yield stress values, ensure they remain positive to maintain physical meaning of the yield surfaces.

## Output

Each script generates high-quality 3D or 2D plots with:
- Proper axis labels with mathematical notation
- Grid lines for reference
- Optimal viewing angles
- Professional formatting suitable for presentations and publications

## Mathematical Significance

- **Tresca vs von Mises**: von Mises criterion is more accurate for ductile metals, while Tresca provides a conservative estimate
- **Geometric Relationship**: von Mises surface always circumscribes Tresca surface
- **Deviatoric Analysis**: The π-plane representations show that yielding is independent of hydrostatic pressure for these criteria
- **Engineering Applications**: These visualizations help in understanding material behavior under complex stress states

> [!TIP]
> Use the combined visualization (`tresca_and_von_mises.m`) to clearly see how the von Mises cylinder always contains the Tresca hexagon, demonstrating the conservative nature of the Tresca criterion.

## File Structure

```
├── tresca.m                    # 3D Tresca yield surface
├── von_mises.m                 # 3D von Mises yield surface  
├── drucker.m                   # 3D Drucker-Prager yield surface
├── tresca_and_von_mises.m      # Combined 3D visualization
├── deviatoric_tresca.m         # 2D Tresca in π-plane
├── deviatoric_von.m            # 2D von Mises in π-plane
└── README.md                   # This file
```

## Author

**Aiden Azarnoush**  
Email: a.m.azarnoush@gmail.com

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Feel free to fork this repository and submit pull requests for improvements or additional yield criteria implementations.

## References

- Hill, R. (1998). *The Mathematical Theory of Plasticity*
- Lubliner, J. (1990). *Plasticity Theory*  
- Chen, W.F. & Han, D.J. (1988). *Plasticity for Structural Engineers*

---

## Dedication

*This work is dedicated to my beloved mother, **Simin Nematpour**, who passed away. I love her and miss her deeply. Her memory continues to inspire my academic pursuits and passion for engineering.*

---

*These visualizations were developed as part of advanced plasticity coursework and provide intuitive understanding of fundamental yield criteria in materials science and engineering.*
```
