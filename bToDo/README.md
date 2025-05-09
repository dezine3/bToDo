
 __       ______          ____              
/\ \     /\__  _\        /\  _`\            
\ \ \____\/_/\ \/    ___ \ \ \/\ \    ___   
 \ \ '__`\  \ \ \   / __`\\ \ \ \ \  / __`\ 
  \ \ \*\ \  \ \ \ /\ \*\ \\ \ \_\ \/\ \*\ \
   \ \_,__/   \ \_\\ \____/ \ \____/\ \____/
    \/___/     \/_/ \/___/   \/___/  \/___/ 
                                            

# bToDo — A Simple Desktop Calendar with Event Management

v0.1.0-alpha
Updated 5/5/2025

github: https://github.com/patbritton/bToDo

bToDo is a simple yet stylish calendar and event reminder app built with PySide6. It features event notifications, themes, encryption, and backup/export options.

---

## Requirements

- Python 3.8+
- PySide6
- pycryptodome
- winotify (Windows only, optional for toast notifications)

Install dependencies with:

    pip install -r requirements.txt

---

##  How to Run

1. Open **Command Prompt**.
2. Navigate to the folder containing the project files:

       cd path\to\bToDo

3. Run the app:

       python main.py

---

OR:

Find the Windows installer file at \Installer\bToDo_Setup.exe

## Encrypted Data

All event and settings data is securely encrypted and saved to `britton_data.enc`.

---

## Files Included

- `main.py` — Entry point
- `main_window.py` — GUI and logic
- `data_manager.py` — Handles event data and encryption
- `notification_manager.py` — Manages Windows notifications

---

## Features

- Add, edit, and delete events
- Event reminders with toast notifications
- Encrypted local storage
- Export to iCalendar (.ics)
- Theming support (light/dark/custom styles)

---

## License

Created by Patrick Britton. 

MIT License (license.txt)