### Strafe test case by Ayat Ospanov

#### Installation
* Install pip requirements (pip install -r requirements.txt)
* Export flask app name (export FLASK_APP=manage)
* Run:
    * flask migrate
    * flask run
    
#### Usage
Flask creates web-server on localhost:5000

##### API commands
* Start tracking a channel: /api/v1.0/track/start/\<channel name\>
    * ex. localhost:5000/api/v1.0/track/start/dreamhackcs
* Stop tracking a channel: /api/v1.0/track/stop/\<channel name\>
    * ex. localhost:5000/api/v1.0/track/stop/dreamhackcs
* Stop tracking all channels: /api/v1.0/track/start_all
    * ex. localhost:5000/api/v1.0/track/stop_all
* Get channel's message frequency: api/v1.0/stats/\<channel name\>/freq/<window>
    * ex. localhost:5000/api/v1.0/stats/dreamhackcs/freq
    * window is a window in minutes to get messages from now back on. Optional. By default = 10
* Get channel's mood frequency: api/v1.0/stats/\<channel name\>/mood/<window>
    * ex. localhost:5000/api/v1.0/stats/dreamhackcs/mood
    * window is a window in minutes to get messages from now back on. Optional. By default = 10

###### What is mood?
Implemented mood is an average sentiment of messages. Sentiment analysis was done by NLTKs API (http://text-processing.com/api/sentiment/).

###### How channel tracking works
For each channel there is a ChatTracker instance created in a thread. List of threads is global and organized as a dict.

PS. I did not remove my Twitch IRC oauth key so you can test it without creating one. But I will delete it soon! 