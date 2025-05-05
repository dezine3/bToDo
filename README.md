![banner](https://github.com/user-attachments/assets/cf43329b-f059-467e-8ab8-6de2d4b74926)
                              

# bToDo — A Simple Desktop Calendar with Event Management

bToDo is a simple yet stylish calendar and event reminder app built with PySide6. It features event notifications, themes, encryption, and backup/export options.

---

## 🖥 Requirements

- Python 3.8+
- PySide6
- pycryptodome
- winotify (Windows only, optional for toast notifications)

Install dependencies with:

    pip install -r requirements.txt

---

## How to Run

1. Open **Command Prompt or terminal**.
2. Navigate to the folder containing the project files:

       cd path\to\bToDo

3. Run the app:

       python main.py

---

## Encrypted Data

All event and settings data is securely encrypted and saved to `britton_data.enc`. Includes sample data.

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

![Screenshot 2025-05-05 165911](https://github.com/user-attachments/assets/227475bf-a4aa-45f8-bb63-4244fccec4d8)
![Screenshot 2025-05-05 165920](https://github.com/user-attachments/assets/09d46422-0e93-4775-8ac3-f7ddb97590e2)
![Screenshot 2025-05-05 165938](https://github.com/user-attachments/assets/de5af0df-923d-4ebf-90a5-c0b7f26eff89)
![Screenshot 2025-05-05 165956](https://github.com/user-attachments/assets/dc2b346c-a64c-493f-9add-4fbe05dc05d2)

---

## License

Created by Patrick Britton. Free to use and modify.
