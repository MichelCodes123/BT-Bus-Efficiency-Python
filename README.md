## Introduction
The goal of the app is to help improve the decision making process of transit riders on their daily commute. Since there are typically various different ways to reach a specific destination, riders may leverage the app to determine which routes tend to arrive on time, or severely late. Thus alternate bus routes may be taken in order to reach a destination faster. 

## Methodology 

### Determining Bus Delays
Bramptons bus schedules are defined in GTFS format on their website. This indicates the times that buses should arrive at a specific stop. Brampton Transit also provides GTFS-RT (Real time data), that provide information about the buses currently running on the road.

SampleData: 
```json
{

"id": "608",

	"vehicle": {
		"trip": {
			"trip_id": "2025-08--250728-MULTI-Saturday-01",
			"schedule_relationship": "ADDED",
			"route_id": "14"
		},
		
		"position": {
			"latitude": 43.744072,
			"longitude": -79.72025,
			"bearing": 113.0,
			"speed": 1.0
		
		},
		"current_status": "IN_TRANSIT_TO",
		"timestamp": "1754913625",
		"stop_id": "00003450",
		"vehicle": {
			"id": "608",
			"label": "608"
		
			}
		
	}

},
```

*Note: Brampton transit provides their GTFS-RT data through an easily accessible API, that returns information in JSON format. This saves me the time of having to parse a protobuffer in order to start manipulating the data. Thumbs up for Brampton Transit*

1. For every bus on the road, determine the stop that it is currently going to. "stop_id" and "current_status" are the fields of interest. 
2. Determine the *scheduled* arrival time for that specific trip. I map the "trip_id" and the "stop_id" to the scheduled arrival time. To create this mapping, I leverage the regular GTFS data (stored in the trips.txt file), and a python script which iterates through the data, and creates the mapping in JSON format. 
3. Get the current arrival time in Toronto.
4. Compare these two values to determine if the bus is delayed. 

### Calculating Efficiency
Disclaimer: The methods used to calculate efficiency are quite basic, and may not give a precise measurement.

**Stop Efficiency**
- Each stop has scheduled arrivals throughout the day. Delayed trips are awarded a score based on the length of the delay, higher score indicates smaller to no delay. A larger score indicates a higher delay. At the end of the day, each arrival time is given a score, and average is taken out of all the scores.
    - This daily average is included in the weekly average to determine the 7 day moving average for each stop. 

*Assumptions:*
The daily averages should be composed of the same number of arrival trips, when computing the weekly average. 

**Overall Bus Efficiency**
- Average of each stop efficiency score (weekly average score)


## Caveats
- Bus scheduling can be unpredictable. Brampton transit may add bus lines on the fly, some may go out of service unexpectedly. Detours can increase bus delays. Buses can come much earlier than scheduled. The app cannot predict all these possible usecases.

- 4 Bus routes were excluded from the calculation.. Any "LOOP" routes causes issues with the way I performed the on-time performance calculations. I hope to revisit this in the future.


## Project Learning Goals 
This project was very fun to work on, the main focuses were as followed. 
- Bolster my python scripting skills
- Work more with java, and create a spring boot application.
- Get exposure to AWS, and leverging the capabilities of its various services. 
- Program something with real impact. Working on personal projects can be a bore, and it's often difficult to come up with a good idea. This project came about after the Bus 501 I was trying to catch on a particular day didnt come at the right time. It was annoying, but helped bring forth this project idea.

The project was actually extemely daunting at first, especially having to try to understand the GTFS format. Breaking up each step of the requirements into manageable chunks, helped alot. 



