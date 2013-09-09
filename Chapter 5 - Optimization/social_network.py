import math
import Image, ImageDraw

people = ['Charlie', 'Augustus', 'Veruca', 'Violet',
          'Mike', 'Joe', 'Willy', 'Miranda']
links = [
       ('Augustus', 'Willy'),
       ('Mike', 'Joe'),
       ('Miranda', 'Mike'),
       ('Violet', 'Augustus'),
       ('Miranda', 'Willy'),
       ('Charlie', 'Mike'),
       ('Veruca', 'Joe'),
       ('Miranda', 'Augustus'),
       ('Willy', 'Augustus'),
       ('Joe', 'Charlie'),
       ('Veruca', 'Augustus'),
       ('Miranda', 'Joe')]

def is_crossed(line1, line2):
    # extract coordinates of start point
    # and end point for each line
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2

    # calculate the denominator
    den = (x2 - x1) * (y4 - y3) - (y2 - y1) * (x4 - x3)

    # for two parallel lines, denominator would be 0
    if den == 0: return False

    # Otherwise t and u are the fraction of the
    # line where they cross
    t = ((x3 - x1) * (y4 - y3) - (y3 - y1) * (x4 - x3)) / float(den)
    u = ((x3 - x1) * (y2 - y1) - (y3 - y1) * (x2 - x1)) / float(den)

    # If the fraction is between 0 and 1 for both lines
    # then they cross each other
    if 0 < t < 1 and 0 < u < 1:
        return True
    return False

def cross_count(sol):
    # Convert the number list into a dictionary of person:(x,y)
    loc = dict([
        (people[i], (sol[2 * i], sol[2 * i + 1]))
        for i in range(len(people))
    ])
    total = 0

    # Loop through every pair of links
    for i in range(len(links)):
        for j in range(i+1, len(links)):
            # get the locations
            (x1, y1), (x2, y2) = loc[links[i][0]], loc[links[i][1]]
            (x3, y3), (x4, y4) = loc[links[j][0]], loc[links[j][1]]

            if is_crossed((x1, y1, x2, y2), (x3, y3, x4, y4)):
                total += 1

    # calculate distance between every pair of nodes
    for i in range(len(people)):
        for j in range(i+1, len(people)):
            # get the locations of two nodes
            (x1, y1), (x2, y2) = loc[people[i]], loc[people[j]]

            # find the distance between them
            dist = math.sqrt(pow(x1 - x2, 2) + pow(y1 - y2, 2))

            # penalize any nodes closer than 50 pixels
            if dist < 50:
                total += (1.0 - (dist / 50.0))

    return total

def draw_network(sol, dim=(400, 400), filename='network.jpg'):
    # create the image
    img = Image.new('RGB', dim, (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # create the position dict
    pos = dict([
        (people[i], (sol[2 * i], sol[2 * i + 1]))
        for i in range(len(people))
    ])

    # Draw Links
    for (a, b) in links:
        draw.line((pos[a], pos[b]), fill=(0, 0, 0))

    # draw people
    for name, coor in pos.items():
        draw.text(coor, name, (0, 0, 0))

    img.save(filename, 'JPEG')