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

  for (const auto & param : {"decay_constant", "residence_time", "leakage_rate", "TBR", "burn_rate"})
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
  // Locate the element containing the evaluation point, if any, so that field functors can also
  // be evaluated. Functions, Postprocessors, constants, and scalar variables do not require it.
  auto point_locator = Base::_mesh.getPointLocator();
  point_locator->enable_out_of_mesh_mode();
  _functor_arg.elem = (*point_locator)(_functor_arg.point);

  // Element-dependent functors (field variables, functor materials) must be defined at the
  // evaluation point, otherwise they would dereference a null element or silently return a value
  // from outside their block restriction
  for (const auto & [param_name, functor_name, functor] : _registered_functors)
  {
    if (isElementIndependent(functor_name, *functor))
      continue;
    if (!_functor_arg.elem)
      this->paramError("evaluation_point",
                       "The evaluation point (",
                       _functor_arg.point,
                       ") is outside the mesh, but functor '",
                       functor_name,
                       "' supplied to '",
                       param_name,
                       "' requires an element to be evaluated. Move the evaluation point inside "
                       "the mesh or use a Function, Postprocessor, or scalar variable instead.");
    const auto sub_id = _functor_arg.elem->subdomain_id();
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
GenericReal<is_ad>
FuelCycleSystemScalarKernelTempl<is_ad>::computeQpResidual()
{
  GenericReal<is_ad> partial_residual = 0;
  const auto & _qp = _functor_arg;
  const auto _i = Base::_i;
  const auto _state = _is_implicit ? Moose::currentState() : Moose::oldState();
  for (unsigned int i = 0; i < _n_inputs; ++i)
    partial_residual += -(*(_input_vals[i]))[_i] * (*(_input_fractions[i]))(_qp, _state);

  for (unsigned int i = 0; i < _n_other_sources; ++i)
    partial_residual += -(*(_other_sources[i]))(_qp, _state);

  for (unsigned int i = 0; i < _n_other_sinks; ++i)
    partial_residual += (*(_other_sinks[i]))(_qp, _state);

  partial_residual += -_TBR(_qp, _state) * _burn_rate(_qp, _state);
  if (!_disable_residence_time)
  {
    partial_residual += _leakage_rate(_qp, _state) / _residence_time(_qp, _state) * Base::_u[_i];
    partial_residual += Base::_u[_i] / _residence_time(_qp, _state);
  }
  partial_residual += _decay_constant(_qp, _state) * Base::_u[_i];
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
    const auto & _qp = _functor_arg;
    const auto _i = Base::_i;
    const auto _state = _is_implicit ? Moose::currentState() : Moose::oldState();
    if (!_disable_residence_time)
    {
      partial_residual += _leakage_rate(_qp, _state) / _residence_time(_qp, _state);
      partial_residual += 1 / _residence_time(_qp, _state);
    }
    partial_residual += _decay_constant(_qp, _state);
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
