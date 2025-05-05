# File: data_manager.py
# bToDo - Created by Patrick Britton
# Date: 2025-04-28
# Updated: 2025-04-29 (Added style_name to default settings)

import base64
import json
import os
import sys

# PyCryptodome imports
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes # Note: Imported but not used in provided code

# Constants (Consider moving defaults here if shared across modules)
DEFAULT_STYLE = "Default Light"
DEFAULT_ACCENT_COLOR = "#2A82DA"

class DataManager:
    def __init__(self, data_file='britton_data.enc'):
        self.data_file = data_file
        self.events = []
        # Default settings - Added 'style_name'
        self.settings = {
            "theme": "light", # Kept for potential fallback/simplicity
            "accent_color": DEFAULT_ACCENT_COLOR,
            "style_name": DEFAULT_STYLE
        }
        # Hardcoded passphrase and salt - Not recommended for production
        self._passphrase = "BrittonCalendarDefaultKey"
        salt = b"britton_calendar_salt"
        # Derive encryption key using PBKDF2
        try:
            self._key = PBKDF2(self._passphrase.encode('utf-8'), salt, dkLen=32, count=100_000, hmac_hash_module=SHA256)
        except Exception as e:
            print(f"FATAL: Failed to derive encryption key: {e}", file=sys.stderr)
            # Indicate failure; methods using _key should check or will raise errors
            self._key = None
            # Alternatively, exit or raise a critical error:
            # raise RuntimeError(f"FATAL: Failed to derive encryption key: {e}") from e

        # Load existing data if the file exists and key derivation succeeded
        if self._key and os.path.exists(self.data_file):
            try:
                self._load_from_file()
            except Exception as e: # Keep broad exception for loading
                print(f"Warning: Failed to load data file '{self.data_file}': {e}", file=sys.stderr)
                # Reset to defaults on load failure to ensure consistent state
                self.events = []
                self.settings = { # Reset to defaults including style_name
                     "theme": "light",
                     "accent_color": DEFAULT_ACCENT_COLOR,
                     "style_name": DEFAULT_STYLE
                }

    def _encrypt_data(self, plaintext_bytes):
        """Encrypts plaintext bytes using AES-EAX."""
        if not self._key:
             raise RuntimeError("Encryption key is not available.")
        cipher = AES.new(self._key, AES.MODE_EAX) # EAX mode creates nonce automatically
        ciphertext, tag = cipher.encrypt_and_digest(plaintext_bytes)
        # Return nonce, tag, and ciphertext needed for decryption
        return cipher.nonce, tag, ciphertext

    def _decrypt_data(self, nonce, tag, ciphertext):
        """Decrypts ciphertext using AES-EAX."""
        if not self._key:
             raise RuntimeError("Encryption key is not available.")
        cipher = AES.new(self._key, AES.MODE_EAX, nonce=nonce)
        # Decrypt and verify integrity using the tag
        plaintext = cipher.decrypt_and_verify(ciphertext, tag) # Raises ValueError on failure
        return plaintext

    def _load_from_file(self):
        """Loads and decrypts data from the data file."""
        if not self._key:
             print("Warning: Cannot load data, encryption key is not available.", file=sys.stderr)
             return # Avoid proceeding without a key

        try:
            with open(self.data_file, 'rb') as f:
                file_bytes = f.read()
        except IOError as e:
             raise IOError(f"Failed to read data file '{self.data_file}': {e}") from e

        # Basic check for minimum length (nonce + tag)
        # AES-EAX nonce is 16 bytes, tag is 16 bytes
        if len(file_bytes) < 32:
            raise ValueError(f"Data file '{self.data_file}' is too short.")

        # Extract nonce, tag, and ciphertext from the file bytes
        nonce, tag, ciphertext = file_bytes[:16], file_bytes[16:32], file_bytes[32:]

        try:
            # Decrypt the data
            plaintext = self._decrypt_data(nonce, tag, ciphertext)
            # Decode from UTF-8 and parse JSON
            data = json.loads(plaintext.decode('utf-8'))

            # Update events and settings, providing defaults if keys are missing
            # Ensures that if new settings are added later, old files load with defaults
            loaded_events = data.get('events', [])
            # Basic validation: ensure events is a list
            self.events = loaded_events if isinstance(loaded_events, list) else []

            loaded_settings = data.get('settings', {})
            # Ensure settings is a dict and merge with defaults (loaded values override)
            default_settings = {
                "theme": "light",
                "accent_color": DEFAULT_ACCENT_COLOR,
                "style_name": DEFAULT_STYLE
            }
            if isinstance(loaded_settings, dict):
                default_settings.update(loaded_settings) # Update defaults with loaded values
            self.settings = default_settings

        except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as e:
            # Handle specific errors during decryption/parsing
            raise ValueError(f"Failed to decrypt or parse data file '{self.data_file}': {e}") from e
        except Exception as e: # Catch-all for other potential errors (like Crypto errors)
            raise RuntimeError(f"An unexpected error occurred loading data: {e}") from e


    def save_to_file(self):
        """Encrypts and saves the current events and settings to the data file."""
        if not self._key:
             print("Error: Cannot save data, encryption key is not available.", file=sys.stderr)
             # Consider raising an exception to make the failure explicit
             raise RuntimeError("Cannot save data: Encryption key unavailable.")

        # Prepare data dictionary using current state
        data = {"events": self.events, "settings": self.settings}

        try:
            # Serialize data to JSON string, encode to bytes
            # Use indent for readability if decrypted manually, but makes file larger
            plaintext = json.dumps(data, ensure_ascii=False, indent=None).encode('utf-8')
            # Encrypt the plaintext bytes
            nonce, tag, ciphertext = self._encrypt_data(plaintext)
            # Write the nonce, tag, and ciphertext concatenated to the file
            # Use a temporary file and rename for atomic write (safer)
            temp_file_path = self.data_file + ".tmp"
            with open(temp_file_path, 'wb') as f:
                f.write(nonce + tag + ciphertext)
            os.replace(temp_file_path, self.data_file) # Atomic replace if possible

        except TypeError as e:
            print(f"Error: Failed to serialize data to JSON before saving: {e}", file=sys.stderr)
            # Potentially inspect self.events or self.settings for non-serializable data
        except (IOError, OSError) as e:
            print(f"Error: Failed to write data file '{self.data_file}': {e}", file=sys.stderr)
            # Attempt to clean up temporary file if rename failed
            if os.path.exists(temp_file_path):
                 try: os.remove(temp_file_path)
                 except OSError: pass
        except Exception as e: # Catch other errors (e.g., encryption)
            print(f"Error: An unexpected error occurred during save: {e}", file=sys.stderr)


    def add_event(self, event):
        """Adds an event to the list and saves."""
        if not isinstance(event, dict):
             print("Error: Attempted to add non-dictionary event.", file=sys.stderr)
             return
        self.events.append(event)
        try:
            self.save_to_file()
        except Exception as e:
            # If save fails, consider rolling back the add?
            print(f"Error saving after adding event: {e}", file=sys.stderr)
            self.events.pop() # Basic rollback: remove the just-added event
            raise # Re-raise the exception from save_to_file

    def update_event(self, event_id, updated_event):
        """Updates an existing event identified by event_id and saves."""
        if not isinstance(updated_event, dict):
             print("Error: Attempted to update with non-dictionary event data.", file=sys.stderr)
             return
        original_event = None
        found_index = -1
        for i, ev in enumerate(self.events):
            if ev.get('id') == event_id:
                original_event = ev.copy() # Store copy for potential rollback
                found_index = i
                self.events[i] = updated_event
                break
        if found_index == -1:
            print(f"Warning: Event ID '{event_id}' not found for update.", file=sys.stderr)
            # Don't save if nothing was updated
            return
        try:
            self.save_to_file()
        except Exception as e:
            print(f"Error saving after updating event {event_id}: {e}", file=sys.stderr)
            # Rollback the update if save fails
            if found_index != -1 and original_event is not None:
                self.events[found_index] = original_event
            raise


    def delete_event(self, event_id):
        """Deletes an event identified by event_id and saves."""
        original_length = len(self.events)
        # Filter list, preserving original order
        original_events = self.events[:] # Create shallow copy for potential rollback
        self.events = [ev for ev in self.events if ev.get('id') != event_id]
        deleted = len(self.events) < original_length

        if not deleted:
            print(f"Warning: Event ID '{event_id}' not found for deletion.", file=sys.stderr)
            # Don't save if nothing changed
            return False # Indicate event not found/deleted

        try:
            self.save_to_file()
            return True # Indicate successful deletion and save
        except Exception as e:
            print(f"Error saving after deleting event {event_id}: {e}", file=sys.stderr)
            # Rollback the deletion if save fails
            self.events = original_events
            raise # Re-raise the exception from save_to_file


    def backup_to_file(self, backup_path):
        """Saves the current state and copies the data file to a backup location."""
        try:
            # Ensure the main file is up-to-date before copying
            self.save_to_file()
        except Exception as e:
             # If saving fails, maybe we shouldn't proceed with backup?
             print(f"Error: Failed to save current state before backup: {e}", file=sys.stderr)
             raise RuntimeError(f"Backup cancelled because saving current state failed: {e}") from e

        try:
            # Copy the encrypted data file
            with open(self.data_file, 'rb') as original, open(backup_path, 'wb') as backup:
                # Read in chunks for potentially large files
                chunk_size = 65536 # 64k
                while True:
                    chunk = original.read(chunk_size)
                    if not chunk:
                        break
                    backup.write(chunk)
        except FileNotFoundError:
             # This shouldn't happen if save_to_file succeeded, but handle defensively
             print(f"Error: Main data file '{self.data_file}' not found for backup.", file=sys.stderr)
             raise
        except IOError as e:
             print(f"Error: Failed to read/write during backup to '{backup_path}': {e}", file=sys.stderr)
             raise
        except Exception as e: # Catch other unexpected errors
             print(f"Error: An unexpected error occurred during backup file copy: {e}", file=sys.stderr)
             raise


    def export_to_ics(self, ics_path):
        """Exports calendar events to an iCalendar (.ics) file."""
        # Import datetime locally as in original
        from datetime import datetime, time, timedelta

        # Inner function for formatting date/time strings
        def format_dt_for_ics(date_str, time_str):
            """Formats date and optional time for iCal DTSTART/DTEND.
               Returns tuple: (formatted_string, is_date_only)
            """
            try:
                base_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if time_str:
                    # Parse 'hh:mm AP' format
                    ev_time = datetime.strptime(time_str, "%I:%M %p").time()
                    dt = datetime.combine(base_date, ev_time)
                    # Format as UTC (naive conversion, assumes local time = UTC)
                    # TODO: Implement proper timezone handling if needed
                    return dt.strftime("%Y%m%dT%H%M%SZ"), False
                else:
                    # Format as YYYYMMDD for date-only events
                    return base_date.strftime("%Y%m%d"), True
            except ValueError as e:
                print(f"Warning: Could not format date/time for iCal: {date_str} {time_str} ({e})", file=sys.stderr)
                return "INVALID_DATE_FORMAT", True


        # iCalendar header lines
        ics_lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//bToDo//EN", # Keep original PRODID
            "CALSCALE:GREGORIAN",
            # Optionally add timezone information here if times are not UTC
            # "BEGIN:VTIMEZONE", ... "END:VTIMEZONE"
        ]

        # Process each event
        events_exported = 0
        for ev in self.events:
            ev_date = ev.get('date')
            ev_time = ev.get('time') # hh:mm AP format or empty

            if not ev_date:
                print(f"Warning: Skipping event for iCal export due to missing date: {ev.get('title')}", file=sys.stderr)
                continue

            dtstart_str, is_date_only = format_dt_for_ics(ev_date, ev_time)

            if dtstart_str == "INVALID_DATE_FORMAT":
                 print(f"Warning: Skipping event for iCal export due to invalid date/time format: {ev.get('title')}", file=sys.stderr)
                 continue

            # Generate unique ID and timestamp
            uid_base = ev.get('id', str(hash(ev.get('title', '') + ev_date)))
            uid = f"{uid_base}@brittoncalendar.local" # Make UID more unique
            dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

            summary = ev.get('title', 'No Title')
            description = ev.get('description', '')
            # Escape necessary characters in text fields for iCal format
            summary = summary.replace("\\", "\\\\").replace("\n", "\\n").replace(",", "\\,").replace(";", "\\;")
            description = description.replace("\\", "\\\\").replace("\n", "\\n").replace(",", "\\,").replace(";", "\\;")

            # Build VEVENT lines
            ics_lines.append("BEGIN:VEVENT")
            ics_lines.append(f"UID:{uid}")
            ics_lines.append(f"DTSTAMP:{dtstamp}")

            if is_date_only:
                # For all-day events, use VALUE=DATE property
                ics_lines.append(f"DTSTART;VALUE=DATE:{dtstart_str}")
                # DTEND for all-day is typically the start of the *next* day
                try:
                    end_date = datetime.strptime(dtstart_str, "%Y%m%d").date() + timedelta(days=1)
                    ics_lines.append(f"DTEND;VALUE=DATE:{end_date.strftime('%Y%m%d')}")
                except ValueError:
                     # Fallback if date parsing failed somehow
                     print(f"Warning: Could not calculate DTEND for all-day event {summary}", file=sys.stderr)
                     ics_lines.append(f"DTEND;VALUE=DATE:{dtstart_str}") # Use start date
            else:
                # For events with specific times (assuming UTC as formatted)
                ics_lines.append(f"DTSTART:{dtstart_str}")
                # DTEND: iCal requires duration or end time. Assume 1 hour duration for now.
                try:
                    start_dt_obj = datetime.strptime(dtstart_str, "%Y%m%dT%H%M%SZ")
                    end_dt_obj = start_dt_obj + timedelta(hours=1)
                    ics_lines.append(f"DTEND:{end_dt_obj.strftime('%Y%m%dT%H%M%SZ')}")
                except ValueError:
                     print(f"Warning: Could not calculate DTEND for timed event {summary}", file=sys.stderr)
                     ics_lines.append(f"DTEND:{dtstart_str}") # Use start time as fallback


            ics_lines.append(f"SUMMARY:{summary}")
            if description: # Only add description if it's not empty
                ics_lines.append(f"DESCRIPTION:{description}")
            # TODO: Add ALARM component if ev.get('notify') is True?

            ics_lines.append("END:VEVENT")
            events_exported += 1

        # iCalendar footer
        ics_lines.append("END:VCALENDAR")

        # Check if any events were actually added before writing
        if events_exported == 0:
             print("Info: No valid events found to export.", file=sys.stderr)
             # Maybe raise an error or return False instead of writing an empty calendar?
             # For now, we write the empty structure.

        try:
            # Write the combined lines to the specified file
            # Use UTF-8 encoding and standard CRLF line endings for iCal
            with open(ics_path, 'w', encoding='utf-8', newline='\r\n') as f:
                f.write("\r\n".join(ics_lines))
        except IOError as e:
             print(f"Error: Failed to write iCal file to '{ics_path}': {e}", file=sys.stderr)
             raise # Re-raise IO error
        except Exception as e: # Catch other unexpected errors
             print(f"Error: An unexpected error occurred during iCal export: {e}", file=sys.stderr)
             raise # Re-raise other errors


    def get_event_by_id(self, event_id):
        """Retrieves an event dictionary by its ID."""
        # Simple linear search
        for ev in self.events:
            if ev.get('id') == event_id:
                return ev # Return the matching event dictionary
        return None # Return None if no event with the given ID is found