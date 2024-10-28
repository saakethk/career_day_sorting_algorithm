
import csv
from dataclasses import dataclass, field
from typing import List

# CONSTANTS

NUM_ASSIGNED_CLASSES = 4 # Number of classes to assign to each student
NUM_CHOICES = 7 # Number of choices for student
SPECIAL_SESSIONS = [44, 45, 46]

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
    choices_given: List[int] = 0
    
    # Assigns student choice they chose
    def assignChoice(self, index: int, sessions: dict, wasChosen: bool = True):

        if (wasChosen):
            assigned_choice = self.choices.pop(index)
            self.choices_given += 1
            chosen_session: Session = sessions[assigned_choice]
        else:
            chosen_session: Session = sessions[index]

        self.assigned.append(
            CondensedSession(
                id=chosen_session.id,
                subject=chosen_session.subject,
                teacher=chosen_session.teacher,
                presenter=chosen_session.presenter
            )
        )

        debug(self.assigned)

    # Gets csv formatted row
    def getCSVRow(self):
        
        row = f"{self.first_name}, {self.last_name}, {self.homeroom}, {self.first_period}, {self.id}, {self.grade}"
        
        for session in self.assigned:
            row += f", {session.id}, {session.teacher}"

        row += f"\n"

        return row
    
    # Checks whether the student has already chosen a session
    def checkChosen(self, session_id: int):

        for session in self.assigned:
            if session.id == session_id:
                debug("match")
                debug(session_id)
                debug(session.id)
                return False
            
        return True
        

@dataclass
class Class:
    min_limit: int
    max_limit: int
    students: List[Student] = field(default_factory=getDefaultStudents)

    # Adds a student to class
    def addStudent(self, student: Student):
        self.students.append(student)

    # Check how many students are still needed in class
    def needsStudents(self):
        if (len(self.students) < self.min_limit):
            return self.min_limit - len(self.students)
        else:
            return 0

@dataclass(order=True)
class Session:
    id: int
    subject: str
    teacher: str
    presenter: str
    classes: List[Class]

    # Checks whether student meets requirement for special session
    def checkStudent(self, student: Student):

        if (self.id in SPECIAL_SESSIONS) and (student.grade >= 9):
            return True
        elif (self.id in SPECIAL_SESSIONS) and (student.grade <= 9):
            return False
        else:
            return True


    # Gets csv formatted row
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
    if False:
        print(statement)

# Gets student data and converts to custom defined type
def getStudentData(filename: str):

    # Sort function
    def sortStudents(student: Student):
        # return student.timestamp
        return student.grade + ((student.timestamp / 1000000000) * 2)

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
                        choices=[int(row[choice]) for choice in range(7, len(row))]
                    )
                )
            
    return sorted(student_data, reverse=True)

# Gets student data and converts to custom defined type
def getSessionData(filename: str):
    
    session_data: dict = {}
    
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
                session_data[int(row[0])] = Session(
                    id=int(row[0]),
                    subject=row[1].replace("[", "").replace("]", ""),
                    teacher=row[2].strip(),
                    presenter=row[3].strip(),
                    classes = getDefaultClasses(min_limit=min_students, max_limit=max_students)
                )
            
    return session_data

# Gets sorted list of sessions based on class size
def getSmallClasses(sessions: dict, class_index: int):

    sessions: List[Session] = sessions.values()  

    def getSortKey(e: Session):
        return len(e.classes[class_index].students)

    return sorted(sessions, key=getSortKey)

# Gets sorted list of sessions based on class size
def getSmallSpecialClasses(sessions: dict, class_index: int):

    sessions: List[Session] = sessions.values()  
    filtered_sessions: List[Session] = []

    for session in sessions:
        if session.id in SPECIAL_SESSIONS:
            filtered_sessions.append(session)

    def getSortKey(e: Session):
        return len(e.classes[class_index].students)

    return sorted(filtered_sessions, key=getSortKey)

def getSpecialSessionStudentsRemaining(sessions: List[Session], class_index: int):

    students_needed: int = 0

    for session in sessions:
        if session.id in SPECIAL_SESSIONS:
            chosen_class = session.classes[class_index]
            students_needed += chosen_class.needsStudents()

    return students_needed

# Decides whether small classes need to be prioritized
def prioritizeSmallClasses(sessions: dict, class_index: int, student: Student, middle_school_students_remaining: int, high_school_students_remaining: int, active: bool):

    if (active):
        if (student.grade < 9):
            middle_school_students_needed: int = 0
            sessions: List[Session] = getSmallClasses(sessions, class_index)

            for session in sessions:
                chosen_class = session.classes[class_index]
                if (session.id not in SPECIAL_SESSIONS):
                    middle_school_students_needed += chosen_class.needsStudents()

            return (middle_school_students_remaining <= middle_school_students_needed)
        else:
            high_school_students_needed: int = 0
            sessions: List[Session] = getSmallClasses(sessions, class_index)

            for session in sessions:
                chosen_class = session.classes[class_index]
                if (session.id in SPECIAL_SESSIONS):
                    high_school_students_needed += chosen_class.needsStudents()

            return (high_school_students_remaining <= high_school_students_needed)

    else:
        return False, False
    
def getStudentsSortedByChoices(students: List[Student]):

    def getSortKey(e: Student):
        return e.choices_given

    return sorted(students, key=getSortKey, reverse=True)
    
def getNumMiddleSchoolStudents(students: List[Student]):

    num_students: int = 0

    for student in students:
        if student.grade < 9:
            num_students += 1

    return num_students

def getNumHighSchoolStudents(students: List[Student]):

    num_students: int = 0

    for student in students:
        if student.grade >= 9:
            num_students += 1

    return num_students

def fillClasses(students: List[Student], sessions: List[Session]):

    students = getStudentsSortedByChoices(students)
    
    for class_index in range(NUM_ASSIGNED_CLASSES):
        special_sessions = getSmallSpecialClasses(sessions, class_index)
        for session in special_sessions:
            chosen_class = session.classes[class_index]
            while (chosen_class.needsStudents() != 0):
                # print(session.id)
                print(chosen_class.needsStudents())
                for student in students:
                    if (student.grade >= 9) and (student.checkChosen(session.id)):
                        student.assigned[class_index] = CondensedSession(
                            id=session.id,
                            subject=session.subject,
                            teacher=session.teacher,
                            presenter=session.presenter
                        )
                        chosen_class.addStudent(student=student)
                        break

    students = getStudentsSortedByChoices(students)

    for class_index in range(NUM_ASSIGNED_CLASSES):
        special_sessions = getSmallClasses(sessions, class_index)
        for session in special_sessions:
            chosen_class = session.classes[class_index]
            while (chosen_class.needsStudents() != 0):
                # print(session.id)
                print(chosen_class.needsStudents())
                for student in students:
                    if (student.checkChosen(session.id)):
                        student.assigned[class_index] = CondensedSession(
                            id=session.id,
                            subject=session.subject,
                            teacher=session.teacher,
                            presenter=session.presenter
                        )
                        chosen_class.addStudent(student=student)
                        break

    return students

# Assigns students to classes
def assignStudents(students: List[Student], sessions: List[Session], prioritize_small_classes: bool, account_for_special_sessions: bool):

    # Goes through the numebr of classes that need to be assigned
    for class_index in range(NUM_ASSIGNED_CLASSES):

        middle_school_students_remaining = getNumMiddleSchoolStudents(students)
        high_school_students_remaining = getNumHighSchoolStudents(students)

        # Goes through all the students
        for student in students:

            class_assigned = False
            choice_index = 0

            while not class_assigned:
                
                # Checks if they have enough choices left to pick from
                if (choice_index < len(student.choices)) and (not prioritizeSmallClasses(sessions, class_index, student, middle_school_students_remaining, high_school_students_remaining, prioritize_small_classes)):

                    # Gets session
                    session_chosen: Session = sessions[student.choices[choice_index]]

                    # Gets class
                    class_chosen: Class = session_chosen.classes[class_index]

                    # Checks if they have already chose class and if class has room
                    if student.checkChosen(session_chosen.id) and session_chosen.checkStudent(student) and(len(class_chosen.students) < class_chosen.max_limit):
                        # Gives student class
                        class_assigned = True
                        class_chosen.addStudent(student=student)
                        student.assignChoice(index=choice_index, sessions=sessions)
                        if (student.grade < 9):
                            middle_school_students_remaining -= 1
                        else:
                            high_school_students_remaining -=1
                        debug(f"CHOICE - Student (Id: {student.id}) was assigned choice #{choice_index} for class #{class_index}. - {high_school_students_remaining}, {middle_school_students_remaining}")
                    else:
                        # Attempts to give them one of other choices
                        choice_index += 1

                else:


                    # In case none of students choices can be filled

                    if (choice_index - len(student.choices)) < 0:
                        selection_index = 0
                    else:
                        selection_index = choice_index - len(student.choices)

                    if (student.grade > 8) and (selection_index < len(SPECIAL_SESSIONS)):
                        small_classes: List[Session] = getSmallSpecialClasses(sessions=sessions, class_index=class_index)
                    else:
                        small_classes: List[Session] = getSmallClasses(sessions=sessions, class_index=class_index)

                    session_chosen: Session = small_classes[selection_index]
                    class_chosen: Class = session_chosen.classes[class_index]

                    # Checks if there is room in smallest class and that they havent already taken class
                    if student.checkChosen(session_chosen.id) and session_chosen.checkStudent(student) and (len(class_chosen.students) < class_chosen.max_limit):
                        # Gives student class
                        class_assigned = True
                        class_chosen.addStudent(student=student)
                        student.assignChoice(index=session_chosen.id, sessions=sessions, wasChosen=False)
                        if (student.grade < 9):
                            middle_school_students_remaining -= 1
                        else:
                            high_school_students_remaining -=1
                        debug(f"SMALL - Student (Id: {student.id}) was assigned choice #{choice_index} for class #{class_index}.")
                    else:
                        # Lets user know all classes have been filled if the smallest class is full
                        choice_index += 1
                        debug(f"All sessions for class #{class_index} are full.")

    return fillClasses(students, sessions)

# Writes the student selection file
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

# Writes the student session selection file
def writeSessionSelectionFile(filename, sessions: dict):

    # Opens filename for writing
	f = open(filename, "w")

    # Writes header
	f.write(f"NUM_SESSIONS, {len(sessions)}\n")
	f.write("SESSION_ID, SUBJECT, TEACHER, CLA1_NUM_STUDENTS, CLA1_REQ, CLA2_NUM_STUDENTS, CLA2_REQ, CLA3_NUM_STUDENTS, CLA3_REQ, CLA4_NUM_STUDENTS, CLA4_REQ\n")

	for index in range(1, len(sessions.values())+1):
        # Writes row
		f.write(sessions[index].getCSVRow())

	f.close()

# Sample Data
# sessions = getSessionData(filename="sample_data/sessions.csv")
# students = getStudentData(filename="sample_data/students.csv")

# Real Data
sessions = getSessionData(filename="real_data/sessions.csv")
students = getStudentData(filename="real_data/students.csv")

students = assignStudents(students=students, sessions=sessions, prioritize_small_classes=True, account_for_special_sessions=True)
writeStudentSelectionFile(filename="output/schedule.csv", students=students)
writeSessionSelectionFile(filename="output/updated_sessions.csv", sessions=sessions)
print("Done")
                

