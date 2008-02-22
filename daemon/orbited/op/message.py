
class OrbitMessage(object):

    def __init__(self, recipients, payload, complete_cb):
        self.recipients = recipients
        self.payload = payload
        self.complete_cb = complete_cb
        self.failed = []
        self.succeed_count = 0

    def single_recipient_event(self, recipient):
        return SingleRecipientEvent(
            self.payload, self.recipient, self.success, self.failure)

    def failure(self, recipient, reason):
        self.failed.append((recipient, reason))
        self.check_complete()

    def success(self, recipient):
        self.succeed_count += 1
        self.check_complete()

    def check_complete(self):
        if len(self.failed) + self.succeed_count == len(self.recipients):
            self.complete_cb(self.failed)

class SingleRecipientMessage(object):
    
    def __init__(self, payload, recipient, success_cb, failure_cb):
        self.payload = payload
        self.recipient = recipient
        self.success_cb = success_cb
        self.failure_cb = failure_cb
    
    def success(self):
        self.success_cb(recipient)
        
    def failure(self, reason="unknown"):
        self.failure_cb(reason)
