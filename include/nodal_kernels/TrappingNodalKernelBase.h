/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2025 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#pragma once

#include "NodalKernel.h"

#include "metaphysicl/dualdynamicsparsenumberarray.h"

using MetaPhysicL::DualNumber;
using MetaPhysicL::DynamicSparseNumberArray;

class Function;

/// Local AD number type used to assemble manual Jacobians for trapping kernels.
typedef DualNumber<Real, DynamicSparseNumberArray<Real, unsigned int>> LocalDN;

/**
 * Shared implementation for trapped-species trapping nodal kernels.
 *
 * This base class owns the common occupancy bookkeeping, empty-site assembly,
 * and manual Jacobian logic used by both dimensional and dimensionless
 * trapping kernels.
 */
class TrappingNodalKernelBase : public NodalKernel
{
public:
  /**
   * Build the shared trapping kernel state from the supplied rate and residual scaling.
   */
  TrappingNodalKernelBase(const InputParameters & parameters,
                          Real trapping_rate_coefficient,
                          Real residual_denominator);

  static InputParameters validParams();

protected:
  /**
   * Initialize the trapped-species variables that contribute to site occupancy.
   * @param other_weights Physical occupancy weight for each coupled trapped species
   * @param self_weight Physical occupancy weight for this kernel's primary variable
   */
  void initializeOccupancyTracking(const std::vector<Real> & other_weights, Real self_weight);

  Real computeQpResidual() override;
  Real computeQpJacobian() override;
  Real computeQpOffDiagJacobian(unsigned int jvar) override;

  /// Effective trapping-rate coefficient multiplying the Arrhenius factor.
  const Real _trapping_rate_coefficient;
  /// Trapping activation energy, expressed in Kelvin.
  const Real _trapping_energy;
  /// Atomic number density of the host material.
  const Real _N;
  /// Fraction of host sites available for trapping as a function of position.
  const Function & _Ct0;
  /// Coupled mobile-species concentration.
  const VariableValue & _mobile_concentration;
  /// Number of additional trapped concentrations coupled into the occupancy calculation.
  unsigned int _n_other_concs;
  /// Coupled concentration fields that consume trapping sites, including this kernel's variable.
  std::vector<const VariableValue *> _occupancy_concentrations;
  /// Physical occupancy weight associated with each trapped concentration.
  std::vector<Real> _occupancy_weights;
  /// Variable numbers corresponding to occupancy concentrations plus the mobile concentration.
  std::vector<unsigned int> _var_numbers;
  /// Most recent node for which the cached Jacobian state was assembled.
  const Node * _last_node;
  /// Coupled temperature field.
  const VariableValue & _temperature;
  /// Variable number of the coupled temperature (for the analytic temperature Jacobian).
  const unsigned int _temperature_var;
  /// Denominator used to scale the residual after empty-site assembly.
  const Real _residual_denominator;
  /// Cached AD residual used to extract diagonal and off-diagonal Jacobian entries.
  LocalDN _jacobian;

private:
  /// Rebuild the cached AD residual when the active node changes.
  void ADHelper();
};
