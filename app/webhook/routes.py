from flask import Blueprint, request, jsonify
from datetime import datetime
from app.extension import mongo

webhook = Blueprint('webhook', __name__, url_prefix='/webhook')

@webhook.route('/receiver', methods=["POST"])
def receiver():
    # Debug print to check if the endpoint is hit
    print("Receiver endpoint hit")

    # Check if the request contains JSON
    if not request.is_json:
        print("Request is not JSON")
        return {'error': 'Request must contain JSON data'}, 400

    data = request.json
    print("Data received:", data)  # Debug print to check received data

    event_type = None
    message = None

    # Get the GitHub event header
    event_header = request.headers.get('X-GitHub-Event')
    print("GitHub Event Header:", event_header)  # Debug print for event header

    if event_header == 'push':
        author = data.get('pusher', {}).get('name', 'Unknown')
        to_branch = data.get('ref', '').split('/')[-1]
        timestamp = datetime.now().strftime('%d %B %Y - %I:%M %p UTC')
        event_type = 'push'
        message = f'{author} pushed to {to_branch} on {timestamp}'

    elif event_header == 'pull_request':
        author = data.get('pull_request', {}).get('user', {}).get('login', 'Unknown')
        from_branch = data.get('pull_request', {}).get('head', {}).get('ref', 'Unknown')
        to_branch = data.get('pull_request', {}).get('base', {}).get('ref', 'Unknown')
        timestamp = datetime.now().strftime('%d %B %Y - %I:%M %p UTC')
        event_type = 'pull_request'
        message = f'{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}'

    elif event_header == 'pull_request_review' and data.get('action') == 'closed' and data.get('pull_request', {}).get('merged'):
        author = data.get('pull_request', {}).get('user', {}).get('login', 'Unknown')
        from_branch = data.get('pull_request', {}).get('head', {}).get('ref', 'Unknown')
        to_branch = data.get('pull_request', {}).get('base', {}).get('ref', 'Unknown')
        timestamp = datetime.now().strftime('%d %B %Y - %I:%M %p UTC')
        event_type = 'merge'
        message = f'{author} merged branch {from_branch} to {to_branch} on {timestamp}'

    # If a message was constructed, save to MongoDB
    if message:
        try:
            mongo.db.webhook_events.insert_one({
                'author': author,
                'to_branch': to_branch,
                'timestamp': datetime.utcnow().strftime('%d %B %Y - %I:%M %p UTC'),
                'event_type': event_type,
                'message': message
            })
            return {'message': message}, 200
        except Exception as e:
            print("Database insertion error:", str(e))  # Debug print for DB errors
            return {'error': str(e)}, 500

    # Handle unsupported event types or malformed requests
    return {'error': 'Unsupported event type or malformed request'}, 400

@webhook.route('/events', methods=["GET"])
def get_events():
    # Fetch and return recent events from MongoDB
    events = mongo.db.webhook_events.find().sort([('_id', -1)]).limit(10)
    event_list = [{'message': event.get('message', 'No message')} for event in events]
    return jsonify(event_list)
