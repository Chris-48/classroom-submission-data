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
        """Return the ID of the user"""

        return self.service.userProfiles().get(userId="me", fields="id").execute()["id"]


    def get_courses(self) -> dict:
        """Return a dictionary with the courses and the corresponding id"""

        courses = {}
        next_page_token = None

        while True:
            response = self.service.courses().list(
                pageToken=next_page_token, 
                fields="nextPageToken,courses(name,id)"
            ).execute()

            courses.update({course["name"] : course["id"] for course in response["courses"]})

            next_page_token = response.get("nextPageToken")

            if next_page_token is None:
                break

        return courses        

    def get_course_activities(self, course_id) -> dict:
        """Return a dictionary with the course activities and the corresponding id"""

        activities = {}
        next_page_token = None

        while True:
            response = self.service.courses().courseWork().list(
                pageToken=next_page_token,
                courseId=course_id, 
                fields="nextPageToken,courseWork(title, id)"
            ).execute()

            activities.update({activity["title"] : activity["id"] for activity in response["courseWork"]})

            next_page_token = response.get("nextPageToken")

            if next_page_token is None:
                break
        
        return activities

    def get_course_topics(self, course_id) -> dict:
        """Return a dictionary with the topics of the course and the corresponding id"""
        
        topics = {}
        next_page_token = None

        while True:
            response = self.service.courses().topics().list(
                pageToken=next_page_token,
                courseId=course_id, 
                fields="nextPageToken,topic(name,topicId)"
            ).execute()

            topics.update({topic["name"] : topic["topicId"] for topic in response["topic"]})
            
            next_page_token = response.get("nextPageToken")

            if next_page_token is None:
                break
        
        return topics


    def get_activities_from_topic(self, course_id, topic_id) -> dict:
        """Return a dictionary with the course activities and the corresponding id"""
    
        activities = {}
        next_page_token = None

        while True:
            response = self.service.courses().courseWork().list(
                pageToken=next_page_token,
                courseId=course_id, 
                fields="nextPageToken,courseWork(title,id,topicId)"
            ).execute()

            activities.update({activity["title"] : activity["id"] for activity in response["courseWork"] if activity.get("topicId", None) == topic_id})
            
            next_page_token = response.get("nextPageToken")

            if next_page_token is None:
                break

        return activities

    
    def get_students(self, course_id) -> dict:
        """Return a dictionary with the stundents names and the corresponding id"""

        students = {}
        next_page_token = None

        while True:
            response = self.service.courses().students().list(
                pageToken=next_page_token,
                courseId = course_id,
                fields="nextPageToken,students(profile/id,profile/name/fullName)"
            ).execute()
            
            students.update({student["profile"]["id"] : student["profile"]["name"]["fullName"] for student in response["students"]})

            next_page_token = response.get("nextPageToken")

            if next_page_token is None:
                break

        return students


    def submission_data(self, course_id, activity_id, students : dict) -> dict:
        """
        Return a dictionary with the stundents names as keys and 'Missing'/'Done' as values acording to the submission state
        
        students: a dict with the students id as keys and students names as values
        """        
        
        submissions = {}
        next_page_token = None

        while True:
            response = self.service.courses().courseWork().studentSubmissions().list(
                courseId = course_id,
                courseWorkId = activity_id,
                fields="nextPageToken,studentSubmissions(userId,state)"
            ).execute()

            submissions.update({students[ submission["userId"] ] : "Missing" if  submission["state"] == "CREATED" else "Done" for submission in response["studentSubmissions"]})            

            next_page_token = response.get("nextPageToken")

            if next_page_token is None:
                break

        return submissions

