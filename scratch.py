# coding=utf-8
import base64
from acfun.protos import AcProtos


class Acer:
    is_logined = False


class AcWsConfig:
    did = "web_357274059B73A55C"
    userId = 39088
    acSecurity = b"FNBFtVbhPzG/4RmeIdaRrw=="
    ssecurity = acSecurity
    visitor_st = None
    api_st = None
    api_at = None
    acer = Acer()


class AcWsConfig2:
    did = "web_357274059B73A55C"
    userId = 39088
    acSecurity = b"K9950XfTKDXUVtWEuLvDrA=="
    ssecurity = acSecurity
    visitor_st = None
    api_st = None
    api_at = None
    acer = Acer()


conf = AcWsConfig()
conf2 = AcWsConfig2()
p = AcProtos(conf)
p2 = AcProtos(conf2)

send1 = "q80AAQAAARIAAACgCAAQsLECGAA4gwFAAUr1AQgBEvABQ2haaFkyWjFiaTV0YVdSbmNtOTFibVF1WVhCcExuTjBFbUJPZWlxdHpEclJUR1FDLVg5ZlZyRlR1SDhpYjBjZDRtN29qQ0RQT0VZRjFaY3I2RHlMQ1hZNUllN3RZam05b0JjU05yelF3ZGxvdDVzQUItWmhPM0UyZ29VLWhIZ19KVld6UTQtejJLUGxDM3h4Y2tBSXY2UWZpaV9HZmlZamFOQWFFby1WdENhMUJzVjZ1WFJIbVBKc3Q3ZXh6Q0lnZ0NYN254OW85UFpHV3RKOGxLQWhuUXdKLXZRMFlZZk5lVEVHUzRFSVlGVW9CVEFCUAFiCUFDRlVOX0FQUBt9cCcN6w5CDEygugHXY+lNCnSIKrA1XO8FIsnrXplAriz5Aj0OSFpW8oZzZPB6rTuET90XRabQuGchqABBq07qDX7lL1dtKuwCXty28dfuL0ZiFopRIlt9fLQruGH1W2IDZARYlxoF1Gh92dibhLgpT5+A7u2wPdU+lWNSiq9E9O0z+JNci++z9iJASz2XmngPKiqg0J7qKfxbmBLaiHk="
# recv1 = "q80AAQAAACQAAACgCA0QsLECGJeHgNzUk5D+eCgBOIQBQAFQAWIJQUNGVU5fQVBQDfgD9/LE1PiEQfb4mZFiPoGomiqHa1dEuqlrYMtBhjrApTxqH7Jt0CHp2cMXPDgkyLcdw7Lapn3mTZ5eN7TZA4Bl1h0ZteIAaTqxjFZo9Fhp8hif3gK4AWAKy7ZgrVxHe6kISbr0pNO+5Iyj2Qs76HvAh+QKtMJLTzenxwlKrRx5h+JnvSUWlHGGUoudJoo/2got50ECGQsZJdQws50XBQ=="
my_send1 = "q80AAQAAAQ0AAACQELCxAjh/QAFK9QEIARLwAUNoWmhZMloxYmk1dGFXUm5jbTkxYm1RdVlYQnBMbk4wRW1ELUYxX3hpdjRrMDdncnIyLUgzSHJuVnp2d1gzMnZRc2ZoQ2RaVXFscGVMYW5TaU1GcXFDbDJCdFJkTG14S21YWWZrZy0yYlNlcHJvdzdoQlc3eGJlX2tycDZVTnQ0VWk4UnJQcnotYWJkd0xiQk9JdWZrUVFHeG1RQnZWT3JldDBhRXV0aGt1RFhwdlZsdXA3TlhkUk5Md1l3VkNJZ2ZHdWpNUnF3Z3VtNlJkalBzMFRHU0JkYV95Ni1UTnEzZTlCQnBpOGk1SzRvQlRBQlABYglBQ0ZVTl9BUFDwgrKEWFj5X6KGOg8OKJNT6YicKCugRTtW6lUM/u9jl0pTHHJUh4mb4Vjsd/PtSoV6vBqRHcHWtZz0ooUGKw1lo8hj2jIocXBm9+Y9sOwDIH7Wo8grAttosPRS+YGm6m5n+6nd8d3Mn42rtBjC3QMug4lRMky4ixpLdRLgqJQKi1TDacJ7wEeqtgIuQcsboO8="

# p.receive(base64.standard_b64decode(send1))
p2.receive(base64.standard_b64decode(my_send1))
# k = base64.standard_b64decode("Ag7J8T4EIqXJ9SPNEFv4iA==")
# print(len(k), k)

if __name__ == '__main__':
    pass
