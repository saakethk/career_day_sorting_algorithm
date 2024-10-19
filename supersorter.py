
import csv
from dataclasses import dataclass, field
from typing import List

# CONSTANTS

NUM_ASSIGNED_CLASSES = 4 # Number of classes to assign to each student
NUM_CHOICES = 7 # Number of choices for student

# CUSTOM TYPES (Source: https://www.datacamp.com/tutorial/python-data-classes)

def getDefaultStudents():
    return []

def getDefaultAssigned():
    return []

def getDefaultClasses(min_limit: int, max_limit: int, num_classes: int = NUM_ASSIGNED_CLASSES):
    return [Class(min_limit=min_limit, max_limit=max_limit) for _ in range(num_classes)]

@dataclass
class CondensedSession:
    id: int
    subject: str
    teacher: str
    presenter: str

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
    assigned: List[CondensedSession] = field(default_factory=getDefaultAssigned)
    
    def assignChoice(self, index: int, sessions: List[any], wasChosen: bool = True):

        if (wasChosen):
            assigned_choice = self.choices.pop(index)
            chosen_session: Session = sessions[assigned_choice-1]
        else:
            chosen_session: Session = sessions[index-1]

        self.assigned.append(
            CondensedSession(
                id=chosen_session.id,
                subject=chosen_session.subject,
                teacher=chosen_session.teacher,
                presenter=chosen_session.presenter
            )
        )

    def getCSVRow(self):
        
        row = f"{self.first_name}, {self.last_name}, {self.homeroom}, {self.first_period}, {self.id}, {self.grade}"
        
        for session in self.assigned:
            row += f", {session.id}, {session.teacher}"

        row += f"\n"

        return row
    
    def checkChosen(self, session_id: int):

        for session in self.assigned:
            if session.id == session_id:
                return True
            
        return False
        

@dataclass
class Class:
    min_limit: int
    max_limit: int
    students: List[Student] = field(default_factory=getDefaultStudents)

    def addStudent(self, student: Student):
        self.students.append(student)

@dataclass(order=True)
class Session:
    id: int
    subject: str
    teacher: str
    presenter: str
    classes: List[Class]

    def getCSVRow(self):
        
        row = f"{self.id}, {self.subject}, {self.teacher}"
        
        for session_class in self.classes:
            num_students = len(session_class.students)
            meets_limits = True if (num_students >= session_class.min_limit and num_students <= session_class.max_limit) else False
            row += f", {len(session_class.students)}, {meets_limits}"

        row += "\n"

        return row

# FUNCTIONS

# Debug function for logging
def debug(statement: str):
    if True:
        print(statement)

# Gets student data and converts to custom defined type
def getStudentData(filename: str):
    
    student_data: List[Student] = []
    
    with open(filename, mode="r") as file:
        reader = csv.reader(file)

        # Initializes metadata
        num_students = 0

        # Reads in lines of file
        for index, row in enumerate(reader):

            if (index == 0): # Gets number of students
                num_students = int(row[1])
                next(reader) # Skips header 
            else:
                student_data.append(
                    Student(
                        timestamp=int(row[0]),
                        first_name=row[1].strip(),
                        last_name=row[2].strip(),
                        homeroom=row[3].strip(),
                        first_period=row[4].strip(),
                        id=int(row[5]),
                        grade=int(row[6]),
                        choices=[int(choice) for choice in [row[7], row[8], row[9], row[10], row[11], row[12], row[13]]]
                    )
                )
            
    return sorted(student_data, reverse=True)

# Gets student data and converts to custom defined type
def getSessionData(filename: str):
    
    session_data: List[Session] = []
    
    with open(filename, mode="r") as file:
        reader = csv.reader(file)

        # Initializes metadata
        num_sessions = 0
        min_students = 0
        max_students = 0
        
        # Reads in lines of file
        for index, row in enumerate(reader):

            if (index == 0): # Gets number of sessions
                num_sessions = int(row[1])
            elif (index == 1): # Gets min students for session
                min_students = int(row[1])
            elif (index == 2): # Gets max students for session
                max_students = int(row[1])
                next(reader) # Skips header
            else:
                session_data.append(
                    Session(
                        id=int(row[0]),
                        subject=row[1].replace("[", "").replace("]", ""),
                        teacher=row[2].strip(),
                        presenter=row[3].strip(),
                        classes = getDefaultClasses(min_limit=min_students, max_limit=max_students)
                    )
                )
            
    return sorted(session_data, reverse=True)

def getSmallClasses(sessions: List[Session], class_index: int):

    def getSortKey(e: Session):
        return len(e.classes[class_index].students)

    return sorted(sessions, key=getSortKey)

def assignStudents(students: List[Student], sessions: List[Session]):

    # Goes through the numebr of classes that need to be assigned
    for class_index in range(NUM_ASSIGNED_CLASSES):

        # Goes through all the students
        for student in students:

            class_assigned = False
            choice_index = 0

            while not class_assigned:
                
                # Checks if they have enough choices left to pick from
                if (choice_index < len(student.choices)):

                    # Gets session
                    session_chosen: Session = sessions[student.choices[choice_index]-1]

                    # Gets class
                    class_chosen: Class = session_chosen.classes[class_index]

                    # Checks if there is room in smallest class and that they havent already taken class
                    if (not student.checkChosen(session_chosen.id)) and (len(class_chosen.students) < class_chosen.max_limit):
                        # Gives student class
                        class_assigned = True
                        class_chosen.addStudent(student=student)
                        student.assignChoice(index=choice_index, sessions=sessions)
                        debug(f"Student (Id: {student.id}) was assigned choice #{choice_index} for class #{class_index}.")
                    else:
                        # Attempts to give them one of other choices
                        choice_index += 1

                else:

                    # In case none of students choices can be filled
                    small_classes: List[Session] = getSmallClasses(sessions=sessions, class_index=class_index)
                    session_chosen: Session = small_classes[choice_index - len(student.choices)]
                    class_chosen: Class = session_chosen.classes[class_index]

                    # Checks if there is room in smallest class and that they havent already taken class
                    if (not student.checkChosen(session_chosen.id)) and (len(class_chosen.students) < class_chosen.max_limit):
                        # Gives student class
                        class_assigned = True
                        class_chosen.addStudent(student=student)
                        student.assignChoice(index=session_chosen.id, sessions=sessions, wasChosen=False)
                        debug(f"Student (Id: {student.id}) was assigned choice #{choice_index} for class #{class_index}.")
                    else:
                        # Lets user know all classes have been filled if the smallest class is full
                        choice_index += 1
                        debug(f"All sessions for class #{class_index} are full.")

    return students

def writeStudentSelectionFile(filename, students: List[Student]):

    # Opens filename for writing
	f, average_score = open(filename, "w"), 0

    # Writes header
	f.write(f"NUM_STUDENTS, {len(students)}\n")
	f.write("FIRST_NAME, LAST_NAME, HR_TEACH, FIRST_PERIOD, STUDENT_ID, GRADE, ")
	f.write("SEL1_ID, SEL1_TEACH, SEL2_ID, SEL2_TEACH, SEL3_ID, SEL3_TEACH, ")
	f.write("SEL4_ID, SEL4_TEACH\n")

	for student in students:
        # Writes row
		f.write(student.getCSVRow());average_score += NUM_CHOICES - len(student.choices)

	f.close();debug(f"Average score: {average_score/len(students)}")

def writeSessionSelectionFile(filename, sessions: List[Session]):

    # Opens filename for writing
	f = open(filename, "w")

    # Writes header
	f.write(f"NUM_SESSIONS, {len(sessions)}\n")
	f.write("SESSION_ID, SUBJECT, TEACHER, CLA1_NUM_STUDENTS, CLA1_REQ, CLA2_NUM_STUDENTS, CLA2_REQ, CLA3_NUM_STUDENTS, CLA3_REQ, CLA4_NUM_STUDENTS, CLA4_REQ\n")

	for session in sessions:
        # Writes row
		f.write(session.getCSVRow())

	f.close()

sessions = getSessionData(filename="sample_data/sessions.csv")
students = getStudentData(filename="sample_data/students.csv")
students = assignStudents(students=students, sessions=sessions)
writeStudentSelectionFile(filename="output/schedule.csv", students=students)
writeSessionSelectionFile(filename="output/updated_sessions.csv", sessions=sessions)
                

