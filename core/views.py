import json

from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import LoginForm, RegisterForm


class RealCodeLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        if not form.cleaned_data.get("remember_me"):
            self.request.session.set_expiry(0)
        return response

FEATURES = [
    {"lang": "HTML", "title": "Interactive Browser", "icon": "layout", "color": "primary", "slug": None},
    {"lang": "CSS", "title": "Live Styling", "icon": "palette", "color": "secondary", "slug": None},
    {"lang": "JavaScript", "title": "Real Website Simulation", "icon": "zap", "color": "warning", "slug": "javascript"},
    {"lang": "Python", "title": "Interactive Playground", "icon": "terminal", "color": "success", "slug": "python"},
    {"lang": "C", "title": "Embedded Systems Simulator", "icon": "cpu", "color": "accent", "slug": "c"},
    {"lang": "Arduino", "title": "Virtual Hardware", "icon": "circuit-board", "color": "primary", "slug": "arduino"},
    {"lang": "Networking", "title": "Packet Animation", "icon": "network", "color": "secondary", "slug": None},
    {"lang": "SQL", "title": "Live Database", "icon": "database", "color": "success", "slug": None},
    {"lang": "APIs", "title": "Request Simulator", "icon": "webhook", "color": "warning", "slug": None},
    {"lang": "AI", "title": "Model Visualization", "icon": "brain-circuit", "color": "accent", "slug": None},
]

PYTHON_LESSONS = [
    {
        "slug": "variables-and-types",
        "title": "Variables & Types",
        "desc": "A real signup form's data in memory — watch Python infer str, int, float, bool the instant each field is assigned.",
        "pct": 0,
        "duration": "12 min",
        "starter_code": (
            'username = "alex_dev"\n'
            "age = 27\n"
            "account_balance = 149.99\n"
            "is_verified = True\n"
            "\n"
            "print(username, age, account_balance, is_verified)\n"
            "print(type(username).__name__, type(account_balance).__name__)\n"
        ),
        "hints": {
            "explain": "This is what a signup form looks like once it hits your backend: each field binds to a value in memory. Python doesn't need a type declaration — the type is attached to the value itself, not the variable name.",
            "wrong": "Nothing's broken. Try changing age = 27 to age = \"27\" (a string, like raw form input often arrives) and re-run — watch the type badge flip from int to str.",
            "challenge": "Challenge: add an email variable and a signup_date variable, then print type(...).__name__ for each — this is exactly what a User model validates.",
        },
    },
    {
        "slug": "conditionals",
        "title": "Conditionals",
        "desc": "An e-commerce discount calculator — step through if / elif / else tier logic inside a real function call.",
        "pct": 0,
        "duration": "15 min",
        "starter_code": (
            "def get_discount(order_total):\n"
            "    if order_total >= 200:\n"
            "        return 0.20\n"
            "    elif order_total >= 100:\n"
            "        return 0.10\n"
            "    elif order_total >= 50:\n"
            "        return 0.05\n"
            "    else:\n"
            "        return 0.0\n"
            "\n"
            "order_total = 120\n"
            "discount = get_discount(order_total)\n"
            'print("Order total:", order_total, "-> Discount:", discount)\n'
        ),
        "hints": {
            "explain": "This is a real checkout discount-tier calculator. get_discount() tests each spending threshold top to bottom and stops at the first one that's true — only one branch ever runs, same as pricing logic in a production cart service.",
            "wrong": "Nothing's wrong — try setting order_total = 30 and re-run to fall all the way through to the else branch (no discount).",
            "challenge": "Challenge: add a loyalty_member parameter that adds an extra 5% discount on top, regardless of tier.",
        },
    },
    {
        "slug": "lists-and-dicts",
        "title": "Lists & Dictionaries",
        "desc": "A warehouse inventory system — iterate a dict with .items() and watch both product name and stock count update each loop.",
        "pct": 0,
        "duration": "20 min",
        "starter_code": (
            'inventory = {"wireless_mouse": 42, "usb_cable": 118, "webcam": 7}\n'
            "\n"
            "total_units = 0\n"
            "for product, stock in inventory.items():\n"
            "    total_units += stock\n"
            '    print(product, "->", stock, "units")\n'
            "\n"
            'print("Total units in warehouse:", total_units)\n'
        ),
        "hints": {
            "explain": "This mirrors a real warehouse stock report. .items() gives you (key, value) pairs one at a time — that's why the loop unpacks into two variables, product and stock.",
            "wrong": "Nothing's wrong — try adding a new product to the inventory dict before the loop and re-run.",
            "challenge": "Challenge: track which product has the lowest stock in a variable called low_stock_alert — real systems use this to trigger reordering.",
        },
    },
    {
        "slug": "loops-and-functions",
        "title": "Loops, Functions & Memory",
        "desc": "A shopping cart checkout total — trace real Python execution line by line as it sums real prices.",
        "pct": 0,
        "duration": "18 min",
        "starter_code": (
            "def cart_total(prices):\n"
            "    total = 0\n"
            "    for price in prices:\n"
            "        total += price\n"
            "    return total\n"
            "\n"
            "cart = [19.99, 45.00, 7.50, 120.00]\n"
            "checkout_total = cart_total(cart)\n"
            'print("Checkout total: $", checkout_total)\n'
        ),
        "hints": {
            "explain": "This is the core of every e-commerce checkout: cart_total() loops over the cart once, adding each price into total, then returns it — classic accumulator pattern.",
            "wrong": "Nothing broken by default — try removing \"return total\" and see what the function gives back instead (hint: None) — a common real-world checkout bug.",
            "challenge": "Challenge: add a free_shipping_threshold — if checkout_total is over $100, print a free shipping message.",
        },
    },
    {
        "slug": "seat-booking",
        "title": "Movie Theater Seat Booking",
        "desc": "A real seat-map availability checker — nested loops scan every row and seat, calling a helper function on each one.",
        "pct": 0,
        "duration": "20 min",
        "starter_code": (
            "def is_seat_available(row, seat, booked_seats):\n"
            "    return (row, seat) not in booked_seats\n"
            "\n"
            "booked_seats = {(1, 2), (2, 3), (3, 1)}\n"
            "rows = 3\n"
            "seats_per_row = 3\n"
            "available_count = 0\n"
            "\n"
            "for row in range(1, rows + 1):\n"
            "    for seat in range(1, seats_per_row + 1):\n"
            "        if is_seat_available(row, seat, booked_seats):\n"
            "            available_count += 1\n"
            '            print(f"Seat {row}-{seat}: available")\n'
            "        else:\n"
            '            print(f"Seat {row}-{seat}: BOOKED")\n'
            "\n"
            'print("Total available seats:", available_count)\n'
        ),
        "hints": {
            "explain": "This is exactly how a real booking system renders a seat map: a nested loop walks every (row, seat) pair, and is_seat_available() gets called once per seat — 9 calls total for a 3x3 theater. The outer loop is rows, the inner loop is seats within that row.",
            "wrong": "Nothing's wrong — try adding (2, 1) to booked_seats and re-run to see one more seat flip to BOOKED.",
            "challenge": "Challenge: add a price_for_seat(row) function that charges more for row 1 (front row) than the back rows, and print the total revenue from booked seats.",
        },
    },
    {
        "slug": "library-checkout",
        "title": "Library Book Checkout System",
        "desc": "A real library circulation desk — a function checks availability against live inventory as each request is processed in a loop.",
        "pct": 0,
        "duration": "15 min",
        "starter_code": (
            "def can_checkout(book, available_books):\n"
            "    return available_books.get(book, 0) > 0\n"
            "\n"
            'inventory = {"Python Basics": 2, "Data Structures": 0, "Web Design": 1}\n'
            "\n"
            'requests = ["Python Basics", "Data Structures", "Web Design", "Python Basics"]\n'
            "\n"
            "for book in requests:\n"
            "    if can_checkout(book, inventory):\n"
            "        inventory[book] -= 1\n"
            '        print(f"{book}: checked out (left: {inventory[book]})")\n'
            "    else:\n"
            '        print(f"{book}: NOT AVAILABLE")\n'
        ),
        "hints": {
            "explain": "This is a real library circulation system: can_checkout() checks the live inventory dict before each checkout, and the loop processes requests one at a time — exactly why two people can't check out the same last copy of a book.",
            "wrong": "Nothing's wrong — try adding \"Data Structures\" earlier in requests before its stock runs out, and watch it succeed instead of failing.",
            "challenge": "Challenge: add a return_book(book, inventory) function and call it partway through to put a copy back in stock.",
        },
    },
    {
        "slug": "gpa-calculator",
        "title": "GPA Calculator",
        "desc": "A real school grade-point calculator — a function converts each test score to a grade point inside a loop, then averages them.",
        "pct": 0,
        "duration": "15 min",
        "starter_code": (
            "def gpa_from_scores(scores):\n"
            "    total = 0\n"
            "    for score in scores:\n"
            "        if score >= 90:\n"
            "            total += 4.0\n"
            "        elif score >= 80:\n"
            "            total += 3.0\n"
            "        elif score >= 70:\n"
            "            total += 2.0\n"
            "        else:\n"
            "            total += 1.0\n"
            "    return total / len(scores)\n"
            "\n"
            "student_scores = [95, 82, 76, 88]\n"
            "gpa = gpa_from_scores(student_scores)\n"
            'print("Scores:", student_scores)\n'
            'print(f"GPA: {gpa:.2f}")\n'
        ),
        "hints": {
            "explain": "This is a real GPA calculator: the loop inside gpa_from_scores() converts each raw test score into a grade point (4.0, 3.0, 2.0, or 1.0) using the same tiered thresholds a real school transcript system uses, then averages them.",
            "wrong": "Nothing's wrong — try adding a 65 to student_scores and re-run to see the GPA drop.",
            "challenge": "Challenge: add support for a 95+ score to count as 4.3 (an A+), and see how much it raises the GPA.",
        },
    },
]


C_LESSONS = [
    {
        "slug": "parking-sensor",
        "title": "Parking Sensor",
        "desc": "A car's ultrasonic parking sensor — read distance, warn the driver with an LED and buzzer before they hit something.",
        "pct": 0,
        "duration": "15 min",
        "sensor": {"kind": "distance", "label": "Distance", "unit": "cm", "min": 0, "max": 100, "default": 12},
        "starter_code": (
            "#include <stdio.h>\n"
            "\n"
            "int main() {\n"
            "    int distance = read_distance_cm();\n"
            "\n"
            "    if (distance < 20) {\n"
            "        led_on();\n"
            "        buzzer_on();\n"
            '        printf("WARNING: Obstacle at %d cm\\n", distance);\n'
            "    } else {\n"
            "        led_off();\n"
            "        buzzer_off();\n"
            '        printf("Clear: %d cm\\n", distance);\n'
            "    }\n"
            "\n"
            "    return 0;\n"
            "}\n"
        ),
        "hints": {
            "explain": "This is a real car parking-sensor loop: read the ultrasonic distance, and if something's closer than 20cm, light the warning LED and sound the buzzer — same logic used in real reversing-assist systems.",
            "wrong": "Nothing's wrong — drag the Distance slider above 20cm and hit Run again to see the 'Clear' path instead.",
            "challenge": "Challenge: add a second, closer threshold (under 5cm) that also prints \"STOP\" as a more urgent warning.",
        },
    },
    {
        "slug": "night-light",
        "title": "Automatic Night Light",
        "desc": "A dusk-to-dawn porch light — read ambient light level and switch the LED on only when it's dark.",
        "pct": 0,
        "duration": "12 min",
        "sensor": {"kind": "light", "label": "Light level", "unit": "", "min": 0, "max": 1023, "default": 120},
        "starter_code": (
            "#include <stdio.h>\n"
            "\n"
            "int main() {\n"
            "    int light_level = read_light_level();\n"
            "\n"
            "    if (light_level < 300) {\n"
            "        led_on();\n"
            '        printf("Dark (%d) -> light ON\\n", light_level);\n'
            "    } else {\n"
            "        led_off();\n"
            '        printf("Bright (%d) -> light OFF\\n", light_level);\n'
            "    }\n"
            "\n"
            "    return 0;\n"
            "}\n"
        ),
        "hints": {
            "explain": "This is exactly how real dusk-to-dawn porch lights work: a photoresistor reports a light level, and a single threshold check decides whether the LED should be on.",
            "wrong": "Nothing's wrong — drag the light slider above 300 and re-run to see the light switch OFF.",
            "challenge": "Challenge: add a second tier — below 50 (very dark), also turn on a buzzer to simulate a security alert.",
        },
    },
    {
        "slug": "conveyor-ramp",
        "title": "Conveyor Belt Speed Ramp",
        "desc": "A factory conveyor motor — ramp speed up gradually in a loop instead of jumping straight to full power.",
        "pct": 0,
        "duration": "15 min",
        "sensor": None,
        "starter_code": (
            "#include <stdio.h>\n"
            "\n"
            "int main() {\n"
            "    int speed;\n"
            "\n"
            "    for (speed = 0; speed <= 100; speed += 25) {\n"
            "        set_motor_speed(speed);\n"
            '        printf("Motor speed: %d%%\\n", speed);\n'
            "    }\n"
            "\n"
            "    return 0;\n"
            "}\n"
        ),
        "hints": {
            "explain": "Real conveyor and fan motors ramp speed up gradually instead of jumping straight to 100% — sudden full power can jerk the belt or trip a breaker. This for loop increases speed in steps of 25%.",
            "wrong": "Nothing's wrong — try changing the step from += 25 to += 10 for a smoother, slower ramp.",
            "challenge": "Challenge: add a matching ramp-down loop after this one that brings speed back to 0 in the same steps.",
        },
    },
    {
        "slug": "temperature-alarm",
        "title": "Server Room Temperature Alarm",
        "desc": "A server-room monitor — poll temperature in a loop and sound a buzzer alarm the moment it overheats.",
        "pct": 0,
        "duration": "18 min",
        "sensor": {"kind": "temperature", "label": "Start temp", "unit": "°C", "min": -10, "max": 50, "default": 28},
        "starter_code": (
            "#include <stdio.h>\n"
            "\n"
            "int is_overheating(int temp) {\n"
            "    return temp > 30;\n"
            "}\n"
            "\n"
            "int main() {\n"
            "    int temp = read_temperature_c();\n"
            "    int checks = 0;\n"
            "\n"
            "    while (checks < 3) {\n"
            "        if (is_overheating(temp)) {\n"
            "            buzzer_on();\n"
            '            printf("ALERT: %d C - overheating!\\n", temp);\n'
            "        } else {\n"
            "            buzzer_off();\n"
            '            printf("OK: %d C\\n", temp);\n'
            "        }\n"
            "        temp += 2;\n"
            "        checks += 1;\n"
            "    }\n"
            "\n"
            "    return 0;\n"
            "}\n"
        ),
        "hints": {
            "explain": "This mirrors a real server-room or fridge monitor: is_overheating() is a separate function the while loop calls on every check — a real deployment would run this forever, we just cap it at 3 checks so you can watch it happen.",
            "wrong": "Nothing's wrong — drag the start temperature slider above 30°C to see the ALERT fire immediately on the first check.",
            "challenge": "Challenge: change is_overheating() to also require two consecutive high readings before alerting, to avoid false alarms from a single spike.",
        },
    },
    {
        "slug": "elevator-dispatch",
        "title": "Elevator Dispatch System",
        "desc": "A real elevator controller — an outer loop travels floor by floor, a function decides where to stop, and a nested loop rings the door chime.",
        "pct": 0,
        "duration": "20 min",
        "sensor": None,
        "starter_code": (
            "#include <stdio.h>\n"
            "\n"
            "int should_stop(int floor) {\n"
            "    return floor % 2 == 0;\n"
            "}\n"
            "\n"
            "int main() {\n"
            "    int floor;\n"
            "    int chime;\n"
            "\n"
            "    for (floor = 1; floor <= 5; floor++) {\n"
            "        set_motor_speed(60);\n"
            '        printf("Elevator passing floor %d\\n", floor);\n'
            "\n"
            "        if (should_stop(floor)) {\n"
            "            set_motor_speed(0);\n"
            "            led_on();\n"
            '            printf("Stopping at floor %d\\n", floor);\n'
            "\n"
            "            for (chime = 0; chime < 2; chime++) {\n"
            "                buzzer_on();\n"
            '                printf("Door chime %d\\n", chime + 1);\n'
            "                buzzer_off();\n"
            "            }\n"
            "\n"
            "            led_off();\n"
            "        }\n"
            "    }\n"
            "\n"
            '    printf("Elevator reached top floor\\n");\n'
            "    return 0;\n"
            "}\n"
        ),
        "hints": {
            "explain": "This is a real elevator control loop: the outer for loop travels floor by floor (motor running), should_stop() is called on every floor to decide whether to stop, and when it does, a nested loop rings the door chime twice before continuing — a loop inside a loop, plus a function call, exactly like a real lift controller's dispatch logic.",
            "wrong": "Nothing's wrong — try changing should_stop() to floor % 3 == 0 and re-run to see it stop at different floors.",
            "challenge": "Challenge: add a second function, doors_are_clear(), that must also return true before the elevator can continue past a stop — simulate a safety sensor check.",
        },
    },
    {
        "slug": "sprinkler-zones",
        "title": "Automatic Sprinkler Zones",
        "desc": "A real farm/garden irrigation controller — a loop checks soil moisture across 4 zones, calling a function to decide which ones need water.",
        "pct": 0,
        "duration": "15 min",
        "sensor": None,
        "starter_code": (
            "#include <stdio.h>\n"
            "\n"
            "int needs_water(int moisture) {\n"
            "    return moisture < 40;\n"
            "}\n"
            "\n"
            "int main() {\n"
            "    int zone;\n"
            "\n"
            "    for (zone = 1; zone <= 4; zone++) {\n"
            "        int moisture = 15 + zone * 10;\n"
            '        printf("Zone %d moisture: %d%%\\n", zone, moisture);\n'
            "\n"
            "        if (needs_water(moisture)) {\n"
            "            set_motor_speed(80);\n"
            '            printf("Zone %d: WATERING\\n", zone);\n'
            "        } else {\n"
            "            set_motor_speed(0);\n"
            '            printf("Zone %d: OK, skip\\n", zone);\n'
            "        }\n"
            "    }\n"
            "\n"
            "    return 0;\n"
            "}\n"
        ),
        "hints": {
            "explain": "This is a real irrigation controller: the loop checks each of 4 zones in turn, and needs_water() decides independently whether that zone's soil is dry enough to trigger the pump — the same per-zone logic used by real farm and garden sprinkler systems.",
            "wrong": "Nothing's wrong — try lowering the threshold in needs_water() from 40 to 30 and re-run to see fewer zones trigger watering.",
            "challenge": "Challenge: add a rain_recently variable that, when true, skips watering entirely regardless of moisture.",
        },
    },
    {
        "slug": "vending-change",
        "title": "Vending Machine Change Dispenser",
        "desc": "A real vending machine's change-making algorithm — a function computes how many of each coin to dispense, called once per denomination.",
        "pct": 0,
        "duration": "15 min",
        "sensor": None,
        "starter_code": (
            "#include <stdio.h>\n"
            "\n"
            "int coins_needed(int cents, int coin_value) {\n"
            "    return cents / coin_value;\n"
            "}\n"
            "\n"
            "int main() {\n"
            "    int change = 87;\n"
            "    int quarters;\n"
            "    int dimes;\n"
            "    int nickels;\n"
            "    int pennies;\n"
            "\n"
            "    quarters = coins_needed(change, 25);\n"
            "    change = change - quarters * 25;\n"
            "\n"
            "    dimes = coins_needed(change, 10);\n"
            "    change = change - dimes * 10;\n"
            "\n"
            "    nickels = coins_needed(change, 5);\n"
            "    change = change - nickels * 5;\n"
            "\n"
            "    pennies = change;\n"
            "\n"
            '    printf("Quarters: %d\\n", quarters);\n'
            '    printf("Dimes: %d\\n", dimes);\n'
            '    printf("Nickels: %d\\n", nickels);\n'
            '    printf("Pennies: %d\\n", pennies);\n'
            "\n"
            "    return 0;\n"
            "}\n"
        ),
        "hints": {
            "explain": "This is the real greedy change-making algorithm every vending machine and cash register uses: coins_needed() is called once per coin denomination, largest first, and each call reduces the remaining change before the next call runs.",
            "wrong": "Nothing's wrong — try changing change = 87 to change = 99 and re-run to see a different coin breakdown.",
            "challenge": "Challenge: add a dollars coin_value of 100 and call coins_needed() with it first, before quarters.",
        },
    },
]

ARDUINO_LESSONS = [
    {
        "slug": "blink-led",
        "title": "Blink the Built-in LED",
        "desc": "The first sketch every Arduino developer writes — a real status LED blinking on and off forever, the exact heartbeat pattern used to show a device is alive.",
        "pct": 0,
        "duration": "10 min",
        "sensor": None,
        "starter_code": (
            "void setup() {\n"
            "  pinMode(LED_BUILTIN, OUTPUT);\n"
            "  Serial.begin(9600);\n"
            "}\n"
            "\n"
            "void loop() {\n"
            "  digitalWrite(LED_BUILTIN, HIGH);\n"
            '  Serial.println("LED ON");\n'
            "  delay(500);\n"
            "  digitalWrite(LED_BUILTIN, LOW);\n"
            '  Serial.println("LED OFF");\n'
            "  delay(500);\n"
            "}\n"
        ),
        "hints": {
            "explain": "setup() runs once when the board powers on — that's where you configure pins. loop() then runs forever after that — here it's the real Arduino \"blink\" pattern: every real device's status LED (routers, phones charging, servers) uses this exact on/delay/off/delay loop.",
            "wrong": "Nothing's wrong — try changing both delay(500) calls to delay(100) and imagine the LED blinking 5x faster.",
            "challenge": "Challenge: make it blink twice as fast for LED ON as for LED OFF, like a real turn signal.",
        },
    },
    {
        "slug": "night-light",
        "title": "Photoresistor Night Light",
        "desc": "A real dusk-to-dawn light sensor read every loop — watch the LED react as the light level changes over 3 real polling cycles.",
        "pct": 0,
        "duration": "15 min",
        "sensor": {"label": "Light level", "unit": "", "sequence": [700, 150, 900]},
        "starter_code": (
            "int lightPin = A0;\n"
            "int ledPin = 13;\n"
            "\n"
            "void setup() {\n"
            "  pinMode(ledPin, OUTPUT);\n"
            "  Serial.begin(9600);\n"
            "}\n"
            "\n"
            "void loop() {\n"
            "  int lightLevel = analogRead(lightPin);\n"
            "  Serial.println(lightLevel);\n"
            "\n"
            "  if (lightLevel < 300) {\n"
            "    digitalWrite(ledPin, HIGH);\n"
            '    Serial.println("Dark -> LED ON");\n'
            "  } else {\n"
            "    digitalWrite(ledPin, LOW);\n"
            '    Serial.println("Bright -> LED OFF");\n'
            "  }\n"
            "\n"
            "  delay(1000);\n"
            "}\n"
        ),
        "hints": {
            "explain": "analogRead(A0) reads a real photoresistor's voltage as a number 0-1023. Because this is inside loop(), it re-reads the sensor every cycle — that's why each of the 3 loop iterations below shows a different light reading and the LED reacting live, exactly like a real porch light responding as the sun sets.",
            "wrong": "Nothing's wrong — try changing the threshold from 300 to 500 and see which readings now count as 'dark'.",
            "challenge": "Challenge: add a second, darker threshold (under 50) that also triggers a buzzer for a security alert.",
        },
    },
    {
        "slug": "ultrasonic-parking-sensor",
        "title": "Ultrasonic Parking Sensor",
        "desc": "A real car parking sensor polling distance every loop — LED and buzzer react live as an object gets closer then moves away.",
        "pct": 0,
        "duration": "18 min",
        "sensor": {"label": "Distance", "unit": "cm", "sequence": [50, 12, 45]},
        "starter_code": (
            "int trigPin = 7;\n"
            "int ledPin = 13;\n"
            "int buzzerPin = 8;\n"
            "\n"
            "void setup() {\n"
            "  pinMode(ledPin, OUTPUT);\n"
            "  pinMode(buzzerPin, OUTPUT);\n"
            "  Serial.begin(9600);\n"
            "}\n"
            "\n"
            "void loop() {\n"
            "  int distance = analogRead(trigPin);\n"
            "  Serial.println(distance);\n"
            "\n"
            "  if (distance < 20) {\n"
            "    digitalWrite(ledPin, HIGH);\n"
            "    digitalWrite(buzzerPin, HIGH);\n"
            '    Serial.println("WARNING: obstacle close");\n'
            "  } else {\n"
            "    digitalWrite(ledPin, LOW);\n"
            "    digitalWrite(buzzerPin, LOW);\n"
            '    Serial.println("Clear");\n'
            "  }\n"
            "\n"
            "  delay(1000);\n"
            "}\n"
        ),
        "hints": {
            "explain": "This is the real loop a reversing car alarm runs: poll the distance sensor, compare against a safe threshold, and react immediately with the LED and buzzer. Because it's inside loop(), it keeps re-checking forever — watch the 3 cycles below show the object approach and then clear.",
            "wrong": "Nothing's wrong — try lowering the threshold from 20 to 10 to make the alarm less sensitive.",
            "challenge": "Challenge: add a second, closer threshold (under 5cm) that also prints \"STOP\" as a more urgent warning.",
        },
    },
    {
        "slug": "traffic-light",
        "title": "Traffic Light Controller",
        "desc": "A real 3-light traffic signal — loop() cycles green, yellow, then red, the exact timing pattern every intersection controller runs.",
        "pct": 0,
        "duration": "12 min",
        "sensor": None,
        "starter_code": (
            "int redPin = 10;\n"
            "int yellowPin = 11;\n"
            "int greenPin = 12;\n"
            "\n"
            "void setup() {\n"
            "  pinMode(redPin, OUTPUT);\n"
            "  pinMode(yellowPin, OUTPUT);\n"
            "  pinMode(greenPin, OUTPUT);\n"
            "  Serial.begin(9600);\n"
            "}\n"
            "\n"
            "void loop() {\n"
            "  digitalWrite(greenPin, HIGH);\n"
            '  Serial.println("GREEN - Go");\n'
            "  delay(1000);\n"
            "  digitalWrite(greenPin, LOW);\n"
            "\n"
            "  digitalWrite(yellowPin, HIGH);\n"
            '  Serial.println("YELLOW - Slow down");\n'
            "  delay(1000);\n"
            "  digitalWrite(yellowPin, LOW);\n"
            "\n"
            "  digitalWrite(redPin, HIGH);\n"
            '  Serial.println("RED - Stop");\n'
            "  delay(1000);\n"
            "  digitalWrite(redPin, LOW);\n"
            "}\n"
        ),
        "hints": {
            "explain": "This is a real traffic light sequence: each loop() cycle turns on exactly one LED at a time in order — green, yellow, red — then repeats. Watch the 3 cycles below run the full sequence 3 times, just like a real intersection controller.",
            "wrong": "Nothing's wrong — try shortening the yellow delay to 300 to make it feel more urgent, like a real caution phase.",
            "challenge": "Challenge: add a pedestrian walk signal on a 4th pin that only turns on during the red phase.",
        },
    },
    {
        "slug": "soil-moisture",
        "title": "Soil Moisture Watering Alert",
        "desc": "A real automatic garden watering system — a function decides whether to run the pump based on a live soil moisture reading each cycle.",
        "pct": 0,
        "duration": "15 min",
        "sensor": {"label": "Soil moisture", "unit": "", "sequence": [200, 600, 350]},
        "starter_code": (
            "int moisturePin = A0;\n"
            "int pumpPin = 9;\n"
            "\n"
            "int needsWater(int moisture) {\n"
            "  return moisture < 400;\n"
            "}\n"
            "\n"
            "void setup() {\n"
            "  pinMode(pumpPin, OUTPUT);\n"
            "  Serial.begin(9600);\n"
            "}\n"
            "\n"
            "void loop() {\n"
            "  int moisture = analogRead(moisturePin);\n"
            "  Serial.println(moisture);\n"
            "\n"
            "  if (needsWater(moisture)) {\n"
            "    digitalWrite(pumpPin, HIGH);\n"
            '    Serial.println("Pump ON");\n'
            "  } else {\n"
            "    digitalWrite(pumpPin, LOW);\n"
            '    Serial.println("Pump OFF");\n'
            "  }\n"
            "\n"
            "  delay(1000);\n"
            "}\n"
        ),
        "hints": {
            "explain": "This is a real automatic garden watering system: needsWater() is a separate function that checks the live soil moisture reading against a threshold every loop() cycle — this is exactly how smart garden and greenhouse controllers decide when to run the pump.",
            "wrong": "Nothing's wrong — drag the soil moisture readings above so all 3 are below 400 and re-run to see the pump stay on the whole time.",
            "challenge": "Challenge: add a maxRuntime check that turns the pump off after it's been on for 2 consecutive cycles, to prevent overwatering.",
        },
    },
]

JS_LESSONS = [
    {
        "slug": "age-verification",
        "title": "Age Verification Gate",
        "desc": "A real access-control check — the exact if/else gate every age-restricted signup form runs.",
        "pct": 0,
        "duration": "10 min",
        "starter_code": (
            "let age = 17;\n"
            "\n"
            "if (age >= 18) {\n"
            '  console.log("Access Granted");\n'
            "} else {\n"
            '  console.log("Access Denied");\n'
            "}\n"
        ),
        "hints": {
            "explain": "This is a real access-control check — the same if/else gate that runs behind every age-restricted signup form. Only one branch ever executes.",
            "wrong": "Nothing is broken — try setting age to 20 and re-run to see the other branch.",
            "challenge": "Challenge: add a third branch that prints \"VIP Access\" when age is over 65.",
        },
        "interpret_js": (
            "(logs) => {\n"
            "  if (logs.some(l => l.includes('Access Granted'))) return { status: 'good', label: 'Access Granted', detail: 'age >= 18' };\n"
            "  if (logs.some(l => l.includes('Access Denied'))) return { status: 'bad', label: 'Access Denied', detail: 'age < 18' };\n"
            "  return { status: 'neutral', label: 'Waiting for output…', detail: '' };\n"
            "}"
        ),
    },
    {
        "slug": "password-strength",
        "title": "Password Strength Checker",
        "desc": "A real signup password meter — loop over validation rules and score the password, exactly like every account-creation form.",
        "pct": 0,
        "duration": "15 min",
        "starter_code": (
            "function checkPasswordStrength(password) {\n"
            "  const rules = [\n"
            '    { test: p => p.length >= 8, label: "At least 8 characters" },\n'
            '    { test: p => /[A-Z]/.test(p), label: "Contains an uppercase letter" },\n'
            '    { test: p => /[0-9]/.test(p), label: "Contains a number" },\n'
            "  ];\n"
            "\n"
            "  let passed = 0;\n"
            "  for (const rule of rules) {\n"
            "    const ok = rule.test(password);\n"
            '    console.log((ok ? "PASS" : "FAIL") + ": " + rule.label);\n'
            "    if (ok) passed++;\n"
            "  }\n"
            "\n"
            "  return passed;\n"
            "}\n"
            "\n"
            'const password = "Secret123";\n'
            "const score = checkPasswordStrength(password);\n"
            'console.log("Strength:", score, "/", 3);\n'
        ),
        "hints": {
            "explain": "This is a real password-strength meter: a for loop runs the password through each rule in an array, printing PASS/FAIL for every one — exactly how signup forms show a live checklist as you type.",
            "wrong": "Nothing's wrong — try changing password to \"abc\" and re-run to see every rule fail.",
            "challenge": "Challenge: add a 4th rule requiring a special character like ! or @, using a regex test.",
        },
        "interpret_js": (
            "(logs) => {\n"
            "  const m = logs.find(l => l.startsWith('Strength:'));\n"
            "  if (!m) return { status: 'neutral', label: 'Waiting for output…', detail: '' };\n"
            "  const score = parseInt(m.split(':')[1], 10) || 0;\n"
            "  if (score >= 3) return { status: 'good', label: 'Strong password', detail: score + ' / 3 rules passed' };\n"
            "  if (score >= 1) return { status: 'neutral', label: 'Weak password', detail: score + ' / 3 rules passed' };\n"
            "  return { status: 'bad', label: 'Very weak password', detail: score + ' / 3 rules passed' };\n"
            "}"
        ),
    },
    {
        "slug": "cart-discount",
        "title": "Shopping Cart Discount",
        "desc": "A real e-commerce checkout — loop to sum the cart, then apply a tiered discount, the exact math behind every store's cart total.",
        "pct": 0,
        "duration": "15 min",
        "starter_code": (
            "const cart = [25.99, 12.50, 40.00, 8.75];\n"
            "\n"
            "let total = 0;\n"
            "for (const price of cart) {\n"
            "  total += price;\n"
            "}\n"
            "\n"
            "let discount = 0;\n"
            "if (total >= 100) {\n"
            "  discount = 0.15;\n"
            "} else if (total >= 50) {\n"
            "  discount = 0.10;\n"
            "}\n"
            "\n"
            "const finalTotal = total - total * discount;\n"
            'console.log("Subtotal: $" + total.toFixed(2));\n'
            'console.log("Discount:", (discount * 100) + "%");\n'
            'console.log("Final total: $" + finalTotal.toFixed(2));\n'
        ),
        "hints": {
            "explain": "This is real checkout math: a for...of loop accumulates the cart's subtotal, then an if/else if chain picks a discount tier — the same two-step pattern (sum, then tier) used in every e-commerce cart service.",
            "wrong": "Nothing's wrong — try adding another item like 30.00 to the cart and re-run to see the subtotal cross into the next discount tier.",
            "challenge": "Challenge: add free shipping messaging that prints when finalTotal is over $75.",
        },
        "interpret_js": (
            "(logs) => {\n"
            "  const discountLine = logs.find(l => l.startsWith('Discount:'));\n"
            "  const totalLine = logs.find(l => l.startsWith('Final total:'));\n"
            "  if (!discountLine || !totalLine) return { status: 'neutral', label: 'Waiting for output…', detail: '' };\n"
            "  const pct = discountLine.split(':')[1].trim();\n"
            "  const total = totalLine.split('$')[1];\n"
            "  if (pct !== '0%') return { status: 'good', label: pct + ' discount applied', detail: 'Final total: $' + total };\n"
            "  return { status: 'neutral', label: 'No discount', detail: 'Final total: $' + total };\n"
            "}"
        ),
    },
    {
        "slug": "shipping-calculator",
        "title": "Shipping Cost Calculator",
        "desc": "A real checkout shipping-rate lookup — a function returns a tiered price based on package weight, called once per item in a loop.",
        "pct": 0,
        "duration": "12 min",
        "starter_code": (
            "function calculateShipping(weightKg) {\n"
            "  if (weightKg <= 1) return 4.99;\n"
            "  if (weightKg <= 5) return 9.99;\n"
            "  if (weightKg <= 20) return 19.99;\n"
            "  return 39.99;\n"
            "}\n"
            "\n"
            "const packages = [0.5, 3, 12, 25];\n"
            "let totalShipping = 0;\n"
            "\n"
            "for (const weight of packages) {\n"
            "  const cost = calculateShipping(weight);\n"
            '  console.log("Package " + weight + "kg -> $" + cost.toFixed(2));\n'
            "  totalShipping += cost;\n"
            "}\n"
            "\n"
            'console.log("Total shipping: $" + totalShipping.toFixed(2));\n'
        ),
        "hints": {
            "explain": "This is a real shipping-rate calculator: calculateShipping() is a pure function that maps a weight to a tiered price, and the loop calls it once per package — the exact pattern every e-commerce checkout uses to price a multi-item order.",
            "wrong": "Nothing's wrong — try adding a 0.2kg package and re-run to see it fall into the cheapest tier.",
            "challenge": "Challenge: add a free-shipping rule that returns 0 when weightKg is 0, to represent a digital/no-shipping item.",
        },
        "interpret_js": (
            "(logs) => {\n"
            "  const m = logs.find(l => l.startsWith('Total shipping:'));\n"
            "  if (!m) return { status: 'neutral', label: 'Waiting for output…', detail: '' };\n"
            "  const total = m.split('$')[1];\n"
            "  return { status: 'good', label: 'Shipping calculated', detail: 'Total: $' + total };\n"
            "}"
        ),
    },
    {
        "slug": "email-validator",
        "title": "Email Validator",
        "desc": "A real signup-form field check — a function tests each address against a pattern inside a loop, exactly like live form validation.",
        "pct": 0,
        "duration": "12 min",
        "starter_code": (
            "function isValidEmail(email) {\n"
            "  const pattern = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;\n"
            "  return pattern.test(email);\n"
            "}\n"
            "\n"
            'const emails = ["user@example.com", "invalid-email", "test@site.org"];\n'
            "\n"
            "for (const email of emails) {\n"
            "  const valid = isValidEmail(email);\n"
            '  console.log(email + " -> " + (valid ? "VALID" : "INVALID"));\n'
            "}\n"
        ),
        "hints": {
            "explain": "This is real signup-form validation: isValidEmail() tests each address against a pattern requiring text, an @, and a domain — the same kind of check that runs live as you type into a real email field, just applied to a list here instead of one input.",
            "wrong": "Nothing's wrong — try adding \"missing-at-sign.com\" to emails and re-run to see it marked INVALID.",
            "challenge": "Challenge: tighten the pattern to also require the domain to end in a known suffix like .com or .org.",
        },
        "interpret_js": (
            "(logs) => {\n"
            "  if (!logs.length) return { status: 'neutral', label: 'Waiting for output…', detail: '' };\n"
            "  const validCount = logs.filter(l => l.endsWith('-> VALID')).length;\n"
            "  const total = logs.length;\n"
            "  if (validCount === total) return { status: 'good', label: 'All emails valid', detail: validCount + ' / ' + total };\n"
            "  if (validCount === 0) return { status: 'bad', label: 'No valid emails', detail: validCount + ' / ' + total };\n"
            "  return { status: 'neutral', label: validCount + ' of ' + total + ' valid', detail: '' };\n"
            "}"
        ),
    },
]


def home(request):
    return render(request, "core/home.html", {"features": FEATURES})


COURSE_URL_NAMES = {"python": "course_python", "c": "course_c", "arduino": "course_arduino", "javascript": "course_javascript"}


def features_with_course_urls():
    features = []
    for f in FEATURES:
        entry = dict(f)
        url_name = COURSE_URL_NAMES.get(f["slug"])
        entry["course_url"] = reverse(url_name) if url_name else None
        features.append(entry)
    return features


def courses(request):
    return render(request, "core/courses.html", {"features": features_with_course_urls()})


def labs(request):
    return render(request, "core/labs.html", {"features": features_with_course_urls()})


@login_required
def dashboard(request):
    context = {
        "xp": 4280,
        "level": 12,
        "streak": 27,
        "weekly_goal_pct": 68,
        "coins": 1540,
        "recent_lessons": [
            {"title": "Age Verification Gate", "course": "JavaScript Fundamentals", "pct": 80, "url": reverse("lesson_javascript", args=["age-verification"])},
            {"title": "Movie Theater Seat Booking", "course": "Python Fundamentals", "pct": 45, "url": reverse("lesson_python", args=["seat-booking"])},
            {"title": "Ultrasonic Parking Sensor", "course": "Arduino & Embedded C", "pct": 100, "url": reverse("lesson_c", args=["parking-sensor"])},
        ],
        "achievements": [
            {"name": "First Steps", "icon": "footprints", "unlocked": True},
            {"name": "7-Day Streak", "icon": "flame", "unlocked": True},
            {"name": "Bug Hunter", "icon": "bug", "unlocked": True},
            {"name": "API Master", "icon": "webhook", "unlocked": False},
        ],
        "leaderboard": [
            {"rank": 1, "name": "Maya Chen", "xp": 9840},
            {"rank": 2, "name": "Diego Ramos", "xp": 9120},
            {"rank": 3, "name": "Amara Obi", "xp": 8770},
            {"rank": 4, "name": "You", "xp": 4280, "is_user": True},
        ],
    }
    return render(request, "core/dashboard.html", context)


def course_python(request):
    return render(request, "core/course_python.html", {"lessons": PYTHON_LESSONS})


def lesson_python(request, slug):
    lesson = next((l for l in PYTHON_LESSONS if l["slug"] == slug), None)
    if lesson is None:
        lesson = PYTHON_LESSONS[0]
    context = {
        "lesson": lesson,
        "starter_code_json": json.dumps(lesson["starter_code"]),
        "hints_json": json.dumps(lesson["hints"]),
    }
    return render(request, "core/lesson_python.html", context)


def course_c(request):
    return render(request, "core/course_c.html", {"lessons": C_LESSONS})


def lesson_c(request, slug):
    lesson = next((l for l in C_LESSONS if l["slug"] == slug), None)
    if lesson is None:
        lesson = C_LESSONS[0]
    context = {
        "lesson": lesson,
        "starter_code_json": json.dumps(lesson["starter_code"]),
        "hints_json": json.dumps(lesson["hints"]),
        "sensor_json": json.dumps(lesson["sensor"]),
    }
    return render(request, "core/lesson_c.html", context)


def course_arduino(request):
    return render(request, "core/course_arduino.html", {"lessons": ARDUINO_LESSONS})


def lesson_arduino(request, slug):
    lesson = next((l for l in ARDUINO_LESSONS if l["slug"] == slug), None)
    if lesson is None:
        lesson = ARDUINO_LESSONS[0]
    context = {
        "lesson": lesson,
        "starter_code_json": json.dumps(lesson["starter_code"]),
        "hints_json": json.dumps(lesson["hints"]),
        "sensor_json": json.dumps(lesson["sensor"]),
    }
    return render(request, "core/lesson_arduino.html", context)


def course_javascript(request):
    return render(request, "core/course_javascript.html", {"lessons": JS_LESSONS})


def lesson_javascript(request, slug):
    lesson = next((l for l in JS_LESSONS if l["slug"] == slug), None)
    if lesson is None:
        lesson = JS_LESSONS[0]
    context = {
        "lesson": lesson,
        "starter_code_json": json.dumps(lesson["starter_code"]),
        "hints_json": json.dumps(lesson["hints"]),
        "interpret_js": lesson["interpret_js"],
    }
    return render(request, "core/lesson_javascript.html", context)


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("dashboard")
    else:
        form = RegisterForm()

    return render(request, "registration/register.html", {"form": form})
