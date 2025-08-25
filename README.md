# Overview
See https://github.com/MichelCodes123/BT-Bus-Efficiency-Project, for the project overview. 

Brampton Transit provides its bus schedule for all its routes in GTFS format. To develop this project, several python scripts were produced to transform the available data into various mappings in JSON format. 

I.e
- Bus route -> [ Total Stops ]
- StopID -> Stop Name

## Main Script
The main script runs throughout the day in order to calculate bus delays and persist the information to the database. 
