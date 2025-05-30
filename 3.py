import datetime, time
global cache_cnt, cnt
#task 1

try: open("log.txt")
except:
  with open("log.txt", "w"):
    pass

def log_decorator(func):
  def wrapper(*args, **kwargs):
    log_text = ""
    log_text += datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
    log_text += f"функция '{func.__name__}' вызвана с агрументами: {str(args)}\n"

    start = time.time()
    res = func(*args, **kwargs)
    end = time.time()

    log_text += datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
    log_text += f"функция '{func.__name__}' завершена. "
    log_text += f"время выполнения: {str(round(end - start, 5))}сек.\n"

    with open("log.txt", "a") as f: f.write(log_text)

    return res

  return wrapper
@log_decorator
def calculate(x, y, operator = '+'):
  return eval(f"{x} {operator} {y}")

print(calculate(3, 5, '-'))
print(calculate(9999, 999, "**"))

#task 2
def rate_limit(max_calls:int = 5, period:int = 60):
  global last
  last = time.time()

  def limiter(func):
    global cnt
    cnt = 1

    def wrapper(*args, **kwargs):
      global cnt, last

      delta = abs(last - time.time())

      if (cnt > max_calls and delta < period):
        print(f"превышен лимит обращений: {max_calls} в {period}сек.")
        return
      else:
        cnt += 1
        last = time.time()

      return func(*args, **kwargs)
    return wrapper
  return limiter
@rate_limit(3, 2)
def send_message(text):
  print(f"отправлено сообщение: {text}")

for _ in range(5):
  send_message("опа")
time.sleep(2)

for _ in range(8):
  send_message("пупупу")
  time.sleep(2)

#task 3
cache_cnt = 0
cnt = 0

def cache_decorator(func):
  cache_dict = {}

  def wrapper(*args, **kwargs):
    global cache_cnt

    if str(args) in cache_dict.keys():
      return cache_dict[str(args)]
    else:
      res = func(*args, **kwargs)
      cache_dict[str(args)] = res
      cache_cnt = cache_cnt + 1

    return res

  return wrapper

@cache_decorator
def fibonacci1(n):
  if n <= 1:
    return n
  return fibonacci1(n-1) + fibonacci1(n-2)

print(fibonacci1(10), f"with cache_decorator: {cache_cnt}")

def fibonacci2(n):
  global cnt

  cnt = cnt + 1
  if n <= 1:
    return n
  return fibonacci2(n-1) + fibonacci2(n-2)

print(fibonacci2(10), f"without cache_docorator: {cnt}")