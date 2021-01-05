# -*- coding: utf-8 -*-
#
from numpy import array, ravel

#E = 1000
#I = 0
#S = 10000000 - E - I
#R = 0

iterationsEv = 0
iterationsOb = 0

def EvolFunc( state ):
	"""
	D = alfa * I
	S = S - S*beta*I/N
	E = E + S*beta*I/N - eps*E
	I = I + eps*E - (alfa+gamma)*I
	R = R + gamma*I
	"""
	global iterationsEv
	iterationsEv +=1
	#print("EvolFunc received", state.tolist())
	S_old, E_old, I_old, R_old, D_old, alfa, beta, eps, gamma = list(ravel(state))
	#alfa, beta, eps, gamma = [0.006, 0.45, 0.125, 0.33]
	results = []
	#for i in range(296):
	D = D_old + alfa * I_old
	S = S_old - S_old*beta*I_old/(S_old+E_old+I_old+R_old)
	E = E_old + S_old*beta*I_old/(S_old+E_old+I_old+R_old) - eps*E_old
	I = I_old + eps*E_old - (alfa+gamma)*I_old
	R = R_old + gamma*I_old
	#S_old, E_old, I_old, R_old, D_old = S, E, I, R,  D
	#results.append([S, E, I,  R,  D])
	#print('SEIRD',S,E,I,R,D)
	#print('N',S+E+I+R)
	#print(array(results))
	results=[S,E,I,R,D,alfa,beta,eps,gamma]
	#print("EvolFunc returns ", array(results).reshape(-1,1).tolist(), iterationsEv)
	return array(results).reshape(-1,1)
#

def ObsOp(state):
	global iterationsOb
	iterationsOb +=1
	#print("ObsOp received", state.tolist())
	#print(state)
	D= state.reshape((-1,9))[:,4]
	#print("ObsOp returns", D.tolist(), iterationsOb)
	#print(D)
	return D


Xb   = array([39900000, 10000, 10000, 80000, 2300,0.006, 0.45, 0.125, 0.33])
#Xb   = array([39900000, 10000, 10000, 80000, 2300,0.00180234428, 0.782912695, 0.129143341, 0.673371666])
deaths = []
cumulative = 0
with open('covid-deaths.csv') as f:
	lines = []
	for line in f:
		fields = line.split(',')
		if fields[1] == 'POL':
			cumulative += float(fields[3][:-1])
			deaths.append(cumulative)

Yobs = array(deaths[-100:]).reshape((-1, 1))
print("Deaths loaded",Yobs.shape)
print(Yobs)
#
print("Iterative resolution of the calibration problem")
print("-----------------------.-----------------------")
print("")
from adao import adaoBuilder
case = adaoBuilder.New('')
print(Xb)
case.setBackground( Vector = Xb, Stored=True )
case.setBackgroundError( ScalarSparseMatrix = 1.e6 )
case.setEvolutionError( ScalarSparseMatrix = 1. )
case.setEvolutionModel( OneFunction = EvolFunc )
case.setObservation( VectorSerie = Yobs, Stored=True )
case.setObservationError( ScalarSparseMatrix = 1. )
case.setObservationOperator( OneFunction = ObsOp )
case.setAlgorithmParameters(
    Algorithm='4DVAR',
    Parameters={
        'StoreSupplementaryCalculations': [
            'Analysis', 'BMA', 'CostFunctionJ', 'CostFunctionJAtCurrentOptimum', 'CostFunctionJb', 'CostFunctionJbAtCurrentOptimum', 'CostFunctionJo', 'CostFunctionJoAtCurrentOptimum', 'CurrentOptimum', 'CurrentState', 'IndexOfOptimum'
            ],
        },
    )
    #'Bounds': [[0.,40000000.],[0.,40000000.],[0.,40000000.],[0.,40000000.],[0.,40000000.]],
calculations = [
            'Analysis', 'BMA', 'CostFunctionJ', 'CostFunctionJAtCurrentOptimum', 'CostFunctionJb', 'CostFunctionJbAtCurrentOptimum', 'CostFunctionJo', 'CostFunctionJoAtCurrentOptimum', 'CurrentOptimum', 'CurrentState', 'IndexOfOptimum'
            ]
for calculation in calculations:
	case.setObserver(
    Info="  Intermediate"+calculation+"at the current iteration:",
    Template='ValuePrinter',
    Variable=calculation,
    )
case.execute()
print("")
#
#-------------------------------------------------------------------------------
#
print("Calibration of %i coefficients in a 1D quadratic function on %i measures"%(
    len(case.get('Background')),
    len(case.get('Observation')),
    ))
print("---------------------------------------------------------------------")
print("")
print("Observation vector.................:", ravel(case.get('Observation')))
print("A priori background state..........:", ravel(case.get('Background')))
print("")
print("Calibration resulting coefficients.:", ravel(case.get('Analysis')[-1]))
