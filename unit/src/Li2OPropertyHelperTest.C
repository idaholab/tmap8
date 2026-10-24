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

/// Solubilities against independently calculated values exp(a / T + b)
TEST(Li2OPropertyHelperTest, solubilityValues)
{
  const auto check = [](const SolubilityModel model, const Real temperature, const Real expected)
  {
    const auto value = computeSolubility(solubilityModelData(model), temperature);
    EXPECT_LT(relativeError(value, expected), 1e-9) << "T = " << temperature;
  };
  check(SolubilityModel::Ohira1989Tritium, 650.0, 22.75114297092991);
  check(SolubilityModel::Ohira1989Hydrogen, 650.0, 72.63047614688442);
}

/// Diffusivity increases and solubility decreases with temperature for every model, and the value
/// is positive and finite across and beyond the documented range
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
    Real previous = std::numeric_limits<Real>::max();
    for (Real t = 0.5 * data.metadata.min_temperature; t <= 1.5 * data.metadata.max_temperature;
         t += 10.0)
    {
      const auto s = computeSolubility(data, t);
      EXPECT_TRUE(std::isfinite(s));
      EXPECT_GT(s, 0.0);
      EXPECT_LT(s, previous);
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
    const Real expected =
        MetaPhysicL::raw_value(d) * data.activation_energy /
        (ideal_gas_constant * temperature * temperature);
    EXPECT_LT(relativeError(d.derivatives()[0], expected), 1e-12);
  }

  for (const auto model : all_solubility_models)
  {
    const auto data = solubilityModelData(model);
    ADReal t = temperature;
    Moose::derivInsert(t.derivatives(), 0, 1.0);

    const auto s = computeSolubility(data, t);
    // dK/dT = -K * a / T^2
    const Real expected = -MetaPhysicL::raw_value(s) * data.a / (temperature * temperature);
    EXPECT_LT(relativeError(s.derivatives()[0], expected), 1e-12);
  }
}
