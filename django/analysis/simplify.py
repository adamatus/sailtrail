"""Simplify a polyline

Modified code from https://github.com/omarestrella/simplify.py, which itself
is modified code from the original javascript version available here:
https://github.com/mourner/simplify-js

Original javascript license:

Copyright (c) 2015, Vladimir Agafonkin
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

   1. Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
# pylint: disable=invalid-name


def get_square_distance(point1, point2):
    """Square distance between two points"""
    dx = point1['lat'] - point2['lat']
    dy = point1['lon'] - point2['lon']

    return dx * dx + dy * dy


def get_square_segment_distance(mid_point, segment_start, segment_end):
    """Square distance between point and a segment"""
    x = segment_start['lat']
    y = segment_start['lon']

    dx = segment_end['lat'] - x
    dy = segment_end['lon'] - y

    if dx != 0 or dy != 0:
        t = (((mid_point['lat'] - x) * dx + (mid_point['lon'] - y) * dy) /
             (dx * dx + dy * dy))

        if t > 1:
            x = segment_end['lat']
            y = segment_end['lon']
        elif t > 0:
            x += dx * t
            y += dy * t

    dx = mid_point['lat'] - x
    dy = mid_point['lon'] - y

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
    """Simplify a line, to a specific tolerance"""
    squared_tolerance = tolerance * tolerance

    if not highest_quality:
        points = simplify_radial_distance(points, squared_tolerance)

    points = simplify_douglas_peucker(points, squared_tolerance)

    return points


def simplify_to_specific_length(points, desired_point_count=100):
    """Simpilfy a line, to a specific number of points"""
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
