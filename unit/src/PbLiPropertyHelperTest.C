/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2026 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#include "gtest/gtest.h"

#include "PbLiPropertyHelper.h"
#include "ModelValidity.h"
#include "MooseTypes.h"
#include "ADReal.h"

#include <cmath>
#include <vector>

using namespace PbLiPropertyHelper;
using namespace ModelValidity;

namespace
{
/// All diffusivity models, so that tests loop over every model
const std::vector<DiffusivityModel> all_diffusivity_models = {DiffusivityModel::Fauvet1988,
                                                              DiffusivityModel::Reiter1991,
                                                              DiffusivityModel::Terai1992,
                                                              DiffusivityModel::Maeda2008};

/// All solubility models, so that tests loop over every model
const std::vector<SolubilityModel> all_solubility_models = {SolubilityModel::Katsuta1985,
                                                            SolubilityModel::Fauvet1988,
                                                            SolubilityModel::Maeda2008,
                                                            SolubilityModel::Reiter1991,
                                                            SolubilityModel::Penalva2024,
                                                            SolubilityModel::Fukada2013MixingRule};

/// Values of the inputs needed by the mixing rule
SolubilityInputs
mixingRuleInputs()
{
  SolubilityInputs inputs;
  inputs.lithium_fraction = 0.17;
  inputs.lithium_sieverts_constant = 1e22;
  inputs.lead_sieverts_constant = 1e20;
  return inputs;
}

/// Relative difference between two values
Real
relativeError(const Real value, const Real reference)
{
  return std::abs(value - reference) / std::abs(reference);
}
}

/// The enum option strings must stay in sync with the names used in input files
TEST(PbLiPropertyHelperTest, optionStrings)
{
  EXPECT_EQ(getDensityModelOptions(), "LinearExpansion");
  EXPECT_EQ(getDiffusivityModelOptions(), "Fauvet1988 Reiter1991 Terai1992 Maeda2008");
  EXPECT_EQ(getSolubilityModelOptions(),
            "Katsuta1985 Fauvet1988 Maeda2008 Reiter1991 Penalva2024 Fukada2013MixingRule");
  EXPECT_EQ(getIsotopeOptions(), "H D T");
}

/// The documented validity ranges (K) and composition ranges of the models
TEST(PbLiPropertyHelperTest, validityRanges)
{
  const auto check = [](const ModelMetadata & m, const Real min_t, const Real max_t)
  {
    EXPECT_DOUBLE_EQ(m.min_temperature, min_t);
    EXPECT_DOUBLE_EQ(m.max_temperature, max_t);
  };
  check(diffusivityModelData(DiffusivityModel::Fauvet1988).metadata, 718.15, 728.15);
  check(diffusivityModelData(DiffusivityModel::Reiter1991).metadata, 508.0, 700.0);
  check(diffusivityModelData(DiffusivityModel::Terai1992).metadata, 573.15, 973.15);
  check(diffusivityModelData(DiffusivityModel::Maeda2008).metadata, 573.15, 773.15);
  check(solubilityModelData(SolubilityModel::Katsuta1985).metadata, 673.15, 773.15);
  check(solubilityModelData(SolubilityModel::Penalva2024).metadata, 514.15, 852.15);

  // Eutectic composition range of most models, single composition for Penalva2024 (Pb-15.7Li)
  const auto terai = diffusivityModelData(DiffusivityModel::Terai1992).metadata;
  EXPECT_TRUE(terai.has_composition_range);
  EXPECT_DOUBLE_EQ(terai.min_composition, 0.157);
  EXPECT_DOUBLE_EQ(terai.max_composition, 0.17);
  EXPECT_EQ(terai.composition_name, "lithium atomic fraction");

  const auto penalva = solubilityModelData(SolubilityModel::Penalva2024).metadata;
  EXPECT_DOUBLE_EQ(penalva.min_composition, 0.157);
  EXPECT_DOUBLE_EQ(penalva.max_composition, 0.157);
}

/// Every model must accept its bounds and midpoint, and reject values just outside. Models without
/// a documented temperature range accept every temperature.
TEST(PbLiPropertyHelperTest, isInRange)
{
  std::vector<ModelMetadata> all_metadata;
  for (const auto model : all_diffusivity_models)
    all_metadata.push_back(diffusivityModelData(model).metadata);
  for (const auto model : all_solubility_models)
    if (model != SolubilityModel::Fukada2013MixingRule)
      all_metadata.push_back(solubilityModelData(model).metadata);

  for (const auto & m : all_metadata)
  {
    EXPECT_TRUE(isInRange(m, m.min_temperature)) << m.citation;
    EXPECT_TRUE(isInRange(m, m.max_temperature)) << m.citation;
    EXPECT_TRUE(isInRange(m, 0.5 * (m.min_temperature + m.max_temperature))) << m.citation;
    EXPECT_FALSE(isInRange(m, m.min_temperature - 1.0)) << m.citation;
    EXPECT_FALSE(isInRange(m, m.max_temperature + 1.0)) << m.citation;
  }

  const auto density = densityModelData(DensityModel::LinearExpansion).metadata;
  EXPECT_TRUE(isInRange(density, 300.0));
  EXPECT_TRUE(isInRange(density, 2000.0));
}

/// The composition check accepts the documented bounds, including 0.157 for Pb-15.7Li, and rejects
/// values outside
TEST(PbLiPropertyHelperTest, compositionRange)
{
  const auto eutectic = diffusivityModelData(DiffusivityModel::Terai1992).metadata;
  EXPECT_TRUE(isCompositionInRange(eutectic, 0.157));
  EXPECT_TRUE(isCompositionInRange(eutectic, 0.17));
  EXPECT_FALSE(isCompositionInRange(eutectic, 0.156));
  EXPECT_FALSE(isCompositionInRange(eutectic, 0.171));

  const auto penalva = solubilityModelData(SolubilityModel::Penalva2024).metadata;
  EXPECT_TRUE(isCompositionInRange(penalva, 0.157));
  EXPECT_FALSE(isCompositionInRange(penalva, 0.17));

  // A model without a composition range accepts any composition
  ModelMetadata unrestricted{"source", 0.0, 1.0, "note"};
  EXPECT_TRUE(isCompositionInRange(unrestricted, 0.9));

  EXPECT_EQ(compositionMessage("mat", "Terai1992", 0.16, eutectic), "");
  const auto message = compositionMessage("mat", "Terai1992", 0.3, eutectic);
  EXPECT_NE(message.find("In mat: model 'Terai1992' is being used outside its documented validity "
                         "range because lithium atomic fraction 0.3000 is outside [0.1570, 0.1700]"),
            std::string::npos)
      << message;
}

/// The density (g/m^3) against hand calculations of rho = 1.052e7 (1 - 1.13e-4 T)
TEST(PbLiPropertyHelperTest, densityValues)
{
  const auto data = densityModelData(DensityModel::LinearExpansion);
  EXPECT_LT(relativeError(computeDensity(data, 700.0), 9.687868e6), 1e-12);
  EXPECT_LT(relativeError(computeDensity(data, 600.0), 9.806744e6), 1e-12);
  EXPECT_LT(relativeError(computeDensity(data, 800.0), 9.568992e6), 1e-12);

  // The density decreases with temperature
  Real previous = computeDensity(data, 300.0);
  for (Real t = 310.0; t <= 1000.0; t += 10.0)
  {
    EXPECT_LT(computeDensity(data, t), previous);
    previous = computeDensity(data, t);
  }
}

/// Diffusivities against independently calculated values D0 * exp(-Ea / (R T))
TEST(PbLiPropertyHelperTest, diffusivityValues)
{
  const auto check = [](const DiffusivityModel model, const Real temperature, const Real expected)
  {
    const auto value = computeDiffusivity(diffusivityModelData(model), temperature);
    EXPECT_LT(relativeError(value, expected), 1e-9) << "T = " << temperature;
  };
  check(DiffusivityModel::Terai1992, 700.0, 2.4166550328994415e-09);
  check(DiffusivityModel::Maeda2008, 650.0, 2.1081760666882994e-09);
  // Fauvet1988 is a single datum, treated as temperature independent
  check(DiffusivityModel::Fauvet1988, 723.15, 1.5e-9);
  check(DiffusivityModel::Fauvet1988, 900.0, 1.5e-9);
}

/// The measured isotope of each model, and the classical isotope scaling of the prefactor
TEST(PbLiPropertyHelperTest, isotopeScaling)
{
  EXPECT_EQ(diffusivityModelData(DiffusivityModel::Terai1992).isotope, Isotope::T);
  EXPECT_EQ(diffusivityModelData(DiffusivityModel::Maeda2008).isotope, Isotope::H);

  EXPECT_DOUBLE_EQ(isotopeScalingFactor(Isotope::H, Isotope::H), 1.0);
  EXPECT_DOUBLE_EQ(isotopeScalingFactor(Isotope::H, Isotope::D), std::sqrt(0.5));
  EXPECT_DOUBLE_EQ(isotopeScalingFactor(Isotope::H, Isotope::T), std::sqrt(1.0 / 3.0));
  EXPECT_DOUBLE_EQ(isotopeScalingFactor(Isotope::T, Isotope::H), std::sqrt(3.0));

  // Without scaling the model is unchanged, with scaling it is for the requested isotope
  const auto unscaled =
      diffusivityModelDataForIsotope(DiffusivityModel::Maeda2008, Isotope::T, false);
  EXPECT_EQ(unscaled.isotope, Isotope::H);
  EXPECT_DOUBLE_EQ(unscaled.prefactor, 1.8e-8);

  const auto scaled = diffusivityModelDataForIsotope(DiffusivityModel::Maeda2008, Isotope::T, true);
  EXPECT_EQ(scaled.isotope, Isotope::T);
  EXPECT_LT(relativeError(computeDiffusivity(scaled, 650.0), 1.2171560196016158e-09), 1e-9);

  // The message names the object, model and both isotopes, and is empty for the same isotope
  const auto metadata = diffusivityModelData(DiffusivityModel::Maeda2008).metadata;
  EXPECT_EQ(isotopeMessage("mat", "Maeda2008", Isotope::H, Isotope::H, metadata), "");
  const auto message = isotopeMessage("mat", "Maeda2008", Isotope::H, Isotope::T, metadata);
  EXPECT_NE(message.find("it was measured for isotope H but isotope T is requested without "
                         "isotope scaling"),
            std::string::npos)
      << message;
}

/// The number density of metal atoms N = rho N_A / M, against hand calculations
TEST(PbLiPropertyHelperTest, atomDensity)
{
  EXPECT_LT(relativeError(averageAtomicMass(0.17), 0.17 * 6.941 + 0.83 * 207.2), 1e-14);
  EXPECT_LT(relativeError(pbliAtomDensity(700.0, 0.17), 3.369315234138314e+28), 1e-9);
  EXPECT_LT(relativeError(pbliAtomDensity(700.0, 0.157), 3.3194085592334526e+28), 1e-9);
}

/// Solubilities against independently calculated values, in atoms m^-3 Pa^-1/2
TEST(PbLiPropertyHelperTest, solubilityValues)
{
  const auto check = [](const SolubilityModel model, const Real temperature, const Real expected)
  {
    const auto data = solubilityModelData(model, mixingRuleInputs());
    EXPECT_LT(relativeError(computeSolubility(data, temperature, 0.17), expected), 1e-9)
        << "T = " << temperature;
  };
  // Atom-fraction fit converted with N(T), mole-based fit converted with N_A
  check(SolubilityModel::Katsuta1985, 723.15, 8.297186405762569e+22);
  check(SolubilityModel::Reiter1991, 600.0, 6.018614855802087e+20);
  // Mixing rule: exp(x ln K_Li + (1 - x) ln K_Pb), independent of temperature
  check(SolubilityModel::Fukada2013MixingRule, 600.0, 2.1877616239495473e+20);
  check(SolubilityModel::Fukada2013MixingRule, 800.0, 2.1877616239495473e+20);
}

/// The mixing rule reduces to the pure-component constants at the composition limits
TEST(PbLiPropertyHelperTest, mixingRuleLimits)
{
  auto inputs = mixingRuleInputs();

  inputs.lithium_fraction = 0.0;
  EXPECT_LT(relativeError(computeSolubility(solubilityModelData(SolubilityModel::Fukada2013MixingRule,
                                                                inputs),
                                            700.0,
                                            inputs.lithium_fraction),
                          1e20),
            1e-12);

  inputs.lithium_fraction = 1.0;
  EXPECT_LT(relativeError(computeSolubility(solubilityModelData(SolubilityModel::Fukada2013MixingRule,
                                                                inputs),
                                            700.0,
                                            inputs.lithium_fraction),
                          1e22),
            1e-12);

  // The mixing rule is the geometric mean for equal weights
  inputs.lithium_fraction = 0.5;
  EXPECT_LT(relativeError(computeSolubility(solubilityModelData(SolubilityModel::Fukada2013MixingRule,
                                                                inputs),
                                            700.0,
                                            inputs.lithium_fraction),
                          1e21),
            1e-12);
}

/// Every positive and finite value over and beyond the documented range
TEST(PbLiPropertyHelperTest, finiteOverTemperatureSweep)
{
  for (const auto model : all_diffusivity_models)
    for (Real t = 300.0; t <= 1200.0; t += 10.0)
    {
      const auto d = computeDiffusivity(diffusivityModelData(model), t);
      EXPECT_TRUE(std::isfinite(d));
      EXPECT_GT(d, 0.0);
    }

  for (const auto model : all_solubility_models)
    for (Real t = 300.0; t <= 1200.0; t += 10.0)
    {
      const auto s = computeSolubility(solubilityModelData(model, mixingRuleInputs()), t, 0.17);
      EXPECT_TRUE(std::isfinite(s));
      EXPECT_GT(s, 0.0);
    }
}

/// AD derivatives must equal the analytic derivatives. This checks the derivative independently of
/// the finite-difference Jacobian regression tests.
TEST(PbLiPropertyHelperTest, adDerivativeMatchesAnalytic)
{
  const Real temperature = 700.0;
  const auto make_ad_temperature = [temperature]()
  {
    ADReal t = temperature;
    Moose::derivInsert(t.derivatives(), 0, 1.0);
    return t;
  };

  // d rho / dT = -rho_0 beta
  const auto density = densityModelData(DensityModel::LinearExpansion);
  const auto rho = computeDensity(density, make_ad_temperature());
  EXPECT_LT(relativeError(rho.derivatives()[0], -density.reference_density * 1.13e-4), 1e-12);

  // dD/dT = D Ea / (R T^2)
  for (const auto model : all_diffusivity_models)
  {
    const auto data = diffusivityModelData(model);
    const auto d = computeDiffusivity(data, make_ad_temperature());
    const Real expected = MetaPhysicL::raw_value(d) * data.activation_energy /
                          (ideal_gas_constant * temperature * temperature);
    if (expected == 0.0)
      EXPECT_DOUBLE_EQ(d.derivatives()[0], 0.0);
    else
      EXPECT_LT(relativeError(d.derivatives()[0], expected), 1e-12);
  }

  // K_s = A exp(-Ea / (R T)) B(T), where B = 1 (atoms, moles) or N(T) (atom fraction), so
  // dK/dT = K (Ea / (R T^2) + d ln(B) / dT) with d ln(N) / dT = -beta / (1 - beta T)
  for (const auto model : all_solubility_models)
  {
    const auto data = solubilityModelData(model, mixingRuleInputs());
    const auto s = computeSolubility(data, make_ad_temperature(), 0.17);
    Real log_derivative =
        data.activation_energy / (ideal_gas_constant * temperature * temperature);
    if (data.basis == SolubilityBasis::AtomFraction)
      log_derivative += -1.13e-4 / (1.0 - 1.13e-4 * temperature);
    const Real expected = MetaPhysicL::raw_value(s) * log_derivative;
    if (expected == 0.0)
      EXPECT_DOUBLE_EQ(s.derivatives()[0], 0.0);
    else
      EXPECT_LT(relativeError(s.derivatives()[0], expected), 1e-12);
  }
}
