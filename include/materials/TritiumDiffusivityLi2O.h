/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2025 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#pragma once

#include "Material.h"

class TritiumDiffusivityLi2O : public Material
{
public:
  static InputParameters validParams();

  TritiumDiffusivityLi2O(const InputParameters & parameters);

protected:
  void computeQpProperties() override;

  const ADVariableValue & _temperature;
  const MooseEnum _model;
  const MooseEnum _validity_action;

  MaterialProperty<Real> & _diffusivity;
  ADMaterialProperty<Real> & _ad_diffusivity;

  bool _issued_warning;
};
