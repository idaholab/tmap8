/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2026 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#pragma once

#include "ValidatedModelMaterial.h"

#include "PbLiPropertyHelper.h"

class SinglePhaseFluidProperties;

/**
 * Computes the hydrogen isotope solubility in PbLi from literature correlations, converted to
 * atoms m$^{-3}$ Pa$^{-1/2}$. The solubility is provided as both a regular and an AD material
 * property. The PbLi density needed to convert atom-fraction correlations comes from the fluid
 * properties of MOOSE (LeadLithiumFluidProperties).
 */
class TritiumSolubilityPbLi : public ValidatedModelMaterial<PbLiPropertyHelper::SolubilityModel,
                                                            PbLiPropertyHelper::SolubilityModelData>
{
public:
  static InputParameters validParams();

  TritiumSolubilityPbLi(const InputParameters & parameters);

protected:
  void computeQpProperties() override;

  /// Lithium atomic fraction of the PbLi (-)
  const Real _lithium_fraction;
  /// Molar mass of lithium (g/mol)
  const Real _lithium_molar_mass;
  /// Molar mass of lead (g/mol)
  const Real _lead_molar_mass;
  /// Fluid properties providing the PbLi density, only evaluated by the atom-fraction models
  const SinglePhaseFluidProperties * const _fp;
  /// Pressure (Pa), if provided, used to check the documented pressure range
  const ADVariableValue * const _pressure;
  /// Regular solubility material property
  MaterialProperty<Real> & _solubility;
  /// AD solubility material property
  ADMaterialProperty<Real> & _ad_solubility;
};
