//* This file is part of the MOOSE framework
//* https://mooseframework.inl.gov
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#pragma once

#include "SinglePhaseFluidProperties.h"
#include "IncompressibleEnergySPScalarKernel.h"

class SinglePhaseFluidProperties;

template <bool is_ad>
class IncompressibleFluidSpeciesTransportSPScalarKernelTempl
  : public std::conditional<is_ad,
                            ADIncompressibleEnergySPScalarKernel,
                            IncompressibleEnergySPScalarKernel>::type
{
  using Base = typename std::conditional<is_ad,
                                         ADIncompressibleEnergySPScalarKernel,
                                         IncompressibleEnergySPScalarKernel>::type;

public:
  IncompressibleFluidSpeciesTransportSPScalarKernelTempl(const InputParameters & parameters);
  virtual bool isADObject() const override { return is_ad; };
  static InputParameters validParams();

protected:
  virtual GenericReal<is_ad> computeQpResidual() override;
  virtual Real computeQpJacobian() override;
  /// Coupled segment fluid temperature
  const VariableValue & _T;
  /// Coupled upstream fluid concentration
  const VariableValue & _Cup;
  /// Coupled downstream fluid concentration
  const VariableValue & _Cdown;
  /// Number of precursor species
  const size_t _n_precursors;
  /// Coupled precursor species concentrations
  std::vector<const VariableValue *> _precursors;
  /// Number of dissociated atoms in wall forming primary species
  const size_t _n_diss;
  /// Coupled wall dissociated atoms
  std::vector<const VariableValue *> _diss;
  /// Precursor half-lives
  std::vector<const Moose::Functor<GenericReal<is_ad>> *> _precursorHLs;
  /// Primary species half-life
  const Moose::Functor<GenericReal<is_ad>> & _primaryHL;
  /// Fluid type string
  const std::string _fluid_type;
  /// Primary species diffusivity in fluid
  const Moose::Functor<GenericReal<is_ad>> & _diffus;
  /// Primary species solubility in fluid
  const Moose::Functor<GenericReal<is_ad>> & _fluid_sol;
  /// Primary species dissociation coefficient
  const Moose::Functor<GenericReal<is_ad>> & _dissoc;
  /// Primary species recombination coefficient
  const Moose::Functor<GenericReal<is_ad>> & _recomb;
  /// Solubility of wall dissociated atoms in wall
  std::vector<const Moose::Functor<GenericReal<is_ad>> *> _wall_sol;
  /// Primary species homonuclear flag
  const bool _is_homonuc;
  /// Primary species equilibrium constant
  const Moose::Functor<GenericReal<is_ad>> & _equib;
};

typedef IncompressibleFluidSpeciesTransportSPScalarKernelTempl<false>
    IncompressibleFluidSpeciesTransportSPScalarKernel;
typedef IncompressibleFluidSpeciesTransportSPScalarKernelTempl<true>
    ADIncompressibleFluidSpeciesTransportSPScalarKernel;
