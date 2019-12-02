import pandas as pd
import random
import numpy as np
import sys
import csv
import time

def cleanPreference(filename, rep):
    data = dict()
    data['course'] = ['21-111', '21-112', '21-120', '21-122', '21-124', '21-127',
                        '21-228', '21-236', '21-238', '21-240', '21-241', '21-242', 
                         '21-254', '21-256', '21-259', '21-260', '21-261', '21-268',
                        '21-269', '21-270', '21-292', '21-369', '21-469']
    course_index = dict()
    for i in range(len(data['course'])):
        course_name = data['course'][i]
        course_index[course_name] = i+1

    
    with open(filename, 'r') as csvfile:
        prefs = list(line for line in csvfile)
        prefs.pop(0)
        nrow, ncol = len(prefs), len(data['course'])
        for i in range(nrow):
            data[str(i+1)] = [0]*ncol
        
        for i in range(len(prefs)):
            pref = prefs[i].strip().split(',')[2:-6]
            selection = [k+1 for k in range(len(pref))]
            
            total_preferences = len(pref)      
            for course in pref:  
                if course[0] == ' ': 
                    course = course[1:]
                number = course[:6]
                if number in course_index:
                    choice = random.choice(selection) 
                    data[str(i+1)][course_index[number]] = choice #student i, course j
                    selection.remove(choice)
            data[str(i+1)] = np.ceil(np.array(data[str(i+1)])*5/total_preferences)
        
        for key in data:
            data[key] = pd.Series(data[key]).repeat(rep)
            
    return pd.DataFrame(data)


def replace_all(text, dic):
    for k, v in dic.items():
        text = text.replace(k, v)
    return text

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
    course_name, course_vol = getCatalog(courseScheduleFile)
    
    repeat = [v for k, v in course_vol.items()]
    
    print("Processing schedules .. ")
    #clean course schedule, return NxT matrix
    #1 if class takes place, 0 otherwise
    N = len(course_name)
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
    pref_df = cleanPreference(preferenceFile, repeat)
    pref_matrix = np.array(pref_df.iloc[:, 1:])
    cost_matrix = 6*np.ones((N,M)) - pref_matrix #revert to cost matrix, the larger the less preferred
    
    
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
    cost = np.multiply(eligibility, cost_matrix)
    print("Finished!")
    
    out = dict()
    out['Course'] = course_name
    for i in range(N):
        out[str(i+1)] = [str(val) for val in cost[:, i]]
        print("Recitation %s found %d candidates."% (course_name[i], sum(cost[i])) )
    
        
    cost_df = pd.DataFrame(out)
    cost_df.to_csv(r'cost.csv', sep = ',', index = False)

        
if __name__ == '__main__':
    course = sys. argv [1]
    student = sys. argv [2]
    pref = sys. argv [3]
    grades = sys. argv [4]
    main(course, student, pref, grades)

    