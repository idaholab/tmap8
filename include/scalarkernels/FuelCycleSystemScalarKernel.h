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

#include <tuple>
#include <unordered_map>

template <bool is_ad>
class FuelCycleSystemScalarKernelTempl
  : public std::conditional<is_ad, ADScalarTimeDerivative, ODETimeDerivative>::type,
    public FunctorInterface
{
  using Base = typename std::conditional<is_ad, ADScalarTimeDerivative, ODETimeDerivative>::type;

public:
  FuelCycleSystemScalarKernelTempl(const InputParameters & parameters);
  virtual bool isADObject() const override { return is_ad; };
  static InputParameters validParams();

  virtual void initialSetup() override;
  virtual void residualSetup() override;
  virtual void jacobianSetup() override;
  virtual void meshChanged() override;

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
  /// Spatial argument used to evaluate all functors. A point (rather than an element) argument
  /// is used so that spatially-dependent functors such as Functions receive a valid location
  /// and so that evaluations bypass the element-keyed functor cache
  Moose::ElemPointArg _functor_arg;

  /// Value of a functor at the evaluation point, read from the cache for element-dependent functors
  GenericReal<is_ad> functorValue(const Moose::Functor<GenericReal<is_ad>> & functor) const;

private:
  /// Locates the element containing the evaluation point and the process that owns it, and checks
  /// that every element-dependent functor can be evaluated there
  void locateEvaluationPoint();
  /// Evaluates element-dependent functors on the process owning the evaluation element and
  /// broadcasts the values to all processes
  void cacheElementDependentFunctors();
  /// State (current or old) at which functors are evaluated
  Moose::StateArg functorState() const;
  /// Records a functor so that its compatibility with the evaluation point can be checked
  void registerFunctor(const std::string & param_name,
                       const MooseFunctorName & functor_name,
                       const Moose::Functor<GenericReal<is_ad>> & functor);
  /// Whether a functor can be evaluated without an element (e.g. Functions, Postprocessors)
  bool isElementIndependent(const MooseFunctorName & functor_name,
                            const Moose::Functor<GenericReal<is_ad>> & functor) const;
  /// Parameter name, functor name, and functor for every functor used by this kernel
  std::vector<std::tuple<std::string, MooseFunctorName, const Moose::Functor<GenericReal<is_ad>> *>>
      _registered_functors;
  /// Process owning the element containing the evaluation point
  processor_id_type _evaluation_pid;
  /// Values of element-dependent functors (field variables, functor materials) at the evaluation
  /// point. These are only computable on the process owning the evaluation element, which is
  /// generally not the process owning the scalar variable's degrees of freedom
  std::unordered_map<const Moose::Functor<GenericReal<is_ad>> *, GenericReal<is_ad>>
      _element_dependent_values;
};

typedef FuelCycleSystemScalarKernelTempl<false> FuelCycleSystemScalarKernel;
typedef FuelCycleSystemScalarKernelTempl<true> ADFuelCycleSystemScalarKernel;
