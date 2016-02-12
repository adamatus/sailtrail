def get_square_distance(p1, p2):
    """Square distance between two points"""
    dx = p1['lat'] - p2['lat']
    dy = p1['lon'] - p2['lon']

    return dx * dx + dy * dy


def get_square_segment_distance(p, p1, p2):
    """Square distance between point and a segment"""
    x = p1['lat']
    y = p1['lon']

    dx = p2['lat'] - x
    dy = p2['lon'] - y

    if dx != 0 or dy != 0:
        t = ((p['lat'] - x) * dx + (p['lon'] - y) * dy) / (dx * dx + dy * dy)

        if t > 1:
            x = p2['lat']
            y = p2['lon']
        elif t > 0:
            x += dx * t
            y += dy * t

    dx = p['lat'] - x
    dy = p['lon'] - y

    return dx * dx + dy * dy


def simplify_radial_distance(points, tolerance):
    """Simplify polyline using radial distance method"""
    length = len(points)
    prev_point = points[0]
    new_points = [prev_point]

    for i in range(length):
        point = points[i]

        if get_square_distance(point, prev_point) > tolerance:
            new_points.append(point)
            prev_point = point

    if prev_point != point:
        new_points.append(point)

    return new_points


def simplify_douglas_peucker(points, tolerance):
    """Simplify polyline using Douglas Peucker method"""
    length = len(points)
    markers = [0] * length  # Maybe not the most efficent way?

    first = 0
    last = length - 1

    first_stack = []
    last_stack = []

    new_points = []

    markers[first] = 1
    markers[last] = 1

    while last:
        max_sqdist = 0

        for i in range(first, last):
            sqdist = get_square_segment_distance(points[i],
                                                 points[first],
                                                 points[last])

            if sqdist > max_sqdist:
                index = i
                max_sqdist = sqdist

        if max_sqdist > tolerance:
            markers[index] = 1

            first_stack.append(first)
            last_stack.append(index)

            first_stack.append(index)
            last_stack.append(last)

        # Can pop an empty array in Javascript, but not Python, so check
        # the length of the list first
        if len(first_stack) == 0:
            first = None
        else:
            first = first_stack.pop()

        if len(last_stack) == 0:
            last = None
        else:
            last = last_stack.pop()

    for i in range(length):
        if markers[i]:
            new_points.append(points[i])

    return new_points


def simplify(points, tolerance=0.1, highest_quality=True):
    squared_tolerance = tolerance * tolerance

    if not highest_quality:
        points = simplify_radial_distance(points, squared_tolerance)

    points = simplify_douglas_peucker(points, squared_tolerance)

    return points


def simplify_to_specific_length(points, desired_point_count=100):
    current_point_count = len(points)
    iterations = 0
    tolerance = 1/100000
    line = points
    while current_point_count > desired_point_count:
        iterations += 1
        line = simplify(points, tolerance=tolerance)
        tolerance += 1/100000
        current_point_count = len(line)
    return line

