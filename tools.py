



"""
CSC-128 Assignment 7 starter: the tools and their schemas
Student Name: Jamil Jordan
"""

import json

# Local state tracking open slots across the calendar week
AVAILABILITY = {
    "Monday": ["214", "216", "220"],
    "Tuesday": ["101", "105", "214"],
    "Wednesday": ["302", "304"],
    "Thursday": ["101", "220"],
    "Friday": ["105", "216", "302"],
    "Saturday": [],
    "Sunday": []
}

HOURS_DATA = {
    "Monday": "8:00 AM - 9:00 PM",
    "Tuesday": "8:00 AM - 9:00 PM",
    "Wednesday": "8:00 AM - 9:00 PM",
    "Thursday": "8:00 AM - 9:00 PM",
    "Friday": "8:00 AM - 5:00 PM",
    "Saturday": "10:00 AM - 4:00 PM",
    "Sunday": "Closed"
}

# --- Tool 1: Read-Only Check Availability ---
def check_availability(day: str) -> str:
    """Returns which rooms are free. Handles variations in day name casing and bad day inputs."""
    day_clean = day.strip().capitalize()
    if day_clean not in AVAILABILITY:
        return f"Error: '{day}' is not a valid day of the week. Please use a full weekday name like 'Monday'."
    
    rooms = AVAILABILITY[day_clean]
    if not rooms:
        return f"There are no available rooms on {day_clean}."
    return f"Available rooms on {day_clean}: {', '.join(rooms)}"

# --- Tool 2: Read-Only View Operating Hours ---
def get_hours(day: str) -> str:
    """Returns the opening hours for a given day."""
    day_clean = day.strip().capitalize()
    if day_clean not in HOURS_DATA:
        return f"Error: '{day}' is not a recognized day. Please provide a standard weekday name."
    return f"Operating hours for {day_clean}: {HOURS_DATA[day_clean]}"

# --- Tool 3: State-Changing Room Booking ---
def book_room(day: str, room: str, name: str) -> str:
    """
    Reserves a specific room on a given day and removes it from availability.
    
    Safety consideration: This function checks that the requested room exists in the 
    current active list for that day before performing a deletion modification. It cannot 
    add new days or wipe out existing confirmed schedules outside of its targeted slot parameters.
    """
    day_clean = day.strip().capitalize()
    room_clean = room.strip()
    name_clean = name.strip()
    
    if day_clean not in AVAILABILITY:
        return f"Error: Cannot book room. '{day}' is not a valid day."
        
    if room_clean not in AVAILABILITY[day_clean]:
        return f"Error: Room {room_clean} is not available on {day_clean}. It may be already booked or invalid."
    
    if not name_clean:
        return "Error: A valid name must be provided to confirm a room booking."

    # State modification: remove the booked room from the open availability array
    AVAILABILITY[day_clean].remove(room_clean)
    return f"Success: Room {room_clean} has been successfully booked for {name_clean} on {day_clean}."

# --- Tool Registry ---
AVAILABLE_TOOLS = {
    "check_availability": check_availability,
    "get_hours": get_hours,
    "book_room": book_room,
}

# --- JSON Tool Schemas with Instructional Prompts ---
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": (
                "INSTRUCTION: Call this tool ONLY when a user explicitly asks which rooms are open, "
                "vacant, or available for booking on a specific day. Do not use this tool to guess "
                "operating hours or to confirm a formal booking."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "day": {
                        "type": "string",
                        "description": "The full name of the day to check (e.g., 'Monday')."
                    }
                },
                "required": ["day"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_hours",
            "description": (
                "INSTRUCTION: Call this tool ONLY when a user asks about the building's operating hours, "
                "opening times, or closing times for a day. Do not use this tool when a user is trying to find "
                "a specific empty room."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "day": {
                        "type": "string",
                        "description": "The full name of the day to inspect (e.g., 'Friday')."
                    }
                },
                "required": ["day"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book_room",
            "description": (
                "INSTRUCTION: Call this tool ONLY when a user provides a day, a room number, and a person's name "
                "with the explicit intent to schedule, claim, or book that room. Do not run this tool without "
                "confirming all three parameters first."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "day": {
                        "type": "string",
                        "description": "The day of the reservation (e.g., 'Tuesday')."
                    },
                    "room": {
                        "type": "string",
                        "description": "The specific room number string to reserve (e.g., '214')."
                    },
                    "name": {
                        "type": "string",
                        "description": "The full name of the individual reserving the room."
                    }
                },
                "required": ["day", "room", "name"],
            },
        },
    },
]

# --- Safe Guarded Dispatcher ---
def dispatch_tool(name: str, arguments_str: str) -> str:
    """
    Validates tool names before dictionary access, parses args safely, 
    and converts runtime crashes into tool result messages.
    """
    # Secure Name Validation Check
    if name not in AVAILABLE_TOOLS:
        return f"Error: Tool '{name}' is not an authorized or existing tool."
    
    # Secure JSON Input Parsing Check
    try:
        args = json.loads(arguments_str) if arguments_str else {}
    except json.JSONDecodeError as e:
        return f"Error: Arguments provided for tool '{name}' were not valid JSON. Detail: {str(e)}"
    
    # Secure Functional Execution Signature Check
    try:
        tool_func = AVAILABLE_TOOLS[name]
        return tool_func(**args)
    except TypeError as e:
        return f"Error: Tool '{name}' argument mismatch or invalid structure. Detail: {str(e)}"
    except Exception as e:
        return f"Error: Tool '{name}' encountered a runtime failure. Detail: {str(e)}"
