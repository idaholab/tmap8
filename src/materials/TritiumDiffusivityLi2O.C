/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2026 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#include "TritiumDiffusivityLi2O.h"

registerMooseObject("TMAP8App", TritiumDiffusivityLi2O);

InputParameters
TritiumDiffusivityLi2O::validParams()
{
  auto params = ValidatedModelMaterial::validParams();
  params.addClassDescription(
      "Computes tritium diffusivity in Li$_2$O from literature correlations and provides both regular and AD material properties.");
  params.addParam<MaterialPropertyName>(
      "property_name", "diffusivity", "The regular material property name for the diffusivity.");
  params.addParam<MaterialPropertyName>(
      "ad_property_name", "ad_diffusivity", "The AD material property name for the diffusivity.");
  params.addRequiredParam<MooseEnum>(
      "model",
      MooseEnum(Li2OPropertyHelper::getDiffusivityModelOptions()),
      "The Li$_2$O tritium diffusivity correlation.");
  return params;
}

TritiumDiffusivityLi2O::TritiumDiffusivityLi2O(const InputParameters & parameters)
  : ValidatedModelMaterial(parameters, Li2OPropertyHelper::diffusivityModelData),
    _diffusivity(declareProperty<Real>(getParam<MaterialPropertyName>("property_name"))),
    _ad_diffusivity(declareADProperty<Real>(getParam<MaterialPropertyName>("ad_property_name")))
{
}

void
TritiumDiffusivityLi2O::computeQpProperties()
{
  checkTemperatureValidity(MetaPhysicL::raw_value(_temperature[_qp]));

  const auto ad_value = Li2OPropertyHelper::computeDiffusivity(_model_data, _temperature[_qp]);
  _diffusivity[_qp] = MetaPhysicL::raw_value(ad_value);
  _ad_diffusivity[_qp] = ad_value;
}
