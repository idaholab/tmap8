/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2026 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#pragma once

#include "Material.h"

#include "ModelValidity.h"

/**
 * Base class for materials that evaluate one literature correlation, selected with an enum
 * parameter, and that must respond when the temperature leaves the documented validity range of
 * the selected model. It provides the 'temperature', 'validity_action', 'prefactor_scaling' and
 * 'activation_energy_scaling' parameters, looks up the model data once at construction, applies the
 * scaling factors to it, and implements the ignore / warning / error behavior in
 * checkTemperatureValidity().
 *
 * Derived classes must add a MooseEnum parameter named 'model' whose options come from the enum
 * class ModelEnum (declared with CreateMooseEnumClass), declare their own properties, and call
 * checkTemperatureValidity() before evaluating the correlation.
 *
 * @tparam ModelEnum enum class of the available models
 * @tparam ModelData struct holding the coefficients of one model, with a member 'metadata' of type
 *                   ModelValidity::ModelMetadata and Real members 'prefactor' and
 *                   'activation_energy' of an Arrhenius expression prefactor * exp(-Ea / (R T))
 */
template <typename ModelEnum, typename ModelData>
class ValidatedModelMaterial : public Material
{
public:
  static InputParameters validParams()
  {
    auto params = Material::validParams();
    params.addRequiredCoupledVar("temperature", "The temperature in K.");
    params.addParam<MooseEnum>(
        "validity_action",
        MooseEnum(ModelValidity::getValidityActionOptions(), "warning"),
        "What to do when the selected model is used outside its documented temperature range: "
        "'ignore' does nothing, 'warning' counts the occurrence as a MOOSE solution warning that "
        "is summarized at the end of the run, and 'error' stops the run.");
    params.addRangeCheckedParam<Real>(
        "prefactor_scaling",
        1.0,
        "prefactor_scaling>=0",
        "Factor multiplying the pre-exponential factor of the selected model. It must not be "
        "negative. The default of 1 uses the model as published.");
    params.addParam<Real>(
        "activation_energy_scaling",
        1.0,
        "Factor multiplying the activation energy of the selected model. It may be negative. The "
        "default of 1 uses the model as published.");
    return params;
  }

  /**
   * @param parameters the input parameters
   * @param lookup function returning the data (coefficients and validity range) of a model
   */
  ValidatedModelMaterial(const InputParameters & parameters, ModelData (*lookup)(ModelEnum))
    : Material(parameters),
      _temperature(adCoupledValue("temperature")),
      _model(getParam<MooseEnum>("model").template getEnum<ModelEnum>()),
      _model_name(getParam<MooseEnum>("model")),
      _validity_action(
          getParam<MooseEnum>("validity_action").template getEnum<ModelValidity::ValidityAction>()),
      _model_data(scaleModelData(lookup(_model))),
      _out_of_range_warning_id(registerInvalidSolutionInternal(
          ModelValidity::warningMessage(name(), _model_name, _model_data.metadata),
          /*warning=*/true))
  {
  }

protected:
  /**
   * Apply the 'prefactor_scaling' and 'activation_energy_scaling' parameters to the data of a model
   * @param data the data of the model as published
   * @return the data with the scaled pre-exponential factor and activation energy
   */
  ModelData scaleModelData(ModelData data) const
  {
    data.prefactor *= getParam<Real>("prefactor_scaling");
    data.activation_energy *= getParam<Real>("activation_energy_scaling");
    return data;
  }

  /**
   * Apply the validity action if the temperature is outside the documented range of the model:
   * nothing for 'ignore', a MOOSE solution warning for 'warning', and an error for 'error'.
   * @param temperature the temperature (K)
   */
  void checkTemperatureValidity(const Real temperature) const
  {
    if (_validity_action == ModelValidity::ValidityAction::ignore ||
        ModelValidity::isInRange(_model_data.metadata, temperature))
      return;

    if (_validity_action == ModelValidity::ValidityAction::warning)
      flagInvalidSolutionInternal<true>(_out_of_range_warning_id);
    else
      mooseError(
          ModelValidity::validityMessage(name(), _model_name, temperature, _model_data.metadata));
  }

  /// Temperature (K)
  const ADVariableValue & _temperature;
  /// Selected model
  const ModelEnum _model;
  /// Name of the selected model, used in messages
  const std::string _model_name;
  /// Behavior when the temperature is outside the documented validity range
  const ModelValidity::ValidityAction _validity_action;
  /// Coefficients (after scaling) and validity range of the selected model
  const ModelData _model_data;
  /// ID of the out-of-range solution warning, registered once at construction
  const InvalidSolutionID _out_of_range_warning_id;
};
