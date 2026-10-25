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
#include <limits>
#include <sstream>
#include <string>

/**
 * Shared data and helper functions for the PbLi property materials (DensityPbLi,
 * TritiumDiffusivityPbLi and TritiumSolubilityPbLi).
 *
 * Each literature model is described by a plain data struct holding its correlation coefficients,
 * the hydrogen isotope it was measured for, and its documented validity range.
 *
 * The code is unit-agnostic. The coefficients are stored in the units g/m$^3$ (density), g/mol
 * (molar masses), m$^2$/s, J/mol, K and atoms m$^{-3}$ Pa$^{-1/2}$, after the conversions
 * documented in the model data.
 */
namespace PbLiPropertyHelper
{
/// Ideal gas constant, from TMAP8PhysicalConstants
const Real ideal_gas_constant = PhysicalConstants::ideal_gas_constant;
/// Avogadro number (1/mol), from TMAP8PhysicalConstants
const Real avogadro_number = PhysicalConstants::avogadro_number;

/// Molar mass of lithium (g/mol)
const Real lithium_molar_mass = 6.941;
/// Molar mass of lead (g/mol)
const Real lead_molar_mass = 207.2;

/// Lithium atomic fraction range of the eutectic Pb-17Li used by most correlations (-)
const Real eutectic_min_lithium_fraction = 0.157;
const Real eutectic_max_lithium_fraction = 0.17;

/// Density models available for PbLi
CreateMooseEnumClass(DensityModel, LinearExpansion);

/// Tritium diffusivity models available for PbLi
CreateMooseEnumClass(DiffusivityModel, Fauvet1988, Reiter1991, Terai1992, Maeda2008);

/// Hydrogen isotope solubility models available for PbLi
CreateMooseEnumClass(
    SolubilityModel, Katsuta1985, Fauvet1988, Maeda2008, Reiter1991, Penalva2024, Fukada2013MixingRule);

/// Hydrogen isotopes, ordered by increasing mass
CreateMooseEnumClass(Isotope, H, D, T);

/// Documented validity range and provenance shared by all models
using ModelValidity::ModelMetadata;

/**
 * Build the metadata of a PbLi model. Composition is the lithium atomic fraction.
 * @param citation short literature citation
 * @param min_temperature lower bound of the documented temperature range (K)
 * @param max_temperature upper bound of the documented temperature range (K)
 * @param note description of the conditions the correlation was derived under
 * @param min_lithium lower bound of the lithium atomic fraction range (-)
 * @param max_lithium upper bound of the lithium atomic fraction range (-)
 */
inline ModelMetadata
pbliMetadata(const std::string & citation,
             const Real min_temperature,
             const Real max_temperature,
             const std::string & note,
             const Real min_lithium = eutectic_min_lithium_fraction,
             const Real max_lithium = eutectic_max_lithium_fraction)
{
  return {citation,
          min_temperature,
          max_temperature,
          note,
          min_lithium,
          max_lithium,
          /*has_composition_range=*/true,
          "lithium atomic fraction"};
}

/// Temperature bounds used for models without a documented temperature range
const Real no_min_temperature = 0.0;
const Real no_max_temperature = std::numeric_limits<Real>::max();

/**
 * Mass number of a hydrogen isotope (-)
 * @param isotope the isotope
 */
inline Real
isotopeMassNumber(const Isotope isotope)
{
  switch (isotope)
  {
    case Isotope::H:
      return 1.0;
    case Isotope::D:
      return 2.0;
    case Isotope::T:
      return 3.0;
  }
  mooseError("Unsupported hydrogen isotope.");
}

/**
 * Name of a hydrogen isotope, used in messages
 * @param isotope the isotope
 */
inline std::string
isotopeName(const Isotope isotope)
{
  switch (isotope)
  {
    case Isotope::H:
      return "H";
    case Isotope::D:
      return "D";
    case Isotope::T:
      return "T";
  }
  mooseError("Unsupported hydrogen isotope.");
}

/**
 * Classical (mass) isotope scaling factor of a diffusivity prefactor, D_requested / D_measured =
 * sqrt(m_measured / m_requested), the ratio predicted by classical rate theory.
 * @param measured the isotope the correlation was measured for
 * @param requested the isotope the diffusivity is requested for
 */
inline Real
isotopeScalingFactor(const Isotope measured, const Isotope requested)
{
  return std::sqrt(isotopeMassNumber(measured) / isotopeMassNumber(requested));
}

/**
 * Build the message describing a model used for another isotope than the one it was measured for
 * without isotope scaling.
 * @param object_name name of the material object
 * @param model_name name of the selected model
 * @param measured the isotope the correlation was measured for
 * @param requested the isotope requested by the user
 * @param metadata the model metadata
 * @return the message, or an empty string if the isotopes are the same
 */
inline std::string
isotopeMessage(const std::string & object_name,
               const std::string & model_name,
               const Isotope measured,
               const Isotope requested,
               const ModelMetadata & metadata)
{
  if (measured == requested)
    return "";

  return "In " + object_name + ": model '" + model_name +
         "' is being used outside its documented validity range because it was measured for "
         "isotope " +
         isotopeName(measured) + " but isotope " + isotopeName(requested) +
         " is requested without isotope scaling. Source: " + metadata.citation + ". " +
         metadata.validity_note;
}

/// Linear density model: rho = reference_density (1 - expansion_coefficient T)
struct DensityModelData
{
  /// Citation, validity range and notes
  ModelMetadata metadata;
  /// Density extrapolated to 0 K, rho_0 (g/m$^3$)
  Real reference_density;
  /// Volumetric thermal expansion coefficient (1/K)
  Real expansion_coefficient;
};

/// Arrhenius diffusivity model: D = prefactor * exp(-activation_energy / (R T))
struct DiffusivityModelData
{
  /// Citation, validity range and notes
  ModelMetadata metadata;
  /// Pre-exponential factor D_0 (m$^2$/s)
  Real prefactor;
  /// Activation energy E_a (J/mol)
  Real activation_energy;
  /// Hydrogen isotope the correlation was measured for
  Isotope isotope;
};

/**
 * Look up the coefficients and validity range of a density model.
 * @param model the density model
 * @return the model data
 */
inline DensityModelData
densityModelData(const DensityModel model)
{
  // No default case: the compiler warns if a model is added to the enum without data
  switch (model)
  {
    case DensityModel::LinearExpansion:
      return {pbliMetadata("Linear PbLi density correlation (unverified source)",
                           no_min_temperature,
                           no_max_temperature,
                           "Source and temperature range not yet verified."),
              1.052e7,
              1.13e-4};
  }
  mooseError("Unsupported PbLi density model.");
}

/**
 * Look up the coefficients and validity range of a diffusivity model, as published.
 * @param model the diffusivity model
 * @return the model data
 */
inline DiffusivityModelData
diffusivityModelData(const DiffusivityModel model)
{
  switch (model)
  {
    case DiffusivityModel::Fauvet1988:
      return {pbliMetadata("Fauvet and Sannier (1988)",
                           718.15,
                           728.15,
                           "Single datum at 450 C, treated as temperature independent. Isotope "
                           "basis not yet verified."),
              1.5e-9,
              0.0,
              Isotope::H};

    case DiffusivityModel::Reiter1991:
      return {pbliMetadata("Reiter et al. (1991), as summarized by Mas de les Valls et al. (2008)",
                           508.0,
                           700.0,
                           "Recommended database fit for eutectic Pb-17Li. Isotope basis not yet "
                           "verified."),
              4.03e-8,
              19500.0,
              Isotope::H};

    case DiffusivityModel::Terai1992:
      return {pbliMetadata("Terai et al. (1992)",
                           573.15,
                           973.15,
                           "Tritium diffusivity fit in Pb-17Li."),
              2.50e-7,
              27000.0,
              Isotope::T};

    case DiffusivityModel::Maeda2008:
      return {pbliMetadata("Maeda et al. (2008)",
                           573.15,
                           773.15,
                           "Hydrogen isotope fit measured in molten Li-Pb. Isotope basis not yet "
                           "verified."),
              1.8e-8,
              11590.0,
              Isotope::H};
  }
  mooseError("Unsupported PbLi diffusivity model.");
}

/**
 * Look up the diffusivity model data for a requested isotope. With isotope scaling the prefactor
 * is multiplied by the classical scaling factor, sqrt(m_measured / m_requested).
 * @param model the diffusivity model
 * @param requested the requested isotope
 * @param isotope_scaling whether to scale the prefactor to the requested isotope
 * @return the model data, with the isotope set to the requested one if it was scaled
 */
inline DiffusivityModelData
diffusivityModelDataForIsotope(const DiffusivityModel model,
                               const Isotope requested,
                               const bool isotope_scaling)
{
  auto data = diffusivityModelData(model);
  if (isotope_scaling)
  {
    data.prefactor *= isotopeScalingFactor(data.isotope, requested);
    data.isotope = requested;
  }
  return data;
}

/**
 * Compute the density rho = rho_0 (1 - beta T).
 * @param data the model data
 * @param temperature the temperature (K); may be a regular or AD type
 */
template <typename T>
inline T
computeDensity(const DensityModelData & data, const T & temperature)
{
  return data.reference_density * (1.0 - data.expansion_coefficient * temperature);
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

/// Basis in which a published solubility fit expresses the dissolved hydrogen isotope
enum class SolubilityBasis
{
  /// Concentration in atoms/m$^3$, K_s in atoms m$^{-3}$ Pa$^{-1/2}$
  AtomsPerVolume,
  /// Concentration in mol/m$^3$, K_s in mol m$^{-3}$ Pa$^{-1/2}$
  MolesPerVolume,
  /// Atom fraction of hydrogen isotope in the metal, K_s in Pa$^{-1/2}$
  AtomFraction
};

/**
 * Sieverts solubility model: K_s = prefactor * exp(-activation_energy / (R T)) in the units of the
 * basis, with C = K_s sqrt(P). Use computeSolubility() to convert it to atoms m^-3 Pa^-1/2.
 */
struct SolubilityModelData
{
  /// Citation, validity range and notes
  ModelMetadata metadata;
  /// Basis of the published fit
  SolubilityBasis basis;
  /// Pre-exponential factor, in the units of the basis
  Real prefactor;
  /// Activation energy E_a (J/mol), negative if the solubility decreases with temperature
  Real activation_energy;
  /// Hydrogen isotope the correlation was measured for
  Isotope isotope;
};

/// Input parameters of the solubility models that depend on user-provided values
struct SolubilityInputs
{
  /// Lithium atomic fraction of the PbLi, x_Li (-)
  Real lithium_fraction = 0.17;
  /// Sieverts constant of pure liquid lithium for the mixing rule (atoms m$^{-3}$ Pa$^{-1/2}$)
  Real lithium_sieverts_constant = std::numeric_limits<Real>::quiet_NaN();
  /// Sieverts constant of pure liquid lead for the mixing rule (atoms m$^{-3}$ Pa$^{-1/2}$)
  Real lead_sieverts_constant = std::numeric_limits<Real>::quiet_NaN();
};

/**
 * Atomic mass of PbLi averaged over the metal atoms, M = x_Li M_Li + (1 - x_Li) M_Pb (g/mol)
 * @param lithium_fraction the lithium atomic fraction (-)
 */
inline Real
averageAtomicMass(const Real lithium_fraction)
{
  return lithium_fraction * lithium_molar_mass + (1.0 - lithium_fraction) * lead_molar_mass;
}

/**
 * Number density of metal atoms in PbLi, N(T) = rho(T) N_A / M, with rho(T) from the default
 * density model (atoms/m^3).
 * @param temperature the temperature (K); may be a regular or AD type
 * @param lithium_fraction the lithium atomic fraction (-)
 */
template <typename T>
inline T
pbliAtomDensity(const T & temperature, const Real lithium_fraction)
{
  return computeDensity(densityModelData(DensityModel::LinearExpansion), temperature) *
         avogadro_number / averageAtomicMass(lithium_fraction);
}

/**
 * Look up the coefficients and validity range of a solubility model, as published.
 * @param model the solubility model
 * @param inputs the user-provided values used by some models
 * @return the model data
 */
inline SolubilityModelData
solubilityModelData(const SolubilityModel model, const SolubilityInputs & inputs = {})
{
  switch (model)
  {
    case SolubilityModel::Katsuta1985:
      // x = exp(-8.17 + 734 / T) sqrt(P / 1e5), i.e. per sqrt(Pa)
      return {pbliMetadata("Katsuta et al. (1985)",
                           673.15,
                           773.15,
                           "Hydrogen in Li17Pb83. The pressure normalization of 1e5 Pa is not yet "
                           "verified."),
              SolubilityBasis::AtomFraction,
              std::exp(-8.17) / std::sqrt(1.0e5),
              -734.0 * ideal_gas_constant,
              Isotope::H};

    case SolubilityModel::Fauvet1988:
      return {pbliMetadata("Fauvet and Sannier (1988)",
                           718.15,
                           728.15,
                           "Single datum at 450 C, treated as temperature independent. Units and "
                           "isotope basis not yet verified."),
              SolubilityBasis::AtomFraction,
              2.7e-8,
              0.0,
              Isotope::H};

    case SolubilityModel::Maeda2008:
      return {pbliMetadata("Maeda et al. (2008)",
                           573.15,
                           773.15,
                           "Hydrogen isotope fit measured in molten Li-Pb. Isotope basis not yet "
                           "verified."),
              SolubilityBasis::AtomFraction,
              2.1e-6,
              18700.0,
              Isotope::H};

    case SolubilityModel::Reiter1991:
      return {pbliMetadata("Reiter et al. (1991), as summarized by Mas de les Valls et al. (2008)",
                           508.0,
                           700.0,
                           "Recommended database fit for eutectic Pb-17Li. Units and isotope basis "
                           "not yet verified."),
              SolubilityBasis::MolesPerVolume,
              1.31e-3,
              1350.0,
              Isotope::H};

    case SolubilityModel::Penalva2024:
      return {pbliMetadata("Penalva et al. (2024)",
                           514.15,
                           852.15,
                           "Certified Pb-15.7Li data averaged over 241-579 C, treated as "
                           "temperature independent. Units and isotope basis not yet verified.",
                           0.157,
                           0.157),
              SolubilityBasis::MolesPerVolume,
              1.95e-2,
              0.0,
              Isotope::H};

    case SolubilityModel::Fukada2013MixingRule:
    {
      // ln K_s = x_Li ln K_Li + (1 - x_Li) ln K_Pb, with constant K_Li and K_Pb: an Arrhenius
      // expression with no temperature dependence
      const Real x = inputs.lithium_fraction;
      return {pbliMetadata("Fukada et al. (2013)",
                           no_min_temperature,
                           no_max_temperature,
                           "Logarithmic mixing rule using user-provided Sieverts constants of pure "
                           "liquid lithium and lead. Mixing rule form not yet verified.",
                           0.0,
                           1.0),
              SolubilityBasis::AtomsPerVolume,
              std::exp(x * std::log(inputs.lithium_sieverts_constant) +
                       (1.0 - x) * std::log(inputs.lead_sieverts_constant)),
              0.0,
              Isotope::H};
    }
  }
  mooseError("Unsupported PbLi solubility model.");
}

/**
 * Compute the Sieverts solubility K_s = prefactor exp(-E_a / (R T)), converted from the basis of
 * the published fit to atoms m^-3 Pa^-1/2 such that C = K_s sqrt(P) with C in atoms/m^3 and P in Pa.
 * Mole-based fits are multiplied by the Avogadro number, and atom-fraction fits by the temperature
 * dependent atom density N(T), assuming that the atom fraction is much smaller than 1.
 * @param data the model data
 * @param temperature the temperature (K); may be a regular or AD type
 * @param lithium_fraction the lithium atomic fraction (-), used by atom-fraction fits
 */
template <typename T>
inline T
computeSolubility(const SolubilityModelData & data, const T & temperature, const Real lithium_fraction)
{
  using std::exp;
  const T arrhenius =
      data.prefactor * exp(-data.activation_energy / (ideal_gas_constant * temperature));

  switch (data.basis)
  {
    case SolubilityBasis::AtomsPerVolume:
      return arrhenius;
    case SolubilityBasis::MolesPerVolume:
      return arrhenius * avogadro_number;
    case SolubilityBasis::AtomFraction:
      return arrhenius * pbliAtomDensity(temperature, lithium_fraction);
  }
  mooseError("Unsupported PbLi solubility basis.");
}
} // namespace PbLiPropertyHelper
