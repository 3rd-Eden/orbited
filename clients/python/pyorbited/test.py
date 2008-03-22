from client import OrbitClient

c = OrbitClient()
c.connect()

for i in range(1,101):
    c.send(["test,/"], "%s: Test" % i)
    