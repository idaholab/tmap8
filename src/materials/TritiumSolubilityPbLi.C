/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2026 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#include "TritiumSolubilityPbLi.h"

#include "SinglePhaseFluidProperties.h"

registerMooseObject("TMAP8App", TritiumSolubilityPbLi);

namespace
{
/// Values of the input parameters used by some solubility models
PbLiPropertyHelper::SolubilityInputs
solubilityInputs(const InputParameters & parameters)
{
  PbLiPropertyHelper::SolubilityInputs inputs;
  inputs.lithium_fraction = parameters.get<Real>("lithium_atomic_fraction");
  inputs.lithium_sieverts_constant = parameters.get<Real>("lithium_sieverts_constant");
  inputs.lead_sieverts_constant = parameters.get<Real>("lead_sieverts_constant");
  return inputs;
}
}

InputParameters
TritiumSolubilityPbLi::validParams()
{
  auto params = ValidatedModelMaterial::validParams();
  params.addClassDescription("Computes hydrogen isotope solubility in PbLi from literature "
                             "correlations, in atoms m$^{-3}$ Pa$^{-1/2}$, and provides both "
                             "regular and AD material properties.");
  params.addParam<MaterialPropertyName>(
      "property_name", "solubility", "The regular material property name for the solubility.");
  params.addParam<MaterialPropertyName>(
      "ad_property_name", "ad_solubility", "The AD material property name for the solubility.");
  params.addRequiredParam<MooseEnum>("model",
                                     MooseEnum(PbLiPropertyHelper::getSolubilityModelOptions()),
                                     "The PbLi hydrogen isotope solubility correlation.");
  params.addParam<Real>("lithium_atomic_fraction",
                        0.17,
                        "Lithium atomic fraction of the PbLi (-). It is checked against the "
                        "documented composition range of the model, converts atom-fraction "
                        "correlations to concentrations, and weights the mixing rule.");
  params.addParam<UserObjectName>(
      "fp",
      "The fluid properties providing the PbLi density, e.g. LeadLithiumFluidProperties. The "
      "density, in kg/m^3, is needed to convert the correlations published as atom fractions to "
      "concentrations. It is required by these models only, and unused by the others.");
  params.addCoupledVar("pressure",
                       "The gas pressure in Pa, at which the density is evaluated and the "
                       "documented pressure range of the selected model is checked. The standard "
                       "atmosphere is used to evaluate the density if it is not provided, and the "
                       "pressure range is then not checked.");
  params.addParam<Real>("lithium_sieverts_constant",
                        std::numeric_limits<Real>::quiet_NaN(),
                        "Sieverts constant of pure liquid lithium in atoms m^-3 Pa^-1/2. Required "
                        "by, and only used with, the Fukada2013MixingRule model. It must be "
                        "positive.");
  params.addParam<Real>("lead_sieverts_constant",
                        std::numeric_limits<Real>::quiet_NaN(),
                        "Sieverts constant of pure liquid lead in atoms m^-3 Pa^-1/2. Required by, "
                        "and only used with, the Fukada2013MixingRule model. It must be positive.");
  return params;
}

TritiumSolubilityPbLi::TritiumSolubilityPbLi(const InputParameters & parameters)
  : ValidatedModelMaterial(
        parameters,
        [&parameters](const PbLiPropertyHelper::SolubilityModel model)
        { return PbLiPropertyHelper::solubilityModelData(model, solubilityInputs(parameters)); }),
    _lithium_fraction(getParam<Real>("lithium_atomic_fraction")),
    _fp(isParamValid("fp") ? &getUserObject<SinglePhaseFluidProperties>("fp") : nullptr),
    _pressure(isCoupled("pressure") ? &adCoupledValue("pressure") : nullptr),
    _solubility(declareProperty<Real>(getParam<MaterialPropertyName>("property_name"))),
    _ad_solubility(declareADProperty<Real>(getParam<MaterialPropertyName>("ad_property_name")))
{
  if (_model == PbLiPropertyHelper::SolubilityModel::Fukada2013MixingRule)
    for (const auto * name : {"lithium_sieverts_constant", "lead_sieverts_constant"})
    {
      if (!isParamSetByUser(name))
        paramError(name, "The Fukada2013MixingRule model requires this parameter.");
      if (getParam<Real>(name) <= 0.0)
        paramError(name, "The Sieverts constant must be positive.");
    }

  if (_model_data.basis == PbLiPropertyHelper::SolubilityBasis::AtomFraction && !_fp)
    paramError(
        "fp",
        "The ",
        _model_name,
        " model is published as an atom fraction and needs the PbLi density to convert it "
        "to a concentration. Provide the fluid properties, e.g. LeadLithiumFluidProperties.");

  checkCompositionValidity(_lithium_fraction, "lithium_atomic_fraction");
}

void
TritiumSolubilityPbLi::computeQpProperties()
{
  checkTemperatureValidity(MetaPhysicL::raw_value(_temperature[_qp]));
  if (_pressure)
    checkPressureValidity(MetaPhysicL::raw_value((*_pressure)[_qp]));

  // Number density of metal atoms from the PbLi density of the fluid properties (kg/m^3 to g/m^3)
  ADReal atom_density = 0.0;
  if (_fp)
  {
    const ADReal pressure = _pressure ? (*_pressure)[_qp] : ADReal(PhysicalConstants::atm_to_Pa);
    const ADReal density =
        _fp->rho_from_p_T(pressure, _temperature[_qp]) * PbLiPropertyHelper::g_per_kg;
    atom_density = PbLiPropertyHelper::atomDensity(density, _lithium_fraction);
  }

  const auto ad_value =
      PbLiPropertyHelper::computeSolubility(_model_data, _temperature[_qp], atom_density);
  _solubility[_qp] = MetaPhysicL::raw_value(ad_value);
  _ad_solubility[_qp] = ad_value;
}
