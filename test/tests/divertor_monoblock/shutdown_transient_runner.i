### This case extends the published divertor monoblock input file to simulate a
### shutdown transient, with some simplifying assumptions that allow it
### to be run in a short amount of time.
### M. Shimada, P.-C. A. Simon, C. T. Icenhour, and G. Singh, “Toward a high-fidelity
### tritium transport modeling for retention and permeation experiments,” Fusion
### Engineering and Design, Volume 203, 2024, 114438, ISSN 0920-3796,
### https://doi.org/10.1016/j.fusengdes.2024.114438.

### Nomenclatures
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

### VARIABLES ###
peak_value = ${units 20 MW/m^2 -> W/m^2}
peak_duration = ${units 1.0 s}
coolant_temperature = ${units 552 K}
W_cond_factor = 1.0

!include divertor_monoblock_explicit_base.i

Functions/timestep_function/expression := "if(t<2e4, 500, if(t<(2e4+${peak_duration}+1), 0.10, 500))"
Functions/retained_t_surface_flux_function/expression := "if(t<2e4, ${plasma_max_retained_t_surface_flux}, if(t<(2e4+${peak_duration}), "
                 "${peak_value}/${plasma_max_heat}*${plasma_max_retained_t_surface_flux}, 0.1*${plasma_max_retained_t_surface_flux}))"
Functions/temperature_flux_bc_function/expression := "if(t<2e4, ${plasma_max_heat}, if(t<(2e4+${peak_duration}), ${peak_value}, 0.1*${plasma_max_heat}))"
Functions/temperature_inner_function/expression := ${coolant_temperature}

Functions/temperature_steady_state/expression := "-1.59786e4*x^2  -1.11629611e4*x + 4.84297313e2 + 1.9491599e6*y^2 + 1.55723201e4*y "
                 "- 7.312884e5*x*y"

Executioner/petsc_options_iname := '-pc_type'
Executioner/petsc_options_value := 'lu'
Executioner/nl_rel_tol := 1e-2
Executioner/nl_abs_tol := 1e-1
Executioner/end_time := ${units 2.0002e4 s}
Executioner/TimeStepper/dt := 100
Executioner/dtmin := 1e-6
Executioner/nl_max_its := 36
Executioner/TimeStepper/optimal_iterations := 10
Executioner/TimeStepper/growth_factor := 2.0

[Executioner]
  [TimeStepper]
    time_t = '0 2e4 2.01e4'
    time_dt = '100 0.001 100'
  []
  error_on_dtmin = False
[]

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
# Continue using the steady-state dummy postprocessor, but add unused definitions
# from the steady-state input.
Postprocessors/unused_parameters/expression := '${num_sectors} + ${rings_H2O} + ${rings_CuCrZr} + ${rings_Cu} + ${rings_W} + ${temperature_coolant_max}
                                                + ${plasma_max_heat} + ${plasma_min_heat} + ${plasma_max_retained_t_surface_flux} + ${plasma_min_retained_t_surface_flux}'

[Postprocessors]
  [time_max_T_W]
    type = TimeExtremeValue
    postprocessor = max_temperature_W
    output_type = extreme_value
    value_type = max
    execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
  []
  [time_max_T_Cu]
    type = TimeExtremeValue
    postprocessor = max_temperature_Cu
    output_type = extreme_value
    value_type = max
    execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
  []
  [time_max_T_CuCrZr]
    type = TimeExtremeValue
    postprocessor = max_temperature_CuCrZr
    output_type = extreme_value
    value_type = max
    execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
  []
[]

VectorPostprocessors/line/execute_on := 'NONE'

Variables/temperature/initial_condition := '${temperature_initial}'

Materials/thermal_conductivity_W/expression := '${W_cond_factor}*(2.41e2 - 2.90e-1 * temperature + 2.54e-4 * temperature^2 - 1.03e-7 * temperature^3 + 1.52e-11 * temperature^4)'

[Controls]
  [stochastic]
    # Sends data to Stochastic
    type = SamplerReceiver
  []
[]

[Outputs]
  # Control outputs, include exodus and csv.
  execute_on = 'none'
[]
