import requests
from flask import jsonify

from api_service import ChatTracker, api_prefix
from manage import app
from models import Chat

running_trackers = dict()


@app.route(api_prefix('/track/start/<channel_name>'))
def start_tracking(channel_name):
    if channel_name not in running_trackers:
        ct = ChatTracker(channel_name)
        ct.start()
        running_trackers[channel_name] = ct
        msg = 'Started tracking {}'.format(channel_name)
    else:
        msg = 'Tracking for "{}" is already active'.format(channel_name)

    return jsonify({
        'message': msg
    })


@app.route(api_prefix('/track/stop/<channel_name>'))
def stop_tracking(channel_name):
    ct = running_trackers.get(channel_name, None)
    if ct:
        ct.shutdown_flag.set()
        msg = 'Stopped tracking {}'.format(channel_name)
    else:
        msg = 'Channel "{}" was not being tracked'.format(channel_name)

    return jsonify({
        'message': msg
    })


@app.route(api_prefix('/track/stop_all'))
def stop_tracking_all():
    channels = []
    for channel_name, ct in running_trackers.items():
        ct.shutdown_flag.set()
        channels += [channel_name]

    return jsonify({
        'message': 'Stopped tracking these channels: {}'.format('\n'.join(channels))
    })


@app.route(api_prefix('/stats/<channel>/freq/'))
@app.route(api_prefix('/stats/<channel>/freq/<int:window>'))
def ch_stats_freq(channel, window=10):
    """
    Counts frequencies of channel messages

    # TODO: Change freq counting type
    !!! This type of freq. counting is not good as it depends on the window.
    !!! e.g. if the window big enough but there are now messages such old, then freq is low
    !!! But for an example it should be OK.

    :param channel: string, channel name
    :param window: period of time in minutes in which we select messages
    :return: freq, messages per min and per sec
    """
    if window == 0:
        window = 10

    msg_num = Chat.get_messages_cnt(channel, window=window)

    return jsonify({
        'messages per minute': msg_num / window,
        'messages per second': msg_num / window / 60
    })


@app.route(api_prefix('/stats/<channel>/mood'))
@app.route(api_prefix('/stats/<channel>/mood/<window>'))
def ch_stats_mood(channel, window=10):
    """
    Computes mood of the channel
    :param channel: channel name
    :param window: period of time in minutes in which we select messages
    :return: mood
    """
    # !!! limit is for test purposes. Sentiment analysis API is not fast
    msgs = Chat.get_messages(channel, window=window, limit=10)

    mood = {
        'neg': 0,
        'neutral': 0,
        'pos': 0
    }
    for msg in msgs:
        r = requests.post('http://text-processing.com/api/sentiment/', {'text': msg})
        # TODO: Implement local sentiment analysis
        # !!! this API is open, thus there are limits
        # !!! moreover relying on outer service is not always good. In production I would implement
        # !!! local sentiment analysis
        # !!! hopefully, for the test case should be OK
        if r.status_code == 200:
            resp = r.json()
            for key, val in mood.items():
                mood[key] = (val + resp['probability'][key]) / 2

    return jsonify({
        'mood': max(mood, key=mood.get),
        'moods': mood
    })
