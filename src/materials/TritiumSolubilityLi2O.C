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
  auto params = Material::validParams();
  params.addClassDescription(
      "Computes hydrogen isotope solubility in Li$_2$O from reduced-species literature "
      "correlations and provides both regular and AD material properties.");
  params.addRequiredCoupledVar("temperature", "The Li$_2$O temperature in K.");
  params.addParam<MaterialPropertyName>(
      "property_name", "solubility", "The regular material property name for the solubility.");
  params.addParam<MaterialPropertyName>(
      "ad_property_name", "ad_solubility", "The AD material property name for the solubility.");
  params.addParam<MooseEnum>(
      "model",
      MooseEnum(Li2OPropertyHelper::getSolubilityModelOptions(), "Ohira1989Tritium"),
      "The Li$_2$O hydrogen isotope solubility correlation.");
  params.addParam<MooseEnum>(
      "validity_action",
      MooseEnum(Li2OPropertyHelper::getValidityActionOptions(), "warning"),
      "What to do when the selected model is used outside its documented temperature range: "
      "'ignore' does nothing, 'warning' counts the occurrence as a MOOSE solution warning that is "
      "summarized at the end of the run, and 'error' stops the run.");
  return params;
}

TritiumSolubilityLi2O::TritiumSolubilityLi2O(const InputParameters & parameters)
  : Material(parameters),
    _temperature(adCoupledValue("temperature")),
    _model(getParam<MooseEnum>("model").getEnum<Li2OPropertyHelper::SolubilityModel>()),
    _model_name(getParam<MooseEnum>("model")),
    _validity_action(
        getParam<MooseEnum>("validity_action").getEnum<Li2OPropertyHelper::ValidityAction>()),
    _model_data(Li2OPropertyHelper::solubilityModelData(_model)),
    _out_of_range_warning_id(registerInvalidSolutionInternal(
        "In " + name() + ": model '" + _model_name +
            "' is being used outside its documented validity range [" +
            std::to_string(_model_data.metadata.min_temperature) + ", " +
            std::to_string(_model_data.metadata.max_temperature) + "] K.",
        /*warning=*/true)),
    _solubility(declareProperty<Real>(getParam<MaterialPropertyName>("property_name"))),
    _ad_solubility(declareADProperty<Real>(getParam<MaterialPropertyName>("ad_property_name")))
{
}

void
TritiumSolubilityLi2O::computeQpProperties()
{
  const Real temperature = MetaPhysicL::raw_value(_temperature[_qp]);

  if (_validity_action != Li2OPropertyHelper::ValidityAction::ignore &&
      !Li2OPropertyHelper::isInRange(_model_data.metadata, temperature))
  {
    if (_validity_action == Li2OPropertyHelper::ValidityAction::warning)
      flagInvalidSolutionInternal<true>(_out_of_range_warning_id);
    else
      mooseError(Li2OPropertyHelper::validityMessage(
          name(), _model_name, temperature, _model_data.metadata));
  }

  const auto ad_value = Li2OPropertyHelper::computeSolubility(_model_data, _temperature[_qp]);
  _solubility[_qp] = MetaPhysicL::raw_value(ad_value);
  _ad_solubility[_qp] = ad_value;
}
