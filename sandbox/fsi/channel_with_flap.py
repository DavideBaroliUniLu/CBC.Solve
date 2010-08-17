__author__ = "Kristoffer Selim and Anders Logg"
__copyright__ = "Copyright (C) 2010 Simula Research Laboratory and %s" % __author__
__license__  = "GNU GPL Version 3 or any later version"

# Last changed: 2010-08-17

from fsiproblem import *

# Command-line parameters
command_line_parameters = Parameters("command_line_parameters")
command_line_parameters.add("ny", 20)
command_line_parameters.add("dt", 0.02)
command_line_parameters.parse()

# Constants related to the geometry of the channel and the obstruction
channel_length  = 4.0
channel_height  = 1.0
structure_left  = 1.4
structure_right = 1.6
structure_top   = 0.5

# Define boundaries
inflow  = "x[0] < DOLFIN_EPS && \
           x[1] > DOLFIN_EPS && \
           x[1] < %g - DOLFIN_EPS" % channel_height
outflow = "x[0] > %g - DOLFIN_EPS && \
           x[1] > DOLFIN_EPS && \
           x[1] < %g - DOLFIN_EPS" % (channel_length, channel_height)
noslip  = "on_boundary && !(%s) && !(%s)" % (inflow, outflow)
fixed   = "x[1] < DOLFIN_EPS && x[0] > %g - DOLFIN_EPS && x[0] < %g + DOLFIN_EPS" % (structure_left, structure_right)

# Define structure subdomain
class Structure(SubDomain):
    def inside(self, x, on_boundary):
        return \
            x[0] > structure_left  - DOLFIN_EPS and \
            x[0] < structure_right + DOLFIN_EPS and \
            x[1] < structure_top   + DOLFIN_EPS

class ChannelWithFlap(FSI):

    def __init__(self):

        # Create the complete mesh
        ny = command_line_parameters["ny"]
        nx = 4*ny
        self.Omega = Rectangle(0.0, 0.0, channel_length, channel_height, nx, ny)

        # Create submeshes for fluid and structure
        self.init_meshes()

        # Initialize base class
        FSI.__init__(self)

    def init_meshes(self):

        # Create cell markers (0 = fluid, 1 = structure)
        D = self.Omega.topology().dim()
        cell_domains = MeshFunction("uint", self.Omega, D)
        cell_domains.set_all(0)
        self.structure = Structure()
        self.structure.mark(cell_domains, 1)

        # Extract submeshes for fluid and structure
        self.Omega_F = SubMesh(self.Omega, cell_domains, 0)
        self.Omega_S = SubMesh(self.Omega, cell_domains, 1)

    #--- Common parameters ---

    def mesh(self):
        return self.Omega

    def end_time(self):
        return 0.04

    def initial_time_step(self):
        return command_line_parameters["dt"]

    def evaluate_functional(self, u_F, p_F, U_S, P_S, U_M, at_end):

        # Only evaluate functional at the end time
        if not at_end: return

        # Compute average displacement
        structure_area = (structure_right - structure_left) * structure_top
        displacement = (1.0/structure_area)*assemble(U_S[0]*dx, mesh=U_S.function_space().mesh())

        # Compute velocity at outflow
        velocity = u_F((4.0, 0.5))[0]

        # Print values of functionals
        info("")
        info_blue("Functional 1 (displacement): %g", displacement)
        info_blue("Functional 2 (velocity):     %g", velocity)
        info("")

    def __str__(self):
        return "Channel with flap FSI problem"

    #--- Parameters for fluid problem ---

    def fluid_mesh(self):
        return self.Omega_F

    def fluid_density(self):
        return 1.0

    def fluid_viscosity(self):
        return 0.002

    def fluid_velocity_dirichlet_values(self):
        return [(0, 0)]

    def fluid_velocity_dirichlet_boundaries(self):
        return [noslip]

    def fluid_pressure_dirichlet_values(self):
        return 1, 0

    def fluid_pressure_dirichlet_boundaries(self):
        return inflow, outflow

    def fluid_velocity_initial_condition(self):
        return (0, 0)

    def fluid_pressure_initial_condition(self):
        return "1 - x[0]"

    #--- Parameters for structure problem ---

    def structure_mesh(self):
        return self.Omega_S

    def structure_density(self):
        return 15.0

    def structure_mu(self):
        return 75.0

    def structure_lmbda(self):
        return 125.0

    def structure_dirichlet_values(self):
        return [(0, 0)]

    def structure_dirichlet_boundaries(self):
        return [fixed]

    def structure_neumann_boundaries(self):
        return "on_boundary"

    #--- Parameters for mesh problem ---

    def mesh_mu(self):
        return 3.8461

    def mesh_lmbda(self):
        return 5.76

    def mesh_alpha(self):
        return 1.0

# Solve problem
problem = ChannelWithFlap()
problem.parameters["solver_parameters"]["plot_solution"] = False
problem.parameters["solver_parameters"]["tolerance"] = 1.0
u_F, p_F, U_S, P_S, U_M = problem.solve()
