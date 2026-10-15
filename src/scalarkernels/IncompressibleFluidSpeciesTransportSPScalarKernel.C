//* This file is part of the MOOSE framework
//* https://mooseframework.inl.gov
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#include "IncompressibleFluidSpeciesTransportSPScalarKernel.h"

// MOOSE includes
#include "ScalarCoupleable.h"

registerMooseObject("TMAP8App", IncompressibleFluidSpeciesTransportSPScalarKernel);
registerMooseObject("TMAP8App", ADIncompressibleFluidSpeciesTransportSPScalarKernel);

template <bool is_ad>
InputParameters
IncompressibleFluidSpeciesTransportSPScalarKernelTempl<is_ad>::validParams()
{
  InputParameters params = is_ad ? ADIncompressibleEnergySPScalarKernel::validParams()
                                 : IncompressibleEnergySPScalarKernel::validParams();
  params.addClassDescription(
      "Implements a generic mass transport solve over a 1D flow path segment.");
  params.addCoupledVar("temperature",
                       {},
                       "Fluid temperature in segment. Takes a "
                       "scalar variable name");
  params.addCoupledVar("upstream_concentration",
                       {},
                       "Concentration of primary species upstream of current segment. Takes a "
                       "scalar variable name");
  params.addCoupledVar("downstream_concentration",
                       {},
                       "Concentration of primary species downstream of current segment. Takes a "
                       "scalar variable name");
  params.addCoupledVar(
      "precursors",
      {},
      "Concentration of species that decay directly into primary molecular/atomic species. Takes a "
      "list of scalar variable names");
  params.addCoupledVar("wall_dissociated_atoms",
                       {},
                       "Concentration of dissociated atoms in the wall that form the molecular "
                       "primary species or are the atomic primary species. Takes a "
                       "list of scalar variable names");
  params.addParam<std::vector<MooseFunctorName>>(
      "precursor_half_lives",
      std::vector<MooseFunctorName>({}),
      "Half lives of species that decay into primary molecular or atomic species [s]. Takes a "
      "vector of functors.");
  params.addParam<MooseFunctorName>("half_life",
                                    "primary molecular or atomic species half life [s].");
  params.addRequiredParam<std::string>("fluid_type",
                                       "Define fluid type with regard to dissolved species state. "
                                       "Accepted values: solvent, metal, gas");
  params.addRequiredParam<MooseFunctorName>("species_diffusivity",
                                            "Diffusivity of primary"
                                            "molecular or atomic species in fluid [m^2/s]");
  params.addParam<MooseFunctorName>("fluid_solubility",
                                    "fluid solubility coefficient [mol/Pa*m^3]"
                                    "(Henry's solubility coefficient is all we need for the fluid, "
                                    "since the wall is always assumed to be metallic).");
  params.addParam<MooseFunctorName>(
      "dissociation_coeff",
      0.0,
      "dissociation coefficient for primary molecular species at surface."
      "Only used if fluid type is gas. [mol/Pa*m^2*s].");
  params.addParam<MooseFunctorName>(
      "recombination_coeff",
      0.0,
      "recombination coefficient for primary molecular species consisting of two atomic species "
      "(coupled variables)."
      "Only used if fluid type is gas. [m^4/s].");
  params.addParam<std::vector<MooseFunctorName>>(
      "wall_solubility",
      std::vector<MooseFunctorName>({}),
      "wall solubility coefficient(s) [mol/Pa*m^3] or [mol/Pa^0.5*m^3]"
      "(Henry's if fluid type is metal [atomic primary species], Sievert's for solvents/gases "
      "[molecular primary species]).");
  params.addParam<bool>("is_homonuclear",
                        true,
                        "Whether primary molecular species is a homonuclear molecule. Does nothing "
                        "if fluid type is metal.");
  params.addParam<MooseFunctorName>(
      "equilibrium_constant", "equilibrium constant for primary non-monatomic molecular species.");

  return params;
}

template <bool is_ad>
IncompressibleFluidSpeciesTransportSPScalarKernelTempl<is_ad>::
    IncompressibleFluidSpeciesTransportSPScalarKernelTempl(const InputParameters & parameters)
  : Base(parameters),
    _T(ScalarCoupleable::coupledScalarValue("temperature")),
    _Cup(ScalarCoupleable::coupledScalarValue("upstream_concentration")),
    _Cdown(ScalarCoupleable::coupledScalarValue("downstream_concentration")),
    _n_precursors(ScalarCoupleable::coupledScalarComponents("precursors")),
    _precursors(_n_precursors),
    _n_diss(ScalarCoupleable::coupledScalarComponents("wall_dissociated_atoms")),
    _diss(_n_diss),
    _precursorHLs(
        this->template getParam<std::vector<MooseFunctorName>>("precursor_half_lives").size()),
    _primaryHL(this->template getFunctor<GenericReal<is_ad>>("half_life")),
    _fluid_type(this->template getParam<std::string>("fluid_type")),
    _diffus(this->template getFunctor<GenericReal<is_ad>>("species_diffusivity")),
    _fluid_sol(this->template getFunctor<GenericReal<is_ad>>("fluid_solubility")),
    _dissoc(this->template getFunctor<GenericReal<is_ad>>("dissociation_coeff")),
    _recomb(this->template getFunctor<GenericReal<is_ad>>("recombination_coeff")),
    _wall_sol(_n_diss),
    _is_homonuc(this->template getParam<bool>("is_homonuclear")),
    _equib(this->template getFunctor<GenericReal<is_ad>>("equilibrium_constant"))
{
  auto & PHL_names = MooseBase::getParam<std::vector<MooseFunctorName>>("precursor_half_lives");
  auto & wallsol_names = MooseBase::getParam<std::vector<MooseFunctorName>>("wall_solubility");
  if (_n_precursors != PHL_names.size())
  {
    mooseError("Must provide consistent number of precursors and precursor half lives!");
  }
  for (const auto j : make_range(_n_precursors))
  {
    _precursors[j] = &(ScalarCoupleable::coupledScalarValue("precursors", j));
    _precursorHLs[j] = &(this->template getFunctor<GenericReal<is_ad>>(PHL_names[j]));
  }
  if (_n_diss != wallsol_names.size())
  {
    mooseError("Must provide consistent number of dissociated atoms and wall solubilities!");
  }
  for (const auto j : make_range(_n_diss))
  {
    _diss[j] = &(ScalarCoupleable::coupledScalarValue("wall_dissociated_atoms", j));
    _wall_sol[j] = &(this->template getFunctor<GenericReal<is_ad>>(wallsol_names[j]));
  }
}

template <bool is_ad>
GenericReal<is_ad>
IncompressibleFluidSpeciesTransportSPScalarKernelTempl<is_ad>::computeQpResidual()
{
  GenericReal<is_ad> mass_residual = 0;
  const Moose::ElemArg qp = Moose::ElemArg();
  const int i = 0;
  const auto state = Base::_is_implicit ? Moose::currentState() : Moose::oldState();
  // start by getting fluid properties
  const auto Tin = 1.0 / 2.0 * (1 - abs(Base::_m[i]) / Base::_m[i]) * Base::_Tdown[i] +
                   1.0 / 2.0 * (1 + abs(Base::_m[i]) / Base::_m[i]) * Base::_Tup[i];
  const auto mu = Base::_fp.mu_from_p_T(Base::_Pref(qp, state), (_T[i] + Tin) / 2);
  const auto rho = Base::_fp.rho_from_p_T(Base::_Pref(qp, state), (_T[i] + Tin) / 2);

  // Decide flow regime for MTC
  const auto Dh = 4.0 * Base::_area(qp, state) / Base::_perimeter(qp, state);
  const auto G = abs(Base::_m[i]) / Base::_area(qp, state);
  const auto Re = G * Dh / mu;
  const auto Sc = mu / rho / _diffus(qp, state);
  // Mass transfer to fluid (Linton-Sherwood)
  const auto KT = 0.023 * pow(Re, 0.8) * pow(Sc, 1.0 / 3.0) * _diffus(qp, state) / Dh;
  GenericReal<is_ad> Jm = 0.0;
  if (_fluid_type == "gas")
  {
    if (_recomb(qp, state) != 0.0 & _dissoc(qp, state) != 0.0)
    {
      if (_is_homonuc)
      {
        Jm = 2.0 * _recomb(qp, state) * pow((*(_diss[0]))[i], 2);
      }
      else
      {
        Jm = 1.0;
        for (const auto j : make_range(_n_diss))
        {
          Jm = (*(_diss[j]))[i] * Jm;
        }
        Jm = 2.0 * _recomb(qp, state) * Jm;
      }
      Jm = Jm - _dissoc(qp, state) * Base::_u[i] / _fluid_sol(qp, state);
    }
    else
    {
      mooseError("Can't handle equilibrium case for gas yet.");
    }
  }
  else if (_fluid_type == "metal")
  {
    Jm = KT *
         ((*(_wall_sol[0]))(qp, state) / _fluid_sol(qp, state) * (*(_diss[0]))[i] - Base::_u[i]);
  }
  else if (_fluid_type == "solvent")
  {
    if (_is_homonuc)
    {
      Jm = 2 * KT *
           (_fluid_sol(qp, state) * pow((*(_diss[0]))[i] / (*(_wall_sol[0]))(qp, state), 2) -
            Base::_u[i]);
    }
    else
    {
      Jm = 1.0;
      for (const auto j : make_range(_n_diss))
      {
        Jm = (*(_diss[j]))[i] / (*(_wall_sol[j]))(qp, state) * Jm;
      }
      Jm = sqrt(_equib(qp, state)) * Jm;
      Jm = Jm - Base::_u[i];
      Jm = KT / 1.380649E-23 / 6.022E+23 / _T[i] * Jm;
    }
  }
  // Advection component
  mass_residual += (Base::_m[i] / 2.0 * (1 - abs(Base::_m[i]) / Base::_m[i]) * _Cdown[i] -
                    Base::_m[i] / 2.0 * (1 + abs(Base::_m[i]) / Base::_m[i]) * _Cup[i] +
                    abs(Base::_m[i]) * Base::_u[i]) /
                   Base::_length(qp, state) / Base::_area(qp, state) / rho;
  // Precursor decay
  for (const auto j : make_range(_n_precursors))
  {
    mass_residual -= (*(_precursors[j]))[i] * log(2) / (*(_precursorHLs[j]))(qp, state);
  }
  // Primary species decay
  mass_residual += Base::_u[i] * log(2) / _primaryHL(qp, state);
  // Wall mass transfer
  mass_residual -= Jm * Base::_perimeter(qp, state) / Base::_area(qp, state);

  return mass_residual;
}

template <bool is_ad>
Real
IncompressibleFluidSpeciesTransportSPScalarKernelTempl<is_ad>::computeQpJacobian()
{
  if constexpr (!is_ad)
  {
    GenericReal<is_ad> mass_jacob = 0;
    const Moose::ElemArg qp = Moose::ElemArg();
    const int i = 0;
    const auto state = Base::_is_implicit ? Moose::currentState() : Moose::oldState();
    // start by getting fluid properties
    const auto Tin = 1.0 / 2.0 * (1 - abs(Base::_m[i]) / Base::_m[i]) * Base::_Tdown[i] +
                     1.0 / 2.0 * (1 + abs(Base::_m[i]) / Base::_m[i]) * Base::_Tup[i];
    const auto mu = Base::_fp.mu_from_p_T(Base::_Pref(qp, state), (_T[i] + Tin) / 2);
    const auto rho = Base::_fp.rho_from_p_T(Base::_Pref(qp, state), (_T[i] + Tin) / 2);

    // Decide flow regime for MTC
    const auto Dh = 4.0 * Base::_area(qp, state) / Base::_perimeter(qp, state);
    const auto G = abs(Base::_m[i]) / Base::_area(qp, state);
    const auto Re = G * Dh / mu;
    const auto Sc = mu / rho / _diffus(qp, state);
    // Mass transfer to fluid (Linton-Sherwood)
    const auto KT = 0.023 * pow(Re, 0.8) * pow(Sc, 1.0 / 3.0) * _diffus(qp, state) / Dh;
    auto Jm = 0.0;
    if (_fluid_type == "gas")
    {
      if (_recomb(qp, state) != 0.0 & _dissoc(qp, state) != 0.0)
      {
        Jm = -_dissoc(qp, state) / _fluid_sol(qp, state);
      }
      else
      {
        mooseError("Can't handle equilibrium case for gas yet.");
      }
    }
    else if (_fluid_type == "metal")
    {
      Jm = -KT;
    }
    else if (_fluid_type == "solvent")
    {
      if (_is_homonuc)
      {
        Jm = -2 * KT;
      }
      else
      {
        Jm = -KT / 1.380649E-23 / 6.022E+23 / _T[i];
      }
    }
    // Advection component
    mass_jacob += (abs(Base::_m[i])) / Base::_length(qp, state) / Base::_area(qp, state) / rho;
    // Primary species decay
    mass_jacob += log(2) / _primaryHL(qp, state) * exp(-log(2) / _primaryHL(qp, state) * Base::_dt);
    // Wall mass transfer
    mass_jacob -= Jm * Base::_perimeter(qp, state) / Base::_area(qp, state);

    return mass_jacob;
  }
  else
  {
    mooseError("computeQpJacobian() should not be called in AD mode");
    return 0;
  }
}

template <>
Real
IncompressibleFluidSpeciesTransportSPScalarKernelTempl<true>::computeQpJacobian()
{
  mooseError("Internal error, calling computeQpJacobian in AD class.");
  return 0.0;
}

template class IncompressibleFluidSpeciesTransportSPScalarKernelTempl<false>;
template class IncompressibleFluidSpeciesTransportSPScalarKernelTempl<true>;
