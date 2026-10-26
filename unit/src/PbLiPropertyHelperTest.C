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
const std::vector<DiffusivityModel> all_diffusivity_models = {
    DiffusivityModel::Fauvet1988,
    DiffusivityModel::Reiter1991,
    DiffusivityModel::Reiter1991Hydrogen_DelaporteMathurin,
    DiffusivityModel::Reiter1991Deuterium_DelaporteMathurin,
    DiffusivityModel::Shibuya1987,
    DiffusivityModel::Terai1992,
    DiffusivityModel::Maeda2008,
    DiffusivityModel::Edao2011Hydrogen,
    DiffusivityModel::Edao2011Deuterium,
    DiffusivityModel::Okitsu2012Hydrogen,
    DiffusivityModel::Okitsu2012Deuterium,
    DiffusivityModel::Okada2012Hydrogen,
    DiffusivityModel::Okada2012Deuterium};

/// All solubility models, so that tests loop over every model
const std::vector<SolubilityModel> all_solubility_models = {SolubilityModel::Wu1983,
                                                            SolubilityModel::Chan1984,
                                                            SolubilityModel::Katsuta1985,
                                                            SolubilityModel::Fauvet1988,
                                                            SolubilityModel::Reiter1991Hydrogen,
                                                            SolubilityModel::Reiter1991Deuterium,
                                                            SolubilityModel::Reiter1991Tritium,
                                                            SolubilityModel::Aiello2006,
                                                            SolubilityModel::Maeda2008,
                                                            SolubilityModel::Edao2011Hydrogen,
                                                            SolubilityModel::Edao2011Deuterium,
                                                            SolubilityModel::Okitsu2012Hydrogen,
                                                            SolubilityModel::Okitsu2012Deuterium,
                                                            SolubilityModel::Okada2012Hydrogen,
                                                            SolubilityModel::Okada2012Deuterium,
                                                            SolubilityModel::Alberro2015,
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

/// PbLi density (g/m^3) of the LeadLithiumFluidProperties of MOOSE, rho = 10520.35 - 1.19051 T in
/// kg/m^3, written out here independently of the helper
Real
mooseDensity(const Real temperature)
{
  return (10520.35 - 1.19051 * temperature) * 1000.0;
}

/// Atom density (atoms/m^3) from the density of MOOSE, written out independently of the helper
Real
referenceAtomDensity(const Real temperature, const Real lithium_fraction)
{
  return mooseDensity(temperature) * 6.02214076e23 /
         (lithium_fraction * 6.941 + (1.0 - lithium_fraction) * 207.2);
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
  EXPECT_EQ(getDiffusivityModelOptions(),
            "Fauvet1988 Reiter1991 Reiter1991Hydrogen_DelaporteMathurin "
            "Reiter1991Deuterium_DelaporteMathurin "
            "Shibuya1987 Terai1992 Maeda2008 Edao2011Hydrogen Edao2011Deuterium Okitsu2012Hydrogen "
            "Okitsu2012Deuterium "
            "Okada2012Hydrogen Okada2012Deuterium");
  EXPECT_EQ(getSolubilityModelOptions(),
            "Wu1983 Chan1984 Katsuta1985 Fauvet1988 Reiter1991Hydrogen Reiter1991Deuterium "
            "Reiter1991Tritium Aiello2006 "
            "Maeda2008 Edao2011Hydrogen Edao2011Deuterium Okitsu2012Hydrogen Okitsu2012Deuterium "
            "Okada2012Hydrogen Okada2012Deuterium "
            "Alberro2015 Penalva2024 Fukada2013MixingRule");
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
  check(diffusivityModelData(DiffusivityModel::Maeda2008).metadata, 573.15, 973.15);
  check(diffusivityModelData(DiffusivityModel::Shibuya1987).metadata, 573.15, 773.15);
  check(solubilityModelData(SolubilityModel::Katsuta1985).metadata, 573.0, 723.0);
  check(solubilityModelData(SolubilityModel::Aiello2006).metadata, 600.0, 900.0);
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
  EXPECT_NE(
      message.find("In mat: model 'Terai1992' is being used outside its documented validity "
                   "range because lithium atomic fraction 0.3000 is outside [0.1570, 0.1700]"),
      std::string::npos)
      << message;
}

/// The documented pressure ranges (Pa) of the models, and their absence for the others
TEST(PbLiPropertyHelperTest, pressureRanges)
{
  const auto check = [](const ModelMetadata & m, const Real min_p, const Real max_p)
  {
    EXPECT_TRUE(m.has_pressure_range);
    EXPECT_DOUBLE_EQ(m.min_pressure, min_p);
    EXPECT_DOUBLE_EQ(m.max_pressure, max_p);
  };
  const Real atm = PhysicalConstants::atm_to_Pa;
  check(diffusivityModelData(DiffusivityModel::Fauvet1988).metadata, 1e3, 1e4);
  check(diffusivityModelData(DiffusivityModel::Reiter1991).metadata, 1e3, 1e5);
  check(diffusivityModelData(DiffusivityModel::Terai1992).metadata, 3e3, 3e3);
  check(solubilityModelData(SolubilityModel::Fauvet1988).metadata, 1e3, 1e4);
  check(solubilityModelData(SolubilityModel::Katsuta1985).metadata, 0.146 * atm, 1.05 * atm);
  check(solubilityModelData(SolubilityModel::Reiter1991Tritium).metadata, 1e3, 1e5);
  check(solubilityModelData(SolubilityModel::Aiello2006).metadata, 1e3, 1e5);
  check(solubilityModelData(SolubilityModel::Wu1983).metadata, 0.1, 1.0);
  check(solubilityModelData(SolubilityModel::Chan1984).metadata, 0.0, 1e4);
  check(solubilityModelData(SolubilityModel::Alberro2015).metadata, 1.0, 1e5);

  // Models without a documented pressure range
  EXPECT_FALSE(diffusivityModelData(DiffusivityModel::Maeda2008).metadata.has_pressure_range);
  EXPECT_FALSE(solubilityModelData(SolubilityModel::Penalva2024).metadata.has_pressure_range);
}

/// The pressure check accepts the documented bounds, rejects values outside, and accepts every
/// pressure for a model without a pressure range
TEST(PbLiPropertyHelperTest, pressureValidity)
{
  const auto fauvet = diffusivityModelData(DiffusivityModel::Fauvet1988).metadata;
  EXPECT_TRUE(isPressureInRange(fauvet, 1e3));
  EXPECT_TRUE(isPressureInRange(fauvet, 5e3));
  EXPECT_TRUE(isPressureInRange(fauvet, 1e4));
  EXPECT_FALSE(isPressureInRange(fauvet, 999.0));
  EXPECT_FALSE(isPressureInRange(fauvet, 1.0001e4));

  // A model documented for a single pressure accepts only that pressure
  const auto terai = diffusivityModelData(DiffusivityModel::Terai1992).metadata;
  EXPECT_TRUE(isPressureInRange(terai, 3e3));
  EXPECT_FALSE(isPressureInRange(terai, 3.1e3));

  const auto maeda = diffusivityModelData(DiffusivityModel::Maeda2008).metadata;
  EXPECT_TRUE(isPressureInRange(maeda, 1e-6));
  EXPECT_TRUE(isPressureInRange(maeda, 1e9));

  EXPECT_EQ(pressureMessage("mat", "Fauvet1988", 5e3, fauvet), "");
  const auto message = pressureMessage("mat", "Fauvet1988", 1e5, fauvet);
  EXPECT_NE(message.find("In mat: model 'Fauvet1988' is being used outside its documented validity "
                         "range because pressure 1.00e+05 Pa is outside [1.00e+03, 1.00e+04] Pa"),
            std::string::npos)
      << message;
  EXPECT_EQ(pressureWarningMessage("mat", "Fauvet1988", fauvet),
            "In mat: model 'Fauvet1988' is being used outside its documented pressure range "
            "[1.00e+03, 1.00e+04] Pa. Source: Fauvet and Sannier (1988).");
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
  check(DiffusivityModel::Edao2011Hydrogen, 700.0, 5.417087842613871e-09);
  check(DiffusivityModel::Shibuya1987, 673.15, 8.013847337257099e-10);
  check(DiffusivityModel::Reiter1991Hydrogen_DelaporteMathurin, 600.0, 7.50660030379591e-10);
  check(DiffusivityModel::Okada2012Deuterium, 850.0, 2.903777724542236e-09);
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
  EXPECT_LT(relativeError(atomDensity(mooseDensity(700.0), 0.17), 3.369010920451353e+28), 1e-9);
  EXPECT_LT(relativeError(atomDensity(mooseDensity(700.0), 0.157), 3.3191087530749322e+28), 1e-9);
}

/// Solubilities against independently calculated values, in atoms m^-3 Pa^-1/2
TEST(PbLiPropertyHelperTest, solubilityValues)
{
  const auto check = [](const SolubilityModel model, const Real temperature, const Real expected)
  {
    const auto data = solubilityModelData(model, mixingRuleInputs());
    const auto value =
        computeSolubility(data, temperature, referenceAtomDensity(temperature, 0.17));
    EXPECT_LT(relativeError(value, expected), 1e-9) << "T = " << temperature;
  };
  // Atom-fraction fit converted with N(T) from the density of MOOSE, mole-based fit with N_A
  // Katsuta1985 is a temperature independent Sieverts constant sqrt(P_atm)/X = 2.9e3
  check(SolubilityModel::Katsuta1985, 650.0, 3.6720335469861126e+22);
  check(SolubilityModel::Reiter1991Tritium, 600.0, 6.036283241353147e+20);
  check(SolubilityModel::Aiello2006, 750.0, 1.8196216381245049e+22);
  check(SolubilityModel::Wu1983, 900.0, 2.0801659440595036e+22);
  check(SolubilityModel::Okitsu2012Hydrogen, 850.0, 1.4055269716915588e+21);
  check(SolubilityModel::Alberro2015, 700.0, 4.4576619799900937e+21);
  // Mixing rule: exp(x ln K_Li + (1 - x) ln K_Pb), independent of temperature
  check(SolubilityModel::Fukada2013MixingRule, 600.0, 2.1877616239495473e+20);
  check(SolubilityModel::Fukada2013MixingRule, 800.0, 2.1877616239495473e+20);
}

/// The mixing rule reduces to the pure-component constants at the composition limits
TEST(PbLiPropertyHelperTest, mixingRuleLimits)
{
  auto inputs = mixingRuleInputs();

  inputs.lithium_fraction = 0.0;
  EXPECT_LT(relativeError(
                computeSolubility(
                    solubilityModelData(SolubilityModel::Fukada2013MixingRule, inputs), 700.0, 0.0),
                1e20),
            1e-12);

  inputs.lithium_fraction = 1.0;
  EXPECT_LT(relativeError(
                computeSolubility(
                    solubilityModelData(SolubilityModel::Fukada2013MixingRule, inputs), 700.0, 0.0),
                1e22),
            1e-12);

  // The mixing rule is the geometric mean for equal weights
  inputs.lithium_fraction = 0.5;
  EXPECT_LT(relativeError(
                computeSolubility(
                    solubilityModelData(SolubilityModel::Fukada2013MixingRule, inputs), 700.0, 0.0),
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
      const auto s = computeSolubility(
          solubilityModelData(model, mixingRuleInputs()), t, referenceAtomDensity(t, 0.17));
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
  // dK/dT = K (Ea / (R T^2) + d ln(B) / dT) with d ln(N) / dT = -1.19051 / (10520.35 - 1.19051 T)
  // for the density of MOOSE
  for (const auto model : all_solubility_models)
  {
    const auto data = solubilityModelData(model, mixingRuleInputs());
    const ADReal ad_temperature = make_ad_temperature();
    const ADReal density_g_per_m3 = (10520.35 - 1.19051 * ad_temperature) * 1000.0;
    const auto s = computeSolubility(data, ad_temperature, atomDensity(density_g_per_m3, 0.17));
    Real log_derivative = data.activation_energy / (ideal_gas_constant * temperature * temperature);
    if (data.basis == SolubilityBasis::AtomFraction)
      log_derivative += -1.19051 / (10520.35 - 1.19051 * temperature);
    const Real expected = MetaPhysicL::raw_value(s) * log_derivative;
    if (expected == 0.0)
      EXPECT_DOUBLE_EQ(s.derivatives()[0], 0.0);
    else
      EXPECT_LT(relativeError(s.derivatives()[0], expected), 1e-12);
  }
}
