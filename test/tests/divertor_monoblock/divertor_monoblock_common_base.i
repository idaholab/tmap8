# This input file contains key pieces for the divertor monoblock case.
# It cannot be run on its own and is included in the main input files for all divertor monoblock
# cases. Some input files dependent on this that can be run are:
# - divertor_monoblock.i
# - divertor_monoblock_physics.i
# - divertor_monoblock_physics-single-variable.i
# - steady_state_runner.i
# - shutdown_transient_runner.i
# - elm_transient_runner.i

# Geometry and design
radius_coolant = 0.006 # depends on MOOSE PR 32524  '${units 6.0 mm -> m}'
radius_CuCrZr = 0.0075 #'${units 7.5 mm -> m}'
radius_Cu = 0.0085 # '${units 8.5 mm -> m}'
block_size = 0.028 # depends on MOOSE PR 32524 '${units 28.0 mm -> m}'
num_sectors = 36 # (-) defines mesh size
rings_H2O = 1 # (-)
rings_CuCrZr = 30 # (-)
rings_Cu = 20 # (-)
rings_W = 110 # (-)

# Operation conditions
plasma_ramp_time = '${units 100.0 s}'
plasma_ss_duration = '${units 400.0 s}'
plasma_cycle_time = '${units 1600.0 s}'
plasma_ss_end = '${fparse plasma_ramp_time + plasma_ss_duration}'
plasma_ramp_down_end = '${fparse plasma_ramp_time + plasma_ss_duration + plasma_ramp_time}'

temperature_initial = '${units 300.0 K}'
temperature_coolant_max = '${units 552.0 K}'

plasma_max_heat = '${units 1.0e7 W/m^2}' # Heat flux of 10 MW/m^2 at steady state
plasma_min_heat = '${units 0.0 W/m^2}' # no flux while the pulse is off.

# Initial conditions
C_trapping_init = 1.0e-15 # at.fraction

# Materials properties - W
tungsten_atomic_density = '${units 6.338e28 atoms/m^3}'
density_W = '${units 19300 kg/m^3}'
N_W = '${fparse tungsten_atomic_density / tungsten_atomic_density}' # usually in atoms/m^3, but here normalized by tungsten_atomic_density
Ct0_W = 1.0e-4 # at.fraction - E.A. Hodille et al 2021 Nucl. Fusion 61 1260033, trap 2 (same as trap 1)
trap_per_free_W = 1.0e0 # (-)
alpha_t = '${units 2.75e11 s}' # same for all materials
trapping_energy = '${units 0 K}' # same for all materials
alpha_r = '${units 8.4e12 s}' # same for all materials
detrapping_energy_W = '${units 11604.6 K}' # = 1.00 eV    E.A. Hodille et al 2021 Nucl. Fusion 61 126003, trap 2
# detrapping_energy_W = ${units 9863.9 K} # = 0.85 eV    E.A. Hodille et al 2021 Nucl. Fusion 61 126003, trap 1
# H diffusivity in W
diffusivity_W_D0 = '${units 2.4e-7 m^2/s}'
diffusivity_W_Ea = '${units 4525.8 K}'
# H solubility in W
solubility_W_1_D0 = '${units 2.95e-5 1/Pa^0.5}' # (1.87e24)/(tungsten_atomic_density) 1/m^3/Pa^(1/2) / (1/m^3) = 1/Pa^(1/2)
solubility_W_1_Ea = '${units 12069.0 K}'
solubility_W_2_D0 = '${units 4.95e-8 1/Pa^0.5}' # (3.14e20)/(tungsten_atomic_density) 1/m^3/Pa^(1/2) / (1/m^3) = 1/Pa^(1/2)
solubility_W_2_Ea = '${units 6614.6 K}'

# Materials properties - Cu
density_Cu = '${units 8960.0 kg/m^3}'
N_Cu = 1.0e0 # usually in atoms/m^3, but here normalized by material's atomic density
Ct0_Cu = 5.0e-5 # at.fraction - R. Delaporte-Mathurin et al 2021 Nucl. Fusion 61 036038, trap 3
trap_per_free_Cu = 1.0e0 # (-)
detrapping_energy_Cu = '${units 5802.3 K}' # = 0.50eV  R. Delaporte-Mathurin et al 2021 Nucl. Fusion 61 036038, trap 3
# H diffusivity in Cu
diffusivity_Cu_D0 = '${units 6.60e-7 m^2/s}'
diffusivity_Cu_Ea = '${units 4525.8 K}'
# H solubility in Cu
solubility_Cu_D0 = '${units 4.95e-5 1/Pa^0.5}' # ${fparse 3.14e24 / tungsten_atomic_density} 1/m^3/Pa^(1/2) / (1/m^3) = 1/Pa^(1/2)
solubility_Cu_Ea = '${units 6614.6 K}'

# Materials properties - CuCrZr
density_CuCrZr = '${units 8900.0 kg/m^3}'
specific_heat_CuCrZr = '${units 390.0 J/kg/K}'
N_CuCrZr = 1.0e0 # usually in atoms/m^3, but here normalized by material's atomic density
Ct0_CuCrZr = 5.0e-5 # at.fraction - R. Delaporte-Mathurin et al 2021 Nucl. Fusion 61 036038, trap 4
# Ct0_CuCrZr = 4.0e-2 # at.fraction - R. Delaporte-Mathurin et al 2021 Nucl. Fusion 61 036038, trap 5
trap_per_free_CuCrZr = 1.0e0 # (-)
detrapping_energy_CuCrZr = '${units 5802.3 K}' # = 0.50eV  R. Delaporte-Mathurin et al 2021 Nucl. Fusion 61 036038, trap 4
# detrapping_energy_CuCrZr = ${units 9631.8 K} # = 0.83 eV  R. Delaporte-Mathurin et al 2021 Nucl. Fusion 61 036038, trap 5
# H diffusivity in CuCrZr
diffusivity_CuCrZr_D0 = '${units 3.90e-7 m^2/s}'
diffusivity_CuCrZr_Ea = '${units 4873.9 K}'
# H solubility in CuCrZr
solubility_CuCrZr_D0 = '${units 6.75e-6 1/Pa^0.5}' # ${fparse 4.28e23 / tungsten_atomic_density} 1/m^3/Pa^(1/2) / (1/m^3) = 1/Pa^(1/2)
solubility_CuCrZr_Ea = '${units 4525.8 K}'

# Maximum retained tritium surface flux at the top surface during operation.
# plasma flux at steady state
plasma_max_flux = ${units 1.0e24 at/m^2/s}
# 50% of it corresponds to tritium in a DT plasma
plasma_max_t_flux = ${fparse 50 / 100 * plasma_max_flux}
# Assuming 0.1% of incident tritium is retained in the divertor, leading to a retained tritium surface flux of 5.0e20 at/m^2/s
plasma_max_retained_t_flux = ${fparse 0.1 / 100 * plasma_max_t_flux}
# For the normalized atomic-fraction variable used here, the equivalent Neumann flux is J / N_W = 7.89e-9 m/s
plasma_max_retained_t_surface_flux = '${fparse plasma_max_retained_t_flux / tungsten_atomic_density}' # normalized surface flux (m/s)
plasma_min_retained_t_surface_flux = '${units 0.0 m/s}'

# For postprocessor scaling
diffusivity_fixed = '${units 5.01e-24 g/m^2}' # (3.01604928)/(6.02e23)/[gram(T)/m^2]
# diffusivity_fixed = ${units 5.508e-19 g/m^2}  # (1.0e3)*(1.0e3)/(6.02e23)/(3.01604928) [gram(T)/m^2] alternative
scaling_factor = '${units 3.491e10 g/m^2}' # (1.0e3)*(1.0e3)*(${tungsten_atomic_density})/(6.02e23)/(3.01604928) [gram(T)/m^2]
scaling_factor_2 = '${units 3.44e10 g/m^2}' # (1.0e3)*(1.0e3)*(${tungsten_atomic_density})/(6.02e23)/(3.01604928) [gram(T)/m^2]

[Functions]
  [t_in_cycle]
    type = ParsedFunction
    expression = 't % ${plasma_cycle_time}'
  []
  # pulse between 0 and 1 following the plasma operation
  [pulse_time_function]
    type = ParsedFunction
    symbol_values = 't_in_cycle'
    symbol_names = 't_in_cycle'
    expression = 'if(t_in_cycle < ${plasma_ramp_time}, t_in_cycle/${plasma_ramp_time},
                        if(t_in_cycle < ${plasma_ss_end}, 1,
                        if(t_in_cycle < ${plasma_ramp_down_end}, 1 - (t_in_cycle-${plasma_ss_end})/${plasma_ramp_time}, 0.0)))'
  []
  [retained_t_surface_flux_function]
    type = ParsedFunction
    symbol_values = 'pulse_time_function'
    symbol_names = 'pulse_time_function'
    expression = '(${plasma_max_retained_t_surface_flux} - ${plasma_min_retained_t_surface_flux}) * pulse_time_function + ${plasma_min_retained_t_surface_flux}'
  []
  [temperature_flux_bc_function]
    type = ParsedFunction
    symbol_values = 'pulse_time_function'
    symbol_names = 'pulse_time_function'
    expression = '(${plasma_max_heat} - ${plasma_min_heat}) * pulse_time_function + ${plasma_min_heat}'
  []
  [temperature_inner_function]
    type = ParsedFunction
    symbol_values = 'pulse_time_function'
    symbol_names = 'pulse_time_function'
    expression = '(${temperature_coolant_max} - ${temperature_initial}) * pulse_time_function + ${temperature_initial}'
  []
  [timestep_function]
    type = ParsedFunction
    symbol_values = 't_in_cycle'
    symbol_names = 't_in_cycle'
    expression = 'if(t_in_cycle < ${fparse 0.1 * plasma_ramp_time}   ,  20,
                      if(t_in_cycle < ${fparse 0.9 * plasma_ramp_time}   ,  40,
                      if(t_in_cycle < ${fparse 1.1 * plasma_ramp_time}   ,  20,
                      if(t_in_cycle < ${fparse plasma_ss_end - 20}       ,  40,
                      if(t_in_cycle < ${plasma_ss_end}                   ,  20,
                      if(t_in_cycle < ${fparse plasma_ramp_down_end - 10},   4,
                      if(t_in_cycle < ${fparse plasma_ramp_down_end + 10},  20,
                      if(t_in_cycle < ${fparse plasma_cycle_time - 100}  , 200,
                      if(t_in_cycle < ${plasma_cycle_time}               ,  40,  2)))))))))'
  []
[]

[AuxVariables]
  [flux_y]
    order = FIRST
    family = MONOMIAL
  []
  ############################## AuxVariables for W (block = 4)
  [Sc_C_mobile_W]
    block = 4
  []
  [Sc_C_trapped_W]
    block = 4
  []
  [C_total_W]
    block = 4
  []
  [Sc_C_total_W]
    block = 4
  []
  [S_empty_W]
    block = 4
  []
  [Sc_S_empty_W]
    block = 4
  []
  [S_trapped_W]
    block = 4
  []
  [Sc_S_trapped_W]
    block = 4
  []
  [S_total_W]
    block = 4
  []
  [Sc_S_total_W]
    block = 4
  []
  ############################## AuxVariables for Cu (block = 3)
  [Sc_C_mobile_Cu]
    block = 3
  []
  [Sc_C_trapped_Cu]
    block = 3
  []
  [C_total_Cu]
    block = 3
  []
  [Sc_C_total_Cu]
    block = 3
  []
  [S_empty_Cu]
    block = 3
  []
  [Sc_S_empty_Cu]
    block = 3
  []
  [S_trapped_Cu]
    block = 3
  []
  [Sc_S_trapped_Cu]
    block = 3
  []
  [S_total_Cu]
    block = 3
  []
  [Sc_S_total_Cu]
    block = 3
  []
  ############################## AuxVariables for CuCrZr (block = 2)
  [Sc_C_mobile_CuCrZr]
    block = 2
  []
  [Sc_C_trapped_CuCrZr]
    block = 2
  []
  [C_total_CuCrZr]
    block = 2
  []
  [Sc_C_total_CuCrZr]
    block = 2
  []
  [S_empty_CuCrZr]
    block = 2
  []
  [Sc_S_empty_CuCrZr]
    block = 2
  []
  [S_trapped_CuCrZr]
    block = 2
  []
  [Sc_S_trapped_CuCrZr]
    block = 2
  []
  [S_total_CuCrZr]
    block = 2
  []
  [Sc_S_total_CuCrZr]
    block = 2
  []
[]

[Preconditioning]
  [smp]
    type = SMP
    full = true
  []
[]

[Executioner]
  type = Transient
  scheme = bdf2
  solve_type = NEWTON
  petsc_options_iname = '-pc_type -pc_factor_shift_type'
  petsc_options_value = 'lu NONZERO'
  nl_rel_tol = 1e-6 # 1e-8 works for 1 cycle
  nl_abs_tol = 1e-7 # 1e-11 works for 1 cycle
  end_time = '${fparse 50 * plasma_cycle_time}' # 50 ITER shots
  automatic_scaling = true
  line_search = 'none'
  dtmin = 1e-4
  nl_max_its = 18
  [TimeStepper]
    type = IterationAdaptiveDT
    dt = 20
    optimal_iterations = 15
    iteration_window = 1
    growth_factor = 1.2
    cutback_factor = 0.8
    timestep_limiting_postprocessor = timestep_max_pp
  []
[]
