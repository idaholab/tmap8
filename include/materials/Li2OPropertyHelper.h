/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2026 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#pragma once

#include "MooseEnum.h"
#include "MooseError.h"
#include "ModelValidity.h"
#include "TMAP8PhysicalConstants.h"

#include <cmath>

/**
 * Shared data and helper functions for the Li$_2$O transport property materials
 * (TritiumDiffusivityLi2O and TritiumSolubilityLi2O).
 *
 * Each literature model is described by a plain data struct holding its correlation coefficients
 * and documented validity range.
 *
 * The code is unit-agnostic. The literature coefficients are stored in the units of the
 * source (SI: m$^2$/s, J/mol, K, atm$^{1/2}$).
 */
namespace Li2OPropertyHelper
{
/// Ideal gas constant, from TMAP8PhysicalConstants
const Real ideal_gas_constant = PhysicalConstants::ideal_gas_constant;

/// Tritium diffusivity models available for Li$_2$O
CreateMooseEnumClass(DiffusivityModel,
                     Ohira1989,
                     Tanifuji1987,
                     Kurasawa1991,
                     Terai1988Grain,
                     Terai1988GrainBoundary);

/// Hydrogen isotope solubility models available for Li$_2$O
CreateMooseEnumClass(SolubilityModel, Ohira1989Tritium, Ohira1989Hydrogen);

/// Documented validity range and provenance shared by all models
using ModelValidity::ModelMetadata;

/// Arrhenius diffusivity model: D = prefactor * exp(-activation_energy / (R T))
struct DiffusivityModelData
{
  /// Citation, validity range and notes
  ModelMetadata metadata;
  /// Pre-exponential factor D_0 (m$^2$/s)
  Real prefactor;
  /// Activation energy E_a (J/mol)
  Real activation_energy;
};

/// Sieverts-law solubility model: log10(K_s) = a / T + b
struct SolubilityModelData
{
  /// Citation, validity range and notes
  ModelMetadata metadata;
  /// Coefficient of the inverse temperature (K)
  Real a;
  /// Constant term (-)
  Real b;
};

/**
 * Look up the coefficients and validity range of a diffusivity model.
 * @param model the diffusivity model
 * @return the model data
 */
inline DiffusivityModelData
diffusivityModelData(const DiffusivityModel model)
{
  // No default case: the compiler warns if a model is added to the enum without data
  switch (model)
  {
    case DiffusivityModel::Ohira1989:
      return {{"O'Hira et al. (1989)",
               600.0,
               711.0,
               "Unirradiated single-crystal Li$_2$O equilibrated with reduced tritium gas."},
              1.2e-11,
              45.1e3};

    case DiffusivityModel::Tanifuji1987:
      return {{"Tanifuji et al. (1987)",
               573.0,
               950.0,
               "Neutron-irradiated single-crystal Li$_2$O particles analyzed with a spherical "
               "diffusion model."},
              1.16e-5,
              101.0e3};

    case DiffusivityModel::Kurasawa1991:
      return {{"Kurasawa and Watanabe (1991)",
               450.0 + 273.15,
               820.0 + 273.15,
               "In-situ release interpretation for single-crystal Li$_2$O under sweep-gas "
               "chemistry effects."},
              2.0e-7,
              81.7e3};

    case DiffusivityModel::Terai1988Grain:
      return {{"Terai et al. (1988/1989)",
               360.0 + 273.15,
               600.0 + 273.15,
               "Polycrystalline Li$_2$O grain diffusivity from TTTEx analysis."},
              1.27e-9,
              54.9e3};

    case DiffusivityModel::Terai1988GrainBoundary:
      return {{"Terai et al. (1988/1989)",
               360.0 + 273.15,
               600.0 + 273.15,
               "Polycrystalline Li$_2$O grain-boundary diffusivity from TTTEx analysis."},
              1.61e-2,
              95.1e3};
  }
  mooseError("Unsupported Li2O diffusivity model.");
}

/**
 * Look up the coefficients and validity range of a solubility model.
 * @param model the solubility model
 * @return the model data
 */
inline SolubilityModelData
solubilityModelData(const SolubilityModel model)
{
  switch (model)
  {
    case SolubilityModel::Ohira1989Tritium:
      return {{"O'Hira et al. (1989)",
               583.0,
               963.0,
               "Reduced-species tritium dissolution in single-crystal Li$_2$O."},
              1290.0,
              1.14};

    case SolubilityModel::Ohira1989Hydrogen:
      return {{"O'Hira et al. (1989)",
               476.0,
               963.0,
               "Reduced-species hydrogen dissolution in single-crystal Li$_2$O."},
              1271.0,
              2.33};
  }
  mooseError("Unsupported Li2O solubility model.");
}

/**
 * Compute the diffusivity D = D_0 exp(-E_a / (R T)).
 * @param data the model data
 * @param temperature the temperature (K); may be a regular or AD type
 */
template <typename T>
inline T
computeDiffusivity(const DiffusivityModelData & data, const T & temperature)
{
  using std::exp;
  return data.prefactor * exp(-data.activation_energy / (ideal_gas_constant * temperature));
}

/**
 * Compute the Sieverts-law solubility K_s = 10^(a / T + b), i.e. log10(K_s) = a / T + b. This is
 * equivalent to K_s = K_0 exp(Q / (R T)) with Q = a R ln(10).
 * @param data the model data
 * @param temperature the temperature (K); may be a regular or AD type
 */
template <typename T>
inline T
computeSolubility(const SolubilityModelData & data, const T & temperature)
{
  using std::exp;
  return exp(std::log(10.0) * (data.a / temperature + data.b));
}
}
