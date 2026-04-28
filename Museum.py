class Museum:
    name_museum = ""
    latitude = ""
    longitude = ""
    type = ""
    def set_latitude(self, latitude):
        self.latitude = latitude

    def set_longitude(self, longitude):
        self.longitude = longitude
    def set_name_museum(self, name_museium):
        self.name_museum = name_museium
    def set_type(self, type):
        self.type = type

    def get_type(self):
        if self.type == 'science':
            return "Наука и техника"
        elif self.type == 'culture':
            return "Культура"
        else:
            return "Другое"