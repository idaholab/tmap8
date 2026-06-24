### This input file contains everything necessary for the divertor monoblock
### case that is not used in the physics-based inputs
### M. Shimada, P.-C. A. Simon, C. T. Icenhour, and G. Singh, “Toward a high-fidelity
### tritium transport modeling for retention and permeation experiments,” Fusion
### Engineering and Design, Volume 203, 2024, 114438, ISSN 0920-3796,
### https://doi.org/10.1016/j.fusengdes.2024.114438.

### This input uses the `!include` feature to incorporate other input files
### Nomenclatures
### C_mobile_j      mobile H concentration in "j" material, where j = CuCrZr, Cu, W
### C_trapped_j     trapped H concentration in "j" material, where j = CuCrZr, Cu, W
### C_total_j       total H concentration in "j" material, where j = CuCrZr, Cu, W
###
### Sc_             Scaled
### Int_            Integrated
### ScInt_          Scaled and integrated

C_mobile_CuCrZr_DirichletBC_Coolant = 1.0e-18 # at.fraction
C_mobile_W_init = 1.0e-20 # at.fraction
C_mobile_Cu_init = 5.0e-17 # at.fraction
C_mobile_CuCrZr_init = 1.0e-15 # at.fraction

!include divertor_monoblock_mesh_base.i
!include divertor_monoblock_common_base.i
!include divertor_monoblock_multi_variable_base.i

[Functions]
  [temperature_steady_state]
    type = ParsedFunction
    expression = "-1.59786e4*x^2  -1.11629611e4*x + 4.84297313e2 + 1.9491599e6*y^2 + 1.55723201e4*y "
                 "- 7.312884e5*x*y"
  []
[]

[Postprocessors]
  [Tritium_SideFluxIntegral]
    type = SideDiffusiveFluxIntegral
    boundary = '2to1'
    diffusivity = diffusivity_CuCrZr_nonAD
    variable = Sc_C_total_CuCrZr
    execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
  []
  [Scaled_Tritium_Flux]
    type = ParsedPostprocessor
    expression = '5.01e-24 * Tritium_SideFluxIntegral'
    pp_names = Tritium_SideFluxIntegral
    execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
  []
  [coolant_heat_flux]
    # units of W/m2
    type = SideDiffusiveFluxAverage
    boundary = '2to1'
    diffusivity = thermal_conductivity_CuCrZr
    variable = temperature
    execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
  []
  [max_temperature_W]
    type = ElementExtremeValue
    block = 4
    variable = 'temperature'
    value_type = max
    execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
  []
  [max_temperature_Cu]
    type = ElementExtremeValue
    block = 3
    variable = 'temperature'
    value_type = max
    execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
  []
  [max_temperature_CuCrZr]
    type = ElementExtremeValue
    block = 2
    variable = 'temperature'
    value_type = max
    execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
  []
  [avg_temperature_W]
    type = ElementAverageValue
    variable = temperature
    block = 4
    execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
  []
  [avg_temperature_Cu]
    type = ElementAverageValue
    variable = temperature
    block = 3
    execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
  []
  [avg_temperature_CuCrZr]
    type = ElementAverageValue
    variable = temperature
    block = 2
    execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
  []
  [max_concentration_W]
    type = ElementExtremeValue
    variable = 'C_total_W'
    value_type = max
    block = 4
    execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
  []
  [max_concentration_Cu]
    type = ElementExtremeValue
    variable = 'C_total_Cu'
    value_type = max
    block = 3
    execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
  []
  [max_concentration_CuCrZr]
    type = ElementExtremeValue
    variable = 'C_total_CuCrZr'
    value_type = max
    block = 2
    execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
  []
  [area_W]
    type = VolumePostprocessor
    block = 4
    execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
  []
  [area_Cu]
    type = VolumePostprocessor
    block = 3
    execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
  []
  [area_CuCrZr]
    type = VolumePostprocessor
    block = 2
    execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
  []
  [total_retention]
    type = SumPostprocessor
    values = 'ScInt_C_total_W ScInt_C_total_Cu ScInt_C_total_CuCrZr'
    execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
  []

  # TMAP8 will give an error if the parser does not find a use for defined parameters
  # It also seems that the parser does not deal well with multiple layers of includes,
  # so the definitions of the mesh parameters need to have a use somewhere in this input file
  # This is a dummy postprocessor that is used to satisfy the parser for known terms.
  [unused_parameters]
    type = ParsedPostprocessor
    expression = '${num_sectors} + ${rings_H2O} + ${rings_CuCrZr} + ${rings_Cu} + ${rings_W}'
    enable = False
    outputs = ''
  []
[]

[Problem]
  type = ReferenceResidualProblem
  extra_tag_vectors = 'ref'
  reference_vector = 'ref'
[]

[Variables]
  [temperature]
    order = FIRST
    family = LAGRANGE
  []
  ######################### Variables for W (block = 4)
  [C_mobile_W]
    order = FIRST
    family = LAGRANGE
    initial_condition = ${C_mobile_W_init}
    block = 4
  []
  [C_trapped_W]
    order = FIRST
    family = LAGRANGE
    initial_condition = ${C_trapping_init}
    block = 4
  []
  ######################### Variables for Cu (block = 3)
  [C_mobile_Cu]
    order = FIRST
    family = LAGRANGE
    initial_condition = ${C_mobile_Cu_init}
    block = 3
  []
  [C_trapped_Cu]
    order = FIRST
    family = LAGRANGE
    initial_condition = ${C_trapping_init}
    block = 3
  []
  ######################### Variables for CuCrZr (block = 2)
  [C_mobile_CuCrZr]
    order = FIRST
    family = LAGRANGE
    initial_condition = ${C_mobile_CuCrZr_init}
    block = 2
  []
  [C_trapped_CuCrZr]
    order = FIRST
    family = LAGRANGE
    initial_condition = ${C_trapping_init}
    block = 2
  []
[]

[Kernels]
  ############################## Kernels for W (block = 4)
  [diff_W]
    type = ADMatDiffusion
    variable = C_mobile_W
    diffusivity = diffusivity_W
    block = 4
    extra_vector_tags = ref
  []
  [time_diff_W]
    type = ADTimeDerivative
    variable = C_mobile_W
    block = 4
    extra_vector_tags = ref
  []
  [coupled_time_W]
    type = ScaledCoupledTimeDerivative
    variable = C_mobile_W
    v = C_trapped_W
    block = 4
    extra_vector_tags = ref
  []
  [heat_conduction_W]
    type = HeatConduction
    variable = temperature
    thermal_conductivity = thermal_conductivity_W
    block = 4
    extra_vector_tags = ref
  []
  [time_heat_conduction_W]
    type = SpecificHeatConductionTimeDerivative
    variable = temperature
    specific_heat = specific_heat_W
    density = density_W
    block = 4
    extra_vector_tags = ref
  []
  ############################## Kernels for Cu (block = 3)
  [diff_Cu]
    type = ADMatDiffusion
    variable = C_mobile_Cu
    diffusivity = diffusivity_Cu
    block = 3
    extra_vector_tags = ref
  []
  [time_diff_Cu]
    type = ADTimeDerivative
    variable = C_mobile_Cu
    block = 3
    extra_vector_tags = ref
  []
  [coupled_time_Cu]
    type = ScaledCoupledTimeDerivative
    variable = C_mobile_Cu
    v = C_trapped_Cu
    block = 3
    extra_vector_tags = ref
  []
  [heat_conduction_Cu]
    type = HeatConduction
    variable = temperature
    thermal_conductivity = thermal_conductivity_Cu
    block = 3
    extra_vector_tags = ref
  []
  [time_heat_conduction_Cu]
    type = SpecificHeatConductionTimeDerivative
    variable = temperature
    specific_heat = specific_heat_Cu
    density = density_Cu
    block = 3
    extra_vector_tags = ref
  []
  ############################## Kernels for CuCrZr (block = 2)
  [diff_CuCrZr]
    type = ADMatDiffusion
    variable = C_mobile_CuCrZr
    diffusivity = diffusivity_CuCrZr
    block = 2
    extra_vector_tags = ref
  []
  [time_diff_CuCrZr]
    type = ADTimeDerivative
    variable = C_mobile_CuCrZr
    block = 2
    extra_vector_tags = ref
  []
  [coupled_time_CuCrZr]
    type = ScaledCoupledTimeDerivative
    variable = C_mobile_CuCrZr
    v = C_trapped_CuCrZr
    block = 2
    extra_vector_tags = ref
  []
  [heat_conduction_CuCrZr]
    type = HeatConduction
    variable = temperature
    thermal_conductivity = thermal_conductivity_CuCrZr
    block = 2
    extra_vector_tags = ref
  []
  [time_heat_conduction_CuCrZr]
    type = SpecificHeatConductionTimeDerivative
    variable = temperature
    specific_heat = specific_heat_CuCrZr
    density = density_CuCrZr
    block = 2
    extra_vector_tags = ref
  []
[]

[InterfaceKernels]
  [tied_4to3]
    type = ADPenaltyInterfaceDiffusion
    variable = C_mobile_W
    neighbor_var = C_mobile_Cu
    penalty = 0.05 #  it will not converge with > 0.1, but it creates negative C_mobile _Cu with << 0.1
    # jump_prop_name = solubility_ratio_4to3
    jump_prop_name = solubility_ratio
    boundary = '4to3'
  []
  [tied_3to2]
    type = ADPenaltyInterfaceDiffusion
    variable = C_mobile_Cu
    neighbor_var = C_mobile_CuCrZr
    penalty = 0.05 #  it will not converge with > 0.1, but it creates negative C_mobile _Cu with << 0.1
    # jump_prop_name = solubility_ratio_3to2
    jump_prop_name = solubility_ratio
    boundary = '3to2'
  []
[]

[NodalKernels]
  ############################## NodalKernels for W (block = 4)
  [time_W]
    type = TimeDerivativeNodalKernel
    variable = C_trapped_W
  []
  [trapping_W]
    type = TrappingNodalKernel
    variable = C_trapped_W
    temperature = temperature
    alpha_t = ${alpha_t}
    N = ${N_W}
    Ct0 = ${Ct0_W}
    trapping_energy = ${trapping_energy}
    trap_per_free = ${trap_per_free_W}
    mobile_concentration = 'C_mobile_W'
    extra_vector_tags = ref
  []
  [release_W]
    type = ReleasingNodalKernel
    alpha_r = ${alpha_r}
    temperature = temperature
    detrapping_energy = ${detrapping_energy_W}
    variable = C_trapped_W
  []
  ############################## NodalKernels for Cu (block = 3)
  [time_Cu]
    type = TimeDerivativeNodalKernel
    variable = C_trapped_Cu
  []
  [trapping_Cu]
    type = TrappingNodalKernel
    variable = C_trapped_Cu
    temperature = temperature
    alpha_t = ${alpha_t}
    N = ${N_Cu}
    Ct0 = ${Ct0_Cu}
    trapping_energy = ${trapping_energy}
    trap_per_free = ${trap_per_free_Cu}
    mobile_concentration = 'C_mobile_Cu'
    extra_vector_tags = ref
  []
  [release_Cu]
    type = ReleasingNodalKernel
    alpha_r = ${alpha_r}
    temperature = temperature
    detrapping_energy = ${detrapping_energy_Cu}
    variable = C_trapped_Cu
  []
  ############################## NodalKernels for CuCrZr (block = 2)
  [time_CuCrZr]
    type = TimeDerivativeNodalKernel
    variable = C_trapped_CuCrZr
  []
  [trapping_CuCrZr]
    type = TrappingNodalKernel
    variable = C_trapped_CuCrZr
    temperature = temperature
    alpha_t = ${alpha_t}
    N = ${N_CuCrZr}
    Ct0 = ${Ct0_CuCrZr}
    trapping_energy = ${trapping_energy}
    trap_per_free = ${trap_per_free_CuCrZr}
    mobile_concentration = 'C_mobile_CuCrZr'
    extra_vector_tags = ref
  []
  [release_CuCrZr]
    type = ReleasingNodalKernel
    alpha_r = ${alpha_r}
    temperature = temperature
    detrapping_energy = ${detrapping_energy_CuCrZr}
    variable = C_trapped_CuCrZr
  []
[]

[BCs]
  [C_mob_W_top_flux]
    type = FunctionNeumannBC
    variable = C_mobile_W
    boundary = 'top'
    function = mobile_flux_bc_function
  []
  [mobile_tube]
    type = DirichletBC
    variable = C_mobile_CuCrZr
    value = ${C_mobile_CuCrZr_DirichletBC_Coolant}
    boundary = '2to1'
  []
  [temperature_top]
    type = FunctionNeumannBC
    variable = temperature
    boundary = 'top'
    function = temperature_flux_bc_function
  []
  [temperature_tube]
    type = FunctionDirichletBC
    variable = temperature
    boundary = '2to1'
    function = temperature_inner_function
  []
[]

[Materials]
  ############################## Materials for W (block = 4)
  [diffusivity_W]
    type = ADParsedMaterial
    property_name = diffusivity_W
    coupled_variables = 'temperature'
    block = 4
    expression = '${diffusivity_W_D0}*exp(-${diffusivity_W_Ea}/temperature)'
    outputs = all
  []
  [solubility_W]
    type = ADParsedMaterial
    property_name = solubility_W
    coupled_variables = 'temperature'
    block = 4
    expression = '${solubility_W_1_D0}*exp(-${solubility_W_1_Ea}/temperature) + ${solubility_W_2_D0}*exp(-${solubility_W_2_Ea}/temperature)'
    outputs = all
  []
  [converter_to_regular_W]
    type = MaterialADConverter
    ad_props_in = 'diffusivity_W'
    reg_props_out = 'diffusivity_W_nonAD'
    block = 4
  []
  [heat_transfer_W]
    type = GenericConstantMaterial
    prop_names = 'density_W'
    prop_values = '${density_W}'
    block = 4
  []
  [specific_heat_W]
    type = ParsedMaterial
    property_name = specific_heat_W
    coupled_variables = 'temperature'
    block = 4
    expression = '1.16e2 + 7.11e-2 * temperature - 6.58e-5 * temperature^2 + 3.24e-8 * temperature^3 -5.45e-12 * temperature^4' # [J/kg-K]
    outputs = all
  []
  [thermal_conductivity_W]
    type = ParsedMaterial
    property_name = thermal_conductivity_W
    coupled_variables = 'temperature'
    block = 4
    expression = '2.41e2 - 2.90e-1 * temperature + 2.54e-4 * temperature^2 - 1.03e-7 * temperature^3 + 1.52e-11 * temperature^4' # [W/m-K]
    outputs = all
  []
  ############################## Materials for Cu (block = 3)
  [diffusivity_Cu]
    type = ADParsedMaterial
    property_name = diffusivity_Cu
    coupled_variables = 'temperature'
    block = 3
    expression = '${diffusivity_Cu_D0}*exp(-${diffusivity_Cu_Ea}/temperature)'
    outputs = all
  []
  [solubility_Cu]
    type = ADParsedMaterial
    property_name = solubility_Cu
    coupled_variables = 'temperature'
    block = 3
    expression = '${solubility_Cu_D0}*exp(-${solubility_Cu_Ea}/temperature)'
    outputs = all
  []
  [converter_to_regular_Cu]
    type = MaterialADConverter
    ad_props_in = 'diffusivity_Cu'
    reg_props_out = 'diffusivity_Cu_nonAD'
    block = 3
  []
  [heat_transfer_Cu]
    type = GenericConstantMaterial
    prop_names = 'density_Cu'
    prop_values = '${density_Cu}'
    block = 3
  []
  [specific_heat_Cu]
    type = ParsedMaterial
    property_name = specific_heat_Cu
    coupled_variables = 'temperature'
    block = 3
    expression = '3.16e2 + 3.18e-1 * temperature - 3.49e-4 * temperature^2 + 1.66e-7 * temperature^3' # [J/kg-K]
    outputs = all
  []
  [thermal_conductivity_Cu]
    type = ParsedMaterial
    property_name = thermal_conductivity_Cu
    coupled_variables = 'temperature'
    block = 3
    # expression = '-3.9e-8 * temperature^3 + 3.8e-5 * temperature^2 - 7.9e-2 * temperature + 4.0e2'    # ~ 401.0  [ W/m-K] from R. Delaporte-Mathurin et al 2021 Nucl. Fusion 61 036038,
    expression = '4.21e2 - 6.85e-2 * temperature' # [W/m-K]
    outputs = all
  []
  ############################## Materials for CuCrZr (block = 2)
  [diffusivity_CuCrZr]
    type = ADParsedMaterial
    property_name = diffusivity_CuCrZr
    coupled_variables = 'temperature'
    block = 2
    expression = '${diffusivity_CuCrZr_D0}*exp(-${diffusivity_CuCrZr_Ea}/temperature)'
    outputs = all
  []
  [solubility_CuCrZr]
    type = ADParsedMaterial
    property_name = solubility_CuCrZr
    coupled_variables = 'temperature'
    block = 2
    expression = '${solubility_CuCrZr_D0}*exp(-${solubility_CuCrZr_Ea}/temperature)'
    outputs = all
  []
  [converter_to_regular_CuCrZr]
    type = MaterialADConverter
    ad_props_in = 'diffusivity_CuCrZr'
    reg_props_out = 'diffusivity_CuCrZr_nonAD'
    block = 2
  []
  [heat_transfer_CuCrZr]
    type = GenericConstantMaterial
    prop_names = 'density_CuCrZr specific_heat_CuCrZr'
    prop_values = '${density_CuCrZr} ${specific_heat_CuCrZr}'
    block = 2
  []
  [thermal_conductivity_CuCrZr]
    type = ParsedMaterial
    property_name = thermal_conductivity_CuCrZr
    coupled_variables = 'temperature'
    block = 2
    expression = '3.87e2 - 1.28e-1 * temperature' # [W/m-K]
    outputs = all
  []
  ############################## Materials for others
  [interface_jump_4to3]
    type = SolubilityRatioMaterial
    solubility_primary = solubility_W
    solubility_secondary = solubility_Cu
    boundary = '4to3'
    concentration_primary = C_mobile_W
    concentration_secondary = C_mobile_Cu
  []
  [interface_jump_3to2]
    type = SolubilityRatioMaterial
    solubility_primary = solubility_Cu
    solubility_secondary = solubility_CuCrZr
    boundary = '3to2'
    concentration_primary = C_mobile_Cu
    concentration_secondary = C_mobile_CuCrZr
  []
[]
