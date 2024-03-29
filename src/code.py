import rtc
import alarm
import displayio
import terminalio
from adafruit_magtag.magtag import MagTag
from adafruit_display_text import label
from adafruit_display_shapes import roundrect

magtag = MagTag()
border_thickness = 6

# Graphics
display_width = magtag.graphics.display.width
display_height = magtag.graphics.display.height
magtag.graphics.set_background(0x000000)
magtag.graphics.auto_refresh = True

time_group = displayio.Group()

# Outline
background_rect = roundrect.RoundRect(
    0,
    0,
    display_width,
    display_height,
    10,
    fill=None,
    outline=0xFFFFFF,
    stroke=border_thickness,
)
time_group.append(background_rect)

# Time Background
time_background_rect = roundrect.RoundRect(
    3 * border_thickness,
    display_height // 2 - border_thickness,
    display_width - 6 * border_thickness,
    display_height // 2 - border_thickness,
    10,
    fill=0xFFFFFF,
    outline=None,
    stroke=None,
)
time_group.append(time_background_rect)

# Date Display
date_display = label.Label(terminalio.FONT, text="MON JAN 1")
date_display.anchor_point = (0.5, 0.0)
date_display.anchored_position = (display_width // 2, 2 * border_thickness)
date_display.scale = 3
date_display.background_color = None

# Time Display
time_display = label.Label(terminalio.FONT, text="12:00 AM")
time_display.anchor_point = (0.5, 1.0)
time_display.anchored_position = (
    display_width // 2,
    display_height - 2 * border_thickness,
)
time_display.scale = 5
time_display.color = 0x000000
time_display.background_color = None

time_group.append(date_display)
time_group.append(time_display)

magtag.display.show(time_group)

# Modified from https://learn.adafruit.com/magtag-cat-feeder-clock/getting-the-date-time
def makeTimeText(time_struct):
    """Given a time.struct_time, return a string as H:MM or HH:MM, either
    12- or 24-hour style depending on twelve_hour flag.
    """
    postfix = ""
    if time_struct.tm_hour > 12:
        hour_string = str(time_struct.tm_hour - 12)  # 13-23 -> 1-11 (pm)
        postfix = " PM"
    elif time_struct.tm_hour > 0:
        hour_string = str(time_struct.tm_hour)  # 1-12
        postfix = " AM"
        if time_struct.tm_hour == 12:
            postfix = " PM"  # 12 -> 12 (pm)
    else:
        hour_string = "12"  # 0 -> 12 (am)
        postfix = " AM"
    time_string = hour_string + ":{mm:02d}".format(mm=time_struct.tm_min) + postfix
    time_display.text = time_string


def makeDateText(time_struct):
    days_of_week = ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")
    months = (
        "JAN",
        "FEB",
        "MAR",
        "APR",
        "MAY",
        "JUN",
        "JUL",
        "AUG",
        "SEP",
        "OCT",
        "NOV",
        "DEC",
    )
    date_string = (
        days_of_week[time_struct.tm_wday]
        + " "
        + months[time_struct.tm_mon - 1]
        + " "
        + str(time_struct.tm_mday)
    )
    date_display.text = date_string

now = rtc.RTC().datetime

def updateClock():
    makeTimeText(now)
    makeDateText(now)
    time_to_sleep = 60 - now.tm_sec
    alarm.sleep_memory[0] = now.tm_hour % 256
    magtag.display.refresh()
    magtag.exit_and_deep_sleep(time_to_sleep)

if not alarm.wake_alarm:
    alarm.sleep_memory[0] = 0
    try:
        time_display.text = "Syncing"
        magtag.display.refresh()
        magtag.network.get_local_time()
        updateClock()
    except (ValueError, RuntimeError, ConnectionError, OSError) as e:
        time_display.text = "Error"
        magtag.display.refresh()
        print(e)
elif alarm.sleep_memory[0] != now.tm_hour:
    try:
        magtag.network.get_local_time()
        updateClock()
    except (ValueError, RuntimeError, ConnectionError, OSError) as e:
        print(e)
else:
    updateClock()
