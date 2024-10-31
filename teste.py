import unittest

class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Employee(metaclass = Singleton):
    def __init__(self):
        self.name = 'Rogerio'
        self.salary = 100
        
    def __str__(self):
        return f'{self.name} owns ${self.salary}.'

class EmployeeFactory():
    def __call__(cls, *args, **kwargs):
        return Employee()

def is_singleton(factory: EmployeeFactory) -> bool:
    emp1 = factory()
    emp2 = factory()
    return emp1 is emp2

class Evaluate(unittest.TestCase):
    def test_exercise(self):
        factory = EmployeeFactory()
        ret = is_singleton(factory)
        self.assertTrue(ret)

if __name__ == '__main__':
    unittest.main()