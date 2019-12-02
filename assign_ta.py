from __future__ import print_function
from ortools.graph import pywrapgraph
import time
import numpy as np
import sys
import csv

inputArgs = sys.argv
FILENUM = 2
THRESHOLD = 999999

def main():
  
  cost = createDataArray()
  course_dict = createCourseDict()
  rows = len(cost)
  cols = len(cost[0])
  outputFile = open("output.txt", "w+")
  outputFile.write("Hello Professor Howell! Here's your TA assignment result. \r\n")

  assignment = pywrapgraph.LinearSumAssignment()
  for ta in range(rows):
    for recitation in range(cols):
      if cost[ta][recitation]:
        assignment.AddArcWithCost(ta, recitation, cost[ta][recitation])

  solve_status = assignment.Solve()

  if solve_status == assignment.OPTIMAL:
    print('Total cost = ', assignment.OptimalCost())
    print()
    for i in range(0, assignment.NumNodes()):
      if assignment.AssignmentCost(i) < THRESHOLD:
        result = 'Applicant #%d is assigned to Recitation %s.  Cost = %d' % (
              i,
              course_dict[assignment.RightMate(i)],
              assignment.AssignmentCost(i))
      else:
        result = 'Applicant #%d cannot be assigned to any recitation.' %i
      print(result) 
      outputFile.write(result + "\r\n")

  elif solve_status == assignment.INFEASIBLE:
    print('No assignment is possible.')
  elif solve_status == assignment.POSSIBLE_OVERFLOW:
    print('Some input costs are too large and may cause an integer overflow.')

  outputFile.close()
  print()
  print("Please check out output.txt in your current directory.")

def checkFileExistence(testFile):
  try: 
      openedFile = open(testFile)
      openedFile.close()
  except:
      raise Exception('File cannot be opened.')

def isValidCommand():
  if len(inputArgs) != FILENUM:
    raise Exception("The number of input files is incorrect. A sample command looks like this: 'python assign_ta.py your_cost_matrix.csv'.")
    return False
  return True

def convertInput():
  if isValidCommand():
    inputFile = inputArgs[1]
    checkFileExistence(inputFile)
    with open(inputFile, 'r') as csvfile:
      rawCost  = list(csv.reader(csvfile, delimiter=','))
      print(rawCost)
      print("Cost matrix is created.")
      return rawCost

def createCourseDict():
  if isValidCommand():
    inputFile = inputArgs[1]
    checkFileExistence(inputFile)
    res = dict()
    with open(inputFile, 'r') as csvfile:
      rawCost  = list(csv.reader(csvfile, delimiter=','))
      rawCost.pop(0)
      for i in range(len(rawCost)):
        res[i] = rawCost[i][1]
      return res

def createDataArray():
  rawCost = convertInput()
  for row in rawCost:
    del row[0:2]
    print(row)
  rawCost.pop(0)
  transposedCost = [[int(string[0]) for string in inner] for inner in rawCost]
  cost = [[row[i] for row in transposedCost] for i in range(len(transposedCost[0]))]
  return cost

if __name__ == "__main__":
  start_time = time.perf_counter()
  main()
  print("Finished in ", time.perf_counter() - start_time, "seconds")
