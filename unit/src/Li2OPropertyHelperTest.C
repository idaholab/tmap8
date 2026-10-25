/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2026 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#include "gtest/gtest.h"

#include "Li2OPropertyHelper.h"
#include "ModelValidity.h"
#include "MooseTypes.h"
#include "ADReal.h"

#include <cmath>
#include <utility>
#include <vector>

using namespace Li2OPropertyHelper;
using namespace ModelValidity;

namespace
{
/// All diffusivity models, so that tests loop over every model
const std::vector<DiffusivityModel> all_diffusivity_models = {
    DiffusivityModel::Ohira1989,
    DiffusivityModel::Tanifuji1987,
    DiffusivityModel::Kurasawa1991,
    DiffusivityModel::Terai1988Grain,
    DiffusivityModel::Terai1988GrainBoundary};

/// All solubility models, so that tests loop over every model
const std::vector<SolubilityModel> all_solubility_models = {SolubilityModel::Ohira1989Tritium,
                                                            SolubilityModel::Ohira1989Hydrogen};

/// Relative difference between two values
Real
relativeError(const Real value, const Real reference)
{
  return std::abs(value - reference) / std::abs(reference);
}
}

/// The enum option strings must stay in sync with the names used in input files
TEST(Li2OPropertyHelperTest, optionStrings)
{
  EXPECT_EQ(getDiffusivityModelOptions(),
            "Ohira1989 Tanifuji1987 Kurasawa1991 Terai1988Grain Terai1988GrainBoundary");
  EXPECT_EQ(getSolubilityModelOptions(), "Ohira1989Tritium Ohira1989Hydrogen");
  EXPECT_EQ(ModelValidity::getValidityActionOptions(), "ignore warning error");
}

/// The documented validity ranges (K) of the diffusivity models
TEST(Li2OPropertyHelperTest, diffusivityRanges)
{
  const auto check = [](const DiffusivityModel model, const Real min_t, const Real max_t)
  {
    const auto data = diffusivityModelData(model);
    EXPECT_DOUBLE_EQ(data.metadata.min_temperature, min_t);
    EXPECT_DOUBLE_EQ(data.metadata.max_temperature, max_t);
  };
  check(DiffusivityModel::Ohira1989, 600.0, 711.0);
  check(DiffusivityModel::Tanifuji1987, 573.0, 950.0);
  check(DiffusivityModel::Kurasawa1991, 723.15, 1093.15);
  check(DiffusivityModel::Terai1988Grain, 633.15, 873.15);
  check(DiffusivityModel::Terai1988GrainBoundary, 633.15, 873.15);
}

/// The documented validity ranges (K) of the solubility models
TEST(Li2OPropertyHelperTest, solubilityRanges)
{
  const auto tritium = solubilityModelData(SolubilityModel::Ohira1989Tritium);
  EXPECT_DOUBLE_EQ(tritium.metadata.min_temperature, 583.0);
  EXPECT_DOUBLE_EQ(tritium.metadata.max_temperature, 963.0);

  const auto hydrogen = solubilityModelData(SolubilityModel::Ohira1989Hydrogen);
  EXPECT_DOUBLE_EQ(hydrogen.metadata.min_temperature, 476.0);
  EXPECT_DOUBLE_EQ(hydrogen.metadata.max_temperature, 963.0);
}

/// Every model must accept its bounds and midpoint, and reject values just outside
TEST(Li2OPropertyHelperTest, isInRange)
{
  std::vector<ModelMetadata> all_metadata;
  for (const auto model : all_diffusivity_models)
    all_metadata.push_back(diffusivityModelData(model).metadata);
  for (const auto model : all_solubility_models)
    all_metadata.push_back(solubilityModelData(model).metadata);

  for (const auto & m : all_metadata)
  {
    EXPECT_TRUE(isInRange(m, m.min_temperature)) << m.validity_note;
    EXPECT_TRUE(isInRange(m, m.max_temperature)) << m.validity_note;
    EXPECT_TRUE(isInRange(m, 0.5 * (m.min_temperature + m.max_temperature))) << m.validity_note;
    EXPECT_FALSE(isInRange(m, m.min_temperature - 1.0)) << m.validity_note;
    EXPECT_FALSE(isInRange(m, m.max_temperature + 1.0)) << m.validity_note;
  }
}

/// The validity message is empty in range and names the object, model and temperature otherwise
TEST(Li2OPropertyHelperTest, validityMessage)
{
  const auto metadata = diffusivityModelData(DiffusivityModel::Ohira1989).metadata;

  EXPECT_EQ(validityMessage("mat", "Ohira1989", 650.0, metadata), "");

  // Temperatures are reported with two digits after the decimal point, and no more
  const auto low = validityMessage("mat", "Ohira1989", 599.123456, metadata);
  EXPECT_NE(low.find("In mat: model 'Ohira1989' is being used outside its documented validity "
                     "range because temperature 599.12 K is outside [600.00, 711.00] K"),
            std::string::npos)
      << low;
  EXPECT_NE(low.find("Source: O'Hira et al. (1989)"), std::string::npos) << low;

  const auto high = validityMessage("mat", "Ohira1989", 712.0, metadata);
  EXPECT_NE(high.find("temperature 712.00 K"), std::string::npos) << high;
}

/// The once-per-object warning names the object, model, range (two decimals) and source
TEST(Li2OPropertyHelperTest, warningMessage)
{
  const auto metadata = diffusivityModelData(DiffusivityModel::Kurasawa1991).metadata;
  EXPECT_EQ(warningMessage("mat", "Kurasawa1991", metadata),
            "In mat: model 'Kurasawa1991' is being used outside its documented validity range "
            "[723.15, 1093.15] K. Source: Kurasawa and Watanabe (1991).");
}

/// Diffusivities against independently calculated values D0 * exp(-Ea / (R T))
TEST(Li2OPropertyHelperTest, diffusivityValues)
{
  const auto check = [](const DiffusivityModel model, const Real temperature, const Real expected)
  {
    const auto value = computeDiffusivity(diffusivityModelData(model), temperature);
    EXPECT_LT(relativeError(value, expected), 1e-9) << "T = " << temperature;
  };
  check(DiffusivityModel::Ohira1989, 650.0, 2.850831860955756e-15);
  check(DiffusivityModel::Tanifuji1987, 750.0, 1.0723349962384238e-12);
  check(DiffusivityModel::Kurasawa1991, 900.0, 3.625584536124032e-12);
  check(DiffusivityModel::Terai1988Grain, 753.15, 1.9783096426565976e-13);
  check(DiffusivityModel::Terai1988GrainBoundary, 753.15, 4.086053385035498e-09);
}

/// The temperature-dependent atom density N_at(T) = 12 / a_0(T)^3, verified against hand
/// calculations, and its agreement with the lattice constants of Table I of Farley et al. (1991)
TEST(Li2OPropertyHelperTest, latticeParameterMatchesFarley)
{
  // Hand calculation of N_at for a_0(T) = 4.55224e-10 + 1.69514e-14 T m
  EXPECT_LT(relativeError(li2oAtomDensity(476.0), 1.206742e29), 1e-5);
  EXPECT_LT(relativeError(li2oAtomDensity(650.0), 1.183984e29), 1e-5);
  EXPECT_LT(relativeError(li2oAtomDensity(963.0), 1.144466e29), 1e-5);

  // Lattice constants (Angstrom) of Table I of Farley et al. (1991) as (T in K, a_0), the linear
  // fit must reproduce them to within 0.6%
  const std::vector<std::pair<Real, Real>> farley = {
      {293.0, 4.60},   {293.0, 4.610},  {293.0, 4.612},  {523.0, 4.64},   {773.0, 4.69},
      {873.0, 4.689},  {873.0, 4.693},  {973.0, 4.71},   {1123.0, 4.728}, {1123.0, 4.73},
      {1273.0, 4.77},  {1473.0, 4.807}, {1273.0, 4.764}, {1373.0, 4.78},  {1373.0, 4.782},
      {1473.0, 4.81},  {1603.0, 4.837}, {1603.0, 4.85}};
  for (const auto & [temperature, lattice_parameter] : farley)
  {
    const Real fit = (li2o_lattice_parameter_intercept + li2o_lattice_parameter_slope * temperature) *
                     1e10;
    EXPECT_LT(relativeError(fit, lattice_parameter), 6e-3) << "T = " << temperature << " K";
  }

  // Thermal expansion decreases the atom density as the temperature increases
  Real previous = li2oAtomDensity(300.0);
  for (Real t = 310.0; t <= 1600.0; t += 10.0)
  {
    EXPECT_LT(li2oAtomDensity(t), previous);
    previous = li2oAtomDensity(t);
  }
}

/// The converted pre-exponential factor and activation energy, verified against hand calculations
TEST(Li2OPropertyHelperTest, convertedSolubilityConstants)
{
  // X_0 = 10^-b / sqrt(101325) in Pa^-1/2, such that K_s = N_at(T) X_0 exp(-E_a / (R T))
  const auto hydrogen = solubilityModelData(SolubilityModel::Ohira1989Hydrogen);
  EXPECT_LT(relativeError(hydrogen.prefactor, 1.469406e-5), 1e-6);
  EXPECT_LT(relativeError(hydrogen.activation_energy, 24332.99), 1e-6);

  const auto tritium = solubilityModelData(SolubilityModel::Ohira1989Tritium);
  EXPECT_LT(relativeError(tritium.prefactor, 2.275840e-4), 1e-6);
  EXPECT_LT(relativeError(tritium.activation_energy, 24696.74), 1e-6);

  // The published coefficients are kept alongside the converted ones
  EXPECT_DOUBLE_EQ(hydrogen.a, 1271.0);
  EXPECT_DOUBLE_EQ(hydrogen.b, 2.33);
  EXPECT_DOUBLE_EQ(tritium.a, 1290.0);
  EXPECT_DOUBLE_EQ(tritium.b, 1.14);
}

/// The implemented N_at(T) X_0 exp(-E_a / (R T)) sqrt(P) must equal the concentration obtained directly
/// from the paper's definition, K = sqrt(P_atm) / X with log10(K) = a / T + b and C = N_at X. The
/// reference is written out below from the published numbers, independently of the helper's
/// converted constants.
TEST(Li2OPropertyHelperTest, solubilityMatchesPaperForm)
{
  // Published O'Hira et al. (1989) fits, T in K and K in atm^1/2 (hydrogen: eq. 3, tritium: eq. 4)
  struct Published
  {
    SolubilityModel model;
    Real a, b, t_min, t_max;
  };
  const std::vector<Published> published = {
      {SolubilityModel::Ohira1989Hydrogen, 1271.0, 2.33, 476.0, 963.0},
      {SolubilityModel::Ohira1989Tritium, 1290.0, 1.14, 583.0, 963.0}};

  const Real pa_per_atm = 101325.0;

  for (const auto & fit : published)
  {
    const auto data = solubilityModelData(fit.model);
    for (int i = 0; i <= 10; ++i)
    {
      const Real temperature = fit.t_min + (fit.t_max - fit.t_min) * i / 10.0;
      // Atom density from the lattice parameter of Farley et al. (1991), a_0 = 4.55224e-10 +
      // 1.69514e-14 T m, written out here independently of the helper
      const Real lattice = 4.55224e-10 + 1.69514e-14 * temperature;
      const Real n_atoms = 12.0 / std::pow(lattice, 3); // atoms/m^3
      for (const Real pressure : {0.01, 1.0, 100.0, 1.0e4, 1.0e5}) // Pa
      {
        const Real paper_concentration = n_atoms * std::sqrt(pressure / pa_per_atm) /
                                         std::pow(10.0, fit.a / temperature + fit.b);
        const Real implemented_concentration =
            computeSolubility(data, temperature) * std::sqrt(pressure);
        EXPECT_LT(relativeError(implemented_concentration, paper_concentration), 1e-8)
            << "a = " << fit.a << ", T = " << temperature << " K, P = " << pressure << " Pa";
      }
    }
  }
}

/// Diffusivity and solubility both increase with temperature for every model (the solubility
/// because it is the inverse of the published Sieverts' constant), and the value is positive and
/// finite across and beyond the documented range
TEST(Li2OPropertyHelperTest, monotonicAndFiniteOverTemperatureSweep)
{
  for (const auto model : all_diffusivity_models)
  {
    const auto data = diffusivityModelData(model);
    Real previous = 0.0;
    for (Real t = 0.5 * data.metadata.min_temperature; t <= 1.5 * data.metadata.max_temperature;
         t += 10.0)
    {
      const auto d = computeDiffusivity(data, t);
      EXPECT_TRUE(std::isfinite(d));
      EXPECT_GT(d, previous);
      previous = d;
    }
  }

  for (const auto model : all_solubility_models)
  {
    const auto data = solubilityModelData(model);
    EXPECT_GT(data.activation_energy, 0.0);
    Real previous = 0.0;
    for (Real t = 0.5 * data.metadata.min_temperature; t <= 1.5 * data.metadata.max_temperature;
         t += 10.0)
    {
      const auto s = computeSolubility(data, t);
      EXPECT_TRUE(std::isfinite(s));
      EXPECT_GT(s, previous);
      previous = s;
    }
  }
}

/// AD derivatives must equal the analytic derivatives. This checks the derivative independently of
/// the finite-difference Jacobian regression tests.
TEST(Li2OPropertyHelperTest, adDerivativeMatchesAnalytic)
{
  const Real temperature = 650.0;

  for (const auto model : all_diffusivity_models)
  {
    const auto data = diffusivityModelData(model);
    ADReal t = temperature;
    Moose::derivInsert(t.derivatives(), 0, 1.0);

    const auto d = computeDiffusivity(data, t);
    // dD/dT = D * Ea / (R T^2)
    const Real expected = MetaPhysicL::raw_value(d) * data.activation_energy /
                          (ideal_gas_constant * temperature * temperature);
    EXPECT_LT(relativeError(d.derivatives()[0], expected), 1e-12);
  }

  for (const auto model : all_solubility_models)
  {
    const auto data = solubilityModelData(model);
    ADReal t = temperature;
    Moose::derivInsert(t.derivatives(), 0, 1.0);

    const auto s = computeSolubility(data, t);
    // K = N_at(T) X_0 exp(-Ea / (R T)), so dK/dT = K (Ea / (R T^2) + d ln(N_at) / dT) with
    // d ln(N_at) / dT = -3 slope / a_0(T)
    const Real lattice = li2o_lattice_parameter_intercept + li2o_lattice_parameter_slope * temperature;
    const Real expected =
        MetaPhysicL::raw_value(s) * (data.activation_energy /
                                         (ideal_gas_constant * temperature * temperature) -
                                     3.0 * li2o_lattice_parameter_slope / lattice);
    EXPECT_LT(relativeError(s.derivatives()[0], expected), 1e-12);
  }
}
