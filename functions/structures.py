class jcnt():
    def __init__(self):
        self.position = 0
        self.query_start = 0
        self.frame = ''
        self.ppm = 0.0
        self.orf = ''
        self.pos_que = ''

    def __repr__(self):
        string = "<Junction pos:%d, q.start:%d, ppm:%.3f, frame:%s, orf:%s>" % (self.position,
                                                                                self.query_start,
                                                                                self.ppm,
                                                                                self.frame,
                                                                                self.orf)
        return string

    def __eq__(self, other):
        return self.pos_que == other.pos_que

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__repr__())