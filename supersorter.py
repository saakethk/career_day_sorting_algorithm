
import csv
from dataclasses import dataclass, field
from typing import List

# CUSTOM TYPES (Source: https://www.datacamp.com/tutorial/python-data-classes)

@dataclass(order=True)
class Student:
    grade: int
    timestamp: int
    first_name: str
    last_name: str
    homeroom: str
    first_period: str
    id: int
    choices: List[int]

@dataclass
class Class:
    students: List[Student] = field(default_factory=list)
    min_limit: int
    max_limit: int

def getDefaultClasses(num_classes: int):
    return [0 for _ in range(num_classes)]

@dataclass
class Session:
    id: int
    subject: str
    teacher: str
    presenter: str
    classes: List[Class] = field(default_factory=getDefaultClasses)

# FUNCTIONS

# Gets student data and converts to custom defined type
def getStudentData(filename: str):
    
    student_data: List[Student] = []
    
    with open(filename, mode="r") as file:
        reader = csv.reader(file)
        
        # Skips first few lines
        skip_lines = 2
        for _ in range(skip_lines):
            next(reader)

        # Reads remaining rows and converts rows to student object
        for row in reader:
            student_data.append(
                Student(
                    timestamp=int(row[0]),
                    first_name=row[1],
                    last_name=row[2],
                    homeroom=row[3],
                    first_period=row[4],
                    id=int(row[5]),
                    grade=int(row[6]),
                    choices=[int(choice) for choice in [row[7], row[8], row[9], row[10], row[11], row[12], row[13]]]
                )
            )
            
    return student_data

# Gets student data and converts to custom defined type
def getSessionData(filename: str):
    
    # student_data: List[Session] = []
    
    with open(filename, mode="r") as file:
        reader = csv.reader(file)
        
        # Skips first few lines
        metadata_lines = 3
        for row in range(metadata_lines):
            print(reader[row])
            next(reader)

        # Reads remaining rows and converts rows to student object
        for row in reader:
            print(row)
            
    # return student_data


students = getStudentData("students.csv")
sessions = getSessionData("sessions.csv")
                

