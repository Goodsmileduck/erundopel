class Request:
    def __init__(self, request_body):
        self.request_body = request_body

    def __getitem__(self, key):
        return self.request_body[key]

    @property
    def intents(self):
        return self.request_body['request'].get('nlu', {}).get('intents', {})

    @property
    def state(self):
        return self.request_body.get('state', None)

    @property
    def type(self):
        return self.request_body.get('request', {}).get('type')
    
    @property
    def new_session(self):
        return self.request_body.get('session', {}).get('new')