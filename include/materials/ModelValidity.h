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
#include <limits>
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
  /// Lower bound of the documented composition range (-), unrestricted by default
  Real min_composition = 0.0;
  /// Upper bound of the documented composition range (-), unrestricted by default
  Real max_composition = 1.0;
  /// Whether the documented composition range restricts the model
  bool has_composition_range = false;
  /// Name of the composition variable used in messages, e.g. "atomic fraction of the solute"
  std::string composition_name = "composition";
  /// Lower bound of the documented pressure range (Pa), unrestricted by default
  Real min_pressure = 0.0;
  /// Upper bound of the documented pressure range (Pa), unrestricted by default
  Real max_pressure = std::numeric_limits<Real>::max();
  /// Whether the documented pressure range restricts the model
  bool has_pressure_range = false;
  /// Whether the temperature is checked against the documented range, e.g. false for a model that
  /// is documented for a single temperature but is treated as temperature independent
  bool check_temperature = true;
};

/**
 * Check whether a temperature lies within the documented validity range (bounds included).
 * @param metadata the model metadata
 * @param temperature the temperature (K)
 */
inline bool
isInRange(const ModelMetadata & metadata, const Real temperature)
{
  return !metadata.check_temperature ||
         (temperature >= metadata.min_temperature && temperature <= metadata.max_temperature);
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

/// Tolerance on the composition bounds
constexpr Real composition_tolerance = 1e-9;

/// Relative tolerance on the pressure bounds
constexpr Real pressure_tolerance = 1e-9;

/**
 * Check whether a pressure lies within the documented pressure range (bounds included, up to a
 * small relative tolerance). It is always true if the model has no pressure range.
 * @param metadata the model metadata
 * @param pressure the pressure (Pa)
 */
inline bool
isPressureInRange(const ModelMetadata & metadata, const Real pressure)
{
  return !metadata.has_pressure_range ||
         (pressure >= metadata.min_pressure * (1.0 - pressure_tolerance) &&
          pressure <= metadata.max_pressure * (1.0 + pressure_tolerance));
}

/**
 * Format the documented pressure range in scientific notation.
 * @param metadata the model metadata
 * @return the range, e.g. "[1.00e+03, 1.00e+05] Pa"
 */
inline std::string
pressureRange(const ModelMetadata & metadata)
{
  std::ostringstream oss;
  oss << std::scientific << std::setprecision(2) << "[" << metadata.min_pressure << ", "
      << metadata.max_pressure << "] Pa";
  return oss.str();
}

/**
 * Build the message reported once per object when the 'warning' validity action is used for a
 * pressure outside the documented range.
 * @param object_name name of the material object
 * @param model_name name of the selected model
 * @param metadata the model metadata
 */
inline std::string
pressureWarningMessage(const std::string & object_name,
                       const std::string & model_name,
                       const ModelMetadata & metadata)
{
  return "In " + object_name + ": model '" + model_name +
         "' is being used outside its documented pressure range " + pressureRange(metadata) +
         ". Source: " + metadata.citation + ".";
}

/**
 * Build the message describing a pressure outside the documented pressure range.
 * @param object_name name of the material object
 * @param model_name name of the selected model
 * @param pressure the offending pressure (Pa)
 * @param metadata the model metadata
 * @return the message, or an empty string if the pressure is within range
 */
inline std::string
pressureMessage(const std::string & object_name,
                const std::string & model_name,
                const Real pressure,
                const ModelMetadata & metadata)
{
  if (isPressureInRange(metadata, pressure))
    return "";

  std::ostringstream oss;
  oss << "In " << object_name << ": model '" << model_name
      << "' is being used outside its documented validity range because pressure "
      << std::scientific << std::setprecision(2) << pressure << " Pa is outside "
      << pressureRange(metadata) << ". Source: " << metadata.citation << ". "
      << metadata.validity_note;
  return oss.str();
}

/**
 * Check whether a composition lies within the documented composition range (bounds included, up to
 * a small tolerance). It is always true if the model has no composition range.
 * @param metadata the model metadata
 * @param composition the composition (-)
 */
inline bool
isCompositionInRange(const ModelMetadata & metadata, const Real composition)
{
  return !metadata.has_composition_range ||
         (composition >= metadata.min_composition - composition_tolerance &&
          composition <= metadata.max_composition + composition_tolerance);
}

/**
 * Build the message describing a composition outside the documented composition range.
 * @param object_name name of the material object
 * @param model_name name of the selected model
 * @param composition the offending composition (-)
 * @param metadata the model metadata
 * @return the message, or an empty string if the composition is within range
 */
inline std::string
compositionMessage(const std::string & object_name,
                   const std::string & model_name,
                   const Real composition,
                   const ModelMetadata & metadata)
{
  if (isCompositionInRange(metadata, composition))
    return "";

  std::ostringstream oss;
  oss << "In " << object_name << ": model '" << model_name
      << "' is being used outside its documented validity range because "
      << metadata.composition_name << " " << std::fixed << std::setprecision(4) << composition
      << " is outside [" << metadata.min_composition << ", " << metadata.max_composition
      << "]. Source: " << metadata.citation << ". " << metadata.validity_note;
  return oss.str();
}
}
