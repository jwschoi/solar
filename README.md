# Solar Energy Savings Calculator

Solar Energy Savings Calculator is a Python program that calculates the savings for a commercial location with the installation of solar panels. Hourly kWh values from PV Watts API, and utility rates can be updated in "tariffs_csv.csv". Pre-solar intake from "Intake.csv" and outputs to "Template.xlsx".


TOU Hour CSV Guide:

Top Row (summer):
x1, x2: Summer off peak morning start, evening end
x3, x4: Summer part peak morning start and end
x5, x6: Summer part peak evening start and end
x7, x8: Summer peak start and end

Bottom Row (winter):
y1, y2: Winter off peak morning start, evening end
y3, y4: Winter part peak morning start and end
y5, y6: Winter part peak evening start and end
y7, y8: Winter peak start and end

Notes: 
-Always round up when dealing with half hours.
-For tariffs with no winter peak, simply use 24, 0

