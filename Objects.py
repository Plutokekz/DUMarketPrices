class Square:

    def __init__(self, top_left, bottom_right):
        self.tl = top_left
        self.br = bottom_right
        self.back = [top_left, bottom_right]

    def center(self):
        tl_x, tl_y = self.tl
        br_x, br_y = self.br
        return (tl_x+br_x)//2, (tl_y+br_y)//2

    def add_y_offset(self, y_off):
        x, y = self.tl
        y = y + y_off
        self.tl = (x, y)
        x, y = self.br
        y = y + y_off
        self.br = (x, y)

    def reset(self):
        self.tl = self.back[0]
        self.br = self.back[1]


