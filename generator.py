import ezdxf
from ezdxf import units

import math

right_side = True

layer_margin = 2.8 # space between layer cutouts

# key placement stuff
bevel_width = 6 # does not account for keycaps
hole_size = 14-0.25 #Tweaked for best fit
bigger_hole_delta = 1
BHD = bigger_hole_delta
key_spacing = 19.05
keycap_hole_size = key_spacing
corner_radius = 0.01

snap_out_width = 1.2#*bevel_width/4

# case shaping
slope_tweak_top = 8
slope_tweak_bottom = 20
corner_cut_tweak = 20
corner_cut_tweak_far = 15

controller_magic_number=2
top_infill_magic_number=8
inside_infill_magic_number=10
screw_hole_r =  0.6

func_row_height_adjust = 0.5

# Line colouring
inline_colour="#0000ff"
outline_colour="#000000"
tester_colour="#00ff00"

keycap_delta = (key_spacing-hole_size)/2

thumb_scale = 1.75

def transpose_point(point, dx, dy):
    return ((point[0]+dx, point[1]+dy))

def transpose_points_by_point(points, dxy):
    return transpose_points(points, dxy[0], dxy[1])

def transpose_points(points, dx, dy):
    new_points = []
    for point in points:
        new_points.append((point[0]+dx, point[1]+dy))
    return new_points
def scale_points(points, f):
    new_points = []
    for point in points:
        new_points.append((point[0]*f, point[1]*f))
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

def rotate_points(points, angle_degrees):
    # Convert the angle from degrees to radians
    angle_radians = math.radians(angle_degrees)

    rotated_points = []

    for x, y in points:
        # Apply the rotation matrix to each point
        new_x = x * math.cos(angle_radians) - y * math.sin(angle_radians)
        new_y = x * math.sin(angle_radians) + y * math.cos(angle_radians)
        rotated_points.append((new_x, new_y))

    return rotated_points

def rotate_points_around(points, angle_degrees, rotation_point):
    # Convert the angle from degrees to radians
    angle_radians = math.radians(angle_degrees)

    rotated_points = []

    for x, y in points:
        # Translate the point to the origin, apply rotation, and then translate back
        translated_x = x - rotation_point[0]
        translated_y = y - rotation_point[1]

        new_x = (
            translated_x * math.cos(angle_radians) -
            translated_y * math.sin(angle_radians)
        )
        new_y = (
            translated_x * math.sin(angle_radians) +
            translated_y * math.cos(angle_radians)
        )

        # Translate the point back to its original position
        final_x = new_x + rotation_point[0]
        final_y = new_y + rotation_point[1]

        rotated_points.append((final_x, final_y))

    return rotated_points

class Battery():
    def __init__(self, x, y, rot=0):
        self.w = 10+0.5
        self.h = 18+3
        self.d = 0.6
        self.bumper = 3
        self.lead_length = self.w + self.bumper + 4 
        self.x = x
        self.y = y
        self.rot = rot
    def getWidth(self):
        return self.lead_length
    def getCenter(self):
        return (self.lead_length/2, self.h/2)
    def getPoints(self):
        points = [(0,0),
                  (self.lead_length, 0),
                  (self.lead_length, 5),
                  (self.w+self.bumper, 5),
                  (self.w+self.bumper, self.d),
                  (self.w, self.d),
                  (self.w, self.h-self.d),
                  (self.w+self.bumper, self.h-self.d),
                  (self.w+self.bumper, self.h-5),
                  (self.lead_length, self.h-5),
                  (self.lead_length, self.h),
                  (0, self.h)]
        points = transpose_points(rotate_points_around(points, self.rot, self.getCenter()),self.x,self.y)
        return points

class KeyRect():
    def __init__(self, x,y, rot=0, scale=1):
        self.w = hole_size
        self.h = hole_size
        self.x = x
        self.y = y
        self.rot=rot
        self.scale=scale
    def getCenter(self, margin):
        x = self.x-margin
        y = self.y-margin
        w = self.w+margin*2
        h = self.h+margin*2
        return (x+w/2, y+h/2)
    def getPoints(self, margin=0):
        points = [(self.x-margin, self.y-margin),
                  (self.x+self.w+margin, self.y-margin),
                  (self.x+self.w+margin, self.y+self.h+margin),
                  (self.x-margin, self.y+self.h+margin)]
        points = rotate_points_around(points, self.rot, self.getCenter(margin))
        return points

class KeyCapRect(KeyRect):
    def __init__(self, keyrect):
        super().__init__(keyrect.x, keyrect.y, keyrect.rot, keyrect.scale)
        delta = (key_spacing-hole_size)/2
        xdelta = (key_spacing*self.scale-self.w)/2
        self.w = key_spacing*self.scale
        self.h = key_spacing
        self.x = self.x-xdelta
        self.y = self.y-delta
        


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
    w = 18.3+0.2
    h = 34.1+0.2
    support_length = 17
    def __init__(self,  x, y, rot=0):
        self.rot = rot
        self.x = x
        self.y = y
        self.points = transpose_points([(0,0),
                       (0,bevel_width),
                       (-controller_magic_number, bevel_width),
                       (-controller_magic_number, bevel_width+24.5),
                       (-controller_magic_number+19, bevel_width+24.5),
                       (-controller_magic_number+19, bevel_width),
                       (-controller_magic_number+19-controller_magic_number, bevel_width),
                       (-controller_magic_number+19-controller_magic_number, 0)], x, y)
        self.points_with_support = transpose_points([(0,0),
                       (0,bevel_width),
                       (-controller_magic_number, bevel_width),
                       (-controller_magic_number, bevel_width+24.5),
                       (-controller_magic_number+19/3, bevel_width+24.5), #support
                       (-controller_magic_number+19/3, bevel_width+24.5-self.support_length),#support
                       (-controller_magic_number+2*19/3, bevel_width+24.5-self.support_length),#support
                       (-controller_magic_number+2*19/3, bevel_width+24.5), #support
                       (-controller_magic_number+19, bevel_width+24.5),
                       (-controller_magic_number+19, bevel_width),
                       (-controller_magic_number+19-controller_magic_number, bevel_width),
                       (-controller_magic_number+19-controller_magic_number, 0)], x, y)

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
        
        
    def addKey(self, x, y, rot=0, scale=1):
        self.keys.append(KeyRect(x, y, rot, scale))



def draw_keyhole(msp, x, y, width, height, rx, ry, rot = 0, offsetx=0, offsety=0, colour=inline_colour):
    points=[(x, y), (x, y+height), (x+width, y+height), (x+width, y), (x, y)]
    msp.add_lwpolyline(points=points, close=True)
        


def draw_outline(msp, points, colour = outline_colour):
    msp.add_lwpolyline(points=points, close=True)

def draw_keyholes(msp, board, top_left):
    mirror_point = keyboard_width*2+layer_margin*3
    for col in board.cols:
        for keyrect in col.keys:
            points = keyrect.getPoints()
            points = transpose_points(points, top_left[0],top_left[1])
            msp.add_lwpolyline(points=points, close=True)
    for keyrect in board.keys:
        points = keyrect.getPoints()
        points = transpose_points(points, top_left[0],top_left[1])
        msp.add_lwpolyline(points=points, close=True)
   
def calculate_outline(top_left, top_right, bottom_right, bottom_left, simple=False, controller_support=False):
    points = [top_left]
    if simple:
        points.append(transpose_point(board.controllers[0].points[-1],top_left[0], top_left[1]))
    else:
        if controller_support:
            points.extend(transpose_points(board.controllers[0].points_with_support,top_left[0], top_left[1]))
        else:
            points.extend(transpose_points(board.controllers[0].points,top_left[0], top_left[1]))
        
    points.extend([transpose_point(top_right,0,slope_tweak_top), 
                   transpose_point(bottom_right,0,-slope_tweak_bottom-corner_cut_tweak),
                   transpose_point(bottom_right,-corner_cut_tweak, -slope_tweak_bottom),
                   transpose_point(bottom_left,corner_cut_tweak_far,0),
                   transpose_point(bottom_left, 0, -math.tan(math.radians(90-25))*corner_cut_tweak_far)])
    return points


def calculate_reset_divit(top_left, top_right, bottom_right, bottom_left, wire=False):
    x_offset = 10
    width = 10
    depth = 4.5
    if wire:
        width += x_offset
        x_offset= 0
    points = []
    points.append(transpose_point(top_left, board.controllers[0].points[-1][0]+x_offset+width, 0)) 
    points.append(transpose_point(top_left, board.controllers[0].points[-1][0]+x_offset+width, depth)) 
    points.append(transpose_point(top_left, board.controllers[0].points[-1][0]+x_offset, depth)) 
    points.append(transpose_point(top_left, board.controllers[0].points[-1][0]+x_offset, 0)) 
    return points


def calculate_inline_part1(top_left, top_right, bottom_right, bottom_left, b):

    outline = calculate_outline(top_left, top_right, bottom_right, bottom_left, simple=True)

    points = [transpose_point(top_left,bevel_width, 0)]
    #points.append(transpose_point(board.controllers[0].points[0],top_left[0], top_left[1]+bevel_width))
    #points.append(transpose_point(board.controllers[0].points[0],top_left[0], top_left[1]+2*bevel_width/3))
    #points.append(transpose_point(board.controllers[0].points[-1],top_left[0], top_left[1]+2*bevel_width/3))
    #points.append(transpose_point(board.controllers[0].points[-1],top_left[0], top_left[1]+bevel_width/3))
    #points.append(transpose_point(board.controllers[0].points[0],top_left[0], top_left[1]+bevel_width/3))
    #points.append(transpose_point(board.controllers[0].points[0],top_left[0], top_left[1]))
    
    #rotate and reverse the outline
    outline = outline[1:]+outline[:1]
    outline.reverse()
    points.extend(outline)
    
    #points.append(transpose_point(top_left, board.controllers[0].points[-1][0], 0)) ### snap-out divit point
    points.append(transpose_point(board.controllers[0].points[-1],top_left[0], top_left[1]+bevel_width/4)) ### end of snap-out
    points.append(transpose_point(board.controllers[0].points[0],top_left[0], top_left[1]+bevel_width/4)) ### start of snap-out
    points.append(transpose_point(board.controllers[0].points[0],top_left[0], top_left[1])) ### snap-out divit point
    ### Cut Here ###
    return points

def calculate_inline_part2(top_left, top_right, bottom_right, bottom_left, b):
    points = []
    points.append(transpose_point(top_left, bevel_width, bevel_width)) ###
    points.append(transpose_point(board.controllers[0].points[0],top_left[0], top_left[1]+bevel_width)) ###
    points.append(transpose_point(board.controllers[0].points[0],top_left[0], top_left[1]+bevel_width/4+snap_out_width )) ###
    points.append(transpose_point(board.controllers[0].points[-1],top_left[0], top_left[1]+bevel_width/4+snap_out_width)) ###
    points.append(transpose_point(top_left, board.controllers[0].points[-1][0], bevel_width))

    points.append(transpose_point(board.controllers[0].points[-1],top_left[0]+controller_magic_number, top_left[1]+bevel_width))
    points.append(transpose_point(board.controllers[0].points[-1],top_left[0]+controller_magic_number, top_left[1]+bevel_width+top_infill_magic_number))
    points.append((top_left[0]+board.cols[2].x, top_left[1]+bevel_width))
    #points.append((top_left[0]+board.cols[-1].x+hole_size+2*bigger_hole_delta+2, top_right[1]+slope_tweak_top+bevel_width))
    points.append((top_right[0]-bevel_width, top_right[1]+slope_tweak_top+bevel_width))
    if (b):
        points.append((top_right[0]-bevel_width, top_right[1]+slope_tweak_top+bevel_width+key_spacing*3+3))
        points.append((top_left[0]+board.cols[-1].x+hole_size+2*bigger_hole_delta+2, top_right[1]+slope_tweak_top+bevel_width+key_spacing*3+3))
        #    points.append(       transpose_point(bottom_right,-corner_cut_tweak-bevel_width, -slope_tweak_bottom-bevel_width))
        points.append((top_left[0]+board.cols[-1].x+hole_size+2*bigger_hole_delta+2, bottom_right[1]-slope_tweak_bottom-bevel_width))
    else:
        #points.append((top_left[0]+board.cols[-1].x+hole_size+2*bigger_hole_delta+2, top_right[1]+slope_tweak_top+bevel_width+hole_size))
        points.append((top_right[0]-bevel_width, top_right[1]+slope_tweak_top+bevel_width+hole_size))
        points.append(transpose_point(bottom_right,-bevel_width,-slope_tweak_bottom-corner_cut_tweak-bevel_width))
        points.append(transpose_point(bottom_right,-corner_cut_tweak-bevel_width, -slope_tweak_bottom-bevel_width))
    points.extend([ 
                   #(top_left[0]+board.cols[3].x, top_right[1]+board.cols[3].y+key_spacing*3.5),
                   (top_left[0]+board.cols[3].x, top_right[1]+board.cols[3].y+key_spacing*4),
                   transpose_point(bottom_left,corner_cut_tweak_far+bevel_width,-bevel_width),
                   transpose_point(bottom_left, bevel_width, (-math.tan(math.radians(90-25))*corner_cut_tweak_far) -bevel_width),
                   transpose_point(bottom_left, bevel_width+inside_infill_magic_number, (-math.tan(math.radians(90-25))*corner_cut_tweak_far) -bevel_width),
                   transpose_point(bottom_left, bevel_width+inside_infill_magic_number, (-math.tan(math.radians(90-25))*corner_cut_tweak_far) -bevel_width-inside_infill_magic_number),
                   transpose_point(bottom_left, bevel_width, (-math.tan(math.radians(90-25))*corner_cut_tweak_far) -bevel_width-inside_infill_magic_number)])
    return points

def calculate_top_inline(top_left, top_right, bottom_right, bottom_left):
    points = []
    #gen the top row points
    top_row = []
    for col in board.cols:
        rect = KeyCapRect(col.keys[0]).getPoints()
        top_row.append((rect[0][0], rect[0][1]))
        top_row.append((rect[1][0], rect[1][1]))

    bottom_row = []
    for col in board.cols:
        rect = KeyCapRect(col.keys[-1]).getPoints()
        bottom_row.append((rect[3][0], rect[3][1]))
        bottom_row.append((rect[2][0], rect[2][1]))
    bottom_row.reverse()
    
    points.append(transpose_points(top_row, top_left[0], top_left[1])+transpose_points(bottom_row, top_left[0], top_left[1]))

    for key in board.keys:
        rect = KeyCapRect(key).getPoints()
        points.append(transpose_points_by_point(rect,top_left))

    return points


def draw_screw_holes(msp, top_left, top_right, bottom_right, bottom_left):

    holes = [transpose_point(top_left, board.controllers[0].points[-1][0]+bevel_width*1.5, bevel_width*1.2),
            transpose_point(top_left, keyboard_width-bevel_width/2, slope_tweak_top+bevel_width/2),
            transpose_point(top_left, board.cols[3].x, board.cols[3].y+key_spacing*4+bevel_width-1),
            transpose_point(top_left, bevel_width+inside_infill_magic_number/2, board.cols[0].keys[2].y+2*key_spacing/3),
            transpose_point(top_right,-bevel_width*2,key_spacing*5.5)
            ]
    for hole in holes:
        msp.add_circle(center=hole, radius=screw_hole_r)

def draw_battery(msp, top_left):
    points = transpose_points(board.battery.getPoints(), top_left[0], top_left[1])

    draw_outline(msp, points, inline_colour)

### BOARD Definition

#dwg = svgwrite.Drawing('keyboard_case.svg', profile='full', size=(f"400mm", f"600mm"))
#dwgPreview = svgwrite.Drawing('keyboard_case_preview.svg', profile='full', size=(f"400mm", f"600mm"))

docCuts = ezdxf.new()
docCuts.units = units.MM
docCuts.header['$MEASUREMENT'] = 1
mspCuts = docCuts.modelspace()

docPreview = ezdxf.new()
docPreview.units = units.MM
docPreview.header['$MEASUREMENT'] = 1
mspPreview = docPreview.modelspace()

# Generate top 
board = Board(0,0)
offset_of_extra_key = 4
offset_from_extra_key = 2
stagger0 = key_spacing+bevel_width*3+2
stagger1 = stagger0-2.5-2
stagger2 = stagger1-2.5
stagger3 = stagger2+2.8+1
stagger4 = stagger3+4.5+4
stagger5 = stagger4+2
board.addCol(stagger0, bevel_width+key_spacing+offset_of_extra_key+offset_from_extra_key)
board.addCol(stagger1)
board.addCol(stagger2)
board.addCol(stagger3)
board.addCol(stagger4)
board.addCol(stagger5)

for i in range(0,len(board.cols)):
    board.cols[i].addKey()
    board.cols[i].addKey()
    board.cols[i].addKey()

board.cols[3].addKey()

#board.addKey(bevel_width,bevel_width + stagger0 + key_spacing/2) # top extra key
board.addKey(board.cols[0].x-key_spacing +2, board.cols[0].keys[2].y+hole_size+10.25,90-25, scale=thumb_scale ) # thumb 1
board.addKey(bevel_width+offset_of_extra_key,bevel_width + stagger0 + key_spacing + key_spacing/2) # extra key
board.addKey(board.cols[1].x+key_spacing/2, board.cols[1].keys[2].y+hole_size+6+0.25, -8) # thumb 3
board.addKey(board.cols[1].x+key_spacing/2 - 22, board.cols[0].keys[2].y+hole_size+7.25,-15 ) # thumb 2
#board.addKey(board.cols[3].x, board.cols[0].keys[2].y+key_spacing ) # thumb 4


# Func row
for i in range(6):
    board.addKey(board.cols[0].x+key_spacing*i,bevel_width*3-func_row_height_adjust) # extra key

# macro col
for i in range(3):
    board.addKey(board.cols[len(board.cols)-1].x+key_spacing+7,
                 bevel_width*3+i*key_spacing-func_row_height_adjust)

keyboard_height = board.keys[0].y+32 
print(keyboard_height)
print(board.keys[0].y)
board.controllers.append(Controller(bevel_width+5, 0))

####



batt = Battery(0,0, 180)
keyboard_width = bevel_width*2 + board.cols[-1].x+ board.cols[-1].w + batt.getWidth()
print("Width"+str(keyboard_width))
mirror_point = keyboard_width*2+layer_margin*3


batt.x = keyboard_width-batt.getWidth()-bevel_width*1.5-1-0.75 # adjusted not to clip corner-cut
batt.y = 7+2*keyboard_height/4
board.battery=batt

def doLayer4(d, top_left, top_right, bottom_right, bottom_left):
    """
    The switchplate
    """
    draw_keyholes(d, board, top_left)
    
    points = calculate_reset_divit(top_left, top_right, bottom_right, bottom_left, wire=True)
    draw_outline(d, points, outline_colour)

    points = calculate_outline(top_left, top_right, bottom_right, bottom_left, controller_support=True)
    draw_outline(d, points)
    draw_battery(d, top_left)

def doLayer3(d, top_left, top_right, bottom_right, bottom_left):
    for col in board.cols:
        for keyrect in col.keys:
            points = transpose_points_by_point(keyrect.getPoints(margin=BHD), top_left)
            d.add_lwpolyline(points=points, close=True)
    for keyrect in board.keys:
        points = transpose_points_by_point(keyrect.getPoints(margin=BHD), top_left)
        d.add_lwpolyline(points=points, close=True)
    
    points = calculate_outline(top_left, top_right, bottom_right, bottom_left)
    draw_outline(d, points)
    
    points = calculate_reset_divit(top_left, top_right, bottom_right, bottom_left)
    draw_outline(d, points, outline_colour)

    draw_screw_holes(d, top_left, top_right, bottom_right, bottom_left)
    draw_battery(d, top_left)


def doLayer2(d, top_left, top_right, bottom_right, bottom_left, b=False):
    points = calculate_inline_part1(top_left, top_right, bottom_right, bottom_left, b)
    draw_outline(d, points, outline_colour)
    
    points = calculate_inline_part2(top_left, top_right, bottom_right, bottom_left, b)
    draw_outline(d, points, outline_colour)

    draw_screw_holes(d, top_left, top_right, bottom_right, bottom_left)
    

    points = calculate_reset_divit(top_left, top_right, bottom_right, bottom_left)
    draw_outline(d, points, outline_colour)

    if(b):
        draw_battery(d, top_left)

def doLayer2b(d, top_left, top_right, bottom_right, bottom_left, b=False):
    points = calculate_inline_part1(top_left, top_right, bottom_right, bottom_left, b)
    draw_outline(d, points, outline_colour)
    
    points = calculate_inline_part2(top_left, top_right, bottom_right, bottom_left, b)
    draw_outline(d, points, outline_colour)
    
    draw_screw_holes(d, top_left, top_right, bottom_right, bottom_left)

    points = calculate_reset_divit(top_left, top_right, bottom_right, bottom_left)
    draw_outline(d, points, outline_colour)
    
    if(b):
        draw_battery(d, top_left)

def doLayer1(d, top_left, top_right, bottom_right, bottom_left):
    points = calculate_outline(top_left, top_right, bottom_right, bottom_left, simple=True)
    draw_outline(d, points)
    draw_screw_holes(d, top_left, top_right, bottom_right, bottom_left)


def doLayer0(d, top_left, top_right, bottom_right, bottom_left, b = False):
    points = calculate_outline(top_left, top_right, bottom_right, bottom_left, simple=True)
    draw_outline(d, points)
    
    points_list = calculate_top_inline(top_left, top_right, bottom_right, bottom_left)
    for points in points_list:
        draw_outline(d, points, inline_colour)
    if (b):
        draw_battery(d, top_left)

def doHoleTester(d, top_left):
    draw_keyhole(d, top_left[0], top_left[1], hole_size-0.1, hole_size-0.1, 0, 0, colour=tester_colour)
    draw_keyhole(d, top_left[0]+key_spacing, top_left[1], hole_size-0.05, hole_size-0.05, 0, 0, colour=tester_colour)
    draw_keyhole(d, top_left[0]+key_spacing*2, top_left[1], hole_size, hole_size, 0, 0, colour=tester_colour)
    draw_keyhole(d, top_left[0]+key_spacing*3, top_left[1], hole_size+0.05, hole_size+0.05, 0, 0, colour=tester_colour)
    for i in range(1,7):
        draw_keyhole(d, top_left[0]+key_spacing*(3+i), top_left[1], hole_size+(i/10), hole_size+(i/10), 0, 0, colour=tester_colour)


# Layer 4 (the plate)

top_left = (layer_margin,layer_margin)
top_right = (top_left[0]+keyboard_width, top_left[1])
bottom_right = (top_left[0]+keyboard_width, top_left[1]+keyboard_height)
bottom_left = (top_left[0], top_left[1]+keyboard_height)

doLayer4(mspCuts, top_left, top_right, bottom_right, bottom_left)


# layer 3 (same as plate but bigger holes)
top_left = (layer_margin, keyboard_height+layer_margin*2)
top_right = (top_left[0]+keyboard_width, top_left[1])
bottom_right = (top_left[0]+keyboard_width, top_left[1]+keyboard_height)
bottom_left = (top_left[0], top_left[1]+keyboard_height)

doLayer3(mspCuts, top_left, top_right, bottom_right, bottom_left)

# layer 2 (just the outline, where all the wiring is)
top_left = (layer_margin, keyboard_height*2+layer_margin*3)
top_right = (top_left[0]+keyboard_width, top_left[1])
bottom_right = (top_left[0]+keyboard_width, top_left[1]+keyboard_height)
bottom_left = (top_left[0], top_left[1]+keyboard_height)

doLayer2(mspCuts, top_left, top_right, bottom_right, bottom_left, b=False)


# layer 2b (just the outline, where all the wiring is)
top_left = (layer_margin*2+keyboard_width, layer_margin)
top_right = (top_left[0]+keyboard_width, top_left[1])
bottom_right = (top_left[0]+keyboard_width, top_left[1]+keyboard_height)
bottom_left = (top_left[0], top_left[1]+keyboard_height)

doLayer2b(mspCuts, top_left, top_right, bottom_right, bottom_left, b=True)

# layer 1 (bottom)
top_left = (layer_margin, keyboard_height*3+layer_margin*4)
top_right = (top_left[0]+keyboard_width, top_left[1])
bottom_right = (top_left[0]+keyboard_width, top_left[1]+keyboard_height)
bottom_left = (top_left[0], top_left[1]+keyboard_height)

doLayer1(mspCuts, top_left, top_right, bottom_right, bottom_left)

# layer 0 (tippy top)

top_left = (layer_margin*2+keyboard_width, keyboard_height*1+layer_margin*2)
top_right = (top_left[0]+keyboard_width, top_left[1])
bottom_right = (top_left[0]+keyboard_width, top_left[1]+keyboard_height)
bottom_left = (top_left[0], top_left[1]+keyboard_height)

doLayer0(mspCuts, top_left, top_right, bottom_right, bottom_left)
# layer 0b (tippy top)

top_left = (layer_margin*2+keyboard_width, keyboard_height*2+layer_margin*3)
top_right = (top_left[0]+keyboard_width, top_left[1])
bottom_right = (top_left[0]+keyboard_width, top_left[1]+keyboard_height)
bottom_left = (top_left[0], top_left[1]+keyboard_height)

doLayer0(mspCuts, top_left, top_right, bottom_right, bottom_left, b=True)


# hole-tester

top_left = (layer_margin*3+keyboard_width, keyboard_height*4+layer_margin*5)

doHoleTester(mspCuts, top_left)

docCuts.saveas("keeb_cuts.dxf")

##### Generate layered preview

top_left = (layer_margin,layer_margin)
top_right = (top_left[0]+keyboard_width, top_left[1])
bottom_right = (top_left[0]+keyboard_width, top_left[1]+keyboard_height)
bottom_left = (top_left[0], top_left[1]+keyboard_height)

doLayer0(mspPreview, top_left, top_right, bottom_right, bottom_left)
doLayer1(mspPreview, top_left, top_right, bottom_right, bottom_left)
doLayer2b(mspPreview, top_left, top_right, bottom_right, bottom_left, b=True)
doLayer2(mspPreview, top_left, top_right, bottom_right, bottom_left, b=False)
doLayer3(mspPreview, top_left, top_right, bottom_right, bottom_left)
doLayer4(mspPreview, top_left, top_right, bottom_right, bottom_left)

docPreview.saveas("keeb_preview.dxf")

