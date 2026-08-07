/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2025 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#pragma once

#include "MooseEnum.h"
#include "MooseError.h"
#include "TMAP8PhysicalConstants.h"

#include <cmath>
#include <limits>
#include <sstream>
#include <string>
#include <vector>

namespace Li2OPropertyHelper
{
const Real ideal_gas_constant = PhysicalConstants::ideal_gas_constant;

struct ModelMetadata
{
  std::string citation;
  Real min_temperature;
  Real max_temperature;
  std::string validity_note;
};

inline ModelMetadata
diffusivityMetadata(const MooseEnum & model)
{
  if (model == "Ohira1989")
    return {"O'Hira et al. (1989)",
            600.0,
            711.0,
            "Unirradiated single-crystal Li2O equilibrated with reduced tritium gas."};

  if (model == "Tanifuji1987")
    return {"Tanifuji et al. (1987)",
            573.0,
            950.0,
            "Neutron-irradiated single-crystal Li2O particles analyzed with a spherical diffusion "
            "model."};

  if (model == "Kurasawa1991")
    return {"Kurasawa and Watanabe (1991)",
            450.0 + 273.15,
            820.0 + 273.15,
            "In-situ release interpretation for single-crystal Li2O under sweep-gas chemistry "
            "effects."};

  if (model == "Terai1988Grain")
    return {"Terai et al. (1988/1989)",
            360.0 + 273.15,
            600.0 + 273.15,
            "Polycrystalline Li2O grain diffusivity from TTTEx analysis."};

  if (model == "Terai1988GrainBoundary")
    return {"Terai et al. (1988/1989)",
            360.0 + 273.15,
            600.0 + 273.15,
            "Polycrystalline Li2O grain-boundary diffusivity from TTTEx analysis."};

  mooseError("Unsupported Li2O diffusivity model: ", model);
}

inline ModelMetadata
solubilityMetadata(const MooseEnum & model)
{
  if (model == "Ohira1989")
    return {"O'Hira et al. (1989)",
            -std::numeric_limits<Real>::max(),
            std::numeric_limits<Real>::max(),
            "Reduced-species tritium dissolution in single-crystal Li2O. The published "
            "coefficient form has been implemented directly; the exact reported validity window "
            "for the solubility fit still needs verification from the primary paper."};

  mooseError("Unsupported Li2O solubility model: ", model);
}

inline std::string
validityMessage(const std::string & object_name,
                const MooseEnum & model,
                const Real temperature,
                const ModelMetadata & metadata)
{
  std::vector<std::string> violations;

  if (temperature < metadata.min_temperature || temperature > metadata.max_temperature)
  {
    std::ostringstream oss;
    oss << "temperature " << temperature << " K is outside [" << metadata.min_temperature << ", "
        << metadata.max_temperature << "] K";
    violations.push_back(oss.str());
  }

  if (violations.empty())
    return "";

  std::ostringstream oss;
  oss << "In " << object_name << ": model '" << model
      << "' is being used outside its documented validity range because ";
  for (std::size_t i = 0; i < violations.size(); ++i)
  {
    oss << violations[i];
    if (i + 1 < violations.size())
      oss << " and ";
  }
  oss << ". " << metadata.validity_note;
  return oss.str();
}

inline void
handleValidity(const std::string & object_name,
               const MooseEnum & model,
               const Real temperature,
               const ModelMetadata & metadata,
               const MooseEnum & validity_action,
               bool & issued_warning)
{
  const auto message = validityMessage(object_name, model, temperature, metadata);
  if (message.empty())
    return;

  if (validity_action == "ignore")
    return;

  if (validity_action == "warning")
  {
    if (!issued_warning)
    {
      mooseWarning(message);
      issued_warning = true;
    }
    return;
  }

  if (validity_action == "error")
    mooseError(message);

  mooseError("Unsupported Li2O validity_action: ", validity_action);
}

template <typename T>
inline T
computeDiffusivity(const MooseEnum & model, const T & temperature)
{
  using std::exp;

  if (model == "Ohira1989")
    return 1.2e-11 * exp(-45.1e3 / (ideal_gas_constant * temperature));

  if (model == "Tanifuji1987")
    return 1.16e-5 * exp(-101.0e3 / (ideal_gas_constant * temperature));

  if (model == "Kurasawa1991")
    return 2.0e-7 * exp(-81.7e3 / (ideal_gas_constant * temperature));

  if (model == "Terai1988Grain")
    return 1.27e-9 * exp(-54.9e3 / (ideal_gas_constant * temperature));

  if (model == "Terai1988GrainBoundary")
    return 1.61e-2 * exp(-95.1e3 / (ideal_gas_constant * temperature));

  mooseError("Unsupported Li2O diffusivity model: ", model);
}

template <typename T>
inline T
computeSolubility(const MooseEnum & model, const T & temperature)
{
  using std::pow;

  if (model == "Ohira1989")
    return pow(10.0, 1290.0 / temperature + 1.14);

  mooseError("Unsupported Li2O solubility model: ", model);
}
}
