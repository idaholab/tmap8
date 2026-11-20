/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2025 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#include "ADMatReactionFlexible.h"

// MOOSE includes
#include "MooseVariable.h"
#include "NonlinearSystem.h"

registerMooseObject("TMAP8App", ADMatReactionFlexible);

InputParameters
ADMatReactionFlexible::validParams()
{
  InputParameters params = ADKernel::validParams();
  params.addCoupledVar("vs",
                       "Set this to make vs a list of coupled variables, otherwise it will use the "
                       "kernel's nonlinear variable for v");
  params.addClassDescription(
      "Kernel to add -coeff*K*vs, where coeff=coefficient, K=reaction rate, vs=variables product");
  params.addParam<MaterialPropertyName>(
      "reaction_rate_name", "K", "The reaction rate used with the kernel");
  params.addParam<Real>("coeff",
                        1.,
                        "A coefficient for multiplying the reaction term. It can be used to "
                        "include the stoichiometry of a reaction for specific species.");
  return params;
}

ADMatReactionFlexible::ADMatReactionFlexible(const InputParameters & parameters)
  : ADKernel(parameters),
    _num_vs(coupledComponents("vs")),
    _vs(adCoupledValues("vs")),
    _reaction_rate(getADMaterialProperty<Real>("reaction_rate_name")),
    _coeff(getParam<Real>("coeff"))
{
}

ADReal
ADMatReactionFlexible::computeQpResidual()
{
  if (_num_vs == 0)
    return -_coeff * _reaction_rate[_qp] * _test[_i][_qp];
  else
  {
    // The product is an ADReal so that derivatives with respect to the coupled variables
    // (including the kernel's own variable) are included in the Jacobian
    ADReal prod_vs = 1.0;
    for (const auto * const v : _vs)
      prod_vs *= (*v)[_qp];
    return -_coeff * _reaction_rate[_qp] * _test[_i][_qp] * prod_vs;
  }
}
