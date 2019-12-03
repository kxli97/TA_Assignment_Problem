# TA Assignment Solver

> TODO's for DEV Team:
- ~~Compute a 92x92 score matrix from the matrices we have created so far~~
- ~~Revert it to a cost matrix since the package uses a minimization objective function; for example, the score matrix [10, 20, 30] should be reverted to a cost matrix like [30, 20, 10]~~
- ~~Fill it into the template cost_matrix.csv; you can refer to the format of cost_matrix_small.csv~~
- ~~Need to fix the dictionary in assign_ta.py~~

> TODO's for Presentation:
- Diagrams + Description (Xiaohua + Shane)
- Pipeline (Selena)
- Matrices Visualization (Kimberly)
- Polish the deck style (Together)

> TODO's for Report:


## DEMO
1. Install ortools package (make sure you're using Python3)
```
python -m pip install --upgrade --user ortools
```
2. Run this command to get cost matrix:
```bash
python feature_engineering.py course_schedule.csv student_schedule.csv undergrad_preferences.csv grades.csv cost.csv
```

3. Run this command to get TAs assigned (You can replace the cost.csv with your own cost matrix):
```bash
python assign_ta.py cost.csv
```

4. Check out the output.txt file in your current directory
