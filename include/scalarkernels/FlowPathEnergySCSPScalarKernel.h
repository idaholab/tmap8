/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2025 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#pragma once

#include "ODETimeDerivative.h"
#include "ADScalarTimeDerivative.h"
#include "FunctorInterface.h"
#include "MooseTypes.h"
#include "SinglePhaseFluidProperties.h"

class SinglePhaseFluidProperties;

template <bool is_ad>
class FlowPathEnergySCSPScalarKernelTempl
  : public std::conditional<is_ad, ADScalarTimeDerivative, ODETimeDerivative>::type,
    public FunctorInterface
{
  using Base = typename std::conditional<is_ad, ADScalarTimeDerivative, ODETimeDerivative>::type;

public:
  FlowPathEnergySCSPScalarKernelTempl(const InputParameters & parameters);
  virtual bool isADObject() const override { return is_ad; };
  static InputParameters validParams();

protected:
  virtual GenericReal<is_ad> computeQpResidual() override;
  virtual Real computeQpJacobian();
  const SinglePhaseFluidProperties & _fp;
  const VariableValue & _m;
  const VariableValue & _Tup;
  const VariableValue & _Tdown;
  const VariableValue & _Tw;
  bool _is_implicit;
  const Moose::Functor<GenericReal<is_ad>> & _Pref;
  const Moose::Functor<GenericReal<is_ad>> & _area;
  const Moose::Functor<GenericReal<is_ad>> & _perimeter;
  const Moose::Functor<GenericReal<is_ad>> & _length;
};

typedef FlowPathEnergySCSPScalarKernelTempl<false> FlowPathEnergySCSPScalarKernel;
typedef FlowPathEnergySCSPScalarKernelTempl<true> ADFlowPathEnergySCSPScalarKernel;