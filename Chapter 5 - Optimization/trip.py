import time

# list of peoples and their respective locations
people = [
    ('Seymour', 'BOS'),
    ('Franny', 'DAL'),
    ('Zooey', 'CAK'),
    ('Walt', 'MIA'),
    ('Buddy', 'ORD'),
    ('Les', 'OMA')
]

# LaGuardia airport in New York
destination = 'LGA'

flights = {}
for line in open('schedule.txt'):
    # extract origin, destination, departure time,
    # arrival time and price from each line
    origin, dest, depart, arrive, price = line.strip().split(',')
    flights.setdefault((origin, dest), [])

    # add details to the list of possible flights
    flights[(origin, dest)].append((depart, arrive, int(price)))

def get_minutes(t):
    x = time.strptime(t, '%H:%M')
    return x[3] * 60 + x[4]

def print_schedule(solution):
    for i in range(len(solution) / 2):
        name = people[i][0]
        origin = people[i][1]
        out = flights[(origin, destination)][solution[2 * i]]
        ret = flights[(origin, destination)][solution[2 * i + 1]]
        print '%10s%10s %5s-%5s $%3s %5s-%5s $%3s' % (
            name, origin, out[0], out[1], out[2],
            ret[0], ret[1], ret[2]
        )

def schedule_cost(solution):
    total_price = 0
    latest_arrival = 0
    earliest_depart = 24 * 60

    for i in range(len(solution) / 2):
        # get the inbound and outbound flights
        origin = people[i][1]
        out_bound = \
        flights[(origin, destination)][int(solution[2 * i])]
        return_flight = \
        flights[(origin, destination)][int(solution[2 * i + 1])]

        # total price is the price of all outbound and return flights
        total_price += (out_bound[2] + return_flight[2])

        # track the latest arrival and earliest departure
        if latest_arrival < get_minutes(out_bound[1]):
            latest_arrival = get_minutes(out_bound[1])
        if earliest_depart > get_minutes(return_flight[0]):
            earliest_depart = get_minutes(return_flight[0])
    # end of first loop
    # every person must wait at the airport
    # until the latest person arrives. they also
    # must arrive at the same time and wait for
    # their flights
    total_wait = 0
    for i in range(len(solution) / 2):
        origin = people[i][1]
        out_bound = \
        flights[(origin, destination)][int(solution[2 * i])]
        return_flight = \
        flights[(origin, destination)][int(solution[2 * i + 1])]
        total_wait += latest_arrival - get_minutes(out_bound[1])
        total_wait += get_minutes(return_flight[0]) - earliest_depart
    # end of second loop
    # Does this solution require an extra
    # day of car rental? That will be $50!
    if latest_arrival > earliest_depart: total_price += 50

    return total_price + total_wait