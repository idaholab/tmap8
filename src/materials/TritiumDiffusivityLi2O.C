/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2025 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#include "TritiumDiffusivityLi2O.h"

#include "Li2OPropertyHelper.h"

registerMooseObject("TMAP8App", TritiumDiffusivityLi2O);

InputParameters
TritiumDiffusivityLi2O::validParams()
{
  auto params = Material::validParams();
  params.addClassDescription(
      "Computes tritium diffusivity in Li2O from literature correlations and provides both "
      "regular and AD material properties.");
  params.addRequiredCoupledVar("temperature", "The Li2O temperature in K.");
  params.addParam<MaterialPropertyName>(
      "property_name", "diffusivity", "The regular material property name for the diffusivity.");
  params.addParam<MaterialPropertyName>(
      "ad_property_name", "ad_diffusivity", "The AD material property name for the diffusivity.");
  params.addRequiredParam<MooseEnum>(
      "model",
      MooseEnum("Ohira1989 Tanifuji1987 Kurasawa1991 Tanaka1988Grain "
                "Tanaka1988GrainBoundary"),
      "The Li2O tritium diffusivity correlation.");
  params.addParam<MooseEnum>("validity_action",
                             MooseEnum("ignore warning error", "warning"),
                             "How the material responds when the selected model is used outside "
                             "its documented validity range.");
  return params;
}

TritiumDiffusivityLi2O::TritiumDiffusivityLi2O(const InputParameters & parameters)
  : Material(parameters),
    _temperature(adCoupledValue("temperature")),
    _model(getParam<MooseEnum>("model")),
    _validity_action(getParam<MooseEnum>("validity_action")),
    _diffusivity(declareProperty<Real>(getParam<MaterialPropertyName>("property_name"))),
    _ad_diffusivity(declareADProperty<Real>(getParam<MaterialPropertyName>("ad_property_name"))),
    _issued_warning(false)
{
}

void
TritiumDiffusivityLi2O::computeQpProperties()
{
  const Real temperature = MetaPhysicL::raw_value(_temperature[_qp]);
  const auto metadata = Li2OPropertyHelper::diffusivityMetadata(_model);
  Li2OPropertyHelper::handleValidity(
      name(), _model, temperature, metadata, _validity_action, _issued_warning);

  const auto ad_value = Li2OPropertyHelper::computeDiffusivity(_model, _temperature[_qp]);
  _diffusivity[_qp] = MetaPhysicL::raw_value(ad_value);
  _ad_diffusivity[_qp] = ad_value;
}
