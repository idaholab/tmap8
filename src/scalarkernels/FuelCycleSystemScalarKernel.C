/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2025 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/
#include "FuelCycleSystemScalarKernel.h"

// MOOSE includes
#include "Assembly.h"
#include "FEProblemBase.h"
#include "libmesh/point_locator_base.h"
#include "metaphysicl/parallel_dualnumber.h"
#include "metaphysicl/parallel_semidynamicsparsenumberarray.h"
#include "MooseVariableScalar.h"
#include "FunctorInterface.h"
#include "TMAP8PhysicalConstants.h"
#include "ScalarCoupleable.h"

registerMooseObject("TMAP8App", FuelCycleSystemScalarKernel);
registerMooseObject("TMAP8App", ADFuelCycleSystemScalarKernel);

template <bool is_ad>
InputParameters
FuelCycleSystemScalarKernelTempl<is_ad>::validParams()
{
  InputParameters params =
      is_ad ? ADScalarTimeDerivative::validParams() : ODETimeDerivative::validParams();
  params += FunctorInterface::validParams();
  params.addClassDescription(
      "Implements a generic scalar system component for tritium fuel cycle calculations.");
  params.addCoupledVar("inputs",
                       {},
                       "Variables (usually tritium inventory) which feed into this system. Takes a "
                       "list of scalar variable names");
  params.addParam<std::vector<MooseFunctorName>>(
      "input_fractions",
      std::vector<MooseFunctorName>({}),
      "Fraction of upstream variable (inventory) coming into this system. Must be the same length "
      "as 'inputs'");
  params.addParam<MooseFunctorName>("decay_constant",
                                    PhysicalConstants::tritium_decay_const,
                                    "The decay constant of tritium (ln(2)/half-life)");
  params.addParam<MooseFunctorName>(
      "residence_time", 1, "The residence time for tritium in this system");
  params.addParam<MooseFunctorName>(
      "leakage_rate", 0, "The fractional loss rate for tritium in this system");
  params.addParam<bool>("steady_state",
                        false,
                        "Whether to apply a psuedo steady-state approximation (ignore dt term)");
  params.addParam<bool>(
      "is_implicit",
      false,
      "Whether an explicit (previous value calculation) or implicit (current value) is used");
  params.addParam<MooseFunctorName>("TBR", 0.0, "Tritium breeding ratio");
  params.addParam<std::vector<MooseFunctorName>>(
      "other_sources",
      std::vector<MooseFunctorName>({}),
      "Other tritium sources - terms not dependent on any scalar variables");
  params.addParam<std::vector<MooseFunctorName>>(
      "other_sinks",
      std::vector<MooseFunctorName>({}),
      "Other tritium sinks - terms not dependent on any scalar variables");
  params.addParam<MooseFunctorName>("burn_rate", 0.0, "Burn rate of tritium within this system");
  params.addParam<bool>("disable_residence_time",
                        false,
                        "Assume an infinite residence time. (no leakage from this system).");
  params.addParam<Point>("evaluation_point",
                         Point(),
                         "Spatial point at which the functor parameters (e.g. Functions) are "
                         "evaluated. Field functors additionally require this point to lie within "
                         "the mesh.");
  return params;
}

template <bool is_ad>
FuelCycleSystemScalarKernelTempl<is_ad>::FuelCycleSystemScalarKernelTempl(
    const InputParameters & parameters)
  : Base(parameters),
    FunctorInterface(this),
    _n_inputs(ScalarCoupleable::isCoupledScalar("inputs")
                  ? ScalarCoupleable::coupledScalarComponents("inputs")
                  : 0),
    _n_other_sources(
        this->template getParam<std::vector<MooseFunctorName>>("other_sources").size()),
    _n_other_sinks(this->template getParam<std::vector<MooseFunctorName>>("other_sinks").size()),
    _input_vals(_n_inputs),
    _input_fractions(
        this->template getParam<std::vector<MooseFunctorName>>("input_fractions").size()),
    _decay_constant(this->template getFunctor<GenericReal<is_ad>>("decay_constant")),
    _residence_time(this->template getFunctor<GenericReal<is_ad>>("residence_time")),
    _leakage_rate(this->template getFunctor<GenericReal<is_ad>>("leakage_rate")),
    _pseudo_steady_state(this->template getParam<bool>("steady_state")),
    _disable_residence_time(this->template getParam<bool>("disable_residence_time")),
    _is_implicit(this->template getParam<bool>("is_implicit")),
    _TBR(this->template getFunctor<GenericReal<is_ad>>("TBR")),
    _other_sources(this->template getParam<std::vector<MooseFunctorName>>("other_sources").size()),
    _other_sinks(this->template getParam<std::vector<MooseFunctorName>>("other_sinks").size()),
    _burn_rate(this->template getFunctor<GenericReal<is_ad>>("burn_rate")),
    _functor_arg({nullptr, this->template getParam<Point>("evaluation_point"), false})
{
  if (_n_inputs != _input_fractions.size())
  {
    mooseError("\"input_fractions\" must be defined with the same length as \"inputs\".");
  }
  auto & input_functor_names =
      MooseBase::getParam<std::vector<MooseFunctorName>>("input_fractions");
  for (size_t i = 0; i < _n_inputs; ++i)
  {
    if ((ScalarCoupleable::coupledScalar("inputs", i)) == (Base::_var).number())
    {
      mooseError("Primary variable cannot be listed as a coupled variable.");
    }
    _input_vals[i] = &(ScalarCoupleable::coupledScalarValue("inputs", i));
    _input_fractions[i] = &(this->template getFunctor<GenericReal<is_ad>>(input_functor_names[i]));
  }
  auto & other_source_names = MooseBase::getParam<std::vector<MooseFunctorName>>("other_sources");
  for (size_t i = 0; i < _n_other_sources; ++i)
  {
    _other_sources[i] = &(this->template getFunctor<GenericReal<is_ad>>(other_source_names[i]));
  }
  auto & other_sink_names = MooseBase::getParam<std::vector<MooseFunctorName>>("other_sinks");
  for (size_t i = 0; i < _n_other_sinks; ++i)
  {
    _other_sinks[i] = &(this->template getFunctor<GenericReal<is_ad>>(other_sink_names[i]));
  }

  for (const auto & param :
       {"decay_constant", "residence_time", "leakage_rate", "TBR", "burn_rate"})
    registerFunctor(param,
                    this->template getParam<MooseFunctorName>(param),
                    this->template getFunctor<GenericReal<is_ad>>(param));
  for (size_t i = 0; i < _n_inputs; ++i)
    registerFunctor("input_fractions", input_functor_names[i], *_input_fractions[i]);
  for (size_t i = 0; i < _n_other_sources; ++i)
    registerFunctor("other_sources", other_source_names[i], *_other_sources[i]);
  for (size_t i = 0; i < _n_other_sinks; ++i)
    registerFunctor("other_sinks", other_sink_names[i], *_other_sinks[i]);
}

template <bool is_ad>
void
FuelCycleSystemScalarKernelTempl<is_ad>::registerFunctor(
    const std::string & param_name,
    const MooseFunctorName & functor_name,
    const Moose::Functor<GenericReal<is_ad>> & functor)
{
  _registered_functors.emplace_back(param_name, functor_name, &functor);
}

template <bool is_ad>
bool
FuelCycleSystemScalarKernelTempl<is_ad>::isElementIndependent(
    const MooseFunctorName & functor_name, const Moose::Functor<GenericReal<is_ad>> & functor) const
{
  auto & problem = Base::_fe_problem;
  return functor.isConstant() || problem.hasPostprocessorValueByName(functor_name) ||
         problem.hasFunction(functor_name) || problem.hasScalarVariable(functor_name);
}

template <bool is_ad>
void
FuelCycleSystemScalarKernelTempl<is_ad>::initialSetup()
{
  Base::initialSetup();
  locateEvaluationPoint();
}

template <bool is_ad>
void
FuelCycleSystemScalarKernelTempl<is_ad>::meshChanged()
{
  Base::meshChanged();
  locateEvaluationPoint();
}

template <bool is_ad>
void
FuelCycleSystemScalarKernelTempl<is_ad>::residualSetup()
{
  Base::residualSetup();
  cacheElementDependentFunctors();
}

template <bool is_ad>
void
FuelCycleSystemScalarKernelTempl<is_ad>::jacobianSetup()
{
  Base::jacobianSetup();
  cacheElementDependentFunctors();
}

template <bool is_ad>
void
FuelCycleSystemScalarKernelTempl<is_ad>::locateEvaluationPoint()
{
  const auto & comm = this->comm();
  _element_dependent_values.clear();
  for (const auto & [param_name, functor_name, functor] : _registered_functors)
    if (!isElementIndependent(functor_name, *functor))
      _element_dependent_values.emplace(functor, 0);

  // Find a locally owned element containing the evaluation point. The point may lie on an element
  // boundary, or on a partition boundary of a distributed mesh, so the process with the lowest id
  // owning a containing element is selected to evaluate element-dependent functors
  auto point_locator = Base::_mesh.getPointLocator();
  point_locator->enable_out_of_mesh_mode();
  std::set<const Elem *> candidates;
  (*point_locator)(_functor_arg.point, candidates);
  _functor_arg.elem = nullptr;
  for (const auto * const elem : candidates)
    if (elem->processor_id() == comm.rank() &&
        (!_functor_arg.elem || elem->id() < _functor_arg.elem->id()))
      _functor_arg.elem = elem;

  _evaluation_pid = _functor_arg.elem ? comm.rank() : DofObject::invalid_processor_id;
  comm.min(_evaluation_pid);
  if (_evaluation_pid != comm.rank())
    _functor_arg.elem = nullptr;
  subdomain_id_type sub_id = _functor_arg.elem ? _functor_arg.elem->subdomain_id() : 0;
  if (_evaluation_pid != DofObject::invalid_processor_id)
    comm.broadcast(sub_id, _evaluation_pid);

  // Element-dependent functors (field variables, functor materials) must be defined at the
  // evaluation point, otherwise they would dereference a null element or silently return a value
  // from outside their block restriction
  for (const auto & [param_name, functor_name, functor] : _registered_functors)
  {
    if (!_element_dependent_values.count(functor))
      continue;
    if (_evaluation_pid == DofObject::invalid_processor_id)
      this->paramError("evaluation_point",
                       "The evaluation point (",
                       _functor_arg.point,
                       ") is outside the mesh, but functor '",
                       functor_name,
                       "' supplied to '",
                       param_name,
                       "' requires an element to be evaluated. Move the evaluation point inside "
                       "the mesh or use a Function, Postprocessor, or scalar variable instead.");
    if (!functor->hasBlocks(sub_id))
      this->paramError("evaluation_point",
                       "Functor '",
                       functor_name,
                       "' supplied to '",
                       param_name,
                       "' is not defined on subdomain ",
                       sub_id,
                       ", which contains the evaluation point (",
                       _functor_arg.point,
                       ").");
  }
}

template <bool is_ad>
void
FuelCycleSystemScalarKernelTempl<is_ad>::cacheElementDependentFunctors()
{
  if (_element_dependent_values.empty())
    return;
  // The scalar residual is computed only on the process owning the scalar degrees of freedom, but
  // element-dependent functors can only be evaluated where the element's solution is available
  const auto state = functorState();
  for (auto & [functor, value] : _element_dependent_values)
  {
    if (_evaluation_pid == this->comm().rank())
      value = (*functor)(_functor_arg, state);
    this->comm().broadcast(value, _evaluation_pid);
  }
}

template <bool is_ad>
Moose::StateArg
FuelCycleSystemScalarKernelTempl<is_ad>::functorState() const
{
  return _is_implicit ? Moose::currentState() : Moose::oldState();
}

template <bool is_ad>
GenericReal<is_ad>
FuelCycleSystemScalarKernelTempl<is_ad>::functorValue(
    const Moose::Functor<GenericReal<is_ad>> & functor) const
{
  const auto it = _element_dependent_values.find(&functor);
  if (it != _element_dependent_values.end())
    return it->second;
  return functor(_functor_arg, functorState());
}

template <bool is_ad>
GenericReal<is_ad>
FuelCycleSystemScalarKernelTempl<is_ad>::computeQpResidual()
{
  GenericReal<is_ad> partial_residual = 0;
  const auto _i = Base::_i;
  for (unsigned int i = 0; i < _n_inputs; ++i)
    partial_residual += -(*(_input_vals[i]))[_i] * functorValue(*_input_fractions[i]);

  for (unsigned int i = 0; i < _n_other_sources; ++i)
    partial_residual += -functorValue(*_other_sources[i]);

  for (unsigned int i = 0; i < _n_other_sinks; ++i)
    partial_residual += functorValue(*_other_sinks[i]);

  partial_residual += -functorValue(_TBR) * functorValue(_burn_rate);
  if (!_disable_residence_time)
  {
    partial_residual += functorValue(_leakage_rate) / functorValue(_residence_time) * Base::_u[_i];
    partial_residual += Base::_u[_i] / functorValue(_residence_time);
  }
  partial_residual += functorValue(_decay_constant) * Base::_u[_i];
  if (!_pseudo_steady_state)
    partial_residual += Base::_u_dot[_i];
  return partial_residual;
}

template <bool is_ad>
Real
FuelCycleSystemScalarKernelTempl<is_ad>::computeQpJacobian()
{
  if constexpr (!is_ad)
  {
    Real partial_residual = 0;
    const auto _i = Base::_i;
    if (!_disable_residence_time)
    {
      partial_residual += functorValue(_leakage_rate) / functorValue(_residence_time);
      partial_residual += 1 / functorValue(_residence_time);
    }
    partial_residual += functorValue(_decay_constant);
    if (!_pseudo_steady_state)
      partial_residual += Base::_du_dot_du[_i];
    return partial_residual;
  }
  else
  {
    mooseError("computeQpJacobian() should not be called in AD mode");
    return 0;
  }
}

template <>
Real
FuelCycleSystemScalarKernelTempl<true>::computeQpJacobian()
{
  mooseError("Internal error, calling computeQpJacobian in AD class.");
  return 0.0;
}

template class FuelCycleSystemScalarKernelTempl<false>;
template class FuelCycleSystemScalarKernelTempl<true>;
