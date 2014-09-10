import json
from rq.decorators import job
from flask import Flask
from flask import request
from bandwith_sdk.client_v4 import (Call,
                                    Bridge,
                                    Client,
                                    Event,
                                    AnswerCallEvent,
                                    PlaybackCallEvent,
                                    HangupEvent)

app = Flask(__name__)
# Client('u-**********', 't-******', 's-********')

NoSqlStorage = {}


@app.route('/v1/events', methods=['POST'])
def events_v1():
    event = json.loads(request.data.decode('ascii'))
    # Example of deserialized event:
    # {
    #     'time': '2014-07-23T13:04:39Z',
    #     'applicationId': 'a-73mq4rpnghrtbqprtr45zdy',
    #     'eventType': 'incomingcall',
    #     'callState': 'active',
    #     'callId': 'c-pkyusdpacfmvmopvd7p3dmi',
    #     'callUri': 'https://127.0.0.1/v1/users/u-2qep46jwram5oyyqqa5muli/calls/c-pkyusdpacfmvmopvd7p3dmi',
    #     'from': '+14084782637',
    #     'to': '+14082149398'
    # }
    event = Event.create(**event)
    #event = Event.create(request.data)

    call = event.call  # or Call('c-pkyusdpacfmvmopvd7p3dmi')
    if isinstance(event, AnswerCallEvent):
        do_play_audio.delay(call, 'Hello.mp3')
    elif isinstance(event, PlaybackCallEvent):
        do_bridge.delay(call)
    elif isinstance(event, HangupEvent):
        """
        Create a CDR
        """
    else:
        """
        Anything else ...
        """
    NoSqlStorage.update({event.callId: event})
    return b''


@job('default')
def do_play_audio(call_id, file):
    Call(call_id).play_audio(file)


@job('default')
def do_bridge(*calls):
    Bridge.create(*calls)


app.debug = True
app.run()
