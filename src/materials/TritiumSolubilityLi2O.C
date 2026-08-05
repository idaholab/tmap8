/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2025 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#include "TritiumSolubilityLi2O.h"

#include "Li2OPropertyHelper.h"

registerMooseObject("TMAP8App", TritiumSolubilityLi2O);

InputParameters
TritiumSolubilityLi2O::validParams()
{
  auto params = Material::validParams();
  params.addClassDescription(
      "Computes tritium solubility in Li2O from reduced-species literature correlations and "
      "provides both regular and AD material properties.");
  params.addRequiredCoupledVar("temperature", "The Li2O temperature in K.");
  params.addParam<MaterialPropertyName>(
      "property_name", "solubility", "The regular material property name for the solubility.");
  params.addParam<MaterialPropertyName>(
      "ad_property_name", "ad_solubility", "The AD material property name for the solubility.");
  params.addParam<MooseEnum>(
      "model", MooseEnum("Ohira1989", "Ohira1989"), "The Li2O tritium solubility correlation.");
  params.addParam<MooseEnum>("validity_action",
                             MooseEnum("ignore warning error", "warning"),
                             "How the material responds when the selected model is used outside "
                             "its documented validity range.");
  return params;
}

TritiumSolubilityLi2O::TritiumSolubilityLi2O(const InputParameters & parameters)
  : Material(parameters),
    _temperature(adCoupledValue("temperature")),
    _model(getParam<MooseEnum>("model")),
    _validity_action(getParam<MooseEnum>("validity_action")),
    _solubility(declareProperty<Real>(getParam<MaterialPropertyName>("property_name"))),
    _ad_solubility(declareADProperty<Real>(getParam<MaterialPropertyName>("ad_property_name"))),
    _issued_warning(false)
{
}

void
TritiumSolubilityLi2O::computeQpProperties()
{
  const Real temperature = MetaPhysicL::raw_value(_temperature[_qp]);
  const auto metadata = Li2OPropertyHelper::solubilityMetadata(_model);
  Li2OPropertyHelper::handleValidity(
      name(), _model, temperature, metadata, _validity_action, _issued_warning);

  const auto ad_value = Li2OPropertyHelper::computeSolubility(_model, _temperature[_qp]);
  _solubility[_qp] = MetaPhysicL::raw_value(ad_value);
  _ad_solubility[_qp] = ad_value;
}
