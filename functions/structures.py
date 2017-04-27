class jcnt():
    def __init__(self):
        self.position = 0
        self.query_start = 0
        self.frame = ''
        self.ppm = 0.0
        self.orf = ''
        self.frame_orf = False
        self.count = 1

    def __repr__(self):
        string = "<Junction pos:%d, " \
                 "q.start:%d, ppm:%.3f, " \
                 "frame:%s, orf:%s, " \
                 "count:%d>" % (self.position, self.query_start, self.ppm, self.frame, self.orf, self.count)
        return string

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__repr__())

