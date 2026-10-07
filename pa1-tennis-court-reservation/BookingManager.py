# BookingManager.py
from Day import Day

INVALID_DAY_CODE = "Invalid day code. Use one of: MON, TUE, WED, THU, FRI, SAT, SUN.\n"

# manage bookings (also uses day object)
class BookingManager:

    def __init__(self):
        self.users = {
            "user1": "1", "user2": "2", "user3": "3", "user4": "4", "user5": "5",
            "user6": "6", "user7": "7", "user8": "8", "user9": "9", "user10": "10"
        }
        self.days = { "MON": Day("Monday"), "TUE": Day("Tuesday"), "WED": Day("Wednesday"), 
                     "THU": Day("Thursday"), "FRI": Day("Friday"), "SAT": Day("Saturday"), "SUN": Day("Sunday") }

    def authenticate(self, userName, password):
        pw = self.users.get(userName)
        return pw is not None and pw == str(password)
    
    # make booking if the user, day, and slot is valid (and the slot is empty) (and the user has not booked for the day already)
    def make_booking(self, userName, day, slot):
        if userName not in self.users:
            return (False, "Unknown user")
        
        if day not in self.days:
            return (False, INVALID_DAY_CODE)
        
        return self.days[day].book_slot(slot, userName)
            
    # cancel booking if the user is valid and has a booking for the day
    def cancel_booking(self, userName, day):
        if day not in self.days:
            return (False, INVALID_DAY_CODE)
        
        if userName not in self.users:
            return (False, "Unknown user: " + userName)

        return self.days[day].cancel_slot(userName) 

    # view the schedule of the week
    def view_week_schedule(self):
        parts = []
        for day in self.days.values():
            parts.append(day.view_day())
        return "\n".join(parts)

    # view the schedule of the day
    def view_day_schedule(self, day):
        if day not in self.days:
            return (False, INVALID_DAY_CODE)
        
        return (True, self.days[day].view_day())
    
    # view the schedule of the user
    def view_self_schedule(self, userName):
        lines = []
        lines.append("Self Schedule of the user " + userName + "\n")
        for day in self.days.values():
            line = day.view_user_day(userName)
            lines.append(line)
        return "\n".join(lines)

    # reset week at the beggining of the each week
    def reset_week(self):
        for day in self.days.values():
            day.reset_day()
        
        return (True, "Reset the slots. All slots are free.\n")