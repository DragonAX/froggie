import svgwrite 
from svgwrite import cm, mm
MM = 3.7795
layer_margin = 10 # space between layer cutouts
bevel_width = 6 # does not account for keycaps
hole_size = 14.265
bigger_hole_delta = 1
BHD = bigger_hole_delta
key_spacing = 19.05
keycap_hole_size = key_spacing
corner_radius = 0.1

key_colour="purple"
boarder_colour="black"

def transpose_points(points, dx, dy):
    new_points = []
    for point in points:
        new_points.append((point[0]+dx, point[1]+dy))
    return new_points
def scale_points(points, f):
    print(points)
    new_points = []
    for point in points:
        new_points.append((point[0]*f, point[1]*f))
    print(new_points)
    return new_points

def mirror_points(points, axis="x"):
    mirrored_points = []
    if axis == "x":
        for x, y in points:
            mirrored_points.append((-x, y))
    elif axis == "y":
        for x, y in points:
            mirrored_points.append((x, -y))
    else:
        raise ValueError("Invalid axis. Use 'x' or 'y'.")
    return mirrored_points

class KeyRect():
    w = hole_size
    h = hole_size
    def __init__(self, x,y, rot=0):
        self.x = x
        self.y = y
        self.rot=rot

class Column():
    def __init__(self, x,y,w):
        self.w = w
        self.h = 0
        self.x = x 
        self.y = y
        self.keys = []
    def addKey(self):
        number_of_keys = len(self.keys)
        self.keys.append(KeyRect(self.x, self.y+number_of_keys*key_spacing))

class Controller():
    w = 18+1
    h = 23.5+1
    def __init__(self,dwg,  x, y, rot=0):
        self.rot = rot
        self.x = x
        self.y = y
        self.points = transpose_points([(0,0),
                       (0,bevel_width),
                       (-4, bevel_width),
                       (-4, bevel_width+24.5),
                       (-4+19, bevel_width+24.5),
                       (-4+19, bevel_width),
                       (-4+19-4, bevel_width),
                       (-4+19-4, 0)], x, y)

        #self.path = dwg.path(["V {bevel_width}", "H -4", "V 24.5", "H 19", "V -24.5", "H -4", "V {bevel_width}"], stroke="black",
        #                              fill="none",
        #                              stroke_width=1)

class Board():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.cols = []
        self.keys = []
        self.controllers = []
        self.displays = []

    def addCol(self, stagger, extra_space=0):
        number_of_cols = len(self.cols)
        if (number_of_cols > 0):
            self.cols.append(Column(self.cols[-1].x+self.cols[-1].w+extra_space, self.y+stagger+bevel_width, key_spacing))
        else:
            self.cols.append(Column(self.x+key_spacing*number_of_cols+extra_space, self.y+stagger+bevel_width, key_spacing))
        
        
    def addKey(self, x, y, rot=0):
        self.keys.append(KeyRect(x, y, rot))



# Function to create a rectangular cutout with rounded corners
def rounded_rectangle(dwg, x, y, width, height, rx, ry, txfrm = None):
    print("rounded_rectangle: "+str([x,y,width, height, rx, ry]))
    if txfrm == None:
        dwg.add(dwg.rect((x*mm, y*mm), (width*mm, height*mm), rx=rx*mm, ry=ry*mm, fill='none', stroke=key_colour))
    else:
        dwg.add(dwg.rect((x*mm, y*mm), (width*mm, height*mm), rx=rx*mm, ry=ry*mm, fill='none', stroke=key_colour, transform=txfrm))



dwg = svgwrite.Drawing('keyboard_case.svg', profile='full', size=(f"400mm", f"600mm"))
# Generate top 
board = Board(0,0)
stagger0 = 10
stagger1 = stagger0-2.5
stagger2 = stagger1-2.5
stagger3 = stagger2+2.6
stagger4 = stagger3+4.5
board.addCol(stagger0, bevel_width+key_spacing+2+4)
board.addCol(stagger1)
board.addCol(stagger2)
board.addCol(stagger3)
board.addCol(stagger4)
board.addCol(stagger4)

for i in range(0,6):
    board.cols[i].addKey()
    board.cols[i].addKey()
    board.cols[i].addKey()

#board.addKey(bevel_width,bevel_width + stagger0 + key_spacing/2) # top extra key
board.addKey(bevel_width,bevel_width + stagger0 + key_spacing + key_spacing/2) # bottom ectra key
board.addKey(board.cols[1].x+key_spacing/2, board.cols[1].keys[2].y+hole_size+6) # thumb 3
board.addKey(board.cols[1].x+key_spacing/2 - 22, board.cols[0].keys[2].y+hole_size+7.25,-15 ) # thumb 2
board.addKey(board.cols[0].x-key_spacing +2, board.cols[0].keys[2].y+hole_size+10.25,-25 ) # thumb 1




board.controllers.append(Controller(dwg, bevel_width+5, 0))

keyboard_width = bevel_width*2 + board.cols[-1].x+ board.cols[-1].w
keyboard_height = 100

# Layer 4 (the plate)

top_left = (layer_margin,layer_margin)
top_right = (top_left[0]+keyboard_width, top_left[1])
bottom_right = (top_left[0]+keyboard_width, top_left[1]+keyboard_height)
bottom_left = (top_left[0], top_left[1]+keyboard_height)

for col in board.cols:
    for keyrect in col.keys:
        rounded_rectangle(dwg, keyrect.x+top_left[0], keyrect.y+top_left[1], keyrect.w, keyrect.h, corner_radius,corner_radius)
for keyrect in board.keys:
    rounded_rectangle(dwg, keyrect.x+top_left[0], keyrect.y+top_left[1], keyrect.w, keyrect.h, corner_radius,corner_radius, txfrm = 'rotate(%s, %s, %s)' % (keyrect.rot, MM*(keyrect.x+top_left[0]+keyrect.w/2), MM*(keyrect.y+top_left[1]+keyrect.h/2)))


points = [top_left]
points.extend(transpose_points(board.controllers[0].points,top_left[0], top_left[1]))
points.extend([top_right, bottom_right, bottom_left])

outline = dwg.polygon(fill='none', stroke='black')
outline.points.extend(scale_points(points, MM))
dwg.add(outline)

mirror_point = keyboard_width*2+layer_margin*3
outline = dwg.polygon(fill='none', stroke='black')
points = transpose_points(mirror_points(points), mirror_point, 0)
outline.points.extend(scale_points(points, MM))
dwg.add(outline)

# layer 3 (same as plate but bigger holes)
top_left = (layer_margin, keyboard_height+layer_margin*2)
top_right = (top_left[0]+keyboard_width, top_left[1])
bottom_right = (top_left[0]+keyboard_width, top_left[1]+keyboard_height)
bottom_left = (top_left[0], top_left[1]+keyboard_height)

for col in board.cols:
    for keyrect in col.keys:
        rounded_rectangle(dwg, keyrect.x+top_left[0]-BHD, keyrect.y+top_left[1]-BHD, keyrect.w+BHD*2, keyrect.h+BHD*2, corner_radius,corner_radius)
for keyrect in board.keys:
    rounded_rectangle(dwg, keyrect.x+top_left[0]-BHD, keyrect.y+top_left[1]-BHD, keyrect.w+BHD*2, keyrect.h+BHD*2, corner_radius,corner_radius, txfrm = 'rotate(%s, %s, %s)' % (keyrect.rot, MM*(keyrect.x+top_left[0]-BHD+(keyrect.w+BHD*2)/2), MM*(keyrect.y+top_left[1]-BHD+(keyrect.h+BHD*2)/2)))
outline = dwg.polygon(fill='none', stroke='black')
outline.points.extend(scale_points([top_left], MM))
outline.points.extend(scale_points(transpose_points(board.controllers[0].points,top_left[0], top_left[1]),MM))
outline.points.extend(scale_points([top_right, bottom_right, bottom_left], MM))
dwg.add(outline)

# layer 2 (just the outline, where all the wiring is)
top_left = (layer_margin, keyboard_height*2+layer_margin*3)
top_right = (top_left[0]+keyboard_width, top_left[1])
bottom_right = (top_left[0]+keyboard_width, top_left[1]+keyboard_height)
bottom_left = (top_left[0], top_left[1]+keyboard_height)

outline = dwg.polygon(fill='none', stroke='black')
outline.points.extend(scale_points([top_left], MM))
outline.points.extend(scale_points([top_right, bottom_right, bottom_left], MM))
dwg.add(outline)

outline = dwg.polygon(fill='none', stroke=key_colour)
points = [(top_left[0]+bevel_width, top_left[1]+bevel_width),
          (top_left[0]+keyboard_width-bevel_width, top_left[1]+bevel_width),
          (top_left[0]+keyboard_width-bevel_width, top_left[1]+keyboard_height-bevel_width),
          (top_left[0]+bevel_width, top_left[1]+keyboard_height-bevel_width)]
outline.points.extend(scale_points(points, MM))
dwg.add(outline)

# layer 1 (bottom)
top_left = (layer_margin, keyboard_height*3+layer_margin*4)
top_right = (top_left[0]+keyboard_width, top_left[1])
bottom_right = (top_left[0]+keyboard_width, top_left[1]+keyboard_height)
bottom_left = (top_left[0], top_left[1]+keyboard_height)

outline = dwg.polygon(fill='none', stroke='black')
outline.points.extend(scale_points([top_left], MM))
outline.points.extend(scale_points([top_right, bottom_right, bottom_left], MM))
dwg.add(outline)
dwg.save()
