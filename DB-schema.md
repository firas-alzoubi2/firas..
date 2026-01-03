**USERS Table:-**
* user_id : INT [PK]
* username : VARCHAR(50)
* email : VARCHAR(100)
* phone : VARCHAR(20)
* user_type : VARCHAR(20)
* created_at : DATETIME
* updated_at : DATETIME

**ACCOUNTS Table:-**
* account_id : INT [PK]
* user_id : INT [FK]
* password_hash : VARCHAR(255)
* status : VARCHAR(20)
* last_login : DATETIME
* password_changed_at : DATETIME
* created_at : DATETIME
* updated_at : DATETIME

**DRIVERS Table:-**
* driver_id : INT [PK]
* user_id : INT [FK]
* vehicle_id : INT [FK]
* license_number : VARCHAR(50)
* license_type : VARCHAR(20)
* license_expiry : DATE
* average_rating : DECIMAL(3,2)
* total_trips : INT
* status : VARCHAR(20)
* created_at : DATETIME
* updated_at : DATETIME

**VEHICLES Table:-**
* vehicle_id : INT [PK]
* plate_number : VARCHAR(20) [UK]
* vehicle_type : VARCHAR(20)
* model : VARCHAR(50)
* brand : VARCHAR(50)
* year : INT
* capacity : INT
* color : VARCHAR(20)
* average_rating : DECIMAL(3,2)
* status : VARCHAR(20)
* created_at : DATETIME
* updated_at : DATETIME

**TRIPS Table:-**
* trip_id : INT [PK]
* driver_id : INT [FK]
* vehicle_id : INT [FK]
* trip_name : VARCHAR(100)
* start_location : VARCHAR(255)
* end_location : VARCHAR(255)
* departure_time : DATETIME
* arrival_time : DATETIME
* price : DECIMAL(10,2)
* available_seats : INT
* status : VARCHAR(20)
* cancelled_by : VARCHAR(20)
* cancellation_reason : TEXT
* created_at : DATETIME
* updated_at : DATETIME

**TRIP_BOOKINGS Table:-**
* booking_id : INT [PK]
* trip_id : INT [FK]
* user_id : INT [FK]
* seats_booked : INT
* total_price : DECIMAL(10,2)
* status : VARCHAR(20)
* booking_date : DATETIME
* created_at : DATETIME
* updated_at : DATETIME

**RATINGS Table:-**
* rating_id : INT [PK]
* trip_id : INT [FK]
* user_id : INT [FK]
* driver_id : INT [FK]
* vehicle_id : INT [FK]
* user_rating : INT
* driver_rating : INT
* vehicle_rating : INT
* user_comment : TEXT
* driver_comment : TEXT
* created_at : DATETIME

**ADMIN_LOGS Table:-**
* log_id : INT [PK]
* admin_id : INT [FK]
* action_type : VARCHAR(50)
* entity_type : VARCHAR(50)
* entity_id : INT
* description : TEXT
* created_at : DATETIME

***

*Relations*

**USERS to ACCOUNTS**
* **Relation:** 1:1 (One-to-One)
* **Description:** Each user `has` exactly one account.
* **Foreign Key:** `user_id` in the ACCOUNTS table refers to `user_id` in the USERS table.

**USERS to DRIVERS**
* **Relation:** 1:1 (One-to-One)
* **Description:** A user `is` a driver (or can be). This is likely an optional 1:1 relationship where not all users are drivers.
* **Foreign Key:** `user_id` in the DRIVERS table refers to `user_id` in the USERS table.

**USERS to TRIP_BOOKINGS**
* **Relation:** 1:N (One-to-Many)
* **Description:** One user `books` multiple trips.
* **Foreign Key:** `user_id` in the TRIP_BOOKINGS table refers to `user_id` in the USERS table.

**USERS to ADMIN_LOGS**
* **Relation:** 1:N (One-to-Many)
* **Description:** One user (specifically an admin type) `logs` multiple actions.
* **Foreign Key:** `admin_id` in the ADMIN_LOGS table refers to `user_id` in the USERS table.

**DRIVERS to VEHICLES**
* **Relation:** N:1 (Many-to-One)
* **Description:** A driver `drives` a specific vehicle. *Note: The diagram shows `vehicle_id` inside the Drivers table, suggesting a Driver is assigned to a specific Vehicle, or perhaps currently active on one.*
* **Foreign Key:** `vehicle_id` in the DRIVERS table refers to `vehicle_id` in the VEHICLES table.

**DRIVERS to TRIPS**
* **Relation:** 1:N (One-to-Many)
* **Description:** One driver `manages` (or conducts) multiple trips.
* **Foreign Key:** `driver_id` in the TRIPS table refers to `driver_id` in the DRIVERS table.

**VEHICLES to TRIPS**
* **Relation:** 1:N (One-to-Many)
* **Description:** One vehicle is `used_in` multiple trips.
* **Foreign Key:** `vehicle_id` in the TRIPS table refers to `vehicle_id` in the VEHICLES table.

**TRIPS to TRIP_BOOKINGS**
* **Relation:** 1:N (One-to-Many)
* **Description:** One trip `contains` multiple bookings.
* **Foreign Key:** `trip_id` in the TRIP_BOOKINGS table refers to `trip_id` in the TRIPS table.

**TRIPS to RATINGS**
* **Relation:** 1:N (One-to-Many)
* **Description:** One trip is `rated` multiple times (presumably by the passenger and driver).
* **Foreign Key:** `trip_id` in the RATINGS table refers to `trip_id` in the TRIPS table.

**USERS to RATINGS**
* **Relation:** 1:N (One-to-Many)
* **Description:** One user (passenger) `rates` multiple trips/drivers.
* **Foreign Key:** `user_id` in the RATINGS table refers to `user_id` in the USERS table.

**DRIVERS to RATINGS**
* **Relation:** 1:N (One-to-Many)
* **Description:** One driver receives (or gives) multiple ratings.
* **Foreign Key:** `driver_id` in the RATINGS table refers to `driver_id` in the DRIVERS table.

**VEHICLES to RATINGS**
* **Relation:** 1:N (One-to-Many)
* **Description:** One vehicle is `rated` multiple times.
* **Foreign Key:** `vehicle_id` in the RATINGS table refers to `vehicle_id` in the VEHICLES table.

---

*IMPORTANT NOTES*
in **USERS** Diagram, user_type values are: Administrator, Driver, Passenger.

in **ACCOUNTS** Diagram, status values are: Active, Disabled, Deleted.

in **TRIPS** Diagram, status values are: Upcoming, Ongoing, Completed, Cancelled.

