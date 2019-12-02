# TA Assignment Solver

> TODO's for Team:
- Compute a 43x92 score matrix from the matrices we have created so far
- Revert it to a cost matrix since the package uses a minimization objective function; for example, the score matrix [10, 20, 30] should be reverted to a cost matrix like [30, 20, 10]
- Fill it into the template cost_matrix.csv; you can refer to the format of cost_matrix_small.csv
- (Optional) After running the script, replace the Recitation # with real course numbers and Applicant # with names in the output file

## DEMO
1. Install ortools package (make sure you're using Python3)
```
python -m pip install --upgrade --user ortools
```
2. Run this command to get cost matrix:
```bash
python feature_engineering.py course_schedule.csv student_schedule.csv undergrad_preferences.csv grades.csv cost.csv
```

3. Run this command:
```bash
python assign_ta.py cost.csv
```
or replace cost.csv with your cost matrix

4. Check out the output.txt file in your current directory
