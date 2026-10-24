/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2026 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#pragma once

#include "Material.h"

#include "Li2OPropertyHelper.h"

/**
 * Computes the tritium diffusivity in Li$_2$O from literature Arrhenius correlations.
 * The diffusivity is provided as both a regular and an AD material property. The model
 * coefficients are looked up once at construction, so evaluating a quadrature point involves
 * no model-dependent branching.
 */
class TritiumDiffusivityLi2O : public Material
{
public:
  static InputParameters validParams();

  TritiumDiffusivityLi2O(const InputParameters & parameters);

protected:
  void computeQpProperties() override;

  /// Temperature (K)
  const ADVariableValue & _temperature;
  /// Selected diffusivity model
  const Li2OPropertyHelper::DiffusivityModel _model;
  /// Name of the selected model, used in messages
  const std::string _model_name;
  /// Behavior when the temperature is outside the documented validity range
  const Li2OPropertyHelper::ValidityAction _validity_action;
  /// Coefficients and validity range of the selected model
  const Li2OPropertyHelper::DiffusivityModelData _model_data;
  /// ID of the out-of-range solution warning, registered once at construction
  const InvalidSolutionID _out_of_range_warning_id;

  /// Regular diffusivity material property
  MaterialProperty<Real> & _diffusivity;
  /// AD diffusivity material property
  ADMaterialProperty<Real> & _ad_diffusivity;
};
