/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2026 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#pragma once

#include "Material.h"

class TritiumSolubilityLi2O : public Material
{
public:
  static InputParameters validParams();

  TritiumSolubilityLi2O(const InputParameters & parameters);

protected:
  void computeQpProperties() override;

  const ADVariableValue & _temperature;
  const MooseEnum _model;
  const MooseEnum _validity_action;

  MaterialProperty<Real> & _solubility;
  ADMaterialProperty<Real> & _ad_solubility;

  bool _issued_warning;
};
