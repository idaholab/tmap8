### This case extends the published divertor monoblock input file to simulate an
### Edge-Localized Mode transient, with some simplifying assumptions that allow it
### to be run in a short amount of time.
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
### F_permeation    permeation flux
### F_recombination recombination flux
###
### Sc_             Scaled
### Int_            Integrated
### ScInt_          Scaled and integrated

!include divertor_monoblock_explicit_base.i
base_power = 10e6 # ${units 10 MW/m^2 -> W/m^2}
coolant_temperature = ${units 552 K}
elm_value = ${units 1147 MW/m^2 -> W/m^2}
elm_duration = ${units 1.32 ms -> s}
W_cond_factor = 1.0

# scales the BCs bases on the new base power
Functions/retained_t_surface_flux_function/expression := "if(t<2e2, (${base_power}*${plasma_max_retained_t_surface_flux}/${plasma_max_heat}),
if(t<(2e2+${elm_duration}*1/3),
(${base_power}*${plasma_max_retained_t_surface_flux}/${plasma_max_heat})+(t-2e2)/(${elm_duration}*1/3)*((${elm_value}*${plasma_max_retained_t_surface_flux}/${plasma_max_heat})-(${base_power}*${plasma_max_retained_t_surface_flux}/${plasma_max_heat})),
if(t<(2e2+(${elm_duration}*1/3)+(${elm_duration}*2/3)),
(${elm_value}*${plasma_max_retained_t_surface_flux}/${plasma_max_heat})-(t-2e2-(${elm_duration}*1/3))/(${elm_duration}*2/3)*((${elm_value}*${plasma_max_retained_t_surface_flux}/${plasma_max_heat})-(${base_power}*${plasma_max_retained_t_surface_flux}/${plasma_max_heat})), (${base_power}*${plasma_max_retained_t_surface_flux}/${plasma_max_heat}))))"
Functions/temperature_inner_function/expression := "${coolant_temperature}"
Executioner/petsc_options_iname := '-pc_type'
Executioner/petsc_options_value := 'lu'
Executioner/nl_rel_tol := 1e-5
Executioner/nl_abs_tol := 1e-6
Executioner/end_time := 2.01e2
Executioner/dtmin := 1e-6
Executioner/nl_max_its := 36
Executioner/TimeStepper/dt := 125
Executioner/TimeStepper/growth_factor := 2.0

[Executioner]
  [TimeStepper]
    time_t = '0 2e2 2.01e2'
    time_dt = '100 0.0001 100'
  []
  error_on_dtmin = False
[]

Postprocessors/F_recombination/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
Postprocessors/F_permeation/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
Postprocessors/Int_C_mobile_W/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
Postprocessors/ScInt_C_mobile_W/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
Postprocessors/Int_C_trapped_W/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
Postprocessors/Int_C_total_W/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
Postprocessors/Int_C_mobile_Cu/execute_on = 'MULTIAPP_FIXED_POINT_END FINAL'
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
# There is a lot of overlap with the divertor monoblock case, but the terms defined there for the temperature profile and tritium flux are unused here.
# Add them to the dummy postprocessor so the parser does not complain.
Postprocessors/unused_parameters/expression := '${plasma_max_retained_t_surface_flux} + ${plasma_min_retained_t_surface_flux} + ${temperature_initial} + ${temperature_coolant_max} + ${num_sectors}
 + ${rings_H2O} + ${rings_CuCrZr} + ${rings_Cu} + ${rings_W}'

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
Materials/thermal_conductivity_W/expression := '${W_cond_factor}*(2.41e2 - 2.90e-1 * temperature + 2.54e-4 * temperature^2 - 1.03e-7 * temperature^3 + 1.52e-11 * temperature^4)'

[Outputs]
  execute_on = 'none'
[]


[ICs]
  [temperature_ic]
    type = FunctionIC
    function = temperature_steady_state
    variable = temperature
  []
[]
