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
 * source or, where stated, converted to SI (m$^2$/s, J/mol, K, atoms m$^{-3}$ Pa$^{-1/2}$).
 */
namespace Li2OPropertyHelper
{
/// Ideal gas constant, from TMAP8PhysicalConstants
const Real ideal_gas_constant = PhysicalConstants::ideal_gas_constant;

/**
 * Lattice parameter of anti-fluorite Li$_2$O, a_0(T) = a_0_intercept + a_0_slope T, from a
 * weighted linear least-squares fit to Table I of Farley et al., J. Phys.: Condens. Matter 3, 4761
 * (1991) (293-1603 K, neutron diffraction and earlier data, weighted by the quoted errors).
 */
/// Intercept of the linear lattice parameter fit (m)
const Real li2o_lattice_parameter_intercept = 4.55224e-10;
/// Slope of the linear lattice parameter fit (m/K)
const Real li2o_lattice_parameter_slope = 1.69514e-14;

/// Atoms per Li$_2$O unit cell: 4 formula units (Li$_2$O) of 3 atoms each (-)
const Real li2o_atoms_per_unit_cell = 12.0;

/**
 * Number density of all lattice atoms (Li and O) in Li$_2$O, N_at = 12 / a_0(T)^3 (atoms/m^3). This
 * is the density relative to which O'Hira et al. (1989) define the atom fraction X. It decreases
 * with temperature because of the thermal expansion of Li$_2$O.
 * @param temperature the temperature (K); may be a regular or AD type
 */
template <typename T>
inline T
li2oAtomDensity(const T & temperature)
{
  const T lattice_parameter =
      li2o_lattice_parameter_intercept + li2o_lattice_parameter_slope * temperature;
  return li2o_atoms_per_unit_cell / (lattice_parameter * lattice_parameter * lattice_parameter);
}

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

/**
 * Solubility fit as published by O'Hira et al. (1989): log10(K) = a / T + b, with T in K and
 * K = sqrt(P) / X the Sieverts' constant, where P is the gas pressure in atm and X the atom
 * fraction of hydrogen isotope in the solid, X = n_H / (n_Li + n_O + n_H).
 */
struct SolubilityFit
{
  /// Citation, validity range and notes
  ModelMetadata metadata;
  /// Coefficient of the inverse temperature in the published fit (K)
  Real a;
  /// Constant term of the published fit (-)
  Real b;
};

/**
 * Sieverts solubility in the form used by TMAP8, C = K_s sqrt(P) with
 * K_s = N_at(T) X_0 exp(-E_a / (R T)), C in atoms/m^3, P in Pa and K_s in atoms m^-3 Pa^-1/2,
 * derived from a published fit by convertSolubilityFit().
 */
struct SolubilityModelData
{
  /// Citation, validity range and notes
  ModelMetadata metadata;
  /// Coefficient a of the published fit, log10(K) = a / T + b (K)
  Real a;
  /// Constant b of the published fit, log10(K) = a / T + b (-)
  Real b;
  /// Pre-exponential factor X_0 of the atom fraction (Pa^-1/2)
  Real prefactor;
  /// Activation energy E_a (J/mol)
  Real activation_energy;
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
 * Look up the published fit and validity range of a solubility model.
 * @param model the solubility model
 * @return the fit exactly as published (log10 of Sieverts' constant, in atm^1/2)
 */
inline SolubilityFit
publishedSolubilityFit(const SolubilityModel model)
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
 * Convert a published solubility fit to the Sieverts solubility used by TMAP8.
 *
 * The published constant is K = sqrt(P_atm) / X, i.e. the inverse of the solubility, with the
 * gas pressure in atm and X the atom fraction. Inverting and changing units gives
 *   X = 10^(-b) 10^(-a / T) sqrt(P_atm),   C = N_at X,   P_atm = P / atm_to_Pa,
 * so that C = K_s sqrt(P) with K_s = N_at(T) X_0 exp(-E_a / (R T)) and
 *   X_0 = 10^(-b) / sqrt(atm_to_Pa)   (Pa^-1/2),
 *   E_a = a R ln(10)                  (J/mol).
 * The temperature dependence of N_at(T) is given by li2oAtomDensity().
 * @param fit the published fit
 * @return the data in the form used by TMAP8
 */
inline SolubilityModelData
convertSolubilityFit(const SolubilityFit & fit)
{
  return {fit.metadata,
          fit.a,
          fit.b,
          std::pow(10.0, -fit.b) / std::sqrt(PhysicalConstants::atm_to_Pa),
          fit.a * ideal_gas_constant * std::log(10.0)};
}

/**
 * Look up the Sieverts solubility data of a model, converted from the published fit.
 * @param model the solubility model
 * @return the model data
 */
inline SolubilityModelData
solubilityModelData(const SolubilityModel model)
{
  return convertSolubilityFit(publishedSolubilityFit(model));
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
 * Compute the Sieverts solubility K_s = N_at(T) X_0 exp(-E_a / (R T)), such that C = K_s sqrt(P)
 * with C in atoms/m^3 and P in Pa. See convertSolubilityFit() for the relation to the published
 * fit.
 * @param data the model data
 * @param temperature the temperature (K); may be a regular or AD type
 */
template <typename T>
inline T
computeSolubility(const SolubilityModelData & data, const T & temperature)
{
  using std::exp;
  return li2oAtomDensity(temperature) * data.prefactor *
         exp(-data.activation_energy / (ideal_gas_constant * temperature));
}
}
