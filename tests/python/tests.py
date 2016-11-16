#!/usr/bin/env python

# Test QP solver against Maros Mezaros Benchmark suite
import sys
import scipy.io as spio
import scipy.sparse as spspa
import scipy as sp
import numpy as np
import ipdb
import quadprog.problem as qp
from quadprog.solvers.solvers import *

reload(qp)


def load_maros_meszaros_problem(f):
    # Load file
    m = spio.loadmat(f)

    # Convert matrices
    P = m['Q'].astype(float)
    n = P.shape[0]
    q = m['c'].T.flatten().astype(float)
    A = m['A'].astype(float)
    A = spspa.vstack([A, spspa.eye(n)])
    uA = np.append(m['ru'].T.flatten().astype(float),
                   m['ub'].T.flatten().astype(float))
    lA = np.append(m['rl'].T.flatten().astype(float),
                   m['lb'].T.flatten().astype(float))
    # Define problem
    p = qp.quadprogProblem(P, q, A, lA, uA)

    return p


def main():
    sp.random.seed(2)
    # Possible ops:  {'small1', 'small2', 'random', 'maros_meszaros', 'lp'}
    example = 'small1'

    if example == 'maros_meszaros':
        # Maros Meszaros Examples
        f = 'tests/maros_meszaros/CVXQP2_S.mat'
        # f = 'tests/maros_meszaros/CVXQP1_S.mat'
        #  f = 'tests/maros_meszaros/PRIMAL3.mat'
        # f = 'tests/maros_meszaros/QBANDM.mat'
        p = load_maros_meszaros_problem(f)

    elif example == 'small1':
        # Our Examples
        # Small Example 1
        P = spspa.csc_matrix(np.array([[4., 1.], [1., 2.]]))
        q = np.ones(2)
        A = spspa.vstack([spspa.csc_matrix(np.ones((1, 2))),
                         spspa.eye(P.shape[0])]).tocsc()
        lA = np.array([1.0, 0.0, 0.0])
        uA = np.array([1.0, 0.7, 0.7])

        p = qp.quadprogProblem(P, q, A, lA, uA)
    elif example == 'small2':
        # Small Example 2
        P = spspa.csc_matrix(np.array([[11., 0.], [0., 0.]]))
        q = np.array([3, 4])
        A = spspa.csc_matrix(np.array([[-1, 0], [0, -1], [-1, -3],
                                      [2, 5], [3, 4]]))
        uA = np.array([0., 0., -15, 100, 80])
        lA = -np.inf * np.ones(len(uA))
        p = qp.quadprogProblem(P, q, A, lA, uA)
    elif example == 'random':
        # Random Example
        n = 5
        m = 6
        # Generate random Matrices
        Pt = sp.randn(n, n)
        P = spspa.csc_matrix(np.dot(Pt.T, Pt))
        q = sp.randn(n)
        A = spspa.csc_matrix(sp.randn(m, n))
        uA = 3 + sp.randn(m)
        # lA = uA
        lA = -3 + sp.randn(m)

        p = qp.quadprogProblem(P, q, A, lA, uA)
    elif example == 'lp':
        # Random Example
        n = 50
        m = 10
        # Generate random Matrices
        P = spspa.csc_matrix(np.zeros((n, n)))
        q = sp.randn(n)
        A = spspa.vstack([spspa.csc_matrix(sp.randn(m, n)), spspa.eye(n)])
        lA = np.append(sp.randn(m), 0. * np.ones(n))
        uA = np.append(5 + sp.randn(m), 5. * np.ones(n))
        p = qp.quadprogProblem(P, q, A, lA, uA)
    else:
        assert False, "Unknown example"

    # Solve with CPLEX
    resultsCPLEX = p.solve(solver=CPLEX, verbose=1)

    # Solve with GUROBI
    resultsGUROBI = p.solve(solver=GUROBI, OutputFlag=1)

    # Solve with OSQP. You can pass options to OSQP solver
    resultsOSQP = p.solve(solver=OSQP, max_iter=50000,
                          eps_rel=1e-5,
                          eps_abs=1e-5,
                          alpha=1.6,
                          rho=1.6,
                          scale_steps=10,
                          scale_problem=False,
                          scale_norm=2,
                          polish=False,
                          print_level=2)

    # # Reuse factorizations
    # if example == 'random':
    #     c = sp.randn(nx)
    #     beq = sp.randn(neq)
    #     bineq = 100 * sp.rand(nineq)

    print "\n"
    print("Comparison CPLEX - GUROBI")
    print("-------------------------")
    print "Difference in objective value %.8f" % \
        np.linalg.norm(resultsCPLEX.objval - resultsGUROBI.objval)
    print "Norm of solution difference %.8f" % \
        np.linalg.norm(resultsCPLEX.x - resultsGUROBI.x)
    print "Norm of dual difference %.8f" % \
        np.linalg.norm(resultsCPLEX.dual - resultsGUROBI.dual)

    print "\n"
    print("Comparison OSQP - GUROBI")
    print("-------------------------")
    print "Difference in objective value %.8f" % \
        np.linalg.norm(resultsOSQP.objval - resultsGUROBI.objval)
    print "Norm of solution difference %.8f" % \
        np.linalg.norm(resultsOSQP.x - resultsGUROBI.x)
    print "Norm of dual difference %.8f" % \
        np.linalg.norm(resultsOSQP.dual - resultsGUROBI.dual)
    ipdb.set_trace()

# Parsing optional command line arguments
if __name__ == '__main__':
    if len(sys.argv) == 1:
        main()
    else:
        main(sys.argv[1:])
