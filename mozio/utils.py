from .models import Vertex, Point


# Size(lng/lat) of cell for storing service aria data in cache table
# Changing this will corrupt all the data in Point model
CELL_SIZE = 0.2


def save_polygon_in_table(company, polygon):
    vertices = Vertex.objects.filter(polygon=polygon)
    if not vertices:
        return

    # Manipulating points(lat/lng) in integers for better perffomance
    vertices = [[int(v.lat / CELL_SIZE), int(v.lng / CELL_SIZE)] for v in vertices]

    path_length = len(vertices)
    start_point = vertices[0]

    def point_inside_polygon(x, y):
        inside = False

        p1x, p1y = start_point
        for i in range(path_length + 1):
            p2x, p2y = vertices[i % path_length]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside

    min_lat = min(v[0] for v in vertices)
    max_lat = max(v[0] for v in vertices)
    min_lng = min(v[1] for v in vertices)
    max_lng = max(v[1] for v in vertices)

    for lng in xrange(min_lng, max_lng):
        for lat in xrange(min_lat, max_lat):
            if point_inside_polygon(lat, lng):
                Point.objects.get_or_create(lat=lat, lng=lng, company=company)