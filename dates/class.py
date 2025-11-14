class Cars:
    def __init__(self, make, model, year):
        self.make =make
        self.model = model
        self.year =year
car1 = Cars("Toyota", "Corolla", 2020)
car2 = Cars("Honda", "Civic", 2019)
print(car1.make)
print(car2.model)