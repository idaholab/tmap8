/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2026 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#include "TritiumDiffusivityPbLi.h"

registerMooseObject("TMAP8App", TritiumDiffusivityPbLi);

namespace
{
/// Isotope requested in the input, as the helper enum
PbLiPropertyHelper::Isotope
requestedIsotope(const InputParameters & parameters)
{
  return parameters.get<MooseEnum>("isotope").getEnum<PbLiPropertyHelper::Isotope>();
}
}

InputParameters
TritiumDiffusivityPbLi::validParams()
{
  auto params = ValidatedModelMaterial::validParams();
  params.addClassDescription("Computes hydrogen isotope diffusivity in PbLi from literature "
                             "correlations, with optional classical isotope scaling, and provides "
                             "both regular and AD material properties.");
  params.addParam<MaterialPropertyName>(
      "property_name", "diffusivity", "The regular material property name for the diffusivity.");
  params.addParam<MaterialPropertyName>(
      "ad_property_name", "ad_diffusivity", "The AD material property name for the diffusivity.");
  params.addRequiredParam<MooseEnum>("model",
                                     MooseEnum(PbLiPropertyHelper::getDiffusivityModelOptions()),
                                     "The PbLi hydrogen isotope diffusivity correlation.");
  params.addParam<MooseEnum>("isotope",
                             MooseEnum(PbLiPropertyHelper::getIsotopeOptions(), "T"),
                             "The hydrogen isotope the diffusivity is requested for.");
  params.addParam<bool>("isotope_scaling",
                        false,
                        "Whether to scale the pre-exponential factor of the model from the "
                        "isotope it was measured for to the requested isotope with the classical "
                        "factor sqrt(m_measured / m_requested). If false and the isotopes differ, "
                        "the 'validity_action' applies.");
  params.addParam<Real>("lithium_atomic_fraction",
                        PbLiPropertyHelper::default_lithium_fraction,
                        "Lithium atomic fraction of the PbLi (-), checked against the documented "
                        "composition range of the model.");
  params.addCoupledVar(
      "pressure",
      "The hydrogen isotope partial pressure in Pa. It is only used to check the documented pressure range of the "
      "selected model, and the check is skipped if it is not provided.");
  return params;
}

TritiumDiffusivityPbLi::TritiumDiffusivityPbLi(const InputParameters & parameters)
  : ValidatedModelMaterial(
        parameters,
        [&parameters](const PbLiPropertyHelper::DiffusivityModel model)
        {
          return PbLiPropertyHelper::diffusivityModelDataForIsotope(
              model, requestedIsotope(parameters), parameters.get<bool>("isotope_scaling"));
        }),
    _pressure(isCoupled("pressure") ? &adCoupledValue("pressure") : nullptr),
    _diffusivity(declareProperty<Real>(getParam<MaterialPropertyName>("property_name"))),
    _ad_diffusivity(declareADProperty<Real>(getParam<MaterialPropertyName>("ad_property_name")))
{
  checkCompositionValidity(getParam<Real>("lithium_atomic_fraction"), "lithium_atomic_fraction");

  // The model data was scaled to the requested isotope if requested; otherwise compare directly
  applyParamValidityAction(PbLiPropertyHelper::isotopeMessage(name(),
                                                              _model_name,
                                                              _model_data.isotope,
                                                              requestedIsotope(parameters),
                                                              _model_data.metadata),
                           "isotope");
}

void
TritiumDiffusivityPbLi::computeQpProperties()
{
  checkTemperatureValidity(MetaPhysicL::raw_value(_temperature[_qp]));
  if (_pressure)
    checkPressureValidity(MetaPhysicL::raw_value((*_pressure)[_qp]));

  const auto ad_value = PbLiPropertyHelper::computeDiffusivity(_model_data, _temperature[_qp]);
  _diffusivity[_qp] = MetaPhysicL::raw_value(ad_value);
  _ad_diffusivity[_qp] = ad_value;
}
