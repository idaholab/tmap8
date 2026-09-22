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
#include "Assembly.h"
#include "MooseVariableScalar.h"
#include "FunctorInterface.h"
#include "ScalarCoupleable.h"
#include "SinglePhaseFluidProperties.h"

registerMooseObject("TMAP8App", IncompressibleFluidSpeciesTransportSPScalarKernel);
registerMooseObject("TMAP8App", ADIncompressibleFluidSpeciesTransportSPScalarKernel);

template <bool is_ad>
InputParameters
IncompressibleFluidSpeciesTransportSPScalarKernelTempl<is_ad>::validParams()
{
  InputParameters params =
      is_ad ? ADScalarTimeDerivative::validParams() : ODETimeDerivative::validParams();
  params += FunctorInterface::validParams();
  params.addClassDescription(
      "Implements a generic mass transport solve over a 1D flow path segment.");
  // Lots of inputs so we need to be clear what is what
  // This block defines coupled state variables the kernel relies on, that aren't inherited from the
  // energy kernel.
  params.addCoupledVar("mass_flow_rate",
                       {},
                       "Mass flow rate in component. Takes a "
                       "scalar variable name");
  params.addCoupledVar("inlet_temperature",
                       {},
                       "Fluid temperature of nominal inlet segment/component (N-1). Takes a "
                       "scalar variable name");
  params.addCoupledVar("outlet_temperature",
                       {},
                       "Fluid temperature of nominal outlet segment/component (N+1). Takes a "
                       "scalar variable name");
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
  // This block grabs boolean parameters that control the solve type
  params.addParam<bool>(
      "is_implicit",
      false,
      "Whether an explicit (previous value calculation) or implicit (current value) is used");
  // This block characterizes the geometry and fluid type
  params.addRequiredParam<MooseFunctorName>("reference_pressure", "system reference pressure [Pa]");
  params.addRequiredParam<UserObjectName>("fp", "The name of the user object for fluid properties");
  params.addRequiredParam<MooseFunctorName>("area", "Segment/Component flow area [m^2]");
  params.addRequiredParam<MooseFunctorName>("perimeter", "Segment/Component wetted perimeter [m]");
  params.addRequiredParam<MooseFunctorName>("length", "Segment/Component length [m]");
  // This block specifies the radioactive decay behaviors of precursors and primary species
  params.addParam<std::vector<MooseFunctorName>>(
      "precursor_half_lives",
      std::vector<MooseFunctorName>({}),
      "Half lives of species that decay into primary molecular or atomic species [s]. Takes a "
      "vector of functors.");
  params.addParam<MooseFunctorName>("half_life",
                                    "primary molecular or atomic species half life [s].");
  // This block defines the fluid type and chemical characteristics of fluid/species/wall
  // interactions
  params.addRequiredParam<std::string>(
      "fluid_type",
      "solvent",
      "Define fluid type with regard to dissolved species state. Accepted values: "
      "1) solvent: Dissolves molecular gases, primary species is a molecule, EG water/salts."
      "2) metal: Dissociates molecules into atoms, primary species is an atom, EG lead/sodium."
      "3) gas: Collection of gases with partial pressures, primary species is a molecule, EG "
      "air/helium.");
  params.addRequiredParam<MooseFunctorName>("species_diffusivity",
                                            "Diffusivity of primary"
                                            "molecular or atomic species in fluid [m^2/s]");
  params.addParam<MooseFunctorName>("fluid_solubility",
                                    "fluid solubility coefficient [1/Pa*m^3]"
                                    "(Henry's solubility coefficient is all we need for the fluid, "
                                    "since the wall is always assumed to be metallic).");
  params.addParam<MooseFunctorName>(
      "dissociation_coeff",
      0.0,
      "dissociation coefficient for primary molecular species at surface."
      "Only used if fluid type is gas. [1/Pa*m^2*s]."
      "If disociation & recombination coefficients are not given for gas, we'll proceed assuming "
      "equilibrium and use Sievert's law.");
  params.addParam<MooseFunctorName>(
      "recombination_coeff",
      0.0,
      "recombination coefficient for primary molecular species consisting of two atomic species "
      "(coupled variables)."
      "Only used if fluid type is gas. [m^4/2]."
      "If disociation & recombination coefficients are not given for gas, , we'll proceed assuming "
      "equilibrium and use Sievert's law.");
  params.addParam<std::vector<MooseFunctorName>>(
      "wall_solubility",
      std::vector<MooseFunctorName>({}),
      "wall solubility coefficient(s) [1/Pa*m^3] or [1/Pa^0.5*m^3]"
      "(Henry's if fluid type is metal [atomic primary species], Sievert's for solvents/gases "
      "[molecular primary species])."
      "If primary molecular species is not monatomic, must provide multiple solubility "
      "coefficients."
      "Takes a vector of functors.");
  params.addParam<bool>("is_monatomic",
                        true,
                        "Whether primary molecular species is a monatomic molecule. Does nothing "
                        "if fluid type is metal.");
  params.addParam<MooseFunctorName>(
      "equilibrium_constant",
      "equilibrium constant for primary non-monatomic molecular species."
      "Does nothing if primary species is monatomic or if fluid type is metal or gas.");

  return params;
}

template <bool is_ad>
IncompressibleFluidSpeciesTransportSPScalarKernelTempl<is_ad>::
    IncompressibleFluidSpeciesTransportSPScalarKernelTempl(const InputParameters & parameters)
  : Base(parameters),
    FunctorInterface(this),
    _fp(this->template getUserObject<SinglePhaseFluidProperties>("fp")),
    // Lots of inputs so we need to be clear what is what
    // This block defines coupled state variables the kernel relies on
    _m(ScalarCoupleable::coupledScalarValue("mass_flow_rate")),
    _Tup(ScalarCoupleable::coupledScalarValue("inlet_temperature")),
    _Tdown(ScalarCoupleable::coupledScalarValue("outlet_temperature")),
    // This block grabs boolean parameters that control the solve type
    _is_implicit(this->template getParam<bool>("is_implicit")),
    // This block characterizes the geometry and fluid type
    _Pref(this->template getFunctor<GenericReal<is_ad>>("reference_pressure")),
    _area(this->template getFunctor<GenericReal<is_ad>>("area")),
    _perimeter(this->template getFunctor<GenericReal<is_ad>>("perimeter")),
    _length(this->template getFunctor<GenericReal<is_ad>>("length")),
    // This block defines coupled state variables the kernel relies on, that aren't inherited from
    // the energy kernel.
    _T(ScalarCoupleable::coupledScalarValue("temperature")),
    _Cup(ScalarCoupleable::coupledScalarValue("upstream_concentration")),
    _Cdown(ScalarCoupleable::coupledScalarValue("downstream_concentration")),
    _n_precursors(ScalarCoupleable::coupledScalarComponents("precursors")),
    _precursors(_n_precursors),
    _n_diss(ScalarCoupleable::coupledScalarComponents("wall_dissociated_atoms")),
    _diss(_n_diss),
    // This block specifies the radioactive decay behaviors of precursors and primary species
    _precursorHLs(
        this->template getParam<std::vector<MooseFunctorName>>("precursor_half_lives").size()),
    _primaryHL(this->template getFunctor<GenericReal<is_ad>>("half_life")),
    // This block defines the fluid type and chemical characteristics of fluid/species/wall
    // interactions
    _fluid_type(this->template getParam<std::string>("fluid_type")),
    _diffus(this->template getFunctor<GenericReal<is_ad>>("species_diffusivity")),
    _fluid_sol(this->template getFunctor<GenericReal<is_ad>>("fluid_solubility")),
    _dissoc(this->template getFunctor<GenericReal<is_ad>>("dissociation_coeff")),
    _recomb(this->template getFunctor<GenericReal<is_ad>>("recombination_coeff")),
    _wall_sol(_n_diss),
    _is_monatom(this->template getParam<bool>("is_monatomic")),
    _equib(this->template getFunctor<GenericReal<is_ad>>("equilibrium_constant"))
{
  auto & PHL_names = MooseBase::getParam<std::vector<MooseFunctorName>>("precursor_half_lives");
  auto & wallsol_names = MooseBase::getParam<std::vector<MooseFunctorName>>("wall_solubility");
  if (_n_precursors != PHL_names.size())
  {
    mooseError("Must provide consistent number of precursors and precursor half lives!");
  }
  for (size_t i = 0; i < _n_precursors; ++i)
  {
    _precursors[i] = &(ScalarCoupleable::coupledScalarValue("precursors", i));
    _precursorHLs[i] = &(this->template getFunctor<GenericReal<is_ad>>(PHL_names[i]));
  }
  if (_n_diss != wallsol_names.size())
  {
    mooseError("Must provide consistent number of dissociated atoms and wall solubilities!");
  }
  for (size_t i = 0; i < _n_diss; ++i)
  {
    _diss[i] = &(ScalarCoupleable::coupledScalarValue("wall_dissociated_atoms", i));
    _wall_sol[i] = &(this->template getFunctor<GenericReal<is_ad>>(wallsol_names[i]));
  }
}

template <bool is_ad>
GenericReal<is_ad>
IncompressibleFluidSpeciesTransportSPScalarKernelTempl<is_ad>::computeQpResidual()
{
  GenericReal<is_ad> mass_residual = 0;
  const Moose::ElemArg _qp = Moose::ElemArg();
  const int _i = 0;
  const auto _state = _is_implicit ? Moose::currentState() : Moose::oldState();
  // start by getting fluid properties
  auto _Tin = 1.0 / 2.0 * (1 - abs(_m[_i]) / _m[_i]) * _Tdown[_i] +
              1.0 / 2.0 * (1 + abs(_m[_i]) / _m[_i]) * _Tup[_i];
  auto _mu = _fp.mu_from_p_T(_Pref(_qp, _state), (_T[_i] + _Tin) / 2);
  auto _rho = _fp.rho_from_p_T(_Pref(_qp, _state), (_T[_i] + _Tin) / 2);

  // Decide flow regime for MTC
  auto _Dh = 4.0 * _area(_qp, _state) / _perimeter(_qp, _state);
  auto _G = abs(_m[_i]) / _area(_qp, _state);
  auto _Re = _G * _Dh / _mu;
  auto _Sc = _mu / _rho / _diffus(_qp, _state);
  // Mass transfer to fluid (Linton-Sherwood)
  auto _KT = 0.023 * pow(_Re, 0.8) * pow(_Sc, 1.0 / 3.0) * _diffus(_qp, _state) / _Dh;
  auto _pKT = &_KT;
  GenericReal<is_ad> _Jm = 0.0;
  auto _pJm = &_Jm;
  if (_fluid_type == "gas")
  {
    if (_recomb(_qp, _state) != 0.0 & _dissoc(_qp, _state) != 0.0)
    {
      *_pJm = 1.0;
      for (size_t i = 0; i < _n_diss; ++i)
      {
        *_pJm = (*(_diss[i]))[_i] * *_pJm;
      }
      *_pJm = 2.0 * _recomb(_qp, _state) * *_pJm;
      *_pJm = *_pJm - _dissoc(_qp, _state) * Base::_u[_i] / _fluid_sol(_qp, _state);
    }
    else
    {
      mooseError("Can't handle equilibrium case for gas yet.");
    }
  }
  else if (_fluid_type == "metal")
  {
    *_pJm = *_pKT * ((*(_wall_sol[0]))(_qp, _state) / _fluid_sol(_qp, _state) * (*(_diss[0]))[_i] -
                     Base::_u[_i]);
  }
  else if (_fluid_type == "solvent")
  {
    if (_is_monatom)
    {
      *_pJm =
          2 * (*_pKT) *
          (_fluid_sol(_qp, _state) * pow((*(_diss[0]))[_i] / (*(_wall_sol[0]))(_qp, _state), 2) -
           Base::_u[_i]);
    }
    else
    {
      *_pJm = (*(_diss[0]))[_i] / (*(_wall_sol[0]))(_qp, _state);
      for (size_t i = 1; i < _n_diss; ++i)
      {
        *_pJm = (*(_diss[i]))[_i] / (*(_wall_sol[i]))(_qp, _state) * (*_pJm);
      }
      *_pJm = sqrt(_equib(_qp, _state)) * (*_pJm);
      *_pJm = (*_pJm) - Base::_u[_i];
      *_pJm = (*_pKT) / 1.380649E-23 / _T[_i] * (*_pJm);
    }
  }
  // Advection component
  mass_residual +=
      (_m[_i] / 2.0 * (1 - abs(_m[_i]) / _m[_i]) * _Cdown[_i] -
       _m[_i] / 2.0 * (1 + abs(_m[_i]) / _m[_i]) * _Cup[_i] + abs(_m[_i]) * Base::_u[_i]) /
      _length(_qp, _state) / _area(_qp, _state) / _rho;
  // Precursor decay
  for (size_t i = 0; i < _n_precursors; ++i)
  {
    mass_residual -= (*(_precursors[i]))[_i] * log(2) / (*(_precursorHLs[i]))(_qp, _state) *
                     exp(-log(2) / (*(_precursorHLs[i]))(_qp, _state) * Base::_dt);
  }
  // Primary species decay
  mass_residual += Base::_u[_i] * log(2) / _primaryHL(_qp, _state) *
                   exp(-log(2) / _primaryHL(_qp, _state) * Base::_dt);
  // Wall mass transfer
  mass_residual -= _Jm * _perimeter(_qp, _state) / _area(_qp, _state);
  // Transient term
  mass_residual += Base::_u_dot[_i];

  return mass_residual;
}

template <bool is_ad>
Real
IncompressibleFluidSpeciesTransportSPScalarKernelTempl<is_ad>::computeQpJacobian()
{
  if constexpr (!is_ad)
  {
    GenericReal<is_ad> mass_residual = 0;
    const Moose::ElemArg _qp = Moose::ElemArg();
    const int _i = 0;
    const auto _state = _is_implicit ? Moose::currentState() : Moose::oldState();
    // start by getting fluid properties
    auto _Tin = 1.0 / 2.0 * (1 - abs(_m[_i]) / _m[_i]) * _Tdown[_i] +
                1.0 / 2.0 * (1 + abs(_m[_i]) / _m[_i]) * _Tup[_i];
    auto _mu = _fp.mu_from_p_T(_Pref(_qp, _state), (_T[_i] + _Tin) / 2);
    auto _rho = _fp.rho_from_p_T(_Pref(_qp, _state), (_T[_i] + _Tin) / 2);

    // Decide flow regime for MTC
    auto _Dh = 4.0 * _area(_qp, _state) / _perimeter(_qp, _state);
    auto _G = abs(_m[_i]) / _area(_qp, _state);
    auto _Re = _G * _Dh / _mu;
    auto _Sc = _mu / _rho / _diffus(_qp, _state);
    // Mass transfer to fluid (Linton-Sherwood)
    auto _KT = 0.023 * pow(_Re, 0.8) * pow(_Sc, 1.0 / 3.0) * _diffus(_qp, _state) / _Dh;
    auto _pKT = &_KT;
    auto _Jm = 0.0;
    auto _pJm = &_Jm;
    if (_fluid_type == "gas")
    {
      if (_recomb(_qp, _state) != 0.0 & _dissoc(_qp, _state) != 0.0)
      {
        *_pJm = -_dissoc(_qp, _state) / _fluid_sol(_qp, _state);
      }
      else
      {
        mooseError("Can't handle equilibrium case for gas yet.");
      }
    }
    else if (_fluid_type == "metal")
    {
      *_pJm = -*_pKT;
    }
    else if (_fluid_type == "solvent")
    {
      if (_is_monatom)
      {
        *_pJm = -2 * (*_pKT);
      }
      else
      {
        *_pJm = -(*_pKT) / 1.380649E-23 / _T[_i];
      }
    }
    // Advection component
    mass_residual += (abs(_m[_i])) / _length(_qp, _state) / _area(_qp, _state) / _rho;
    // Primary species decay
    mass_residual +=
        log(2) / _primaryHL(_qp, _state) * exp(-log(2) / _primaryHL(_qp, _state) * Base::_dt);
    // Wall mass transfer
    mass_residual -= _Jm * _perimeter(_qp, _state) / _area(_qp, _state);
    // Transient term
    mass_residual += Base::_du_dot_du[_i];

    return mass_residual;
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
