from flask import jsonify

from api_service import ChatTracker
from manage import app

running_trackers = dict()


@app.route('/api/v1.0/track/start/<channel_name>')
def start_tracking(channel_name):
    ct = ChatTracker(channel_name)
    ct.start()

    running_trackers[channel_name] = ct

    return jsonify({
        'message': 'Started tracking {}'.format(channel_name)
    })


@app.route('/api/v1.0/track/stop/<channel_name>')
def stop_tracking(channel_name):
    ct = running_trackers.get(channel_name, None)
    if ct:
        ct.shutdown_flag.set()
        message = 'Stopped tracking {}'.format(channel_name)
    else:
        message = 'Channel "{}" was not being tracked'.format(channel_name)

    return jsonify({
        'message': message
    })


@app.route('/api/v1.0/track/stop_all')
def stop_tracking_all():
    channels = []
    for channel_name, ct in running_trackers.items():
        ct.shutdown_flag.set()
        channels += channel_name

    return jsonify({
        'message': 'Stopped tracking these channels: {}'.format('\n'.join(channels))
    })
