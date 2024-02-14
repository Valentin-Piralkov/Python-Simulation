import random
import simpy
import numpy as np

# Parameters
RANDOM_SEED = 42
NUM_EMPLOYEES = 3  # Number of employees
AVG_SUPPORT_TIME = 5  # Average time to support a customer
CUSTOMER_INTERVAL = 2  # Generate new customers roughly every x minutes
SIM_TIME = 120  # Simulation time in seconds

# Global variables
customers_handled = 0


class CallCenter:
    def __init__(self, env, num_employees, avg_support_time):
        self.env = env
        self.employee = simpy.Resource(env, num_employees)
        self.avg_support_time = avg_support_time

    def support_customer(self, customer):
        random_time = max(1, np.random.normal(self.avg_support_time, 4))
        yield self.env.timeout(random_time)
        print(f"Customer {customer} has been supported at {self.env.now}")


def customer(env, name, call_center):
    global customers_handled
    print(f"Customer {name} enters the call center at {env.now}")
    with call_center.employee.request() as request:
        yield request
        print(f"Customer {name} is assigned to an employee at {env.now}")
        yield env.process(call_center.support_customer(name))
        print(f"Customer {name} leaves the call center at {env.now}")
        customers_handled += 1


def setup(env, num_employees, avg_support_time, customer_interval):
    call_center = CallCenter(env, num_employees, avg_support_time)
    # Create x customers
    for i in range(1, 6):
        env.process(customer(env, i, call_center))

    while True:
        yield env.timeout(random.randint(customer_interval - 1, customer_interval + 1))
        i += 1
        env.process(customer(env, i, call_center))


# Setup and start the simulation
print("Starting the call center simulation")
random.seed(RANDOM_SEED)
env = simpy.Environment()
env.process(setup(env, NUM_EMPLOYEES, AVG_SUPPORT_TIME, CUSTOMER_INTERVAL))
env.run(until=SIM_TIME)

print(f"Total customers handled: {customers_handled}")
