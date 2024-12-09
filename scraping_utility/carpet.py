import re

def parse_measurement(measurement):
    """
    Parse a room measurement string like '13\'9"x10\'0"' and return the area in square feet.
    """
    match = re.match(r'(\d+)\'(\d+)"x(\d+)\'(\d+)"', measurement)
    if not match:
        raise ValueError("Invalid measurement format")
    
    length_ft = int(match.group(1))
    length_in = int(match.group(2))
    width_ft = int(match.group(3))
    width_in = int(match.group(4))
    
    length = length_ft + length_in / 12
    width = width_ft + width_in / 12
    
    area = length * width
    return area

def calculate_total_area():
    """
    Ask the user for the number of entries and measurements, then calculate the total carpet area.
    """
    total_area = 0
    num_entries = int(input("How many entries do you want to make? "))
    
    for _ in range(num_entries):
        measurement = input("Enter the room measurement (e.g., 13'9\"x10'0\"): ")
        try:
            area = parse_measurement(measurement)
            total_area += area
        except ValueError as e:
            print(e)
            return
    
    print(f"The total carpet area is {total_area:.2f} sq ft")

# Run the function to calculate total area
calculate_total_area()
