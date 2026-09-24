# TMAP8 input file
# Written by Pierre-Clément Simon - Idaho National Laboratory
#
# Published with:
# P.-C. A. Simon,
# "TBD"
#
# Info:
# - This input file couples solid transport and liquid transport with Navier-Stokes
# - It models the tritium extraction experiment (TEX) PbLi loop
# - block 0 on the left corresponds to the solid
# - block 1 on the right corresponds to the liquid
# - Assumes steady state and the liquid velocity is null
#
#
# Once TMAP8 is installed and built (see instructions on the TMAP8 website), run with
# cd ~/projects/TMAP8/test/tests/TEX_pipe_flow_navier_stokes_coupling/
# mpirun -np 1 ~/projects/TMAP8/tmap8-opt -i TEX_modeling_tritium_steady_state.i

# Boundary conditions
concentration_solid_external = 0.0
concentration_liquid_internal = 1.0

# Material properties
diffusion_coefficient_PbLi = 1.0
diffusion_coefficient_V = 1.0

# Convection
convection_transfer_coefficient = 1.0e8

# file names
output_name = TEX_modeling_tritium_out/TEX_modeling_tritium_out

[Mesh]
  [cmg]
    type = CartesianMeshGenerator
    dim = 2
    dx = '0.5 0.5'
    dy = '0.5 0.5'
    ix = '5 10'
    iy = '5 5'
    subdomain_id = '0 1
                    0 1'
  []
  [add_sideset0] # from 0 (solid) to 1 (liquid)
    type = SideSetsBetweenSubdomainsGenerator
    input = cmg
    new_boundary = interface_0_1
    primary_block = 0
    paired_block = 1
  []
  [add_sideset1] # from 1 (liquid) to 0 (solid)
    type = SideSetsBetweenSubdomainsGenerator
    input = add_sideset0
    new_boundary = interface_1_0
    primary_block = 1
    paired_block = 0
  []
[]

[Variables]
  [tritium_solid_fe] # finite element variable for tritium concentration in solid
    block = 0
  []
  [tritium_liquid_fv] # finite volume variable for tritium concentration in liquid
    type = MooseVariableFVReal
    block = 1
  []
[]

[Kernels]
  [tritium_solid_fe_diffusion]
    type = ADMatDiffusion
    variable = tritium_solid_fe
    diffusivity = ${diffusion_coefficient_V}
  []
[]

[BCs]
  [tritium_solid_fe_left]
    type = ADDirichletBC
    boundary = left
    variable = tritium_solid_fe
    value = ${concentration_solid_external}
  []
  [tritium_solid_fe_interface]
    type = ADConvectiveHeatFluxBC
    boundary = interface_0_1
    variable = tritium_solid_fe
    T_infinity_functor = tritium_liquid_fv
    heat_transfer_coefficient_functor = ${convection_transfer_coefficient}
  []
[]

[FVKernels]
  [tritium_liquid_fv_diff]
    type = FVDiffusion
    variable = tritium_liquid_fv
    coeff = ${diffusion_coefficient_PbLi}
  []
[]

[FVBCs]
  [tritium_liquid_fv_right]
    type = FVDirichletBC
    boundary = right
    variable = tritium_liquid_fv
    value = ${concentration_liquid_internal}
  []
  [tritium_liquid_fv_interface]
    type = FVFunctorConvectiveHeatFluxBC
    boundary = interface_1_0
    variable = tritium_liquid_fv
    T_bulk = tritium_liquid_fv
    T_solid = tritium_solid_fe
    heat_transfer_coefficient = ${convection_transfer_coefficient}
    is_solid = false
  []
[]

[Postprocessors]
  [Tritium_amount_solid]
    type = ElementIntegralVariablePostprocessor
    variable = tritium_solid_fe
    block = 0
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [Tritium_concentration_interface_solid]
    type = PointValue
    variable = tritium_solid_fe
    point = '0.5 0 0'
    execute_on = 'INITIAL TIMESTEP_BEGIN TIMESTEP_END LINEAR NONLINEAR'
  []
  [Tritium_amount_liquid]
    type = ElementIntegralVariablePostprocessor
    variable = tritium_liquid_fv
    block = 1
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [Tritium_amount_total]
    type = LinearCombinationPostprocessor
    pp_names = 'Tritium_amount_solid Tritium_amount_liquid'
    pp_coefs = '1   1'
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [dt]
    type = TimestepSize
  []
[]

[Positions]
  [pos]
    type = InputPositions
    positions = '0.51 0.55 0
                 0.61 0.55 0
                 0.71 0.55 0
                 0.81 0.55 0
                 0.91 0.55 0
                 0.99 0.55 0'
  []
[]

[VectorPostprocessors]
  [radial_profile_solid]
    type = LineValueSampler
    variable = 'tritium_solid_fe'
    start_point = '0 0.5 0'
    end_point = '0.5 0.5 0'
    num_points = 10
    sort_by = 'x'
    execute_on = 'TIMESTEP_END FINAL'
  []
  [radial_profile_liquid]
    type = PositionsFunctorValueSampler
    functors = 'tritium_liquid_fv'
    positions = 'pos'
    sort_by = 'x'
    execute_on = 'TIMESTEP_END FINAL'
    # the finite volume variable is discontinuous at faces
    # Note that we are not sampling on faces so it does not matter,
    # we could set it to 'false' to have less checks when sampling
    discontinuous = true
  []
[]

[Preconditioning]
  [Newtonlu]
    type = SMP
    full = true
    solve_type = 'NEWTON'
    petsc_options_iname = '-pc_type -sub_pc_type'
    petsc_options_value = 'asm      lu          '
  []
[]

[Executioner]
  type = Steady
[]

[Outputs]
  file_base = ${output_name}
  csv = true
[]
