CREATE TABLE daily_penalty_records(
    stop_id varchar (10),
    bus_name varchar (50),
    record_date Date,
    penalty float,
    PRIMARY KEY(stop_id, bus_name, record_date)
);

CREATE TABLE bus_stops(
    stop_id varchar(10),
    bus_name varchar(50),
    stop_sequence smallint,
    stop_name varchar (100),
    PRIMARY KEY(stop_id, bus_name, stop_sequence)
);