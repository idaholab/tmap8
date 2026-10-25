/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2026 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#pragma once

#include "MooseEnum.h"

#include <iomanip>
#include <sstream>
#include <string>

/**
 * Types and helper functions describing the documented temperature validity range of a literature
 * correlation, shared by the materials that derive from ValidatedModelMaterial.
 */
namespace ModelValidity
{
/// Behavior when a model is evaluated outside its documented validity range
CreateMooseEnumClass(ValidityAction, ignore, warning, error);

/// Documented validity range and provenance of a literature correlation
struct ModelMetadata
{
  /// Short literature citation of the source
  std::string citation;
  /// Lower bound of the documented temperature range (K)
  Real min_temperature;
  /// Upper bound of the documented temperature range (K)
  Real max_temperature;
  /// Description of the conditions the correlation was derived under
  std::string validity_note;
  /// Lower bound of the documented lithium atomic fraction range (-), unrestricted by default
  Real min_lithium_fraction = 0.0;
  /// Upper bound of the documented lithium atomic fraction range (-), unrestricted by default
  Real max_lithium_fraction = 1.0;
  /// Whether the documented lithium atomic fraction range restricts the model
  bool has_composition_range = false;
};

/**
 * Check whether a temperature lies within the documented validity range (bounds included).
 * @param metadata the model metadata
 * @param temperature the temperature (K)
 */
inline bool
isInRange(const ModelMetadata & metadata, const Real temperature)
{
  return temperature >= metadata.min_temperature && temperature <= metadata.max_temperature;
}

/**
 * Format the documented temperature range, with two digits after the decimal point.
 * @param metadata the model metadata
 * @return the range, e.g. "[600.00, 711.00] K"
 */
inline std::string
temperatureRange(const ModelMetadata & metadata)
{
  std::ostringstream oss;
  oss << std::fixed << std::setprecision(2) << "[" << metadata.min_temperature << ", "
      << metadata.max_temperature << "] K";
  return oss.str();
}

/**
 * Build the message reported once per object when the 'warning' validity action is used.
 * @param object_name name of the material object
 * @param model_name name of the selected model
 * @param metadata the model metadata
 */
inline std::string
warningMessage(const std::string & object_name,
               const std::string & model_name,
               const ModelMetadata & metadata)
{
  return "In " + object_name + ": model '" + model_name +
         "' is being used outside its documented validity range " + temperatureRange(metadata) +
         ". Source: " + metadata.citation + ".";
}

/**
 * Build the message describing a temperature outside the documented validity range.
 * @param object_name name of the material object
 * @param model_name name of the selected model
 * @param temperature the offending temperature (K)
 * @param metadata the model metadata
 * @return the message, or an empty string if the temperature is within range
 */
inline std::string
validityMessage(const std::string & object_name,
                const std::string & model_name,
                const Real temperature,
                const ModelMetadata & metadata)
{
  if (isInRange(metadata, temperature))
    return "";

  std::ostringstream oss;
  oss << "In " << object_name << ": model '" << model_name
      << "' is being used outside its documented validity range because temperature " << std::fixed
      << std::setprecision(2) << temperature << " K is outside " << temperatureRange(metadata)
      << ". Source: " << metadata.citation << ". " << metadata.validity_note;
  return oss.str();
}

/// Tolerance on the lithium atomic fraction bounds, so that e.g. 0.157 matches Pb-15.7Li
constexpr Real composition_tolerance = 1e-9;

/**
 * Check whether a lithium atomic fraction lies within the documented composition range (bounds
 * included, up to a small tolerance). It is always true if the model has no composition range.
 * @param metadata the model metadata
 * @param lithium_fraction the lithium atomic fraction (-)
 */
inline bool
isCompositionInRange(const ModelMetadata & metadata, const Real lithium_fraction)
{
  return !metadata.has_composition_range ||
         (lithium_fraction >= metadata.min_lithium_fraction - composition_tolerance &&
          lithium_fraction <= metadata.max_lithium_fraction + composition_tolerance);
}

/**
 * Build the message describing a lithium atomic fraction outside the documented composition range.
 * @param object_name name of the material object
 * @param model_name name of the selected model
 * @param lithium_fraction the offending lithium atomic fraction (-)
 * @param metadata the model metadata
 * @return the message, or an empty string if the composition is within range
 */
inline std::string
compositionMessage(const std::string & object_name,
                   const std::string & model_name,
                   const Real lithium_fraction,
                   const ModelMetadata & metadata)
{
  if (isCompositionInRange(metadata, lithium_fraction))
    return "";

  std::ostringstream oss;
  oss << "In " << object_name << ": model '" << model_name
      << "' is being used outside its documented validity range because lithium atomic fraction "
      << std::fixed << std::setprecision(4) << lithium_fraction << " is outside ["
      << metadata.min_lithium_fraction << ", " << metadata.max_lithium_fraction
      << "]. Source: " << metadata.citation << ". " << metadata.validity_note;
  return oss.str();
}
}
