"""Configuration for Scholarship Application Tracker."""

SPREADSHEET_ID = "1Dzf0VZoaE9u-1Wr4JRtR6VU-p3ZNZ4XbC9AnGXCq9Ss"
# Use export without gid so public sheets return CSV (gid=0 can cause 400)
SHEET_CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv"
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
