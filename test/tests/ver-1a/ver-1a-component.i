# Verification Problem #1a from TMAP4/TMAP7 V&V document
# Tritium diffusion through SiC layer with depleting source at 2100 C.
# No Soret effect, solubility, or trapping included.

# Physical Constants
# Note that we do NOT use the same number of digits as in TMAP4/TMAP7.
# This is to be consistent with TMAP8PhysicalConstants.h
kb = '${units 1.380649e-23 J/K}' # Boltzmann constant
R = '${units 8.31446261815324 J/mol/K}' # Gas constant

# Data used in TMAP4/TMAP7 case
temperature = '${units 2373 K}'
initial_pressure = '${units 1e6 Pa}'
volume_enclosure = '${units 5.20e-11 m^3 -> mum^3}'
surface_area = '${units 2.16e-6 m^2 -> mum^2}'
diffusivity_SiC = '${units ${fparse 1.58e-4*exp(-308000.0/(R*temperature))} m^2/s -> mum^2/s}'
solubility_constant = '${units ${fparse 7.244e22 / temperature} at/m^3/Pa -> at/mum^3/Pa}'
slab_thickness = '${units 3.30e-5 m -> mum}'

# Useful equations/conversions
concentration_to_pressure_conversion_factor = '${units ${fparse kb*temperature} Pa*m^3 -> Pa*mum^3}'

[Physics]
  [SorptionExchange]
    [0d_solub]
      species = 'v'

      equilibrium_constants = 'K_sol'
      verbose = true
    []
  []
  [Diffusion]
    [multi-D]
      variable_name = 'u'
      diffusivity_matprop = 'diff'

      # Dont add the default preconditioning
      preconditioning = 'defer'

      # To help coupling to trapping
      compute_diffusive_fluxes_on = 'structure_left'
    []
  []
[]

[ActionComponents]
  [structure]
    type = Structure1D
    species = 'u'
    physics = 'multi-D'

    # Material properties
    property_names = 'diff'
    property_values = '${diffusivity_SiC}'

    # Boundary conditions
    fixed_value_bc_variables = 'u'
    fixed_value_bc_boundaries = 'structure_right'
    fixed_value_bc_values = '0'

    # Geometry
    nx = 150
    xmax = ${slab_thickness}
    length_unit_scaling = 1
  []

  [enc]
    type = Enclosure0D
    species = 'v'
    physics = '0d_solub'

    # Conditions
    temperature = '${temperature}'
    species_initial_pressures = '${initial_pressure}'

    # Material properties
    property_names = 'K_sol'
    property_values = '${solubility_constant}'

    # Geometry
    volume = '${volume_enclosure}'

    # Connection to structures
    connected_structures = 'structure'
    connection_boundaries = 'structure_left'
    connection_boundaries_area = '${surface_area}'
  []
[]

[Postprocessors]
  # flux of tritium through the outer SiC surface - compare to TMAP7
  [flux_surface_right]
    type = SideDiffusiveFluxIntegral
    variable = u
    diffusivity = '${diffusivity_SiC}'
    boundary = 'structure_right'
    execute_on = 'initial nonlinear linear timestep_end'
    outputs = 'console csv exodus'
  []
  # flux of tritium through the surface of SiC layer in contact with enclosure
  [flux_surface_left]
    type = SideDiffusiveFluxIntegral
    variable = u
    diffusivity = '${diffusivity_SiC}'
    boundary = 'structure_left'
    execute_on = 'initial nonlinear linear timestep_end'
    outputs = ''
  []
  # scale the flux to get inward direction
  [scaled_flux_surface_left]
    type = ScalePostprocessor
    scaling_factor = -1
    value = flux_surface_left
    execute_on = 'initial nonlinear linear timestep_end'
    outputs = 'console csv exodus'
  []
  # integral of the tritium flux through outer surface of SiC layer
  [integral_release_flux_right]
    type = PressureReleaseFluxIntegral
    variable = u
    boundary = 'structure_right'
    diffusivity = '${diffusivity_SiC}'
    surface_area = '${surface_area}'
    volume = '${volume_enclosure}'
    concentration_to_pressure_conversion_factor = '${concentration_to_pressure_conversion_factor}'
    outputs = 'console'
  []
  # cumulative sum of integral_release_flux_right over time (i.e. cumulative amount released)
  [cumulative_release_right]
    type = CumulativeValuePostprocessor
    postprocessor = 'integral_release_flux_right'
    outputs = 'console'
  []
  # released fraction based on outer layer flux - compare to TMAP4
  [released_fraction_right]
    type = ScalePostprocessor
    value = 'cumulative_release_right'
    scaling_factor = '${fparse 1./(initial_pressure)}'
    outputs = 'console csv exodus'
  []
  # Make a postprocessor take the value of the scalar value v
  [v_value]
    type = ScalarVariable
    variable = v_enc
  []
  # released fraction based on inner layer flux on v - compare to TMAP7
  [released_fraction_left]
    type = LinearCombinationPostprocessor
    pp_names = 'v_value'
    pp_coefs = '${fparse -1./(initial_pressure)}'
    b = 1
  []
  # For testing purposes
  [v]
    type = ScalarVariable
    variable = v_enc
    execute_on = 'INITIAL TIMESTEP_END'
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

  # Time stepping and integration
  dt = .1
  end_time = 140
  dtmin = .1
  scheme = 'bdf2'
  timestep_tolerance = 1e-8

  # Nonlinear solver
  solve_type = PJFNK
  automatic_scaling = true
  l_max_its = 30
  nl_max_its = 5
  petsc_options_iname = '-pc_type -mat_mffd_err'
  petsc_options_value = 'lu       1e-5'
  line_search = 'bt'
[]

[Outputs]
  exodus = true
  print_linear_residuals = false
  [csv]
    type = CSV
    execute_on = 'initial timestep_end'
  []
  [console]
    type = Console
    time_step_interval = 10
  []
[]
