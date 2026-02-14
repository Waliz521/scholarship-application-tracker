"""Configuration for Scholarship Application Tracker."""

SPREADSHEET_ID = "1Dzf0VZoaE9u-1Wr4JRtR6VU-p3ZNZ4XbC9AnGXCq9Ss"
SHEET_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"
)

COLUMNS = [
    "university",
    "program",
    "scholarship",
    "deadline",
    "application_date",
    "application_status",
    "point_of_entry",
    "country",
    "link",
]

LOCAL_CSV_PATH = "scholarships_export.csv"
