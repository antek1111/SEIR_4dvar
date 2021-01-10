import numpy as np
from adao import adaoBuilder


def assimilate(xb, yobs, observation_operator, evolution_func, error_vector=None, verbose=False):
    case = adaoBuilder.New('')
    case.setBackground(Vector=xb, Stored=True)
    if error_vector:
        case.setBackgroundError(DiagonalSparseMatrix=error_vector)
    else:
        case.setBackgroundError(ScalarSparseMatrix=1.e4)
    case.setEvolutionError(ScalarSparseMatrix=0.1)
    case.setEvolutionModel(OneFunction=evolution_func)
    case.setObservation(VectorSerie=yobs, Stored=True)
    case.setObservationError(ScalarSparseMatrix=0.1)
    case.setObservationOperator(OneFunction=observation_operator)
    case.setAlgorithmParameters(
        Algorithm='4DVAR',
        Parameters={
            'StoreSupplementaryCalculations': [
                # 'Analysis', 'BMA', 'CostFunctionJ', 'CostFunctionJAtCurrentOptimum',
                # 'CostFunctionJb', 'CostFunctionJbAtCurrentOptimum', 'CostFunctionJo',
                # 'CostFunctionJoAtCurrentOptimum', 'CurrentOptimum', 'CurrentState', 'IndexOfOptimum'
                'CurrentState'
            ],
            'MaximumNumberOfSteps': 100
        },
    )
    if verbose:
        calculations = [
            # 'Analysis', 'BMA', 'CostFunctionJ', 'CostFunctionJAtCurrentOptimum', 'CostFunctionJb',
            # 'CostFunctionJbAtCurrentOptimum', 'CostFunctionJo', 'CostFunctionJoAtCurrentOptimum',
            # 'CurrentOptimum', 'CurrentState', 'IndexOfOptimum'
            'CurrentState'
        ]
        for calculation in calculations:
            case.setObserver(
                Info="  Intermediate " + calculation + " at the current iteration:",
                Template='ValuePrinter',
                Variable=calculation,
            )
    case.execute()
    print("Calibration of %i coefficients on %i measures" % (
        len(case.get('Background')),
        len(case.get('Observation')),
        ))
    print("---------------------------------------------------------------------")
    print("Calibration resulting coefficients.:", np.ravel(case.get('Analysis')[-1]))
    return np.ravel(case.get('Analysis')[-1])


def prepare_obs(state, obs_operator, evolution_function, size=100):
    a = []
    for i in range(size):
        a.append(obs_operator(state))
        state = evolution_function(state)
    return a


def load_data(size=100, country='POL'):
    deaths = []
    cumulative = 0
    with open('covid-deaths.csv') as f:
        for line in f:
            fields = line.split(',')
            if fields[1] == country:
                cumulative += float(fields[3][:-1])
                deaths.append(cumulative)

    return np.array(deaths[-size:]).reshape((-1, 1))
