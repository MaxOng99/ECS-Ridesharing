from models.environment import Environment

env = Environment(num_locations=10, num_passengers=5, max_coordinates=(100, 100))
print(env)