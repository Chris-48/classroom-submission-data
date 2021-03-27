from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from connections.connection_errors import IdError


class classroom_connection:


    def __init__(self, credentials):
        self.service = build("classroom", "v1", credentials = credentials)
    

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.service.close()

    def __str__(self):
        return "classroom connetion"

    __repr__ = __str__

    def get_courses(self) -> dict:
        """return a dictionary with the courses and the corresponding id"""

        courses = self.service.courses().list().execute()["courses"]

        return {course["name"] : course["id"] for course in courses}


    def get_courses_activities(self, course_id) -> dict:
        """return a dictionary with the course activities and the corresponding id"""
        
        try:
            activities = self.service.courses().courseWork().list(courseId=course_id).execute()["courseWork"]
        except:
            raise IdError(str(self), course_id)

        return {activity["title"] : activity["id"] for activity in activities}

    
    def get_students(self, course_id) -> dict:
        """return a dictionary with the stundents names and the corresponding id"""
        
        try:
            
            students = self.service.courses().students().list(
                courseId = course_id
            ).execute()["students"]

        except HttpError:
            raise IdError(str(self), course_id)
        
        return {student["profile"]["id"] : student["profile"]["name"]["fullName"] for student in students}


    def submission_data(self, course_id, activity_id, students : dict) -> dict:
        """
        return a dictionary with the stundents names as keys and 'Missing'/'Done' as values acording to the submission state
        
        students: a dict with the students id as keys and students names as values
        """
        
        try:
            
            submissions = self.service.courses().courseWork().studentSubmissions().list(
                courseId = course_id,
                courseWorkId = activity_id
            ).execute()["studentSubmissions"]

        except HttpError:
            raise IdError(str(self), [course_id, activity_id])

        return {students[ submission["userId"] ] : "Missing" if  submission["state"]== "CREATED" else "Done" for submission in submissions}
