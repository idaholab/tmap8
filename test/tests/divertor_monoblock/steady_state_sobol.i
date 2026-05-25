### This input file defines a sobol indice analysis of the monoblock input file to simulate an
### steady-state operation of the ITER divertor monoblock,
### with some simplifying assumptions that allow it
### to be run in a short amount of time.
### The physics input file is steady_state_runner.i
### This file should be called directly by TMAP8, preferably with access to multiple cpus
### Output information including summary statistics can be found in a json file

# Define parameters in one spot for easier reading
upper_heat_flux_lower = ${units 9.5 MW/m^2 -> W/m^2}
upper_heat_flux_upper = ${units 10.5 MW/m^2 -> W/m^2}
upper_tritium_flux_lower = ${units 7.495e-9 m/s} # normalized surface flux
upper_tritium_flux_upper = ${units 8.285e-9 m/s} # normalized surface flux
coolant_temperature_lower = ${units 524.4 K}
coolant_temperature_upper = ${units 579.6 K}
N_samples = 10

[StochasticTools]
  # Designate as the Controller/Main Input
[]

[MultiApps]
  # Designate a subapp to control later
  [runner]
    type = SamplerFullSolveMultiApp
    sampler = sobol
    input_files = 'steady_state_runner.i'
    mode = batch-reset
    keep_full_output_history = True
  []
[]

[Controls]
  # Control inputs from Main->Subapp
  [cmdline]
    type = MultiAppSamplerControl
    multi_app = runner
    sampler = sobol
    param_names = "temperature_top_val
                   retained_t_surface_flux_val
                   temperature_tube_val"
  []
[]

[Distributions]
  # Define probability distributions of parameters for sampling
  [H_top]
    type = Uniform
    lower_bound = ${upper_heat_flux_lower}
    upper_bound = ${upper_heat_flux_upper}
  []
  [C_top]
    type = Uniform
    lower_bound = ${upper_tritium_flux_lower}
    upper_bound = ${upper_tritium_flux_upper}
  []
  [H_bot]
    type = Uniform
    lower_bound = ${coolant_temperature_lower}
    upper_bound = ${coolant_temperature_upper}
  []
[]

[Samplers]
  # Sampling methodology using the probability distributions above
  [hypercube_1]
    type = LatinHypercube
    distributions = 'H_top C_top H_bot'
    num_rows = ${N_samples}
    seed = 1001
    execute_on = 'PRE_MULTIAPP_SETUP'
  []
  [hypercube_2]
    type = LatinHypercube
    distributions = 'H_top C_top H_bot'
    num_rows = ${N_samples}
    seed = 1002
    execute_on = 'PRE_MULTIAPP_SETUP'
  []
  [sobol]
    type = Sobol
    sampler_a = hypercube_1
    sampler_b = hypercube_2
    execute_on = 'PRE_MULTIAPP_SETUP'
  []
[]

[Transfers]
  # Define values to extract from subapp
  [results]
    type = SamplerReporterTransfer
    from_multi_app = runner
    sampler = sobol
    stochastic_reporter = results
    #execute_on = 'MULTIAPP_FIXED_POINT_END'
    from_reporter = "F_permeation/value
                       Scaled_Tritium_Flux/value
                       total_retention/value
                       coolant_heat_flux/value
                       max_temperature_W/value
                       max_temperature_Cu/value
                       max_temperature_CuCrZr/value"
  []
  [matrix_results]
    type = SamplerReporterTransfer
    from_multi_app = runner
    sampler = sobol
    stochastic_reporter = matrix
    from_reporter = "F_permeation/value
                       Scaled_Tritium_Flux/value
                       total_retention/value
                       coolant_heat_flux/value
                       max_temperature_W/value
                       max_temperature_Cu/value
                       max_temperature_CuCrZr/value"
  []
[]

[Reporters]
  [results]
    type = StochasticReporter
    execute_on = 'FINAL' # INITIAL TIMESTEP_END MULTIAPP_FIXED_POINT_END
  []
  [stats]
    type = StatisticsReporter
    reporters = "results/results:F_permeation:value
                   results/results:Scaled_Tritium_Flux:value
                   results/results:total_retention:value
                   results/results:coolant_heat_flux:value
                   results/results:max_temperature_W:value
                   results/results:max_temperature_Cu:value
                   results/results:max_temperature_CuCrZr:value"
    compute = 'mean stddev'
    ci_method = 'percentile'
    ci_levels = "0.05 0.10 0.15 0.20 0.25 0.30 0.35 0.40 0.45 0.50
                   0.55 0.60 0.65 0.70 0.75 0.80 0.85 0.90 0.95"
    execute_on = 'FINAL'
  []
  [sobol]
    type = SobolReporter
    sampler = sobol
    reporters = "results/results:F_permeation:value
                   results/results:Scaled_Tritium_Flux:value
                   results/results:total_retention:value
                   results/results:coolant_heat_flux:value
                   results/results:max_temperature_W:value
                   results/results:max_temperature_Cu:value
                   results/results:max_temperature_CuCrZr:value"
    ci_levels = "0.05 0.10 0.15 0.20 0.25 0.30 0.35 0.40 0.45 0.50
                   0.55 0.60 0.65 0.70 0.75 0.80 0.85 0.90 0.95"
    execute_on = 'FINAL'
  []
  [matrix]
    type = StochasticMatrix
    sampler = sobol
    sampler_column_names = "BCs/temperature_top/value
                              BCs/C_mob_W_top_flux/value
                              BCs/temperature_tube/value"
    execute_on = 'FINAL'
    parallel_type = ROOT
  []
[]

[Outputs]
  [out]
    type = JSON
    distributed = False
    execute_on = 'FINAL'
    execute_reporters_on = 'FINAL'
  []
[]
