Start Program

Initialize Calendar with 12 months
For each month
    Create a list of days (1 to 31, depending on the month)

Initialize an empty data storage (e.g., database or local encrypted file)

Define function load_entries()
    Load saved entries securely from storage
    If storage does not exist
        Initialize empty entries for each day

Define function save_entries()
    Save all entries securely to storage

Define function create_entry(month, day, title, description, time, notification)
    Add the entry to the correct month and day
    Set up notification for the specified time
    Save entries

Define function view_entries(month, day)
    Display all entries for selected day

Define function set_notification(entry)
    Schedule a system or app notification at entry.time

Define function switch_theme(theme)
    If theme is "light"
        Apply light mode styles
    Else if theme is "dark"
        Apply dark mode styles

Main Menu:
    Display Calendar (with current theme)
    Allow user to:
        - Select a date
        - View entries
        - Create new entry
        - Edit or delete entry
        - Switch between light and dark mode

Background:
    Continuously check if any notification time is due
    If due, show notification for the entry

On Program Close:
    Save all entries securely

End Program
