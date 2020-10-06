import math


class Axial:
    def __init__(self, q, r):
        self.q = q
        self.r = r

    def __repr__(self):
        return f'({self.q}, {self.r})'


class Cube:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        return f'({self.x}, {self.y}, {self.z})'

    def __add__(self, other):
        return Cube(self.x+other.x, self.y+other.y, self.z+other.z)

    def __sub__(self, other):
        return Cube(self.x+-other.x, self.y-other.y, self.z-other.z)


def axial_to_cube(axial):
    return Cube(axial.q, -axial.q-axial.r, axial.r)


def cube_to_axial(cube):
    return Axial(cube.x, cube.z)


def cube_distance(a, b):
    ax, ay, az = a.x, a.y, a.z
    bx, by, bz = b.x, b.y, b.z
    return (abs(ax-bx) + abs(ay-by) + abs(az-bz))/2


# Linear interpolation for line drawing:
def lerp(a, b, t):
    return a+(b-a)*t


def cube_lerp(a, b, t):
    ax, ay, az = a.x, a.y, a.z
    bx, by, bz = b.x, b.y, b.z
    return Cube(lerp(ax, bx, t), lerp(ay, by, t), lerp(az, bz, t))


def cube_round(cube, epsilon):
    rx = round(cube.x+epsilon)
    ry = round(cube.y+epsilon)
    rz = round(cube.z+epsilon)

    dx = abs(rx-cube.x)
    dy = abs(ry-cube.y)
    dz = abs(rz-cube.z)

    if dx > dy and dx > dz:
        rx = -ry-rz
    elif dy > dz:
        ry = -rx-rz
    else:
        rz = -rx-ry

    return Cube(rx, ry, rz)


def cube_linedraw(a, b, distance, epsilon):
    N = int(distance)
    road = []
    for i in range(0, N+1):
        road.append(cube_round(cube_lerp(a, b, i/N), epsilon))
    return road


if __name__ == '__main__':
    point = (-1, 3)
    print(axial_to_cube(Axial(*point)))
    print(cube_to_axial(axial_to_cube(Axial(*point))))

    print(Cube(1,2,3)+Cube(3,2,1))
