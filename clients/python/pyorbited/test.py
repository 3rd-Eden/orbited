from client import OrbitClient

c = OrbitClient()
c.connect()

for i in range(1,101):
    print c.send(["test,/"], "%s: Test" % i)
    