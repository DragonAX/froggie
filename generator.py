import svgwrite 
from svgwrite import cm, mm
MM = 3.7795

bevel_width = 5
hole_size = 14 #14.265
key_spacing = 19.05
corner_radius = 0.1

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
        dwg.add(dwg.rect((x*mm, y*mm), (width*mm, height*mm), rx=rx*mm, ry=ry*mm, fill='none', stroke='black'))
    else:
        dwg.add(dwg.rect((x*mm, y*mm), (width*mm, height*mm), rx=rx*mm, ry=ry*mm, fill='none', stroke='black', transform=txfrm))



dwg = svgwrite.Drawing('keyboard_case.svg', profile='full', size=(f"600mm", f"400mm"))
# Generate top 
topLayer = Board(0,0)
stagger0 = 10
stagger1 = stagger0-2.5
stagger2 = stagger1-2.5
stagger3 = stagger2+2.6
stagger4 = stagger3+4.5
topLayer.addCol(stagger0, bevel_width+key_spacing+2+4)
topLayer.addCol(stagger1)
topLayer.addCol(stagger2)
topLayer.addCol(stagger3)
topLayer.addCol(stagger4)
topLayer.addCol(stagger4)

for i in range(0,6):
    topLayer.cols[i].addKey()
    topLayer.cols[i].addKey()
    topLayer.cols[i].addKey()

#topLayer.addKey(bevel_width,bevel_width + stagger0 + key_spacing/2) # top extra key
topLayer.addKey(bevel_width,bevel_width + stagger0 + key_spacing + key_spacing/2) # bottom ectra key
topLayer.addKey(topLayer.cols[1].x+key_spacing/2, topLayer.cols[1].keys[2].y+hole_size+6) # thumb 3
topLayer.addKey(topLayer.cols[1].x+key_spacing/2 - 22, topLayer.cols[0].keys[2].y+hole_size+7.25,-15 ) # thumb 2
topLayer.addKey(topLayer.cols[0].x-key_spacing +2, topLayer.cols[0].keys[2].y+hole_size+10.25,-25 ) # thumb 1




topLayer.controllers.append(Controller(dwg, bevel_width+5, 0))

keyboard_width = bevel_width*2 + topLayer.cols[-1].x+ topLayer.cols[-1].w
keyboard_height = 100

for col in topLayer.cols:
    for keyrect in col.keys:
        rounded_rectangle(dwg, keyrect.x, keyrect.y, keyrect.w, keyrect.h, corner_radius,corner_radius)
for keyrect in topLayer.keys:
    #rounded_rectangle(dwg, keyrect.x, keyrect.y, keyrect.w, keyrect.h, corner_radius,corner_radius)
    rounded_rectangle(dwg, keyrect.x, keyrect.y, keyrect.w, keyrect.h, corner_radius,corner_radius, txfrm = 'rotate(%s, %s, %s)' % (keyrect.rot, MM*(keyrect.x+keyrect.w/2), MM*(keyrect.y+keyrect.h/2)))
#for controller in topLayer.controllers:
    #rounded_rectangle(dwg, keyrect.x, keyrect.y, keyrect.w, keyrect.h, corner_radius,corner_radius)
    #dwg.add(controller.path)

#rounded_rectangle(dwg, 0, 0, keyboard_width, keyboard_height, 5, 5)
top_left = (0,0)
top_right = (keyboard_width, 0)
bottom_right = (keyboard_width, keyboard_height)
bottom_left = (0, keyboard_height)

outline = dwg.polygon(fill='none', stroke='black')
outline.points.extend(scale_points([top_left], MM))
outline.points.extend(scale_points(topLayer.controllers[0].points, MM))
outline.points.extend(scale_points([top_right, bottom_right, bottom_left], MM))
dwg.add(outline)

rounded_rectangle(dwg, keyboard_width*2+10, 0, keyboard_width, keyboard_height,  5, 5)
rounded_rectangle(dwg, 0, keyboard_height*2+10, keyboard_width, keyboard_height, 5,5)
dwg.save()
