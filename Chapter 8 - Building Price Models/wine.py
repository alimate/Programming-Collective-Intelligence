from random import random, randint, choice

def wine_price(rating, age):
    peak_age = rating - 50

    # calculate price based on rating
    price = rating / 2.0
    if age > peak_age:
        # past its peak, goes bad in 5 years
        price *= (5 - (age - peak_age))
    else:
        # increase to 5x original value as it
        # approaches its peak
        price *= 5 * ((age + 1) / peak_age)

    if price < 0: return 0
    return price

def first_wine_dataset(length=300):
    rows = []
    for iteration in range(length):
        # create a random age and rating
        rating = random() * 50 + 50
        age = random() * 50

        # get reference price
        price = wine_price(rating, age)

        # add some noise
        price *= (random() * 0.4 + 0.8)

        # add to the dataset
        rows.append(
            {
                'input':(rating, age),
                'output': price
            }
        )
    return rows

def second_wine_dataset(length=300):
    rows = []
    for i in range(length):
        # initialize the variables
        rating = random() * 50 + 50
        age = random() * 50
        aisle = float(randint(1, 20))
        bottle_size = choice([375.0, 750.0, 1500.0, 3000.0])

        # calculate the price
        price = wine_price(rating, age)
        price *= bottle_size / 750

        # add some noise
        price *= (random() * 0.9 + 0.2)

        # add to dataset
        rows.append({'input':(rating, age, aisle, bottle_size),
                     'output':price })
    return rows

def third_wine_dataset(length=300):
    rows = first_wine_dataset(length)
    for row in rows:
        if random < 0.5:
            # wine was bought at a discount store with 50% discount
            row['output'] *= 0.5
    return rows