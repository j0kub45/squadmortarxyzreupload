import math
import numpy as np
from PIL import Image

GRAVITY = 2 * 980
VELOCITY0 = 22000
VELOCITY_MAX = 22000
ACCELERATION = -2250
ACCELERATION_TIME = 2
TIME_DELTA = 0.05
ANGLE_DEG_DELTA = 0.1

SCALE_Y = 300
SCALE_X = 100
SCALE_TIME = 20 / 255


IMG_X_MIN = 0
IMG_X_MAX = 2600
IMG_Y_MIN = 0
IMG_Y_MAX = 2400
IMG_Y_OFFSET = 1200
IMG_ANGLE_MIN = 0
IMG_ANGLE_MAX = (256 * 256 - 1)
IMG_TIME_MIN = 0  # 0 shall be no value
IMG_TIME_MAX = 255

SCALE_ANGLE = math.pi / IMG_ANGLE_MAX
ANGLE_OFFSET = math.pi / 2

X_MIN = int(IMG_X_MIN * SCALE_X)
X_MAX = int(IMG_X_MAX * SCALE_X)
Y_MIN = int((IMG_Y_MIN - IMG_Y_OFFSET + 1) * SCALE_Y)
Y_MAX = int((IMG_Y_MAX - IMG_Y_OFFSET + 1) * SCALE_Y)
ANGLE_DEG_MIN = -90
ANGLE_DEG_MAX = 90
T_MIN = 0
T_MAX = 20

y_x2angle_timeLow = np.zeros((
  (IMG_Y_MAX - IMG_Y_MIN + 1),
  (IMG_X_MAX - IMG_X_MIN + 1),
  3
))

y_angle2xLow = np.zeros((
  (IMG_Y_MAX - IMG_Y_MIN + 1),
  IMG_ANGLE_MAX,
  3
))

y2xMax = np.zeros((
  (IMG_Y_MAX - IMG_Y_MIN + 1),
))

y_x2angle_timeHigh = np.ones((
  (IMG_Y_MAX - IMG_Y_MIN + 1),
  (IMG_X_MAX - IMG_X_MIN + 1),
  3
))

# arr1 = np.zeros((
#   (IMG_Y_MAX - IMG_Y_MIN),
#   (IMG_X_MAX - IMG_X_MIN),
#   3
# ))
# arr2 = np.zeros((
#   (IMG_Y_MAX - IMG_Y_MIN),
#   (IMG_X_MAX - IMG_X_MIN),
#   3
# ))

def save(arrLow, arrHigh, arrXMax, x, y, angle, time):
  #try:
  img_x = int(x / SCALE_X)
  img_y = int(y / SCALE_Y + IMG_Y_OFFSET)
  img_angle = int((angle + ANGLE_OFFSET) / SCALE_ANGLE)
  img_angle0 = img_angle >> 8
  img_angle1 = img_angle - img_angle0 * 256
  img_time = int(time / SCALE_TIME)
  #if IMG_X_MIN < img_x < IMG_X_MAX and 0 < img_y < 255 and 0 # probably the cleaner variant but w/e
  if img_x > arrXMax[img_y]:
    # we're still in low angle area and record new farthest distance
    arrXMax[img_y] = img_x

    #if arrLow[img_y, img_x, 0] == 0: # redundant in presence of max range check

    arrLow[img_y, img_x, 0] = img_angle0
    arrLow[img_y, img_x, 1] = img_angle1
    arrLow[img_y, img_x, 2] = img_time

  elif arrLow[img_y, img_x, 0] + 10 * SCALE_ANGLE < img_angle:
    # found high angle
    # FIXME: some numerical effects seem to cause gaps and weird values here. y-axis probably needs higher resolution
    # i.e. lower scale
    arrHigh[img_y, img_x, 0] = img_angle0
    arrHigh[img_y, img_x, 0] = img_angle1
    arrHigh[img_y, img_x, 2] = img_time
    pass



# def save2(arr1, arr2, x, y, angle, time):
#   #try:
#     img_x = int(x / SCALE_X)
#     img_y = int(y / SCALE_Y + IMG_Y_OFFSET)
#     img_angle = int(angle / SCALE_ANGLE + IMG_ANGLE_OFFSET)
#     img_time = int(time / SCALE_TIME)
#     #if IMG_X_MIN < img_x < IMG_X_MAX and 0 < img_y < 255 and 0
#     arr1[img_y, img_x, 0] = img_angle
#     arr2[img_y, img_x, 2] = img_time
#   #except IndexError as e:
#   #  print(x, y, angle, time)
#   #  print(img_x, img_y, img_angle, img_time)
#   #  raise e

for angle_step in range(int(ANGLE_DEG_MIN/ANGLE_DEG_DELTA), int(ANGLE_DEG_MAX/ANGLE_DEG_DELTA)):
  # reset:
  angle_deg = angle_step * ANGLE_DEG_DELTA
  angle = angle_deg / 180 * math.pi
  start_angle = angle

  x = 0
  y = 200
  dx = math.cos(angle) * VELOCITY0
  dy = math.sin(angle) * VELOCITY0

  for time_step in range(0, int(T_MAX/TIME_DELTA)):
    if y < Y_MIN:
      break

    t = time_step * TIME_DELTA
    x = x + dx * TIME_DELTA
    y = y + dy * TIME_DELTA
    v = math.sqrt(dx * dx + dy * dy)
    #if v > VELOCITY_MAX:
    #  y = y * VELOCITY_MAX / v
    #  x = x * VELOCITY_MAX / v

    if Y_MIN <= y <= Y_MAX and X_MIN <= x <= X_MAX and t > 0:
      save(y_x2angle_timeLow, y_x2angle_timeHigh, y2xMax, x, y, angle, t)

    if t <= ACCELERATION_TIME:
      flight_dir = math.atan2(dy, dx)
      dx = dx + math.cos(flight_dir) * ACCELERATION * TIME_DELTA
      dy = dy + math.sin(flight_dir) * ACCELERATION * TIME_DELTA

    dy = dy - TIME_DELTA * GRAVITY

print("Filling holes...")

def forwardFill(arr, y2xMax):
  (y_len, x_len, _) = arr.shape
  for y_index in range(y_len):
    lastValueIndex = 0
    lastValue = [0,0,0]
    for x_index in range(y2xMax[y_index].astype(int)):
      if arr[y_index, x_index, 0] != 0:
        lastValueIndex = x_index
        lastValue = arr[y_index, x_index]
      else:
        for x_index2 in range(lastValueIndex, x_index + 1):
          arr[y_index, x_index2] = lastValue

forwardFill(y_x2angle_timeLow, y2xMax)

img = Image.fromarray(y_x2angle_timeLow.astype(np.uint8), 'RGB')
img.save('../frontend/public/bm21_low.png')
img = Image.fromarray(y_x2angle_timeHigh.astype(np.uint8), 'RGB')
img.save('bm21_high.png')
img = Image.fromarray(y_angle2xLow.astype(np.uint8), 'RGB')
img.save('bm21_y_angle2x_low.png')
# img1 = Image.fromarray(arr1.astype(np.uint8), 'RGB')
# img2 = Image.fromarray(arr2.astype(np.uint8), 'RGB')
# img1.save('out1.png')
# img2.save('out2.png')

print("done.")
print(math.atan2(0, 1) * 180 / math.pi, math.cos(math.atan2(2,1)), math.sin(math.atan2(2,1)))
print(y_x2angle_timeLow[0:1, 0:10])
print(y_x2angle_timeLow[0:10, 2400:2420])

for r in (i* 100 for i in range(9, 18)):
  print(
    "range: ", r,
    "raw value: ", y_x2angle_timeLow[0 + IMG_Y_OFFSET, r],
    "angle: ", ((y_x2angle_timeLow[0 + IMG_Y_OFFSET, r][0] * 256 + y_x2angle_timeLow[0 + IMG_Y_OFFSET, r][1]) * SCALE_ANGLE - ANGLE_OFFSET) / math.pi*180,
    "time: ", y_x2angle_timeLow[0 + IMG_Y_OFFSET, r][2] * SCALE_TIME
    )