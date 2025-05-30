import os
import numpy as np

director = '/content/data'
frames = []
for file in os.listdir(director):
    frames.append(director + '/' + file)
frames.sort()
print(frames)


def f(filename, method = 'np'):
  if method == np:
    x = np.loadtxt(filename)
  else:
    f = open(filename)
    x = f.readlines()
  return x

def calculate_statistics(x, y):
  return{
      "mean": np.mean(y),
      "max": np.max(y),
      "min": np.min(y)
  }

def calculate_derivative(x, y):
  return np.gradient(y, x)

def calculate_integral(x, y):
  return np.trapz(y, x)

def write_file(filename, statistics, derivative, integral):
  with open(filename, 'w') as file:
        file.write(f"имя файла: {filename}\n")
        file.write(f"статистика:\n")
        file.write(f"среднее: {statistics['mean']}\n")
        file.write(f"максимльное: {statistics['max']}\n")
        file.write(f"минимальное: {statistics['min']}\n")
        file.write(f"производная:\n{derivative}\n")
        file.write(f"определенный интеграл: {integral}\n")



for i in range(1, 10):
  y = f(frames[i], np)
  x = f(frames[0], np)
  statistics = calculate_statistics(x, y)
  derivative = calculate_derivative(x, y)
  integral = calculate_integral(x, y)
  output_filename = f"out_yc-{i}.txt"
  write_file(output_filename, statistics, derivative.tolist(), integral)