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

/// Conversion factor from eV/particle to J/mol, derived from PhysicalConstants
const Real eV_to_J_per_mol = PhysicalConstants::eV_to_J * PhysicalConstants::avogadro_number;

/// Molar mass of lithium (g/mol)
const Real lithium_molar_mass = 6.941;
/// Molar mass of lead (g/mol)
const Real lead_molar_mass = 207.2;

/// Lithium atomic fraction range of the eutectic Pb-17Li used by most correlations (-)
const Real eutectic_min_lithium_fraction = 0.157;
const Real eutectic_max_lithium_fraction = 0.17;

/// Density models available for PbLi
CreateMooseEnumClass(DensityModel, LinearExpansion);

/**
 * Tritium diffusivity models available for PbLi.
 * Reiter1991 is the isotope-averaged fit usually quoted in reviews.
 */
CreateMooseEnumClass(DiffusivityModel,
                     Fauvet1988,
                     Reiter1991,
                     Reiter1991Hydrogen_DelaporteMathurin,
                     Reiter1991Deuterium_DelaporteMathurin,
                     Shibuya1987,
                     Terai1992,
                     Maeda2008,
                     Edao2011Hydrogen,
                     Edao2011Deuterium,
                     Okitsu2012Hydrogen,
                     Okitsu2012Deuterium,
                     Okada2012Hydrogen,
                     Okada2012Deuterium);

/// Hydrogen isotope solubility models available for PbLi
CreateMooseEnumClass(SolubilityModel,
                     Wu1983,
                     Chan1984,
                     Katsuta1985,
                     Fauvet1988,
                     Reiter1991Hydrogen,
                     Reiter1991Deuterium,
                     Reiter1991Tritium,
                     Aiello2006,
                     Maeda2008,
                     Edao2011Hydrogen,
                     Edao2011Deuterium,
                     Okitsu2012Hydrogen,
                     Okitsu2012Deuterium,
                     Okada2012Hydrogen,
                     Okada2012Deuterium,
                     Alberro2015,
                     Penalva2024,
                     Fukada2013MixingRule);

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

/**
 * Add the documented pressure range to the metadata of a model.
 * @param metadata the metadata of the model
 * @param min_pressure lower bound of the documented pressure range (Pa)
 * @param max_pressure upper bound of the documented pressure range (Pa)
 */
inline ModelMetadata
withPressureRange(ModelMetadata metadata, const Real min_pressure, const Real max_pressure)
{
  metadata.min_pressure = min_pressure;
  metadata.max_pressure = max_pressure;
  metadata.has_pressure_range = true;
  return metadata;
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
      // rho = 1.052e7 (1 - 1.13e-4 T) g/m^3 is numerically equivalent to the
      // rho = 10520 - 1.19 T kg/m^3 form of Mas de les Valls et al. (2008) to within 0.1 % over
      // 500-900 K.
      return {pbliMetadata("Linear PbLi density correlation",
                           no_min_temperature,
                           no_max_temperature,
                           "No temperature range is documented."),
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
      // single value 1.5e-9 m^2/s at 723 K
      return {
          withPressureRange(pbliMetadata("Fauvet and Sannier (1988)",
                       718.15,
                       728.15,
                       "Single datum at 723 K, treated as temperature independent, for hydrogen."), 1.0e3, 1.0e4),
          1.5e-9,
          0.0,
          Isotope::H};

    case DiffusivityModel::Reiter1991:
      // This is the expression usually quoted for Reiter.
      // It is therefore best regarded as an isotope-averaged fit.
      return {
          withPressureRange(pbliMetadata("Reiter et al. (1991), also summarized by Mas de les Valls et al. (2008)",
                       508.0,
                       700.0,
                       "Isotope-averaged fit for eutectic Pb-17Li; see "
                       "Reiter1991Hydrogen_DelaporteMathurin and "
                       "Reiter1991Deuterium_DelaporteMathurin for the isotope-specific fits."), 1.0e3, 1.0e5),
          4.03e-8,
          19500.0,
          Isotope::H};

    case DiffusivityModel::Reiter1991Hydrogen_DelaporteMathurin:
      // Fit of 16 digitized H data points from Reiter1991
      // DISCREPANCY: E differs from the averaged 19500 J/mol, so H and the averaged fit diverge by
      // up to ~25 % at the ends of the range.
      return {withPressureRange(pbliMetadata("Reiter (1991), H data fitted by Delaporte-Mathurin et al. (2023)",
                           524.0,
                           690.0,
                           "Arrhenius fit of Reiter's 16 digitized hydrogen data points."), 1.0e3, 1.0e5),
              7.48e-8,
              22956.0,
              Isotope::H};

    case DiffusivityModel::Reiter1991Deuterium_DelaporteMathurin:
      // Fit of 6 digitized D data points
      // DISCREPANCY: D_D/D_H from these fits is ~1.3 at 573 K and
      // ~0.8 at 773 K, i.e. no consistent classical sqrt(m_H/m_D) = 0.71 trend; the scatter of
      // the raw data (factor ~2) is larger than the isotope effect.
      return {withPressureRange(pbliMetadata("Reiter (1991), D data fitted by Delaporte-Mathurin et al. (2023)",
                           524.0,
                           691.0,
                           "Arrhenius fit of Reiter's 6 digitized deuterium data points."), 1.0e3, 1.0e5),
              1.38e-8,
              13609.0,
              Isotope::D};

    case DiffusivityModel::Shibuya1987:
      // three values only: 6.6e-10, 7.8e-10 and 9.5e-10 m^2/s at 573, 673 and 773 K
      // (tritium release from neutron-irradiated Li17Pb83). The Arrhenius form is a least-squares
      // fit of those three points.
      return {
          pbliMetadata("Shibuya et al. (1987), also summarized by Mas de les Valls et al. (2008)",
                       573.15,
                       773.15,
                       "Tritium, isothermal release from neutron-irradiated Li17Pb83. Arrhenius "
                       "fit of the three published values."),
          2.62e-9,
          6630.0,
          Isotope::T};

    case DiffusivityModel::Terai1992:
      // in-pile tritium release.
      return {withPressureRange(pbliMetadata("Terai et al. (1992), also summarized by Mas de les Valls et al. (2008)",
                           573.15,
                           973.15,
                           "Tritium diffusivity fit in Pb-17Li under neutron irradiation."), 3.0e3, 3.0e3),
              2.50e-7,
              27000.0,
              Isotope::T};

    case DiffusivityModel::Maeda2008:
      // unsteady permeation in permeation pot.
      return {pbliMetadata("Maeda et al. (2008)",
                           573.15,
                           973.15,
                           "Hydrogen fit from unsteady permeation through molten Li-Pb. Surface "
                           "resistance affected the data below 673 K."),
              1.8e-8,
              11590.0,
              Isotope::H};

    case DiffusivityModel::Edao2011Hydrogen:
      // Fit of 3 H points from Edao2011Hydrogen
      return {pbliMetadata("Edao et al. (2011)",
                           573.0,
                           873.0,
                           "Hydrogen, transient permeation through Li17Pb83."),
              8.18e-8,
              15800.0,
              Isotope::H};

    case DiffusivityModel::Edao2011Deuterium:
      // Fit of 4  D points from Edao et al. (2011)
      return {pbliMetadata("Edao et al. (2011)",
                           573.0,
                           873.0,
                           "Deuterium, transient permeation through Li17Pb83."),
              5.73e-8,
              13600.0,
              Isotope::D};

    case DiffusivityModel::Okitsu2012Hydrogen:
      // Fit over 5 temperatures in Okitsu et al. (2012)
      return {pbliMetadata("Okitsu et al. (2012)",
                           773.0,
                           973.0,
                           "Hydrogen in two-component (H + D) permeation through Li17Pb83."),
              2.0e-8,
              11200.0,
              Isotope::H};

    case DiffusivityModel::Okitsu2012Deuterium:
      // Fit over 5 temperatures in Okitsu et al. (2012)
      return {pbliMetadata("Okitsu et al. (2012)",
                           773.0,
                           973.0,
                           "Deuterium in two-component (H + D) permeation through Li17Pb83."),
              4.8e-8,
              20300.0,
              Isotope::D};

    case DiffusivityModel::Okada2012Hydrogen:
      // Fit over 5 temperatures in Okada et al. (2012), same data as Okitsu et al. (2012)
      return {pbliMetadata("Okada et al. (2012)",
                           773.0,
                           973.0,
                           "Hydrogen, permeation through Li-Pb, 5 data points. Same data as Okitsu "
                           "et al. (2012), but different fit."),
              4.68e-8,
              17600.0,
              Isotope::H};

    case DiffusivityModel::Okada2012Deuterium:
      // Fit over 5 temperatures in Okada et al. (2012), same data as Okitsu et al. (2012)
      return {pbliMetadata("Okada et al. (2012)",
                           773.0,
                           973.0,
                           "Deuterium, permeation through Li-Pb, 5 data points. Same data as "
                           "Okitsu et al. (2012), but different fit."),
              2.64e-8,
              15600.0,
              Isotope::D};
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
      //  Sieverts constant sqrt(P)/x_H = 2.9e3 sqrt(atm), temperature
      //  independent over 573-723 K and 0.146-1.05 atm, i.e. 1.083e-6 atom fraction Pa^-1/2.
      return {
          withPressureRange(pbliMetadata("Katsuta et al. (1985), also summarized by Mas de les Valls et al. (2008)",
                       573.0,
                       723.0,
                       "Hydrogen in Li17Pb83, hot extraction, no temperature dependence."), 0.146 * PhysicalConstants::atm_to_Pa, 1.05 * PhysicalConstants::atm_to_Pa),
          SolubilityBasis::AtomFraction,
          1.0 / (2.9e3 * std::sqrt(PhysicalConstants::atm_to_Pa)),
          0.0,
          Isotope::H};

    case SolubilityModel::Fauvet1988:
      // from Fauvet and Sannier (1988) (2.7 +/- 0.2)e-8 atom fraction Pa^-1/2 at 723 K
      return {withPressureRange(pbliMetadata(
                  "Fauvet and Sannier (1988), also summarized by Mas de les Valls et al. (2008)",
                  718.15,
                  728.15,
                  "Single datum at 723 K, treated as temperature independent."), 1.0e3, 1.0e4),
              SolubilityBasis::AtomFraction,
              2.7e-8,
              0.0,
              Isotope::H};

    case SolubilityModel::Reiter1991Tritium:
      return {
          withPressureRange(pbliMetadata("Reiter (1991) tritium, also summarized by Mas de les Valls et al. (2008)",
                       508.0,
                       700.0,
                       "Published tritium fit for eutectic Pb-17Li."), 1.0e3, 1.0e5),
          SolubilityBasis::AtomFraction,
          2.32e-8,
          1350.0,
          Isotope::T};

    case SolubilityModel::Reiter1991Hydrogen:
      return {
          withPressureRange(pbliMetadata("Reiter (1991) hydrogen, also summarized by Mas de les Valls et al. (2008)",
                       508.0,
                       700.0,
                       "Published hydrogen fit for eutectic Pb-17Li."), 1.0e3, 1.0e5),
          SolubilityBasis::AtomFraction,
          2.44e-8,
          1350.0,
          Isotope::H};

    case SolubilityModel::Reiter1991Deuterium:
      return {
          withPressureRange(pbliMetadata("Reiter (1991) deuterium, also summarized by Mas de les Valls et al. (2008)",
                       508.0,
                       700.0,
                       "Published deuterium fit for eutectic Pb-17Li."), 1.0e3, 1.0e5),
          SolubilityBasis::AtomFraction,
          2.36e-8,
          1350.0,
          Isotope::D};

    case SolubilityModel::Aiello2006:
      // SOLE absorption device, Pb-15.8Li, measured values 1e-2 to 7e-2).
      // This is the "high solubility" bound used in EU WCLL/HCLL analyses, ~2 orders of
      // magnitude above Reiter1991Tritium.
      return {withPressureRange(pbliMetadata("Aiello et al. (2006)",
                           600.0,
                           900.0,
                           "Hydrogen absorption in Pb-15.8Li with the SOLE device.",
                           0.158,
                           0.158), 1.0e3, 1.0e5),
              SolubilityBasis::MolesPerVolume,
              0.237,
              12844.0,
              Isotope::H};

    case SolubilityModel::Maeda2008:
      // Maeda 2008 unstead permeation measurements
      return {pbliMetadata("Maeda et al. (2008)",
                           573.15,
                           973.15,
                           "Hydrogen fit from unsteady permeation through molten Li-Pb."),
              SolubilityBasis::AtomFraction,
              2.1e-6,
              18700.0,
              Isotope::H};

    case SolubilityModel::Edao2011Hydrogen:
      return {pbliMetadata("Edao et al. (2011)",
                           573.0,
                           873.0,
                           "Hydrogen, transient permeation through Li17Pb83."),
              SolubilityBasis::AtomFraction,
              2.73e-7,
              4180.0,
              Isotope::H};

    case SolubilityModel::Edao2011Deuterium:
      return {pbliMetadata("Edao et al. (2011)",
                           573.0,
                           873.0,
                           "Deuterium, transient permeation through Li17Pb83."),
              SolubilityBasis::AtomFraction,
              4.21e-7,
              3100.0,
              Isotope::D};

    case SolubilityModel::Okitsu2012Hydrogen:
      // note that the paper lists 8.6e5 as prefactor (+ sign), but it is indeed 8.6e-5
      return {pbliMetadata("Okitsu et al. (2012)",
                           773.0,
                           973.0,
                           "Hydrogen in two-component (H + D) permeation through Li17Pb83."),
              SolubilityBasis::AtomFraction,
              8.6e-5,
              53800.0,
              Isotope::H};

    case SolubilityModel::Okitsu2012Deuterium:
      return {pbliMetadata("Okitsu et al. (2012)",
                           773.0,
                           973.0,
                           "Deuterium in two-component (H + D) permeation through Li17Pb83."),
              SolubilityBasis::AtomFraction,
              1.1e-4,
              55200.0,
              Isotope::D};

    case SolubilityModel::Okada2012Hydrogen:
      return {pbliMetadata("Okada et al. (2012)",
                           773.0,
                           973.0,
                           "Hydrogen, permeation through Li-Pb. Same data as Okitsu "
                           "et al. (2012), but different fit."),
              SolubilityBasis::AtomFraction,
              1.41e-4,
              57400.0,
              Isotope::H};

    case SolubilityModel::Okada2012Deuterium:
      return {pbliMetadata("Okada et al. (2012)",
                           773.0,
                           973.0,
                           "Deuterium, permeation through Li-Pb. Same data as Okitsu "
                           "et al. (2012), but different fit."),
              SolubilityBasis::AtomFraction,
              1.65e-4,
              57600.0,
              Isotope::D};

    case SolubilityModel::Wu1983:
      return {
          withPressureRange(pbliMetadata("Wu (1983), as summarized by Mas de les Valls et al. (2008)",
                       850.0,
                       1040.0,
                       "Deuterium, temperature independent value from . Wu (1983) provides other "
                       "models for different compositions, which are not yet included here."), 1.0e-1, 1.0e0),
          SolubilityBasis::AtomFraction,
          6.33e-7,
          0.0,
          Isotope::D};

    case SolubilityModel::Chan1984:
      return {
          withPressureRange(pbliMetadata("Chan and Veleckis (1984), as summarized by Mas de les Valls et al. (2008)",
                       573.0,
                       773.0,
                       "Hydrogen; extrapolation of Li-rich alloy data to Pb-17Li. more "
                       "compositions are available in Chan and Veleckis (1984)"), 0.0, 1.0e4),
          SolubilityBasis::AtomFraction,
          4.7e-7,
          9000.0,
          Isotope::H};

    case SolubilityModel::Fukada2013MixingRule:
    {
      // ln K_s = x_Li ln K_Li + (1 - x_Li) ln K_Pb, with constant K_Li and K_Pb: an Arrhenius
      // expression with no temperature dependence.
      // Fukada et al. (2013), Mater. Trans. 54, 425 reports the Kyushu H/D permeation
      // results (no isotope effect on solubility, D_H ~ 1.4 D_D) and discusses solubility
      // versus Li content. The Kyushu solubility correlations themselves are available as
      // Maeda2008, Edao2011Hydrogen/D and Okitsu2012Hydrogen/D.
      const Real x = inputs.lithium_fraction;
      return {pbliMetadata("Fukada et al. (2013)",
                           no_min_temperature,
                           no_max_temperature,
                           "Logarithmic mixing rule using user-provided Sieverts constants of pure "
                           "liquid lithium and lead.",
                           0.0,
                           1.0),
              SolubilityBasis::AtomsPerVolume,
              std::exp(x * std::log(inputs.lithium_sieverts_constant) +
                       (1.0 - x) * std::log(inputs.lead_sieverts_constant)),
              0.0,
              Isotope::H};
    }

    case SolubilityModel::Alberro2015:
      return {withPressureRange(pbliMetadata(
                  "Alberro et al. (2015)", 523.0, 922.0, "Hydrogen solubility in eutectic PbLi."), 1.0, 1.0e5),
              SolubilityBasis::MolesPerVolume,
              8.64e-3,
              900.0,
              Isotope::H};

    case SolubilityModel::Penalva2024:
      return {pbliMetadata("Penalva et al. (2024)",
                           514.15,
                           852.15,
                           "Certified Pb-15.7Li data averaged over 241-579 C, treated as "
                           "temperature independent.",
                           0.157,
                           0.157),
              SolubilityBasis::MolesPerVolume,
              1.95e-2,
              0.0,
              Isotope::H};
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
