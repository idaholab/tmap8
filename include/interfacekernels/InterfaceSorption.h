/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2025 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#pragma once

#include "InterfaceKernel.h"
#include "ADInterfaceKernel.h"

// switch parent class depending on is_ad value
template <bool is_ad>
using InterfaceKernelParent =
    typename std::conditional<is_ad, ADInterfaceKernel, InterfaceKernel>::type;

/**
 * This interface kernel computes a sorption law at interface between solid and gas in isothermal
 * conditions
 */
template <bool is_ad>
class InterfaceSorptionTempl : public InterfaceKernelParent<is_ad>
{
public:
  static InputParameters validParams();
  InterfaceSorptionTempl(const InputParameters & parameters);

protected:
  virtual GenericReal<is_ad> computeQpResidual(Moose::DGResidualType type) override;
  virtual Real computeQpJacobian(Moose::DGJacobianType type) override;

  ///@{Coefficients of the Arrhenius law for the solubility of the metal solubility = K = K0exp(-Ea/RT)
  const Real _K0;
  const Real _Ea;
  ///@}

  /// Exponent of the sorption law
  const Real & _n_sorption;

  ///@{Unit conversion factors used to scale the concentrations
  const Real & _unit_scale;
  const Real & _unit_scale_neighbor; // neighbor corresponds to the gas
  ///@}

  ///@{Coupled temperature variables
  const GenericVariableValue<is_ad> & _T;
  ///@}

  /// Whether to enforce the sorption law in its inverted form, C_i = (C_s / K)^(1/n) / (R T)
  const bool _use_inverted_sorption;

  /// Penalty associated with the concentration imbalance
  const Real _sorption_penalty;

  /// Whether to use the penalty formulation to enforce the flux balance
  const bool _use_flux_penalty;

  /// Penalty associated with the flux balance
  const Real _flux_penalty;

  ///@{The diffusion coefficients
  const GenericMaterialProperty<Real, is_ad> & _diffusivity;
  const GenericMaterialProperty<Real, is_ad> * _diffusivity_neighbor;
  ///@}

  ///@{Retrieve parent members
  using InterfaceKernelParent<is_ad>::_u;
  using InterfaceKernelParent<is_ad>::_qp;
  using InterfaceKernelParent<is_ad>::_neighbor_value;
  using InterfaceKernelParent<is_ad>::_test;
  using InterfaceKernelParent<is_ad>::_test_neighbor;
  using InterfaceKernelParent<is_ad>::_i;
  using InterfaceKernelParent<is_ad>::_normals;
  using InterfaceKernelParent<is_ad>::_grad_u;
  using InterfaceKernelParent<is_ad>::_grad_neighbor_value;
  ///@}
};

using InterfaceSorption = InterfaceSorptionTempl<false>;
using ADInterfaceSorption = InterfaceSorptionTempl<true>;
