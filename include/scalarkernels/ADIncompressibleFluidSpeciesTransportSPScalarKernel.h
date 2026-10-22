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
#include "ADIncompressibleEnergySPScalarKernel.h"

class SinglePhaseFluidProperties;

class ADIncompressibleFluidSpeciesTransportSPScalarKernel
  : public ADIncompressibleEnergySPScalarKernel
{
  using Base = ADIncompressibleEnergySPScalarKernel;

public:
  ADIncompressibleFluidSpeciesTransportSPScalarKernel(const InputParameters & parameters);
  static InputParameters validParams();

protected:
  virtual ADReal computeQpResidual() override;
  virtual Real computeQpJacobian() override;
  /// Coupled segment fluid temperature
  const ADVariableValue & _T;
  /// Coupled upstream fluid concentration
  const ADVariableValue & _Cup;
  /// Coupled downstream fluid concentration
  const ADVariableValue & _Cdown;
  /// Number of precursor species
  const size_t _n_precursors;
  /// Coupled precursor species concentrations
  std::vector<const ADVariableValue *> _precursors;
  /// Number of dissociated atoms in wall forming primary species
  const size_t _n_diss;
  /// Coupled wall dissociated atoms
  std::vector<const ADVariableValue *> _diss;
  /// Precursor half-lives
  std::vector<const Moose::Functor<ADReal> *> _precursorHLs;
  /// Primary species half-life
  const Moose::Functor<ADReal> & _primaryHL;
  /// Fluid type string
  const std::string _fluid_type;
  /// Primary species diffusivity in fluid
  const Moose::Functor<ADReal> & _diffus;
  /// Primary species solubility in fluid
  const Moose::Functor<ADReal> & _fluid_sol;
  /// Primary species dissociation coefficient
  const Moose::Functor<ADReal> & _dissoc;
  /// Primary species recombination coefficient
  const Moose::Functor<ADReal> & _recomb;
  /// Solubility of wall dissociated atoms in wall
  std::vector<const Moose::Functor<ADReal> *> _wall_sol;
  /// Primary species homonuclear flag
  const bool _is_homonuc;
  /// Primary species equilibrium constant
  const Moose::Functor<ADReal> & _equib;
};
