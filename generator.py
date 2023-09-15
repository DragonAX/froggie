import svgwrite 

bevel_width = 5
hole_size = 14.265
key_spacing = 19.05

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

class Board():
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.cols = []
        self.keys = []

    def addCol(self, stagger, extra_space=0):
        number_of_cols = len(self.cols)
        if (number_of_cols > 0):
            self.cols.append(Column(self.cols[-1].x+self.cols[-1].w+extra_space, self.y+stagger+bevel_width, key_spacing))
        else:
            self.cols.append(Column(self.x+key_spacing*number_of_cols+extra_space, self.y+stagger+bevel_width, key_spacing))
        
        
    def addKey(self, x, y, rot=0):
        self.keys.append(KeyRect(x, y, rot))



# Function to create a rectangular cutout with rounded corners
def rounded_rectangle(dwg, x, y, width, height, rx, ry):
    print("rounded_rectangle: "+str([x,y,width, height, rx, ry]))
    dwg.add(dwg.rect((x, y), (width, height), rx=rx, ry=ry, fill='none', stroke='black'))


# Generate top 
topLayer = Board(0,0)
stagger0 = 10
stagger1 = stagger0-5
stagger2 = stagger1-2
stagger3 = stagger2+7
topLayer.addCol(stagger0, bevel_width+key_spacing+5)
topLayer.addCol(stagger1)
topLayer.addCol(stagger2)
topLayer.addCol(stagger3)
topLayer.addCol(stagger3)

for i in range(0,5):
    topLayer.cols[i].addKey()
    topLayer.cols[i].addKey()
    topLayer.cols[i].addKey()

topLayer.addKey(bevel_width,bevel_width + stagger0 + key_spacing/3)
topLayer.addKey(bevel_width,bevel_width + stagger0 + key_spacing + key_spacing/3)

keyboard_width = bevel_width*2 + topLayer.cols[-1].x+ topLayer.cols[-1].w
keyboard_height = 200

dwg = svgwrite.Drawing('keyboard_case.svg', profile='full')#, size=(f"{keyboard_width+100}mm", f"{keyboard_height+100}mm"))
for col in topLayer.cols:
    for keyrect in col.keys:
        rounded_rectangle(dwg, keyrect.x, keyrect.y, keyrect.w, keyrect.h, 2,2)
for keyrect in topLayer.keys:
    rounded_rectangle(dwg, keyrect.x, keyrect.y, keyrect.w, keyrect.h, 2,2)

rounded_rectangle(dwg, 0, 0, keyboard_width, keyboard_height, 0, 0)

rounded_rectangle(dwg, keyboard_width*2+10, 0, keyboard_width, keyboard_height, 0, 0)
rounded_rectangle(dwg, 0, keyboard_height*2+10, keyboard_width, keyboard_height, 0, 0)
dwg.save()
