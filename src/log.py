import datetime

def __current_time():
  return datetime.datetime.now().strftime("%H:%M:%S %d:%m:%Y")

def log(message):
  print(f"[{__current_time()}]: {str(message)}")
