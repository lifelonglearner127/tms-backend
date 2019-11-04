## About Project
### asgimqtt.py
asgimqtt.py is a MQTT interface from ASGI. It connects to G7 MQTT Server and receives real-time vehicle positioning data published by G7.

- `Functionalities`:
  - Send vehicle positioning data to Django Channel Layres
  - Monitor the entry enter & exit by calculating longitude and latitude between vehicle and stations
  - At first, I tried to query station position data from db when mqtt client receive poition data. But G7 server publish the data every seconds(of course, it can be adjusted on our side). Querying db every second was redundant and useless. So in order to improve the performance, I load station position data into our variables at the first beginning of the process startup or when the station data are updated.
 
- `Why I don't use Redis?`
  - This is because redis is `key-value` in-memory database, (de)serializing the station data might be time-consuming. When we have large data, (de)serializing might be longer than db query time.

- Arguments
    - `settings`: The location of the django project env file, we need to import some of the environment variables from these file in order to send a notification and db access
    - `channel_layer`: this is the channel layer referenced in django project
    - `debug`: Flag to set log level; if it is set, print log
    - `test`: Flag to set this service test mode
        if this flag is set to True, this app do not rely on real distance delta(distance between station and vehicle postion), it rely on `blackdot_delta_distance` and `station_delta_distance` in redis
        ```
        python mqtt/asgimqtt.py --settings .env config.asgi:channel_layer --debug --test
        ```
        - You can use these endpoint to test the black dot and station entry and exit event `test/station-efence` and `test/blackdot-efence`. See the code at `order/views.py`.
