class OrbitMessage(object):

    def __str__(self):
        return "<OrbitMessage \"%s\", %s ((%s))>" % (self.payload, self.recipients, self.args)

    def __init__(self, recipients, payload, cb, args):
        self.recipients = recipients
        self.payload = payload
        self.cb = cb
        self.args = args
        self.failure_recipients = []
        self.success_recipients = []
        self.succeed_count = 0

    def single_recipient_message(self, recipient):
        if recipient not in self.recipients:
            raise ValueError, "invalid recipient value: %s", (recipient,)
        return SingleRecipientMessage(
            self.payload, recipient, self.success, self.failure)

    def failure(self, recipient, reason):
        self.failure_recipients.append((recipient, reason))
        self.check_complete()

    def success(self, recipient):
        self.success_recipients.append(recipient)
        self.check_complete()

    def check_complete(self):
        if len(self.success_recipients) + len(self.failure_recipients) == len(self.recipients):
            print self, "completed,", self.failure_recipients, self.success_recipients, len(self.args)
            self.cb(self, *self.args)

class SingleRecipientMessage(object):
    
    def __init__(self, payload, recipient, success_cb, failure_cb):
        self.payload = payload
        self.recipient = recipient
        self.success_cb = success_cb
        self.failure_cb = failure_cb
    
    def success(self):
        self.success_cb(self.recipient)
        
    def failure(self, reason="unknown"):
        self.failure_cb(self.recipient, reason)

