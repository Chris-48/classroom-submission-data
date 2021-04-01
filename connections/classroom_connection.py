from googleapiclient.discovery import build


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


    def get_user_id(self) -> str:
        """return the ID of the user"""

        return self.service.userProfiles().get(userId="me", fields="id").execute()["id"]


    def get_courses(self) -> dict:
        """return a dictionary with the courses and the corresponding id"""

        courses = self.service.courses().list(fields="courses(name,id)").execute()["courses"]

        if courses:
            return {course["name"] : course["id"] for course in courses}
        return None


    def get_courses_activities(self, course_id) -> dict:
        """return a dictionary with the course activities and the corresponding id"""

        activities = self.service.courses().courseWork().list(
            courseId=course_id, 
            fields="courseWork(title, id)"
        ).execute()["courseWork"]

        if activities:
            return {activity["title"] : activity["id"] for activity in activities}
        return None


    def get_courses_topics(self, course_id) -> dict:
        """return a dictionary with the topics of the course and the corresponding id"""

        topics = self.service.courses().topics().list(
            courseId=course_id, 
            fields="topic(name,topicId)"
        ).execute()["topic"]

        if topics:
            return {topic["name"] : topic["topicId"] for topic in topics}
        return None


    def get_activities_from_topic(self, course_id, topic_id) -> dict:
        """return a dictionary with the course activities and the corresponding id"""
    
        activities = self.service.courses().courseWork().list(
            courseId=course_id, 
            fields="courseWork(title,id,topicId)"
        ).execute()["courseWork"]      

        if activities:
            return {activity["title"] : activity["id"] for activity in activities if activity.get("topicId", None) == topic_id}
        return None

    
    def get_students(self, course_id) -> dict:
        """return a dictionary with the stundents names and the corresponding id"""
    
        students = self.service.courses().students().list(
            courseId = course_id,
            fields="students(profile/id,profile/name/fullName)"
        ).execute()["students"]
        
        if students:
            return {student["profile"]["id"] : student["profile"]["name"]["fullName"] for student in students}
        return None


    def submission_data(self, course_id, activity_id, students : dict) -> dict:
        """
        return a dictionary with the stundents names as keys and 'Missing'/'Done' as values acording to the submission state
        
        students: a dict with the students id as keys and students names as values
        """        
        
        submissions = self.service.courses().courseWork().studentSubmissions().list(
            courseId = course_id,
            courseWorkId = activity_id,
            fields="studentSubmissions(userId,state)"
        ).execute()["studentSubmissions"]

        if submissions:
            return {students[ submission["userId"] ] : "Missing" if  submission["state"] == "CREATED" else "Done" for submission in submissions}
        return None
