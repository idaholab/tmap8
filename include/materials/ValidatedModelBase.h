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

#include <functional>

/**
 * Base class for materials that evaluate one literature correlation, selected with an enum
 * parameter, and that must respond when the temperature leaves the documented validity range of
 * the selected model. It provides the 'temperature' and 'validity_action' parameters, looks up the
 * model data once at construction, and implements the ignore / warning / error behavior in
 * checkTemperatureValidity().
 *
 * Derived classes must add a MooseEnum parameter named 'model' whose options come from the enum
 * class ModelEnum (declared with CreateMooseEnumClass), declare their own properties, and call
 * checkTemperatureValidity() before evaluating the correlation. Correlations with an Arrhenius form
 * that need scaling parameters should derive from ValidatedModelMaterial instead.
 *
 * @tparam ModelEnum enum class of the available models
 * @tparam ModelData struct holding the coefficients of one model, with a member 'metadata' of type
 *                   ModelValidity::ModelMetadata
 */
template <typename ModelEnum, typename ModelData>
class ValidatedModelBase : public Material
{
public:
  static InputParameters validParams()
  {
    auto params = Material::validParams();
    params.addRequiredCoupledVar("temperature", "The temperature in K.");
    params.addParam<MooseEnum>(
        "validity_action",
        MooseEnum(ModelValidity::getValidityActionOptions(), "warning"),
        "What to do when the selected model is used outside its documented range: 'ignore' does "
        "nothing, 'warning' counts the occurrence as a MOOSE solution warning that is summarized "
        "at the end of the run, and 'error' stops the run.");
    return params;
  }

  /**
   * @param parameters the input parameters
   * @param lookup function returning the data (coefficients and validity range) of a model. It is
   *               called once, during construction, and may capture the input parameters.
   */
  ValidatedModelBase(const InputParameters & parameters,
                     const std::function<ModelData(ModelEnum)> & lookup)
    : Material(parameters),
      _temperature(adCoupledValue("temperature")),
      _model(getParam<MooseEnum>("model").template getEnum<ModelEnum>()),
      _model_name(getParam<MooseEnum>("model")),
      _validity_action(
          getParam<MooseEnum>("validity_action").template getEnum<ModelValidity::ValidityAction>()),
      _model_data(lookup(_model)),
      _out_of_range_warning_id(registerInvalidSolutionInternal(
          ModelValidity::warningMessage(name(), _model_name, _model_data.metadata),
          /*warning=*/true))
  {
  }

protected:
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

  /**
   * Apply the validity action if a composition is outside the documented composition range of the
   * model (see ModelMetadata). The composition is an input parameter that is constant in space and
   * time, so this is meant to be called once, from the constructor of the derived class: nothing for
   * 'ignore', a warning for 'warning', and an error on the parameter for 'error'.
   * @param composition the composition (-)
   * @param param_name name of the input parameter holding the composition
   */
  void checkCompositionValidity(const Real composition, const std::string & param_name) const
  {
    applyParamValidityAction(
        ModelValidity::compositionMessage(name(), _model_name, composition, _model_data.metadata),
        param_name);
  }

  /**
   * Apply the validity action to a message describing an input parameter that is outside the
   * documented validity of the model: nothing for 'ignore' or an empty message, a warning for
   * 'warning', and an error on the parameter for 'error'.
   * @param message the message, empty if the parameter is valid
   * @param param_name name of the input parameter
   */
  void applyParamValidityAction(const std::string & message, const std::string & param_name) const
  {
    if (_validity_action == ModelValidity::ValidityAction::ignore || message.empty())
      return;

    if (_validity_action == ModelValidity::ValidityAction::warning)
      mooseWarning(message);
    else
      paramError(param_name, message);
  }

  /// Temperature (K)
  const ADVariableValue & _temperature;
  /// Selected model
  const ModelEnum _model;
  /// Name of the selected model, used in messages
  const std::string _model_name;
  /// Behavior when the temperature is outside the documented validity range
  const ModelValidity::ValidityAction _validity_action;
  /// Coefficients and validity range of the selected model
  const ModelData _model_data;
  /// ID of the out-of-range solution warning, registered once at construction
  const InvalidSolutionID _out_of_range_warning_id;
};
