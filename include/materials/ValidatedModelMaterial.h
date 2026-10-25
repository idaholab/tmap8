/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2026 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#pragma once

#include "ValidatedModelBase.h"

/**
 * Base class for materials that evaluate one Arrhenius literature correlation, selected with an
 * enum parameter, and that must respond when the temperature leaves the documented validity range
 * of the selected model. On top of ValidatedModelBase, it provides the 'prefactor_scaling' and
 * 'activation_energy_scaling' parameters and applies them to the model data once at construction.
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
class ValidatedModelMaterial : public ValidatedModelBase<ModelEnum, ModelData>
{
public:
  static InputParameters validParams()
  {
    InputParameters params = ValidatedModelBase<ModelEnum, ModelData>::validParams();
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
   * @param lookup function returning the data (coefficients and validity range) of a model, as
   *               published. The scaling parameters are applied to it here.
   */
  ValidatedModelMaterial(const InputParameters & parameters,
                         const std::function<ModelData(ModelEnum)> & lookup)
    : ValidatedModelBase<ModelEnum, ModelData>(
          parameters,
          [&lookup, &parameters](const ModelEnum model)
          { return scaleModelData(lookup(model), parameters); })
  {
  }

private:
  /**
   * Apply the 'prefactor_scaling' and 'activation_energy_scaling' parameters to the data of a model
   * @param data the data of the model as published
   * @param parameters the input parameters
   * @return the data with the scaled pre-exponential factor and activation energy
   */
  static ModelData scaleModelData(ModelData data, const InputParameters & parameters)
  {
    data.prefactor *= parameters.get<Real>("prefactor_scaling");
    data.activation_energy *= parameters.get<Real>("activation_energy_scaling");
    return data;
  }
};
