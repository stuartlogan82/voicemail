import os
from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.voice_response import Record, VoiceResponse, Gather, Say, Enqueue, Dial
from twilio.twiml.messaging_response import Message, MessagingResponse
from pprint import pprint


app = Flask(__name__)

account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)

@app.route('/')
def index():
    return "Working!"

@app.route('/voicemail', methods=['POST'])
def voicemail():
    data = request.values
    response = VoiceResponse()
    gather = Gather(action='/voicemail/options?recordSid={}'.format(data['RecordingSid']), method='POST')
    gather.say(
        'Press 1 to keep your recording. 2 to re-record, or 3 to delete and not leave a message', voice='alice', language='en-AU')
    response.append(gather)
    return str(response)

@app.route('/voicemail/options', methods=['POST'])
def voicemail_options():
    data = request.values
    user_input = data['Digits']
    record_sid = data['recordSid']
    response = VoiceResponse()
    if (user_input == '3'):
        client.recordings(record_sid).delete()
        response.say('Message deleted, goodbye', voice='alice', language='en-AU')
    elif (user_input == '2'):
        client.recordings(record_sid).delete()
        response.say('Message deleted', voice='alice', language='en-AU')
        response.redirect('https://handler.twilio.com/twiml/EHf16e2324cd69f34884315a6fe741e1a5')     
    else:
        response.say(
            "Your message has been saved. Thanks for calling, goodbye", voice='alice', language='en-AU')
    return str(response)

@app.route('/voicemail/transcription', methods=['POST'])
def transcription():
    pprint(request.values)
    body = "New message from {}:\n{}".format(request.values['From'], request.values['TranscriptionText'])
    message = client.messages.create(
        to="+447475737643",
        from_="+441622322065",
        body=body
    )

    return str(message)
    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

