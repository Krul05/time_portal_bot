class Museum:
    name_museum = ""
    map_url = ""
    longitude = ""
    type = ""
    def set_map_url(self, map_url):
        self.map_url = map_url

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