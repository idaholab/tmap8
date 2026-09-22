//* This file is part of the MOOSE framework
//* https://mooseframework.inl.gov
//*
//* All rights reserved, see COPYRIGHT for full restrictions
//* https://github.com/idaholab/moose/blob/master/COPYRIGHT
//*
//* Licensed under LGPL 2.1, please see LICENSE for details
//* https://www.gnu.org/licenses/lgpl-2.1.html

#pragma once

#include "ODETimeDerivative.h"
#include "ADScalarTimeDerivative.h"
#include "FunctorInterface.h"
#include "MooseTypes.h"
#include "SinglePhaseFluidProperties.h"

class SinglePhaseFluidProperties;

template <bool is_ad>
class IncompressibleFluidSpeciesTransportSPScalarKernelTempl
  : public std::conditional<is_ad, ADScalarTimeDerivative, ODETimeDerivative>::type,
    public FunctorInterface
{
  using Base = typename std::conditional<is_ad, ADScalarTimeDerivative, ODETimeDerivative>::type;

public:
  IncompressibleFluidSpeciesTransportSPScalarKernelTempl(const InputParameters & parameters);
  virtual bool isADObject() const override { return is_ad; };
  static InputParameters validParams();

protected:
  virtual GenericReal<is_ad> computeQpResidual() override;
  virtual Real computeQpJacobian();
  const SinglePhaseFluidProperties & _fp;
  const VariableValue & _m;
  const VariableValue & _Tup;
  const VariableValue & _Tdown;
  bool _is_implicit;
  const Moose::Functor<GenericReal<is_ad>> & _Pref;
  const Moose::Functor<GenericReal<is_ad>> & _area;
  const Moose::Functor<GenericReal<is_ad>> & _perimeter;
  const Moose::Functor<GenericReal<is_ad>> & _length;
  const VariableValue & _T;
  const VariableValue & _Cup;
  const VariableValue & _Cdown;
  size_t _n_precursors;
  std::vector<const VariableValue *> _precursors;
  size_t _n_diss;
  std::vector<const VariableValue *> _diss;
  std::vector<const Moose::Functor<GenericReal<is_ad>> *> _precursorHLs;
  const Moose::Functor<GenericReal<is_ad>> & _primaryHL;
  std::string _fluid_type;
  const Moose::Functor<GenericReal<is_ad>> & _diffus;
  const Moose::Functor<GenericReal<is_ad>> & _fluid_sol;
  const Moose::Functor<GenericReal<is_ad>> & _dissoc;
  const Moose::Functor<GenericReal<is_ad>> & _recomb;
  std::vector<const Moose::Functor<GenericReal<is_ad>> *> _wall_sol;
  bool _is_monatom;
  const Moose::Functor<GenericReal<is_ad>> & _equib;
};

typedef IncompressibleFluidSpeciesTransportSPScalarKernelTempl<false>
    IncompressibleFluidSpeciesTransportSPScalarKernel;
typedef IncompressibleFluidSpeciesTransportSPScalarKernelTempl<true>
    ADIncompressibleFluidSpeciesTransportSPScalarKernel;
