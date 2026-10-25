/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2026 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#include "DensityPbLi.h"

registerMooseObject("TMAP8App", DensityPbLi);

InputParameters
DensityPbLi::validParams()
{
  auto params = ValidatedModelBase::validParams();
  params.addClassDescription("Computes the density of PbLi as a function of temperature from "
                             "literature correlations and provides both regular and AD material "
                             "properties.");
  params.addParam<MaterialPropertyName>(
      "property_name", "density", "The regular material property name for the density.");
  params.addParam<MaterialPropertyName>(
      "ad_property_name", "ad_density", "The AD material property name for the density.");
  params.addParam<MooseEnum>(
      "model",
      MooseEnum(PbLiPropertyHelper::getDensityModelOptions(), "LinearExpansion"),
      "The PbLi density correlation.");
  return params;
}

DensityPbLi::DensityPbLi(const InputParameters & parameters)
  : ValidatedModelBase(parameters, PbLiPropertyHelper::densityModelData),
    _density(declareProperty<Real>(getParam<MaterialPropertyName>("property_name"))),
    _ad_density(declareADProperty<Real>(getParam<MaterialPropertyName>("ad_property_name")))
{
}

void
DensityPbLi::computeQpProperties()
{
  checkTemperatureValidity(MetaPhysicL::raw_value(_temperature[_qp]));

  const auto ad_value = PbLiPropertyHelper::computeDensity(_model_data, _temperature[_qp]);
  _density[_qp] = MetaPhysicL::raw_value(ad_value);
  _ad_density[_qp] = ad_value;
}
