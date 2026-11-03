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

/**
 * Placeholder used when the MOOSE scalar kernel base class already provides FunctorInterface
 * (newer MOOSE), so that FunctorInterface is not inherited twice. Older MOOSE does not provide
 * it, in which case FunctorInterface is inherited directly. This can be removed after a MOOSE
 * update.
 */
struct FuelCycleNoFunctorInterface
{
  FuelCycleNoFunctorInterface(const MooseObject *) {}
};

template <bool is_ad>
class FuelCycleSystemScalarKernelTempl
  : public std::conditional<is_ad, ADScalarTimeDerivative, ODETimeDerivative>::type,
    public std::conditional<
        std::is_base_of<
            FunctorInterface,
            typename std::conditional<is_ad, ADScalarTimeDerivative, ODETimeDerivative>::type>::
            value,
        FuelCycleNoFunctorInterface,
        FunctorInterface>::type
{
  using Base = typename std::conditional<is_ad, ADScalarTimeDerivative, ODETimeDerivative>::type;
  using TmpFunctorInterface =
      typename std::conditional<std::is_base_of<FunctorInterface, Base>::value,
                                FuelCycleNoFunctorInterface,
                                FunctorInterface>::type;

public:
  FuelCycleSystemScalarKernelTempl(const InputParameters & parameters);
  virtual bool isADObject() const override { return is_ad; };
  static InputParameters validParams();

protected:
  virtual GenericReal<is_ad> computeQpResidual() override;
  virtual Real computeQpJacobian() override;
  // Helper values for bookkeeping
  size_t _n_inputs;
  size_t _n_other_sources;
  size_t _n_other_sinks;
  /* * * * * * * * * * * * * * * * *
   * These vectors hold the system of
   * inputs and outputs that go into this scalar kernel's
   * mass balance equation, and what fraction of the
   * upstream system makes its way into this system
   * * * * * * * * * * * * * * * * */
  std::vector<const VariableValue *> _input_vals;
  std::vector<const Moose::Functor<GenericReal<is_ad>> *> _input_fractions;
  /// Decay constant of tritium (or relevant isotope)
  const Moose::Functor<GenericReal<is_ad>> & _decay_constant;
  /// Residence time of isotope in the system
  const Moose::Functor<GenericReal<is_ad>> & _residence_time;
  /// Leakage rate from this system (epsilon in documentation)
  const Moose::Functor<GenericReal<is_ad>> & _leakage_rate;
  /// Whether to ignore time-dependence for this kernel
  bool _pseudo_steady_state;
  /// Whether to ignore residence-time effects for this kernel
  bool _disable_residence_time;
  /// Whether to use the previous value calculation or the current value for
  /// timestepping
  bool _is_implicit;
  /// Tritium breeding ratio of the system
  const Moose::Functor<GenericReal<is_ad>> & _TBR;
  /// Source terms which may not be from a scalar variable
  std::vector<const Moose::Functor<GenericReal<is_ad>> *> _other_sources;
  /// Sink terms which may not be from a scalar variable
  std::vector<const Moose::Functor<GenericReal<is_ad>> *> _other_sinks;
  /// Rate of tritium consumption in the system, used with TBR to determine tritium production rate
  const Moose::Functor<GenericReal<is_ad>> & _burn_rate;
};

typedef FuelCycleSystemScalarKernelTempl<false> FuelCycleSystemScalarKernel;
typedef FuelCycleSystemScalarKernelTempl<true> ADFuelCycleSystemScalarKernel;
