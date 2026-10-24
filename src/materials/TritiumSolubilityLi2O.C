/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2026 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#include "TritiumSolubilityLi2O.h"

registerMooseObject("TMAP8App", TritiumSolubilityLi2O);

InputParameters
TritiumSolubilityLi2O::validParams()
{
  auto params = ValidatedModelMaterial::validParams();
  params.addClassDescription(
      "Computes hydrogen isotope solubility in Li$_2$O from reduced-species literature correlations and provides both regular and AD material properties.");
  params.addParam<MaterialPropertyName>(
      "property_name", "solubility", "The regular material property name for the solubility.");
  params.addParam<MaterialPropertyName>(
      "ad_property_name", "ad_solubility", "The AD material property name for the solubility.");
  params.addParam<MooseEnum>(
      "model",
      MooseEnum(Li2OPropertyHelper::getSolubilityModelOptions(), "Ohira1989Tritium"),
      "The Li$_2$O hydrogen isotope solubility correlation.");
  return params;
}

TritiumSolubilityLi2O::TritiumSolubilityLi2O(const InputParameters & parameters)
  : ValidatedModelMaterial(parameters, Li2OPropertyHelper::solubilityModelData),
    _solubility(declareProperty<Real>(getParam<MaterialPropertyName>("property_name"))),
    _ad_solubility(declareADProperty<Real>(getParam<MaterialPropertyName>("ad_property_name")))
{
}

void
TritiumSolubilityLi2O::computeQpProperties()
{
  checkTemperatureValidity(MetaPhysicL::raw_value(_temperature[_qp]));

  const auto ad_value = Li2OPropertyHelper::computeSolubility(_model_data, _temperature[_qp]);
  _solubility[_qp] = MetaPhysicL::raw_value(ad_value);
  _ad_solubility[_qp] = ad_value;
}
