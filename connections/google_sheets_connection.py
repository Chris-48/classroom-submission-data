from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from connections.connection_errors import IdError
from connections.connection_errors import CreateSpreadSheetError


class google_sheets_connection:


    def __init__(self, credentials):
        self.service = build("sheets", "v4", credentials = credentials)


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.service.close()

    def __str__(self):
        return "google sheets connection"

    __repr__ = __str__

    def create_spread_sheet(self, title: str) -> str:
        """create a spread sheet and return its id"""
        
        try:

            # create a dict so it can be given for the body param to add the title
            spreadsheet = {
                'properties': 
                {
                    'title': title
                }
            }

            # create the spread sheet
            spread_sheet = self.service.spreadsheets().create(body=spreadsheet).execute()
        
        except:
            raise CreateSpreadSheetError()
        
        return spread_sheet["spreadsheetId"]

    
    def append(self, data: dict, spread_sheet_id, start_sheet="A1"):
        """append data to the given spread sheet"""

        # rearrange the data so it can be added to the spread sheet
        values = (
            (
            tuple(name for name in data.keys()),
            tuple(state for state in data.values())
            )
        )
        
        values_range_body = {
            "majorDimension": "COLUMNS",
            "values": values
        }

        # append the data to the spread sheet
        try:
            self.service.spreadsheets().values().append(
                spreadsheetId = spread_sheet_id,
                valueInputOption = "USER_ENTERED",
                range = start_sheet,
                body = values_range_body
            ).execute()

        except HttpError:
            if start_sheet != "A1":
                print(f"{start_sheet} might be a invalid sheet") 
      
            raise IdError(str(self), spread_sheet_id)