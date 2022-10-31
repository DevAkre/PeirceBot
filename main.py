import requests
import io
import json, string, random
import pathlib
from datetime import date, datetime

from enum import Enum
from pdfminer.high_level import extract_text


class typeE(Enum):
  LUNCH = 0
  DINNER = 1
  BRUNCH = 2

class dayE(Enum):
  Monday = 0
  Tuesday = 1
  Wednesday = 2
  Thursday = 3
  Friday = 4
  Saturday = 5
  Sunday = 6

class Meal:
  type = typeE(0)
  day = dayE(0)
  meals = {}

  def printMeals(self):
    print(self.meals)

  def convMType(self, time):
    if time in range(0,10):
      return "BRUNCH"
    elif time in range(10,14):
      return "LUNCH"
    elif time in range(14,24):
      return "DINNER"


  def getMealMessage(self, day,time):
    Mtype = self.convMType(time)
    msg = day + " " + Mtype + "\n================\n"
    msg += '\n'.join(' = '.join((key.upper(),val)) for (key,val) in self.meals[day][Mtype].items())
    return msg;

  def read(self,text):
    lines = [line.strip() for line in text.splitlines() if line != '']
    for i in range(len(lines)):
      words = lines[i].split()
      if len(words) == 2 and words[-1] in typeE.__members__.keys():
        lines[i] = words[0]
        i+=1
        lines.insert(i, words[1])
    liter = iter(lines)
    while True:
      try:
          # get the next item
          element = next(liter)
          if element in dayE.__members__.keys():
            day = element
            element = next(liter)
            while element == ' ':
              element = next(liter)
            if element in typeE.__members__.keys():
              meal = element
              tempMeal = {}
              while True:
                branch = next(liter).split(' ')
                if len(branch) > 1:
                    tempMeal[branch[0]] = ' '.join(branch[2:])

                if branch[0] == "Soup":
                  break;
                if branch[0] == 'Vegetarian' and meal == "BRUNCH":
                  break;
                if branch[0] == 'Hearth' and meal == "DINNER" and day in ["Saturday","Sunday"]:
                    break;
              if day not in self.meals.keys():
                self.meals[day] = {meal:tempMeal}
              else:
                self.meals[day][meal] = tempMeal



      except StopIteration:
          break

def id_generator(size=10, chars=string.ascii_uppercase + string.digits):
  return ''.join(random.choice(chars) for _ in range(size))

def sendGroupMe(msg , accessToken, groupId):
  msgPacket =    {
        "message": {
          "source_guid": id_generator(),
          "text": msg,
        }
      }


  q_params = {'token': accessToken}
  response = requests.post('https://api.groupme.com/v3/groups/'+groupId+'/messages', json = msgPacket, params = q_params)

week = (datetime.now().strftime("%U"))
weekday = datetime.now().strftime("%A")
hour = int(datetime.now().strftime("%H"))

pdfFile = requests.get('https://www.aviserves.com/kenyon/menus/wk'+ week +'/Peirce_menu_wk'+ week +'.pdf').content
text = extract_text( io.BytesIO(pdfFile)).strip()

sch = Meal()
sch.read(text)
print(text)
sch.printMeals()
msg = sch.getMealMessage(weekday, hour)

data =  json.load(open(pathlib.Path("keys.json").resolve()))

sendGroupMe(msg, data['accessToken'],data['groupId'])
print(msg)
