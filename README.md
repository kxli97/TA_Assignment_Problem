# TA Assignment Problem

## TODO's for Team:
- Compute a 92x92 score matrix from the matrices we have created so far.
- Revert it to a cost matrix since the package uses a minimization objective function. For example, the score matrix [10, 20, 30] should be reverted to a cost matrix like [30, 20, 10].  
- Fill it into the template cost_matrix.csv. You can refer to the format of cost_matrix_small.csv
- (Optional) After running the script, replace the Recitation with real course number in the output file. 

## DEMO
1. Install ortools package (make sure you're using Python3)
```
python -m pip install --upgrade --user ortools
```
2. Run this command:
```bash
python assign_ta.py cost_matrix_small.csv
```
3. Check out the output.txt file in your current directory.
