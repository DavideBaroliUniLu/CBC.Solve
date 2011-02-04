__author__ = "Kristoffer Selim and Anders Logg"
__copyright__ = "Copyright (C) 2010 Simula Research Laboratory and %s" % __author__
__license__  = "GNU GPL Version 3 or any later version"

from dolfin import Parameters, File
from utils import date

def default_parameters():
    "Return default values for solver parameters."

    p = Parameters("solver_parameters");

    p.add("solve_primal", True)
    p.add("solve_dual", True)
    p.add("estimate_error", True)
    p.add("plot_solution", False)
    p.add("save_solution", True)
    p.add("save_series", True)
    p.add("uniform_timestep", False)
    p.add("dorfler_marking", True)

    p.add("tolerance", 0.1)
    p.add("fixedpoint_tolerance", 1e-8)
    p.add("initial_timestep", 0.01)
    p.add("maximum_iterations", 100)
    p.add("num_smoothings", 50)
    p.add("w_h", 0.45)
    p.add("w_k", 0.45)
    p.add("w_c", 0.1)
    p.add("marking_fraction", 0.5)

    return p

def store_parameters(p, prefix="application"):
    "Store parameters to file"

    # Save to file "application_parameters.xml"
    file = File("%s_parameters.xml" % prefix)
    file << p

    # Save to file based on current date
    file = File("%s_parameters-%s.xml" % (prefix, date()))
    file << p
