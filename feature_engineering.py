import pandas as pd
import random
import numpy as np
import sys
import csv
import time

def replace_all(text, dic):
    for k, v in dic.items():
        text = text.replace(k, v)
    return text

def cleanPreference(filename, rep):
    data = dict()
    data['course'] = ['21-111', '21-112', '21-120', '21-122', '21-124', '21-127',
                        '21-228', '21-236', '21-238', '21-240', '21-241', '21-242', 
                         '21-254', '21-256', '21-259', '21-260', '21-261', '21-268',
                        '21-269', '21-270', '21-292', '21-369', '21-469']
    course_index = dict()
    for i in range(len(data['course'])):
        course_name = data['course'][i]
        course_index[course_name] = i

    with open(filename, 'r') as csvfile:
        prefs = list(line for line in csvfile)
        prefs.pop(0)
        nrow, ncol = len(prefs), len(data['course'])
        for i in range(nrow):
            data[str(i+1)] = [0]*ncol

        for i in range(len(prefs)):
            pref = prefs[i].replace('"', "").strip().split(',')[2:-6]
            selection = [k+1 for k in range(len(pref))] #number of choices
            total_preferences = len(pref)

            for course in pref:
                number = course[:7]
                if number[0] == ' ': number = number[1:]
                else: number = number[:6]
                if number in course_index:
                    choice = random.choice(selection) 
                    data[str(i+1)][course_index[number]] = choice #student i, course j
                    selection.remove(choice)
            data[str(i+1)] = np.ceil(np.array(data[str(i+1)])*5/total_preferences)   
        # print(data[str(69)])  
        course_name =  data['course']
        for key in data:
            data[key] = pd.Series(data[key]).repeat(rep) 

    return pd.DataFrame(data), course_name


#read course schedule file
def getCatalog(filename):
    schedule = pd.read_csv(filename).dropna()
    course_name = [name for name in schedule.Number]
    course_catalog = dict() #key: course name, val: how many recitations, typically less than 5
    for i in range(len(schedule.Number)):
        name = schedule.Number.iloc[i]
        name_ = str(name)[0:6]
        if name_ in course_catalog:
            course_catalog[name_] += 1
        else: course_catalog[name_] = 1

    return course_name, course_catalog

def cleanSchedule(filename, nrow, col_start):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    schedule = dict()
    for key in days:
        schedule[key] = list() 
    with open(filename, 'r') as file:
        rawdata = list(file)
        rawdata.pop(0)
        rawdata = rawdata[0:nrow]
        rep = {'"': "", "[": "", "]": "", " ":""}
        for row in rawdata:
            times = replace_all(row, rep)
            times = times.strip().split(',')[col_start:col_start+45]
            for i in range(5):
                sequence = [int(times[int(i+j*5)]) for j in range(9)]
                schedule[days[i]].append(sequence)
        return schedule

def cleanGrades(filename, rep):
    res = list()
    with open(filename, 'r') as file:
        rawdata = list(file)
        rawdata.pop(0)
        for i in range(len(rawdata)):
            row = rawdata[i]
            vals = row.strip().split(',')[1:]
            seq = list()
            for val in vals:
                if int(val) > 3: 
                    seq.append(1) #pass if student got more than b
                else: 
                    seq.append(0) #disqualified otherwise
            for t in range(rep[i]):
                res.append(seq)
    return res

def main(courseScheduleFile, studentScheduleFile, preferenceFile, gradesFile):

    #get catalog: return course number and index alignment, repition of recitation
    recitation_name, course_vol = getCatalog(courseScheduleFile)
    repeat = [v for k, v in course_vol.items()]
    
    print("Processing schedules .. ")
    #clean course schedule, return NxT matrix
    #1 if class takes place, 0 otherwise
    N = len(recitation_name)
    courseSchedule = cleanSchedule(courseScheduleFile, N, 2)
    
    #clean student schedule, return MT matrix
    #1 if student is available, 0 otherwise
    M = 92
    studentSchedule = cleanSchedule(studentScheduleFile, M, 1)
    
    print("Processing grades .. ")
    #clean grades, return NxM matrix
    grades_arr = cleanGrades(gradesFile, repeat)
    grades_matrix = np.array(grades_arr)
    
    print("Processing undergrad preferences .. ")
    #clean preference matrix, return dataframe, then return N*M matrix
    pref_df, class_name = cleanPreference(preferenceFile, repeat)
    # pref_df.to_csv(r'pref.csv', sep = ',', index = False)
    pref_matrix = np.array(pref_df.iloc[:, 1:])
    cost_mat = np.multiply(cost_matrix, 10)

    print("Retrieving eligibility and scores .. ")
    #compute availability matrix NxM, 1 if student can lead recitation, 0 otherwise
    availability = np.zeros((N, M))
    rowtotal = np.zeros(N)
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
        course, student = np.array(courseSchedule[day]), np.array(studentSchedule[day])
        rowsum = np.sum(course, axis = 1)
        rowsum[rowsum>0] = 1 #indicator of whethere or not there's class at all 
        rowtotal += rowsum
        avail = np.dot(course, np.transpose(student))
        avail[ avail > 0] = 1   
        availability = availability + avail  
    availability[ availability<1 ] = 0
    rowtotal[rowtotal<1] = 1 #prevent division overflow
    
    # TA who apply should be available for both days if there're 2 recitation a week
    for col in range(len(availability[0])):
        availability[:, col] = np.divide(availability[:, col], rowtotal)
    availability[ availability<1 ] = 0
    
    #21-236, 21-238, 21-270 don't have recitation/ or recitation in the evening
    #assume everyone is available for now
    availability[15:17, ] = np.ones(92)
    availability[-8:-4, ] = np.ones(92)
 
    #apply grades as a filter
    eligibility = np.multiply(availability, grades_matrix)
    
    #compute cost
    cost = np.multiply(eligibility, cost_mat)
    print("Finished!")

    #filter unqualified people, collapse vertically
    candidates = np.sum(cost, axis = 0)
    #filter unpopular class, collapse horizontally
    recitations = np.sum(cost, axis = 1)
    
    for i in range(N):
        for j in range(M):
            if candidates[j] == 0 or recitations[i] == 0:
                cost[i, j] = 999999

    #make dataframe
    out = dict()
    out['Course'] = recitation_name
    for i in range(M):
        out[str(i+1)] = [int(val) for val in cost[:, i]] 
    #add dummies
    for i in range(M-N):
        for key in out:
            if key == 'Course': out[key].append('dummy'+str(i+1))
            else: out[key].append(int(999999))
   
    cost_df = pd.DataFrame(out)
    cost_df.to_csv(r'cost.csv', sep = ',', index = False)
    
    cost = cost[[0,1,2,3,7,8,13, 15, 16, 17, 18, 21, 22, 23,
     26, 30, 32, 33, 34, 35, 39, 40, 42], :]

    cost[cost == 999999] = 0
    cost[cost > 0] = 1

    interviewee = np.sum(cost, axis = 0) #it's different from candidates!!!
    classes = np.sum(cost, axis = 1) #it's different from recitation!

    outputFile = open("fe_report.txt", "w+")
    outputFile.write("Hi Jason, we are unable to find qualified or available candidates for the following courses: \n")
    for i in range(len(classes)):
        if classes[i] == 0:
            outputFile.write("Course #" + class_name[i])
            outputFile.write('\n')
    outputFile.write('\n')

    outputFile.write("Additionally, \n")
    for i in range(len(classes)):
        print("Found %d candidates for course %s."% (sum(cost[i]), class_name[i]))
        if classes[i] != 0:
            result = "Found %d candidates for course %s."% (sum(cost[i]), class_name[i])
            outputFile.write(result)
            outputFile.write('\n')
    outputFile.write('\n')

    eval_form = dict()
    eval_form["student"] = list()
    eval_form['you_preferred_assignment'] = list()

    outputFile.write("Here are the people who are qualified to teach more than 2 courses. \n")
    for i in range(len(interviewee)):
        if interviewee[i] >2:
            eval_form["student"].append(str(i+1))
            eval_form["you_preferred_assignment"].append("21-XXX")
            outputFile.write("Candidate #" +str(i+1)+': ')
            for j in range(len(cost[:, i])):
                if cost[j, i] >0:
                    outputFile.write(class_name[j]+'; ')
            outputFile.write('\n')
    pd.DataFrame(eval_form).to_csv(r'evaluation.csv', sep = ',', index = False)

    conclusion = "You may consider an interview for them. " +\
            "If you do, please fill out the evaluation form" +\
            "with the COURSE NUMBER of your preferred assignment" +\
            "in the column next to student ID. \n Good Luck! \n"
    outputFile.write(conclusion)
    outputFile.close()

if __name__ == '__main__':
    start_time = time.perf_counter()
  
    course = sys. argv [1]
    student = sys. argv [2]
    pref = sys. argv [3]
    grades = sys. argv [4]
    main(course, student, pref, grades)
    print("Finished in ", time.perf_counter() - start_time, "seconds")

    
