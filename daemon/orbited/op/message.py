class OrbitMessage(object):

    def __str__(self):
        return "<OrbitMessage \"%s\", %s>" % (self.payload, self.recipients)

    def __init__(self, recipients, payload, cb, args):
        self.recipients = recipients
        self.payload = payload
        self.cb = cb
        self.args = args
        self.failed = []
        self.succeed_count = 0

    def single_recipient_message(self, recipient):
        return SingleRecipientMessage(
            self.payload, self.recipient, self.success, self.failure)

    def failure(self, recipient, reason):
        self.failed.append((recipient, reason))
        self.check_complete()

    def success(self, recipient):
        self.succeed_count += 1
        self.check_complete()

    def check_complete(self):
        if len(self.failed) + self.succeed_count == len(self.recipients):
            self.cb(self.failed, *self.args)

class SingleRecipientMessage(object):
    
    def __init__(self, payload, recipient, success, failure):
        self.payload = payload
        self.recipient = recipient
        self.success_cb = success_cb
        self.failure_cb = failure_cb
    
    def success(self):
        self.success_cb(self.recipient)
        
    def failure(self, reason="unknown"):
        self.failure_cb(self.recipient, reason)

