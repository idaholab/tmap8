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
class CoupledPressureFlowPathMomentumSCSPScalarKernelTempl
  : public std::conditional<is_ad, ADScalarTimeDerivative, ODETimeDerivative>::type,
    public FunctorInterface
{
  using Base = typename std::conditional<is_ad, ADScalarTimeDerivative, ODETimeDerivative>::type;

public:
  CoupledPressureFlowPathMomentumSCSPScalarKernelTempl(const InputParameters & parameters);
  virtual bool isADObject() const override { return is_ad; };
  static InputParameters validParams();

protected:
  virtual GenericReal<is_ad> computeQpResidual() override;
  virtual Real computeQpJacobian();
  const VariableValue & _mc;
  size_t _n_temps;
  std::vector<const VariableValue *> _T;
  bool _is_implicit;
  const Moose::Functor<GenericReal<is_ad>> & _Pref;
  const SinglePhaseFluidProperties & _fp;
  size_t _n_segments;
  std::vector<const Moose::Functor<GenericReal<is_ad>> *> _areas;
  std::vector<const Moose::Functor<GenericReal<is_ad>> *> _perimeters;
  std::vector<const Moose::Functor<GenericReal<is_ad>> *> _lengths;
  std::vector<const Moose::Functor<GenericReal<is_ad>> *> _alphas;
  std::vector<const Moose::Functor<GenericReal<is_ad>> *> _forms_losses;
  std::vector<const Moose::Functor<GenericReal<is_ad>> *> _dPps;
  std::vector<const Moose::Functor<GenericReal<is_ad>> *> _roughnesses;
  const Moose::Functor<GenericReal<is_ad>> & _gravity;
};

typedef CoupledPressureFlowPathMomentumSCSPScalarKernelTempl<false> CoupledPressureFlowPathMomentumSCSPScalarKernel;
typedef CoupledPressureFlowPathMomentumSCSPScalarKernelTempl<true> ADCoupledPressureFlowPathMomentumSCSPScalarKernel;