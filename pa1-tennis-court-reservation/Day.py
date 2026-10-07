# Day.py
class Day:
    def __init__(self, name):
        self.name = name
        self.slots = {
            "09": None, "10": None, "11": None, "12": None,
            "13": None, "14": None, "15": None, "16": None,
            "17": None, "18": None, "19": None, "20": None,
            "21": None, "22": None
        }
    
    def book_slot(self, slot, userName):
        if userName in self.slots.values():
            return (False,"User " + userName + " already has a spot for the selected day. A user can only make one booking per day.\n")
        
        if slot not in self.slots:
            return (False, "Selected slot for the day is not valid. Please pick a valid slot.\n")
        
        if self.slots[slot] != None:
            return (False, "Selected slot of the day is not available. Please pick another slot.\n")

        self.slots[slot] = userName
        return (True, "Slot " + slot + " has been booked for user " + userName + "\n")

    def cancel_slot(self, userName):
        for slot, user in self.slots.items():
            if user == userName: # stated "a user can only make one booking per day"
                self.slots[slot] = None
                return (True, "Booking for user " + userName + " at slot " + slot + " has been cancelled.\n")
        
        return (False, "User " + userName + " has no booking for this day.\n")

    def view_day(self):
        lines = []
        lines.append("-- " + self.name + " Schedule: ")
        for slot, user in self.slots.items():
            if user is None:
                lines.append(slot + ":00 - Available      |")
            else:
                lines.append(slot + ":00 - Booked by " + user + " |")
        lines.append("")  
        return "\n".join(lines)

    def view_user_day(self, userName):
        for slot, user in self.slots.items():
            if user == userName: 
                return " " + self.name + ": " + slot + ":00 is booked.\n"
        return " " + self.name + ": - \n"

    # clear all the bookings of the day
    def reset_day(self):
        for key in self.slots:
            self.slots[key] = None

    def isValidSlot(self, slot):
        if slot in self.slots:
            return True
        else:
            return False