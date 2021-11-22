from collections import OrderedDict


class OrderedSet:
    def __init__(self, iterable=None) -> None:
        self.ordered_dict = OrderedDict()
        if iterable:
            self.__construct(iterable)

    def __construct(self, iterable):
        for item in iterable:
            self.add(item)

    def add(self, data):
        self.ordered_dict[data] = None
    
    def remove(self, data):
        self.ordered_dict.pop(data)

    def __len__(self):
        return len(self.ordered_dict)

    def __iter__(self):
        for item in self.ordered_dict.keys():
            yield item
        
