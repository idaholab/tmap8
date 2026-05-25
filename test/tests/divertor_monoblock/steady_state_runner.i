### This case adapts the published divertor monoblock input file under steady-state
### conditions, and is used to do a sobol sensitivity analysis of the underlying model
### by running steady_state_sobol.i directly from TMAP8.
### M. Shimada, P.-C. A. Simon, C. T. Icenhour, and G. Singh, “Toward a high-fidelity
### tritium transport modeling for retention and permeation experiments,” Fusion
### Engineering and Design, Volume 203, 2024, 114438, ISSN 0920-3796,
### https://doi.org/10.1016/j.fusengdes.2024.114438.
### Nomenclatures                                                                                  # Nelson S. Comments/Annotations
###
### C_mobile_j      mobile H concentration in "j" material, where j = CuCrZr, Cu, W
### C_trapped_j     trapped H concentration in "j" material, where j = CuCrZr, Cu, W
### C_total_j       total H concentration in "j" material, where j = CuCrZr, Cu, W
###
### F_permeation    permeation flux
### F_recombination recombination flux
###
### Sc_             Scaled
### Int_            Integrated
### ScInt_          Scaled and integrated

temperature_top_val = ${units 10 MW/m^2}
retained_t_surface_flux_val = ${plasma_max_retained_t_surface_flux} # normalized surface flux [m/s]
temperature_tube_val = ${units 552 K}

[Controls]
  [stochastic]
    # Sends data to Stochastic
    type = SamplerReceiver
  []
[]

### This input uses the `!include` feature to incorporate other input files
!include divertor_monoblock_explicit_base.i

# Geometry and design
num_sectors := 12
rings_CuCrZr := 6
rings_Cu := 4
rings_W := 22

Functions/retained_t_surface_flux_function/expression := '${fparse retained_t_surface_flux_val}'
Functions/temperature_flux_bc_function/expression := '${fparse temperature_top_val}'
Functions/temperature_inner_function/expression := '${fparse temperature_tube_val}'
Functions/timestep_function/expression := 'if(t<100, 25, 400)'

Executioner/nl_rel_tol := 1e-2
Executioner/nl_abs_tol := 1e-1
Executioner/end_time := ${fparse plasma_cycle_time + plasma_ss_duration}
Executioner/nl_max_its := 24
Executioner/TimeStepper/growth_factor := 2.0

Postprocessors/F_recombination/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
Postprocessors/F_permeation/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
Postprocessors/Int_C_mobile_W/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
Postprocessors/Int_C_trapped_W/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
Postprocessors/Int_C_total_W/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
Postprocessors/Int_C_mobile_Cu/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
Postprocessors/ScInt_C_mobile_Cu/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
Postprocessors/Int_C_trapped_Cu/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
Postprocessors/ScInt_C_trapped_Cu/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
Postprocessors/Int_C_total_Cu/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
Postprocessors/ScInt_C_total_Cu/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
Postprocessors/Int_C_mobile_CuCrZr/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
Postprocessors/ScInt_C_mobile_CuCrZr/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
Postprocessors/Int_C_trapped_CuCrZr/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
Postprocessors/ScInt_C_trapped_CuCrZr/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
Postprocessors/Int_C_total_CuCrZr/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
Postprocessors/ScInt_C_total_CuCrZr/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
Postprocessors/temperature_top/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
Postprocessors/temperature_tube/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
Postprocessors/timestep_max_pp/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
# Need to add unused parameters from the divertor monoblock case to the dummy postprocessor
Postprocessors/unused_parameters/expression := '${num_sectors} + ${rings_H2O} + ${rings_CuCrZr} + ${rings_Cu} + ${rings_W}
                  + ${temperature_coolant_max} + ${plasma_max_heat} + ${plasma_min_heat}
                  + ${plasma_max_retained_t_surface_flux} + ${plasma_min_retained_t_surface_flux}'

Variables/temperature/initial_condition= ${temperature_initial}

[Outputs]
  # Control outputs, include exodus and csv.
  execute_on = 'none'
[]
