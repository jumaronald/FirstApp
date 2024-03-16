import time
from payments import MpesaHandler
from kivymd.app import MDApp
from kivymd.uix.label import MDLabel, MDIcon
from kivymd.uix.screen import Screen
from kivy.lang import Builder
from kivymd.uix.button import MDFlatButton, MDRectangleFlatButton, MDIconButton, MDRectangleFlatIconButton
# from kivymd.uix.button import MDFloatingActionButtonSpeedDial, MDFillRoundFlatIconButton, MDFillRoundFlatButton
from kivymd.uix.navigationdrawer import MDNavigationDrawer
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.dialog import MDDialog
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.list import TwoLineListItem
from kivy.utils import get_color_from_hex
from kivymd.uix.textfield import MDTextField
from kivymd.uix.list import ThreeLineListItem, OneLineListItem
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.clock import Clock, mainthread
from kivy.properties import ObjectProperty
from kivy.properties import NumericProperty
from kivy.metrics import dp
import pyrebase
from kivy.graphics import RoundedRectangle
import requests
from kivymd.uix.pickers import MDTimePicker
from kivy.clock import Clock
import datetime

# Window.size = (335, 650)
# Window.softinput_mode = "below_target"

screen_manager = ScreenManager()
screen1 = Screen(name='animation')
screen2 = Screen(name='login')
screen3 = Screen(name='dashboard')
selected_item = []


class EnergyMeterApp(MDApp):
    overlay_color = get_color_from_hex("#6042e4")
    angle = 180
    dialog_message = ""
    dialog_title = ""
    token_cash = 0
    start_time = ""
    present_time = ""
    stop_time = ""
    sharing_start = False
    sharing_stop = False
    stop_counter = 0
    scheduled_event = None
    # senders_count = 0
    token_units = 0.0
    shared_units = 0.0
    dropdown_menu = ObjectProperty(None)
    tither_mode = NumericProperty(0)
    sharing_button = NumericProperty(0)
    checkbox_value = False
    owner_meter_number = ""
    start_time_set = False
    stop_time_set = False
    sharing_status = False
    sender_sharing_status = False
    applied_meters_counter = 0
    meter_list = []
    selected_list = []
    temp = 0
    end_meter = ""
    limitless_check = True
    check_selected = False
    limited_check = False
    power_check = False
    check_unselected = False
    limited_state = ObjectProperty(False)
    infinite_state = ObjectProperty(False)
    power_state = ObjectProperty(False)
    spinner = ObjectProperty(False)
    end_sharing = True

    # initialize firebase Authentication
    auth_config = {"apiKey": "AIzaSyA5bNP6rwTMCzXA8Bf1klmlOcwSxQ-V3Mc",
                   "databaseURL": "",
                   "authDomain": "energy-multimeter.firebaseapp.com",
                   "projectId": "energy-multimeter",
                   "storageBucket": "energy-multimeter.appspot.com",
                   "messagingSenderId": "561633782771",
                   "appId": "1:561633782771:web:945a2f2c6a6db245674086",
                   "measurementId": "G-6BMEJJVSW4"
                   }

    db_config = {"apiKey": "AIzaSyA5bNP6rwTMCzXA8Bf1klmlOcwSxQ-V3Mc",
                 "databaseURL": "https://energy-multimeter-default-rtdb.firebaseio.com/",
                 "authDomain": "energy-multimeter.firebaseapp.com",
                 "projectId": "energy-multimeter",
                 "storageBucket": "energy-multimeter.appspot.com",
                 "messagingSenderId": "561633782771",
                 "appId": "1:561633782771:web:945a2f2c6a6db245674086",
                 "measurementId": "G-6BMEJJVSW4"
                 }

    firebase = pyrebase.initialize_app(auth_config)
    auth = firebase.auth()
    db = pyrebase.initialize_app(db_config)
    database = db.database()

    def __init__(self):
        super(EnergyMeterApp, self).__init__()
        self.active_menu = None
        self.meter_menu = None
        self.dialog = None

    def build(self):
        self.theme_cls.primary_palette = "Orange"
        self.theme_cls.primary_hue = "900"
        self.theme_cls.theme_style = "Dark"
        self.icon = "remm_icon.png"

        active_items = [
            {
                "viewclass": "OneLineListItem",
                "text": "Select as Active Meter",
                "height": dp(40),
                "on_release": lambda x="Item": self.active_meter_callback(x),
            } for i in range(1, 2)
        ]
        self.active_menu = MDDropdownMenu(
            items=active_items,
            elevation=0,
            width_mult=4,
        )

        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": "End Sharing",
                "height": dp(40),
                "on_release": lambda x="Item": self.toolbar_left_callback(x),
            } for i in range(1, 2)
        ]
        self.dropdown_menu = MDDropdownMenu(
            items=menu_items,
            elevation=0,
            width_mult=3,
        )

        animation_file = Builder.load_file("animation.kv")
        login_file = Builder.load_file("login.kv")
        signup_file = Builder.load_file("signup.kv")
        dashboard_file = Builder.load_file("dashboard.kv")
        token_file = Builder.load_file("buy_token.kv")
        tither_token_file = Builder.load_file("tither.kv")
        new_meter_file = Builder.load_file("new_meter.kv")
        meter_owner = Builder.load_file("own_meter.kv")
        unit_share = Builder.load_file("units_tither.kv")
        power = Builder.load_file("power_management.kv")
        share_screen = Builder.load_file("sharing_page.kv")
        application_screen = Builder.load_file("meter_application.kv")
        screen_manager.add_widget(animation_file)
        screen_manager.add_widget(login_file)
        screen_manager.add_widget(signup_file)
        screen_manager.add_widget(dashboard_file)
        screen_manager.add_widget(token_file)
        screen_manager.add_widget(tither_token_file)
        screen_manager.add_widget(new_meter_file)
        screen_manager.add_widget(meter_owner)
        screen_manager.add_widget(unit_share)
        screen_manager.add_widget(power)
        screen_manager.add_widget(share_screen)
        screen_manager.add_widget(application_screen)

        power_screen = screen_manager.get_screen('power')
        power_field = power_screen.ids.power_value

        menu_item = [
            {
                "viewclass": "OneLineListItem",
                "height": dp(56),
                "text": f"{i}W",
                "on_release": lambda x=f"{i}": self.set_item(x),
            } for i in range(200, 10100, 100)]
        self.meter_menu = MDDropdownMenu(
            caller=power_field,
            items=menu_item,
            position="bottom",
            width_mult=4,
        )

        return screen_manager

    def set_item(self, text__item):
        power_screen = screen_manager.get_screen('power')
        power_field = power_screen.ids.power_value
        power_field.text = text__item
        # self.screen.ids.field.text = text__item
        self.meter_menu.dismiss()

    def on_start(self):
        # print(f"This is:{root.manager}")
        Clock.schedule_interval(self.animating_function, .3)
        # Clock.schedule_interval(self.dashboard_display, 2)
        # Clock.schedule_interval(self.time_counter, 1)
        self.login_animation()
        # self.create_database()

    def animating_function(self, *args):
        animating_screen = self.root.get_screen('animation')

        widget = animating_screen.ids.button_blink
        # print(f"look here: ,{widget}")
        animate = Animation(animated_color=(104 / 255, 131 / 255, 139 / 255, 1), blink_size=750, duration=1)
        animate += Animation(opacity=0, duration=1)
        animate += Animation(animated_color=(83 / 255, 134 / 255, 139 / 255, 1), blink_size=300, duration=1)
        animate += Animation(opacity=0, duration=1)
        animate.start(widget)
        animate.bind(on_complete=self.complete_function)

    def complete_function(self, *args):
        animating_screen = self.root.get_screen('animation')
        widget = animating_screen.ids.sliding_pop
        animate_popup = Animation(top_hint=0.3, duration=.85)
        animate_popup.start(widget)
        # print("Animation Complete")
        # self.root_window.close()
        # EnergyMeterApp.get_running_app().stop()

    def reset_function(self, *args):
        widget = args[1]
        widget.animated_color = (1, 1, 1, 1)
        blink_size = 0

    def exit_function(self):
        EnergyMeterApp.get_running_app().stop()

    def toolbar_left_callback(self, text_of_the_option):
        self.end_unlimited_sharing()
        # EnergyMeterApp.get_running_app().stop()
        self.dropdown_menu.dismiss()
        self.root.transition.direction = "left"
        self.root.current = "sharing"
        # return

    def active_meter_callback(self, text_of_the_option):
        # EnergyMeterApp.get_running_app().stop()
        self.active_menu.dismiss()
        login_email_screen = self.root.get_screen('login')
        user = login_email_screen.ids.login_mail.text
        username = user[0:len(user) - 10]
        if len(self.selected_list) != 1:
            self.dialog_message = "Please Only Select One Meter to Complete this Operation"
            self.show_dialog(self)
            return
        if len(self.selected_list) == 1:
            active_meter = self.selected_list[0]
            (self.database.child("Registered Users").child(username).update({"Active Meter": active_meter}))
        # self.root.transition.direction = "left"
        # self.root.current = "sharing"
        # return

    def callback(self, button):

        if self.sharing_button == 2:
            self.active_menu.caller = button
            self.active_menu.open()
        else:
            self.dropdown_menu.caller = button
            self.dropdown_menu.open()

    def active_callback(self, button):
        self.active_menu.caller = button
        self.active_menu.open()

    def login_animation(self, *args):
        animating_screen = self.root.get_screen('login')
        widget = animating_screen.ids.rotate
        animate = Animation(height=55, width=55, spacing=[6, 6], duration=1)
        animate += Animation(height=15, width=15, spacing=[1, 1], duration=1)
        animate += Animation(angle=self.angle, duration=1)
        animate.bind(on_complete=self.login_animation)
        animate.start(widget)
        self.angle += 180

    def signup(self):
        print("waiting for dialog to show")
        email_screen = self.root.get_screen('signup')
        password_screen = self.root.get_screen('signup')
        confirm_password_screen = self.root.get_screen('signup')
        phone_screen = self.root.get_screen('signup')
        valid_data = True
        # widget = animating_screen.ids.rotate
        phone = email_screen.ids.phone.text
        email = email_screen.ids.email.text
        mobile = "254" + phone[1:]
        password = password_screen.ids.password.text
        confirm_password = confirm_password_screen.ids.confirm_password.text
        username = email[0:len(email) - 10]
        signup_data = {"Phone Number": mobile, "Meter Number": "", "Username": username, "Meters Owned": 0,
                       "Active Meter": "", "Temp Units": 0, "Temp Token": 0.0, "Application Approval": 0}
        if phone == "" or email == "" or password == "" or confirm_password == "":
            valid_data = False
            print(f"login Details phone:{phone}, email:{email}, password:{password}")
            self.dialog_message = "All Fields Are Required"
            self.show_dialog(self)
            return
        if password != confirm_password:
            valid_data = False
            self.dialog_message = "Passwords Entered Do Not Match"
            self.show_dialog(self)
            return
        if len(phone) != 10 or not phone.isdigit():
            valid_data = False
            self.dialog_message = "Invalid Phone Number, Check and Try Again"
            self.show_dialog(self)
            return
        if valid_data:
            try:
                user = self.auth.create_user_with_email_and_password(email, password)
                self.database.child("Registered Users").child(username).update(signup_data)

            except requests.exceptions.HTTPError:
                self.dialog_title = "Signup Error!"
                self.dialog_message = "Check Network connection, password Strength and Email Format"
                self.show_dialog(self)

    def show_dialog(self, obj):
        if self.dialog:
            self.dialog.dismiss()
            self.dialog = MDDialog(title=f"{self.dialog_title}",
                                   text=f"{self.dialog_message}",
                                   buttons=[MDRaisedButton(
                                       text="Continue",
                                       md_bg_color='red',
                                       theme_text_color="Custom",
                                       text_color=(0, 0, 0, 1),
                                   )
                                   ],
                                   )
            self.dialog.open()
        if not self.dialog:
            self.dialog = MDDialog(title=f"{self.dialog_title}",
                                   text=f"{self.dialog_message}",
                                   buttons=[MDRaisedButton(
                                       text="Continue",
                                       md_bg_color='red',
                                       theme_text_color="Custom",
                                       text_color=(0, 0, 0, 1),
                                   )
                                   ],
                                   )
            self.dialog.open()

    def login(self):
        login_email_screen = self.root.get_screen('login')
        login_password_screen = self.root.get_screen('login')
        navigation_screen = self.root.get_screen('dashboard')
        email_login = login_email_screen.ids.login_mail.text
        password_login = login_password_screen.ids.login_password.text
        navigation_label = navigation_screen.ids.nav_label
        navigation_label.text = email_login

        print("TODAY IS " + str(datetime.datetime.now()))

        try:
            login = self.auth.sign_in_with_email_and_password(email_login, password_login)
            # self.get_power_state()
            # self.create_database()
            '''
            try:
                all_users = self.database.child("Remote Energy Multimeter").child("Meters").get()
                for user in all_users.each():
                    print(f"Database keys are: {user.key()}")
            except:
                pass
            '''

            self.root.transition.direction = "right"
            self.root.current = "dashboard"
            time.sleep(2)
            Clock.schedule_interval(self.dashboard_display, 2)
        except:
            self.dialog_message = "Invalid Email/Password Also check network connection"
            self.show_dialog(self)
        # Clock.schedule_interval(self.scan_sharing_records, 1)

    def schedule_tracking(self, *args):
        Clock.schedule_interval(self.track_sharing, 2)

    def unschedule_tracking(self, *args):
        Clock.unschedule(self.track_sharing, 2)

    def schedule_dashboard(self, *args):
        Clock.schedule_interval(self.dashboard_display, 2)

    def unschedule_dashboard(self, *args):
        Clock.unschedule(self.dashboard_display)
        login_email_screen = self.root.get_screen('login')
        user = login_email_screen.ids.login_mail.text
        username = user[0:len(user) - 10]
        active_meter = (self.database.child("Registered Users").child(username).child("Active Meter").get())
        active_value = active_meter.val()
        meter_str = active_value
        str_length = len(meter_str)
        d = str_length - 11
        str_num = meter_str[-d:]
        sharing = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + str_num)
                   .child(active_value).child(username).child("Sharing From").get())
        sharing_value = sharing.val()
        units = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + str_num)
                 .child(active_value).child(username).child("units").get())
        units_value = units.val()
        if units_value is None:
            units_value = 0
        if units_value < 0.01 and sharing_value == 0:
            print(f"units=========={units_value}=======share========{sharing_value}")
            self.power_check = True

    def password_reset(self):
        login_email_screen = self.root.get_screen('login')
        email_login = login_email_screen.ids.login_mail.text
        print(email_login)
        if email_login == "":
            self.dialog_message = "Please Provide Your Email Address"
            self.show_dialog(self)
        else:
            try:
                self.auth.send_password_reset_email(email_login)
            except:
                self.dialog_message = "Network Connection Problem or Invalid Email Adress"
                self.show_dialog(self)

    def dashboard_data(self):
        pass

    def create_database(self):
        # user = "jumaronald330@gmail.com"

        login_email_screen = self.root.get_screen('login')
        user = login_email_screen.ids.login_mail.text
        username = user[0:len(user) - 10]

        print(f"this is your email: {username}")
        first_data = {"Location": "Nairobi, Langata", "voltage": 0.0, "current": 0.0, "power": 0,
                      "Meter Availability": 0, "Meter User": username, "Energy Consumed": 0.0, "Power Status": 0}
        second_data = {"Mobile": "0719795557", "Meter Number": "REMM00001A", "units": 0.0, "unlimited Sharing to": 0,
                       "unlimited sharing from": 0, "units shared to": 0.0, "units shared from": 0,
                       "sharing time to": 0,
                       "sharing time from": 0, "shared power": 0.0, "sharing status to": 0, "sharing status from": 0,
                       "sharing to": "", "sharing from": " ", "Token Bought": 0.0}
        # meter_owner = {"Meters":" ", "Till Number":0, "MTD Payment":0, "Debit Amount": " ", "Credit Amount":" "}
        # user_record = {"Phone Number":"", "Meter Number":"", "Username":" "}

        try:
            self.database.child("Remote Energy Multimeter").child("Meters").child("REMM00001A").set(first_data)
            (self.database.child("Remote Energy Multimeter").child("Meters").child("REMM00001A").child(username).
             set(second_data))
            self.database.child("Remote Energy Multimeter").child("Meters").child("REMM00002A").set(" ")
            self.database.child("Remote Energy Multimeter").child("Meters").child("REMM00003A").set(" ")
            self.database.child("Remote Energy Multimeter").child("Meters").child("REMM00004A").set(" ")
            # self.database.child("Registered Users").child("Demo User").set(user_record)
            # self.database.child("Meter Owners").child("Demo User").set(meter_owner)

        except:
            pass

    def dashboard_display(self, *args):
        dashboard_screen = self.root.get_screen('dashboard')
        units = dashboard_screen.ids.tokens_label
        voltage = dashboard_screen.ids.voltage_label
        current = dashboard_screen.ids.current_label
        power = dashboard_screen.ids.power_label
        sent_units = dashboard_screen.ids.sent_label
        received_units = dashboard_screen.ids.received_label
        energy = dashboard_screen.ids.energy_label
        login_email_screen = self.root.get_screen('login')
        user = login_email_screen.ids.login_mail.text
        username = user[0:len(user) - 10]
        # user_meter_number = (self.database.child("Remote Energy Multimeter").child(username).child("User Meter Number").
        # get())
        # meter_number = user_meter_number.val()
        # get_meter_number =

        user_meter_number = (self.database.child("Registered Users").child(username).child("Active Meter").get())
        meter_number = user_meter_number.val()

        if meter_number is None:
            self.dialog_title = "Dashboard Data Failed To Load!"
            self.dialog_message = "No Meter Number is Allocated to You Yet"
            self.show_dialog(self)
            return

        sender_str = meter_number
        sender_str_length = len(sender_str)
        d = sender_str_length - 11
        sender_num = sender_str[-d:]

        available_token = (self.database.child("Remote Energy Multimeter").child("Meters").
                           child("Meter Group" + sender_num).child(meter_number).child(username).child("units").get())
        tokens = str(available_token.val())
        voltage_value = (self.database.child("Remote Energy Multimeter").child("Meters").
                         child("Meter Group" + sender_num).child(meter_number).child("voltage").get())
        volts = str(voltage_value.val())
        current_value = (self.database.child("Remote Energy Multimeter").child("Meters").
                         child("Meter Group" + sender_num).child(meter_number).child("current").get())
        amperes = str(current_value.val())
        #  return
        # self.owner_meter_number =
        try:
            power_value = voltage_value.val() * current_value.val()
            rounded = round(power_value, 3)
            watts = str(rounded)
            power.text = watts + " W"
        except:
            pass

        try:
            units.text = tokens + " KWh"
            voltage.text = volts + " V"
            current.text = amperes + " A"
            # print(f"this is your token: {tokens}")
        except UnboundLocalError:
            pass
        self.scan_sharing_records()

    def incrementor(self):
        token_screen = self.root.get_screen('token')
        add_units = token_screen.ids.units_label
        token_paid = token_screen.ids.cash_label
        self.token_cash += 10
        self.token_units = self.token_cash / 27.998
        rounded = round(self.token_units, 3)
        rounded_units = str(rounded)
        add_units.text = rounded_units
        token_paid.text = str(self.token_cash)

    def decrementor(self):
        token_screen = self.root.get_screen('token')
        add_units = token_screen.ids.units_label
        token_paid = token_screen.ids.cash_label
        if self.token_cash > 10:
            self.token_cash -= 10
            self.token_units = self.token_cash / 27.998
            rounded = round(self.token_units, 3)
            rounded_units = str(rounded)
            add_units.text = rounded_units
        token_paid.text = str(self.token_cash)

    def adder(self):
        token_screen = self.root.get_screen("units_share")
        units_share = token_screen.ids.units_label
        self.shared_units += 0.1
        rounded = round(self.shared_units, 3)
        units_share.text = "                    " + str(rounded)

    def subtractor(self):
        token_screen = self.root.get_screen("units_share")
        unit = token_screen.ids.units_label
        if self.shared_units >= 0.1:
            self.shared_units -= 0.1
            rounded = round(self.shared_units, 3)
            unit.text = "                    " + str(rounded)
        else:
            unit.text = "Input Units Amount to Share"

    def plus(self):
        own_meter_screen = self.root.get_screen("meter_owner")
        add_meters = own_meter_screen.ids.meter_quantity_label
        show_meters = own_meter_screen.ids.meter_number_label
        last_meter = (self.database.child("Remote Energy Multimeter").child("Meters").child("Admin Records")
                      .child("Last Meter").get())
        last_meter_number = last_meter.val()
        get_meters_groups = (self.database.child("Remote Energy Multimeter").child("Meters").child("Admin Records").
                             child("Meters Addition").get())
        num = get_meters_groups.val() + 1
        # last_meter_number = "REMM10001A"
        meter_digits = int(last_meter_number[4:10])
        final_meter = ""

        if add_meters.text == "Quantity of Meters":
            add_meters.text = ""
            show_meters.text = ""
            self.applied_meters_counter += 1
            meter_digits += 1
            self.temp = meter_digits
            add_meters.text = "              " + str(self.applied_meters_counter)
            show_meters.text = "           " + "REMM" + str(meter_digits) + "A" + str(num)
            final_meter = "REMM" + str(meter_digits) + "A" + str(num)
            self.meter_list.append(final_meter)
            self.end_meter = final_meter
            # (self.database.child("Remote Energy Multimeter").child("Meters").child("Admin Records")
            # .update({"Last Meter": final_meter}))
        else:
            self.applied_meters_counter += 1
            # meter_digits = 0
            self.temp += 1
            add_meters.text = "                " + str(self.applied_meters_counter)
            show_meters.text = "           " + "REMM" + str(self.temp) + "A" + str(num)
            final_meter = "REMM" + str(self.temp) + "A" + str(num)
            self.meter_list.append(final_meter)
            print(f"my list: {self.meter_list}")
            self.end_meter = final_meter
            # (self.database.child("Remote Energy Multimeter").child("Meters").child("Admin Records")
            # .update({"Last Meter": final_meter}))

    def minus(self):
        own_meter_screen = self.root.get_screen("meter_owner")
        subtract_meters = own_meter_screen.ids.meter_quantity_label
        show_meters = own_meter_screen.ids.meter_number_label
        last_meter = (self.database.child("Remote Energy Multimeter").child("Meters").child("Admin Records")
                      .child("Last Meter").get())
        last_meter_number = last_meter.val()
        # last_meter_number = "REMM10001A"
        meter_digits = int(last_meter_number[4:10])
        final_meter = ""
        if subtract_meters.text == "Quantity of Meters":
            pass
        else:
            if self.applied_meters_counter > 0:
                self.applied_meters_counter -= 1
                # meter_digits += 1
                self.temp -= 1
                subtract_meters.text = "                " + str(self.applied_meters_counter)
                self.meter_list = self.meter_list[:-1]
                if self.meter_list:
                    final_meter = self.meter_list.pop()
                    self.meter_list.append(final_meter)
                    # show_meters.text = " "
                    show_meters.text = "           " + final_meter
                    print(f"Show Meter Label: {show_meters.text}")
                    print(f"my list: {self.meter_list}")
                    print(f"Final Meter: {final_meter}")
                    self.end_meter = final_meter
                    # (self.database.child("Remote Energy Multimeter").child("Meters").child("Admin Records")
                    # .update({"Last Meter": final_meter}))
            else:
                subtract_meters.text = "Quantity of Meters"
                show_meters.text = "Meter Numbers Selected"

    def meter_tithering(self):
        if self.tither_mode == 1:
            print("unlimited Tithering Selected")
            self.unlimited_sharing()

        elif self.tither_mode == 3:
            print("Token Tithering Selected")
            self.token_sharing()

        elif self.tither_mode == 2:
            print("Time Tithering Selected")
            # if self.start_time_set and self.stop_time_set:
            print("Time Tithering Data Will be Submitted")
            self.start_time_set = False
            self.stop_time_set = False
            self.time_sharing()
        else:
            self.dialog_title = "Sharing Mode Error!"
            self.dialog_message = "Please Select Sharing Mode"
            self.show_dialog(self)

        self.tither_mode = 0

    def change_meter(self):
        current_meter_found = False
        second_meter_found = False
        p = 0
        login_email_screen = self.root.get_screen('login')
        meter_screen = self.root.get_screen('meter_number')
        user = login_email_screen.ids.login_mail.text
        current_meter = meter_screen.ids.pre_meter.text
        second_meter = meter_screen.ids.dest_meter.text
        username = user[0:len(user) - 10]
        # all_users = self.database.child("Remote Energy Multimeter").child("Meters").get()
        meter_owned = (self.database.child("Registered Users").child(username).child("Meters Owned").get())
        meters_counted = meter_owned.val()
        j = meters_counted + 1
        meter_str = second_meter
        sender_str = current_meter
        str_length = len(meter_str)
        sender_str_length = len(sender_str)
        d = sender_str_length - 11
        sender_num = sender_str[-d:]
        f = str_length - 11
        num_str = meter_str[-f:]
        temp_list = []
        # search for current meter existence
        get_meters_groups = (self.database.child("Remote Energy Multimeter").child("Meters").child("Admin Records").
                             child("Meters Addition").get())
        meter_groups = get_meters_groups.val()
        k = meter_groups + 1

        for x in range(1, k):
            unit = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + str(x)).get())
            for item in unit.each():
                if item.key() == second_meter:
                    second_meter_found = True
                    break

        for y in range(1, j):
            meter = (self.database.child("Registered Users").child(username).child("Meter Number").child(f"Meter_{y}")
                     .child(f"Meter-{y}").get())
            meter_value = meter.val()
            # search for current meter existence
            if current_meter == meter_value:
                current_meter_found = True
                break
                # print(f"Database keys are: {user.key()}")
        if current_meter_found and self.checkbox_value:
            # self.checkbox_value = False
            if second_meter != "":
                self.dialog_title = "Failed!!"
                self.dialog_message = "Please Include Current Meter Only"
                self.show_dialog(self)
                return
            user_units = (self.database.child("Remote Energy Multimeter").child("Meters").
                          child("Meter Group" + sender_num).child(current_meter).child(username).child("units").get())
            temp_units = (self.database.child("Registered Users").child(username).child("Temp Token").get())
            token_value = temp_units.val()
            units_value = user_units.val()
            w = meters_counted - 1
            if meters_counted == 1:
                (self.database.child("Registered Users").child(username).update({"Active Meter": ""}))
                (self.database.child("Registered Users").child(username).child("Meter Number").child("Meter_1")
                 .child("Meter-1").remove())
            elif meters_counted > 1:
                active_meter = (self.database.child("Registered Users").child(username).child("Active Meter").get())
                active_value = active_meter.val()
                if active_value == current_meter:
                    (self.database.child("Registered Users").child(username).update({"Active Meter": ""}))
                for v in range(1, j):
                    find_meter = (self.database.child("Registered Users").child(username).child("Meter Number").
                                  child(f"Meter_{v}").child(f"Meter-{v}").get())
                    found_value = find_meter.val()
                    if found_value == current_meter:
                        (self.database.child("Registered Users").child(username).child("Meter Number").
                         child(f"Meter_{v}").remove())
                for z in range(1, j):
                    meters = (self.database.child("Registered Users").child(username).child("Meter Number").
                              child(f"Meter_{z}").child(f"Meter-{z}").get())
                    meters_value = meters.val()
                    if meters_value is not None:
                        temp_list.append(meters_value)
                (self.database.child("Registered Users").child(username).child("Meter Number").remove())
                for item in temp_list:
                    p += 1
                    if p == 1:
                        (self.database.child("Registered Users").child(username).update({"Active Meter": item}))
                    (self.database.child("Registered Users").child(username).child("Meter Number").
                     child(f"Meter_{p}").update({f"Meter-{p}": item}))
                p = 0
            (self.database.child("Registered Users").child(username).update({"Meters Owned": w}))
            (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + sender_num).
             child(current_meter).update({"Meter Availability": 1}))
            (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + sender_num)
             .child(current_meter).child(username).remove())
            (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + sender_num).
             child(current_meter).update({"Power Status": 0}))
            (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + sender_num).
             child(current_meter).update({"Meter User": ""}))
            total_units = token_value + units_value
            (self.database.child("Registered Users").child(username).update({"Temp Token": total_units}))
            return
        if not current_meter_found:
            self.dialog_title = "Meter Number Error!"
            self.dialog_message = "You Have no Ownership of Current Meter Provided"
            self.show_dialog(self)
        elif not second_meter_found:
            self.dialog_title = "Meter Number Error!"
            self.dialog_message = "Destination Meter Number Provided Doesn't Exist"
            self.show_dialog(self)
        elif current_meter_found and second_meter_found:
            token_stored = (self.database.child("Registered Users").child(username).child("Temp Token").get())
            token_value = token_stored.val()
            second_meter_user = (self.database.child("Remote Energy Multimeter").child("Meters").
                                 child("Meter Group" + num_str).child(second_meter).child("Meter User").get())
            meter_availability = (self.database.child("Remote Energy Multimeter").child("Meters").
                                  child("Meter Group" + num_str).child(second_meter).child("Meter Availability").get())
            user_units = (self.database.child("Remote Energy Multimeter").child("Meters").
                          child("Meter Group" + sender_num).child(current_meter).child(username).child("units").get())
            units_bought = (self.database.child("Remote Energy Multimeter").child("Meters").
                            child("Meter Group" + sender_num).child(current_meter).child(username).
                            child("Token Bought").get())

            meter_availability_status = meter_availability.val()
            user_token = user_units.val()
            if user_token is None:
                user_token = 0
            user_token += token_value
            (self.database.child("Registered Users").child(username).update({"Temp Token": 0}))
            token_bought = units_bought.val()
            second_user = second_meter_user.val()

            first_data = {"Meter Number": second_meter, "units": user_token, "Token Bought": token_bought,
                          "Sharing to": 0, "Sharing From": 0, "Unlimited Share From": 0, "Unlimited Share to": 0,
                          "Time Share to": 0, "Time Share From": 0, "Unlimited Sharing From": "",
                          "unlimited Sharing to": "", "Time Sharing From": "", "Time Sharing to": ""}

            if meter_availability_status == 1:
                (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + sender_num).
                 child(current_meter).update({"Meter Number": ""}))
                (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + sender_num).
                 child(current_meter).update({"Meter Availability": 1}))
                (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + sender_num).
                 child(current_meter).update({"current": 0.0}))
                (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + sender_num).
                 child(current_meter).update({"voltage": 0.0}))
                (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + sender_num).
                 child(current_meter).update({"power": 0.0}))
                (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + sender_num).
                 child(current_meter).update({"Energy Consumed": 0.0}))
                (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + sender_num)
                 .child(current_meter).child(username).remove())
                (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str)
                 .child(second_meter).child(second_user).remove())
                (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                 child(second_meter).child(username).set(first_data))
                (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                 child(second_meter).update({"voltage": 0.0}))
                (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                 child(second_meter).update({"power": 0.0}))
                (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                 child(second_meter).update({"current": 0.0}))
                (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                 child(second_meter).update({"Energy Consumed": 0.0}))
                (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                 child(second_meter).update({"Meter User": username}))
                (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                 child(second_meter).update({"Meter Number": second_meter}))
                (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + sender_num).
                 child(current_meter).update({"Power Status": 0}))
                (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + sender_num).
                 child(current_meter).update({"Meter User": ""}))
                (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                 child(second_meter).update({"Meter Availability": 0}))
                if meters_counted == 1:
                    (self.database.child("Registered Users").child(username).update({"Active Meter": second_meter}))
                    (self.database.child("Registered Users").child(username).child("Meter Number").child("Meter_1")
                     .update({"Meter-1": second_meter}))
                elif meters_counted > 1:
                    active_meter = (self.database.child("Registered Users").child(username).child("Active Meter").get())
                    active_value = active_meter.val()
                    if active_value == current_meter:
                        (self.database.child("Registered Users").child(username).update({"Active Meter": ""}))
                    for v in range(1, j):
                        find_meter = (self.database.child("Registered Users").child(username).child("Meter Number").
                                      child(f"Meter_{v}").child(f"Meter-{v}").get())
                        found_value = find_meter.val()
                        if found_value == current_meter:
                            (self.database.child("Registered Users").child(username).child("Meter Number").
                             child(f"Meter_{v}").update({f"Meter-{v}": second_meter}))
            else:
                self.dialog_title = "Meter Availability Error!"
                self.dialog_message = "Destination Meter Number Provided is Occupied"
                self.show_dialog(self)
        self.checkbox_value = False

    def get_power_state(self):
        login_email_screen = self.root.get_screen('login')
        user = login_email_screen.ids.login_mail.text
        power_screen = self.root.get_screen("power")
        switch_state = power_screen.ids.switch_label
        # limited_power = power_limit.text
        username = user[0:len(user) - 10]
        active_meter = (self.database.child("Registered Users").child(username).child("Active Meter").get())
        active_value = active_meter.val()
        meter_str = active_value
        str_length = len(meter_str)
        d = str_length - 11
        str_num = meter_str[-d:]
        infinite_power = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + str_num)
                          .child(active_value).child("Power Limit").get())
        infinite_value = infinite_power.val()
        power_status = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + str_num)
                        .child(active_value).child("Power Status").get())
        power_value = power_status.val()
        sharing = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + str_num)
                   .child(active_value).child(username).child("Sharing From").get())
        sharing_value = sharing.val()
        units = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + str_num)
                 .child(active_value).child(username).child("units").get())
        units_value = units.val()
        try:
            if infinite_value > 0:
                self.infinite_state = False
                self.limited_state = True
            elif infinite_value == 0:
                self.infinite_state = True
                self.limited_state = False
        except TypeError:
            pass
        if power_value == 1:
            self.power_state = False
            switch_state.text = "Turn OFF Your Household Power"
        elif power_value == 0:
            self.power_state = True
            switch_state.text = "Turn ON Your Household Power"
        '''    
        if units_value >= 0.01 or sharing_value == 1:
            # self.power_state = False
            switch_state.text = "Turn OFF Your Household Power"
            (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + str_num).
             child(active_value).update({"Power Status": 1}))
        elif units_value < 0.01 and sharing_value == 0 and self.power_state:
            self.power_state = True
            switch_state.text = "Turn ON Your Household Power"
            (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + str_num).
             child(active_value).update({"Power Status": 0}))
         '''
        print(f"POWER LIMIT IS...{infinite_value}..INFINITE STATE {self.infinite_state}..LIMITED STATE"
              f" {self.limited_state}")

    def get_power_settings(self):
        login_email_screen = self.root.get_screen('login')
        user = login_email_screen.ids.login_mail.text
        power_screen = self.root.get_screen("power")
        power_limit = power_screen.ids.power_value
        limited_power = power_limit.text
        if limited_power == "" and self.limited_check:
            self.dialog_title = "Missing Power Value"
            self.dialog_message = "You Didn't Select Power Value"
            self.show_dialog(self)
            return
        try:
            power_value = int(limited_power)
        except ValueError:
            power_value = 0
        username = user[0:len(user) - 10]
        active_meter = (self.database.child("Registered Users").child(username).child("Active Meter").get())
        active_value = active_meter.val()
        meter_str = active_value
        str_length = len(meter_str)
        d = str_length - 11
        str_num = meter_str[-d:]
        sharing = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + str_num)
                   .child(active_value).child(username).child("Sharing From").get())
        sharing_value = sharing.val()
        units = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + str_num)
                 .child(active_value).child(username).child("units").get())
        units_value = units.val()
        if self.limitless_check:
            (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + str_num).
             child(active_value).update({"Power Limit": 0}))
        if self.limited_check:
            (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + str_num).
             child(active_value).update({"Power Limit": power_value}))

        if self.power_state:
            (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + str_num).
             child(active_value).update({"Power Status": 0}))
        else:
            if units_value >= 0.01 or sharing_value == 1:
                (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + str_num).
                 child(active_value).update({"Power Status": 1}))
            elif units_value < 0.01 and sharing_value == 0:
                (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + str_num).
                 child(active_value).update({"Power Status": 0}))

    def unlimited_checkbox(self, checkbox, value):
        if value:
            self.limitless_check = True
        else:
            self.limitless_check = False

    def limited_checkbox(self, checkbox, value):
        if value:
            self.limited_check = True
        else:
            self.limited_check = False

    def power_button(self):
        print("You Pressed Power Button")
        login_email_screen = self.root.get_screen('login')
        user = login_email_screen.ids.login_mail.text
        power_screen = self.root.get_screen("power")
        switch_state = power_screen.ids.switch_label
        button_color = power_screen.ids.power_button
        # limited_power = power_limit.text
        username = user[0:len(user) - 10]
        active_meter = (self.database.child("Registered Users").child(username).child("Active Meter").get())
        active_value = active_meter.val()
        meter_str = active_value
        str_length = len(meter_str)
        d = str_length - 11
        str_num = meter_str[-d:]
        sharing = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + str_num)
                   .child(active_value).child(username).child("Sharing From").get())
        sharing_value = sharing.val()
        units = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + str_num)
                 .child(active_value).child(username).child("units").get())
        units_value = units.val()
        if self.power_state:
            # self.power_state = True
            switch_state.text = "Turn OFF Your Household Power"
            if units_value >= 0.01 or sharing_value == 1:
                self.power_state = False
                switch_state.text = "Turn OFF Your Household Power"
                (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + str_num).
                 child(active_value).update({"Power Status": 1}))
            elif units_value < 0.01 and sharing_value == 0:
                self.power_state = True
                switch_state.text = "Share or Load Units to Turn ON"
                time.sleep(2)
                # switch_state.text = "Turn ON Your Household Power"
                (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + str_num).
                 child(active_value).update({"Power Status": 0}))
        else:
            self.power_state = True
            switch_state.text = "Turn ON Your Household Power"
            (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + str_num).
             child(active_value).update({"Power Status": 0}))
        print("Power Button Functions Completed Successfully")

    def on_checkbox_active(self, checkbox, value):
        if value:
            self.checkbox_value = True
            # self.dialog_title = " Meter Availability Error!"
            self.dialog_message = "Your Current Meter Number Will be Made Available For Other Users"
            self.show_dialog(self)
            # time.sleep(6)
            # self.dialog.dismiss()
        else:
            self.checkbox_value = False

    def add_meter(self):
        pass

    def time_picker(self):
        time_dialog = MDTimePicker()
        time_dialog.bind(time=self.get_time, on_save=self.schedule)
        time_dialog.open()

    def get_time(self, instance, time):
        print(time)
        selected_time = str(time)
        return selected_time

    def schedule(self, *args):
        # Clock.schedule_once()
        # Clock.schedule_interval(self.time_counter, 1)
        if self.sharing_start:
            # self.start_time_set = True
            self.start_time = self.get_time(*args)

        elif self.sharing_stop:
            # self.start_time_set = True
            self.stop_time = self.get_time(*args)

    def track_sharing(self, *args):
        login_email_screen = self.root.get_screen('login')
        user = login_email_screen.ids.login_mail.text
        username = user[0:len(user) - 10]
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        active_meter = (self.database.child("Registered Users").child(username).child("Active Meter").get())
        meter_value = active_meter.val()
        meter_str = meter_value
        str_length = len(meter_str)
        f = str_length - 11
        num_str = meter_str[-f:]
        tx_value = 0
        rx_value = 0
        sharing_to = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str)
                      .child(meter_value).child(username).child("Sharing to").get())
        to_value = sharing_to.val()
        sharing_from = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str)
                        .child(meter_value).child(username).child("Sharing From").get())
        from_value = sharing_from.val()
        if from_value == 0 and to_value == 0:
            return
        units = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                 child(meter_value).child(username).child("units").get())
        unit_value = units.val()
        if from_value == 1:
            receiver = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str)
                        .child(meter_value).child("Receiver Online").get())
            rx_value = receiver.val()
            rx_value += 1
            if rx_value > 100:
                rx_value = 0
            (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str)
             .child(meter_value).update({"Receiver Online": rx_value}))
        elif to_value == 1:
            sender = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str)
                      .child(meter_value).child("Sender Online").get())
            tx_value = sender.val()
            tx_value += 1
            if tx_value > 100:
                tx_value = 0
        share_to = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                    child(meter_value).child(username).child("Sharing to").get())
        share_value = share_to.val()
        h = share_value + 1
        num = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
               child(meter_value).child(username).child("Time Share to").get())
        c = num.val()
        # print(f">>>{username}>>>>{num_str}>>>>>{meter_value}")
        endless_share = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                         child(meter_value).child(username).child("Unlimited Share to").get())
        endless_value = endless_share.val()
        for k in range(1, h):
            if endless_value > 0:
                m = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                     child(meter_value).child(username).child("Unlimited Sharing to").child(f"Meter_{k}").
                     child(f"Meter-{k}").get())
                meter = m.val()
                receiver_str = meter
                receiver_str_length = len(receiver_str)
                d = receiver_str_length - 11
                p = receiver_str[-d:]
                user = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + p).
                        child(meter).child("Meter User").get())
                user_value = user.val()
                unit_shared = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + p).
                               child(meter).child("Shared Units").get())
                v = unit_shared.val()
                counted = (self.database.child("Remote Energy Multimeter").child("Meters").child
                           ("Meter Group" + num_str).child(meter_value).child("Meter Counted").get())
                counted_value = counted.val()
                counted_value += 1
                receiver = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + p).
                            child(meter).child(user_value).child("Unlimited Share From").get())
                n = receiver.val()
                if counted_value == n:
                    counted_value = 0
                    (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + p).
                     child(meter).update({"Shared Units": 0}))
                (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                 child(meter_value).update({"Meter Counted": counted_value}))
                a = v / n
                if unit_value > 0.2 and a < unit_value:
                    unit_value -= a
                    (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                     child(meter_value).child(username).update({"units": unit_value}))
                    (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + p)
                     .child(meter).update({"Sender Online": tx_value}))
        if c > 0:
            meters = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                      child(meter_value).child(username).child("Time Sharing to").get())
            for y in meters.each():
                # receiver_str = meter
                receiver_str_length = len(y.key())
                d = receiver_str_length - 11
                p = y.key()[-d:]
                user = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + p).
                        child(y.key()).child("Meter User").get())
                user_value = user.val()
                unit_shared = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + p).
                               child(y.key()).child("Shared Units").get())
                v = unit_shared.val()
                count = (self.database.child("Remote Energy Multimeter").child("Meters").child
                         ("Meter Group" + num_str).child(meter_value).child("Meter Counted").get())
                count_value = count.val()
                count_value += 1
                receiver = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + p).
                            child(y.key()).child(user_value).child("Time Share From").get())
                n = receiver.val()
                if count_value == n:
                    count_value = 0
                    (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + p).
                     child(y.key()).update({"Shared Units": 0}))
                (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                 child(meter_value).update({"Meter Counted": count_value}))
                a = v / n
                if unit_value > 0.2 and a < unit_value:
                    unit_value -= a
                    (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                     child(meter_value).child(username).update({"units": unit_value}))
                    (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + p)
                     .child(y.key()).update({"Sender Online": tx_value}))

    def time_counter(self, *args):
        login_email_screen = self.root.get_screen('login')
        user = login_email_screen.ids.login_mail.text
        username = user[0:len(user) - 10]
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        active_meter = (self.database.child("Registered Users").child(username).child("Active Meter").get())
        meter_value = active_meter.val()
        meter_str = meter_value
        str_length = len(meter_str)
        f = str_length - 11
        num_str = meter_str[-f:]

        num = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
               child(meter_value).child(username).child("Time Share to").get())
        c = num.val()
        units = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                 child(meter_value).child(username).child("units").get())
        unit_value = units.val()

        if c >= 1:
            meters = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                      child(meter_value).child(username).child("Time Sharing to").get())
            for t in meters.each():
                receiver_str = t.key()
                receiver_str_length = len(receiver_str)
                d = receiver_str_length - 11
                p = receiver_str[-d:]
                user = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + p).
                        child(t.key()).child("Meter User").get())
                user_value = user.val()
                receiver = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + p).
                            child(t.key()).child(user_value).child("Time Share From").get())
                j = receiver.val()
                print(f"J=={j}........{t.key()}.....User=={user_value}.......P=={p}.....")
                start = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                         child(meter_value).child(username).child("Time Sharing to").child(t.key()).child("Start Time")
                         .get())
                start_value = start.val()
                stop = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                        child(meter_value).child(username).child("Time Sharing to").child(t.key()).child("Stop Time")
                        .get())
                stop_value = stop.val()
                if start_value <= str(current_time) < stop_value:
                    receiver_units = (self.database.child("Remote Energy Multimeter").child("Meters").child
                                      ("Meter Group" + p).child(t.key()).child(user_value).child("units")
                                      .get())
                    token_value = receiver_units.val()
                    infinite_share = (self.database.child("Remote Energy Multimeter").child("Meters").child
                                      ("Meter Group" + p).child(t.key()).child(user_value).child("Unlimited Share From")
                                      .get())
                    share_value = infinite_share.val()
                    if unit_value <= 0.1:
                        if j == 0 and share_value == 0 and token_value == 0:
                            (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + p).
                             child(t.key()).update({"Power Status": 0}))
                        self.dialog_title = "Sharing Stopped"
                        self.dialog_message = f"{meter_value} Doesn't Have Enough Units For Sharing"
                        self.show_dialog(self)
                    else:
                        (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + p).
                         child(t.key()).update({"Power Status": 1}))
                elif str(current_time) >= stop_value:
                    c -= 1
                    j -= 1
                    (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                     child(meter_value).child(username).child("Time Sharing to").child(t.key()).child("Stop Time").
                     remove())
                    (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                     child(meter_value).child(username).child("Time Sharing to").child(t.key()).child("Start Time").
                     remove())
                    (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + p).
                     child(t.key()).child(user_value).child("Time Sharing From").child(meter_value).child("Start Time").
                     remove())
                    (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + p).
                     child(t.key()).child(user_value).child("Time Sharing From").child(meter_value).child("Stop Time").
                     remove())
                    (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                     child(meter_value).child(username).update({"Time Share to": c}))
                    (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + p).
                     child(t.key()).child(user_value).update({"Time Share From": j}))

        # Clock.schedule_interval(self.time_counter, 1)
        print(f"Current Time: {current_time}")
        print(f"Start Time: {self.start_time}")
        print(f"Stop Time: {self.stop_time}")

    def unlimited_recorder(self):
        login_email_screen = self.root.get_screen('login')
        user = login_email_screen.ids.login_mail.text
        username = user[0:len(user) - 10]
        # current_time = datetime.datetime.now().strftime("%H:%M:%S")
        active_meter = (self.database.child("Registered Users").child(username).child("Active Meter").get())
        meter_value = active_meter.val()
        meter_str = meter_value
        str_length = len(meter_str)
        f = str_length - 11
        num_str = meter_str[-f:]
        counted_meter = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                         child(meter_value).child(username).child("Unlimited Share to").get())
        meters_counted = counted_meter.val()
        if meters_counted > 0:
            n = meters_counted + 1
            units = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                     child(meter_value).child(username).child("units").get())
            unit_value = units.val()
            for k in range(1, n):
                m = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                     child(meter_value).child(username).child("Unlimited Sharing to").child(f"Meter_{k}").
                     child(f"Meter-{k}").get())
                meter = m.val()
                receiver_str = meter
                receiver_str_length = len(receiver_str)
                d = receiver_str_length - 11
                p = receiver_str[-d:]
                user = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + p).
                        child(meter).child("Meter User").get())
                user_value = user.val()
                receiver = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + p).
                            child(meter).child(user_value).child("Unlimited Share From").get())
                v = receiver.val()
                receiver_units = (self.database.child("Remote Energy Multimeter").child("Meters").child
                                  ("Meter Group" + p).child(meter).child(user_value).child("units")
                                  .get())
                token_value = receiver_units.val()
                time_share = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + p).
                              child(meter).child(user_value).child("Time Share From").get())
                time_value = time_share.val()
                if unit_value <= 0.1:
                    if token_value == 0 and v <= 1 and time_value == 0:
                        (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + p).
                         child(meter).update({"Power Status": 0}))
                    self.dialog_title = "Sharing Stopped"
                    self.dialog_message = f"{meter_value} Doesn't Have Enough Units For Sharing"
                    self.show_dialog(self)
                else:
                    (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + p).
                     child(meter).update({"Power Status": 1}))

    def scan_sharing_records(self):
        login_email_screen = self.root.get_screen('login')
        user = login_email_screen.ids.login_mail.text
        username = user[0:len(user) - 10]
        # current_time = datetime.datetime.now().strftime("%H:%M:%S")
        active_meter = (self.database.child("Registered Users").child(username).child("Active Meter").get())
        meter_value = active_meter.val()
        meter_str = meter_value
        str_length = len(meter_str)
        f = str_length - 11
        num_str = meter_str[-f:]
        share_state = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                       child(meter_value).child(username).child("Sharing to").get())
        status_value = share_state.val()
        time_state = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                      child(meter_value).child(username).child("Time Share to").get())
        time_value = time_state.val()
        inf_state = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str).
                     child(meter_value).child(username).child("Unlimited Share to").get())
        inf_value = inf_state.val()
        # if status_value == 0:
        # Clock.unschedule(self.scan_sharing_records())
        if status_value and time_value != 0:
            self.time_counter()
        if status_value and inf_value != 0:
            self.unlimited_recorder()
        self.track_sharing()

    def start_sharing(self):
        self.sharing_start = True
        self.sharing_stop = False
        self.time_picker()

    def stop_sharing(self):
        if self.start_time == "":
            # self.dialog_title = "Invalid Operation"
            self.dialog_message = "Please Provide Sharing Start Time"
            self.show_dialog(self)
            return
        self.sharing_stop = True
        self.sharing_start = False
        self.time_picker()

    def time_sharing(self):
        meter_found = False
        sender_num = ""
        sharing_status = False
        tither_screen = self.root.get_screen("tither_token")
        meter_name = tither_screen.ids.search_field
        # get the meter number from the input field which token will be shred with
        meter_number = meter_name.text
        login_email_screen = self.root.get_screen('login')
        user = login_email_screen.ids.login_mail.text
        username = user[0:len(user) - 10]
        # Getting the sender meter number
        user_meter_number = (self.database.child("Registered Users").child(username).child("Active Meter").get())
        meter_number_value = user_meter_number.val()
        general_share = (self.database.child("Remote Energy Multimeter").child("Meters").child("Admin Records").
                         child("Universal Share").get())
        share_value = general_share.val()
        if meter_number_value == "":
            self.dialog_title = "Invalid Operation"
            self.dialog_message = "No Meter is Allocated To You Yet"
            self.show_dialog(self)
            return
        print(f" There Goes Meter Number Value: {meter_number_value}")
        if meter_number == "":
            # self.dialog_title = "Meter Number Error!"
            self.dialog_message = "Please Enter Meter Number!"
            self.show_dialog(self)
            return
        elif meter_number == meter_number_value:
            self.dialog_title = "Invalid Operation"
            self.dialog_message = "Sharing Between Same Meter Not Allowed"
            self.show_dialog(self)
            return
        else:
            time_sharing_data = {"Start Time": self.start_time, "Stop Time": self.stop_time}
            # receiver_meter = {meter_number: ""}

            get_meters_groups = (self.database.child("Remote Energy Multimeter").child("Meters").child("Admin Records").
                                 child("Meters Addition").get())
            meter_groups = get_meters_groups.val()
            j = meter_groups + 1
            # search for current meter existence
            meter_str = meter_number
            sender_str = meter_number_value
            str_length = len(meter_str)
            try:
                sender_str_length = len(sender_str)
                d = sender_str_length - 11
                sender_num = sender_str[-d:]
            except TypeError:
                self.dialog_title = "Invalid Operation"
                self.dialog_message = "No Meter is Allocated To You Yet"
                self.show_dialog(self)
                return

            f = str_length - 11
            # Str2 = Str[-N:]
            num_str = meter_str[-f:]

            meter_user = (self.database.child("Remote Energy Multimeter").child("Meters").
                          child("Meter Group" + num_str).child(meter_number).child("Meter User").get())
            meter_user_name = meter_user.val()

            sender_code = (self.database.child("Remote Energy Multimeter").child("Meters").
                           child("Meter Group" + sender_num).child(meter_number_value).child(username).
                           child("Meter Code").get())
            sender_value = sender_code.val()
            receiver_code = (self.database.child("Remote Energy Multimeter").child("Meters").
                             child("Meter Group" + num_str).child(meter_number).child(meter_user_name).
                             child("Meter Code").get())
            receiver_value = receiver_code.val()
            if receiver_value != sender_value and share_value == 0:
                self.dialog_title = "Failed"
                self.dialog_message = "Universal Sharing is Not Activated"
                self.show_dialog(self)
                return

        for x in range(1, j):
            unit = (self.database.child("Remote Energy Multimeter").child("Meters").
                    child("Meter Group" + str(x)).get())
            for item in unit.each():
                if item.key() == meter_number_value:
                    meter_user = (self.database.child("Remote Energy Multimeter").child("Meters").
                                  child("Meter Group" + sender_num).child(meter_number_value).
                                  child("Meter User").get())
                    user_value = meter_user.val()
                    units = (self.database.child("Remote Energy Multimeter").child("Meters").
                             child("Meter Group" + sender_num).child(meter_number_value).child(user_value).
                             child("units").get())
                    available_units = units.val()
                    sender_status = (self.database.child("Remote Energy Multimeter").child("Meters").
                                     child("Meter Group" + str(x)).child(meter_number_value).child(user_value).
                                     child("Sharing From").get())
                    q = sender_status.val()

                    if q == 1:
                        self.dialog_title = "Failed!"
                        self.dialog_message = "Can't Share While Sharing From Other Meters"
                        self.show_dialog(self)
                        return

                    if available_units <= 0.1:
                        self.dialog_title = "Operation Failed! "
                        self.dialog_message = "Insufficient Units, Load Units and Try Again"
                        self.show_dialog(self)
                        return
                    else:
                        pass

            for y in range(1, j):
                all_meters = (self.database.child("Remote Energy Multimeter").child("Meters").
                              child("Meter Group" + str(y)).get())
                # search for current meter existance
                for m in all_meters.each():
                    print(F"KEY ARE----------------------------{m.key()}")
                    if m.key() == meter_number:
                        meter_found = True
                        meter_availability = (self.database.child("Remote Energy Multimeter").child("Meters").
                                              child("Meter Group" + str(y)).child(m.key()).child("Meter Availability")
                                              .get())
                        available_meter = meter_availability.val()
                        if available_meter == 1:
                            self.dialog_title = "Unused Meter Number!"
                            self.dialog_message = "Meter Number Provided Has no End User"
                            self.show_dialog(self)
                            return
                        else:
                            sharing_data = {"Meter-1": meter_number}
                            print(f"---Meter Group{y}--{meter_number}--{username}---{num_str}")
                            meter_user = (self.database.child("Remote Energy Multimeter").child("Meters").
                                          child("Meter Group" + num_str).child(meter_number).child("Meter User")
                                          .get())
                            meter_user_name = meter_user.val()
                            # print(F"METER NUMBER VALUE-++++++++++++++++++++++++++++++++++{meter_number_value}")
                            receiver_sharing = (self.database.child("Remote Energy Multimeter").child("Meters").
                                                child("Meter Group" + num_str).child(meter_number).
                                                child(meter_user_name).child("Time Share From").get())

                            sender_sharing = (self.database.child("Remote Energy Multimeter").child("Meters").
                                              child("Meter Group" + sender_num).child(meter_number_value).
                                              child(username).child("Time Share to").get())
                            shared_data = {"Meter-1": meter_number_value}
                            sender_share_status = sender_sharing.val()
                            receiver_share_status = receiver_sharing.val()
                            if sender_share_status == 0:
                                (self.database.child("Remote Energy Multimeter").child("Meters").
                                 child("Meter Group" + sender_num).child(meter_number_value).child(username).
                                 update({"Time Share to": 1}))
                                (self.database.child("Remote Energy Multimeter").child("Meters").
                                 child("Meter Group" + sender_num).child(meter_number_value).child(username).
                                 child("Time Sharing to").child(meter_number).set(time_sharing_data))
                                (self.database.child("Remote Energy Multimeter").child("Meters").
                                 child("Meter Group" + sender_num).child(meter_number_value).child(username).
                                 update({"Sharing to": 1}))
                                # sender_share_status
                            else:
                                print(f"--------------------------------------------------------{sender_share_status}")
                                v = receiver_share_status + 1
                                # d = sender_share_status + 1
                                same_meter = (self.database.child("Remote Energy Multimeter").child("Meters").
                                              child("Meter Group" + sender_num).child(meter_number_value).child
                                              (username).child("Time Sharing to").get())
                                for e in same_meter.each():
                                    # print(f"####################################################{e}")
                                    if e.key() == meter_number:
                                        self.dialog_title = "Failed!"
                                        self.dialog_message = "You're Already Sharing to " + meter_number
                                        self.show_dialog(self)
                                        return
                                for f in range(1, v):
                                    print(f"####################################################{f}")
                                    sent_meter = (self.database.child("Remote Energy Multimeter").child("Meters").
                                                  child("Meter Group" + sender_num).child(meter_number_value).
                                                  child(username).child("Unlimited Sharing From").
                                                  child(f"Meter_{f}").child(f"Meter-{f}").get())
                                    m = sent_meter.val()
                                    if m == meter_number:
                                        self.dialog_title = "Failed!"
                                        self.dialog_message = "You're Already Sharing To " + meter_number
                                        self.show_dialog(self)
                                        return

                                    sender_share_status += 1
                                    # t = sender_share_status
                                    (self.database.child("Remote Energy Multimeter").child("Meters").
                                     child("Meter Group" + sender_num).child(meter_number_value).child(username).
                                     update({"Time Share to": sender_share_status}))
                                    (self.database.child("Remote Energy Multimeter").child("Meters").
                                     child("Meter Group" + sender_num).child(meter_number_value).child(username).
                                     child("Time Sharing to").child(meter_number).set(time_sharing_data))
                            if receiver_share_status == 0:
                                (self.database.child("Remote Energy Multimeter").child("Meters").
                                 child("Meter Group" + num_str).child(meter_number).child(meter_user_name).
                                 update({"Time Share From": 1}))
                                (self.database.child("Remote Energy Multimeter").child("Meters").
                                 child("Meter Group" + num_str).child(meter_number).child(meter_user_name).
                                 child("Time Sharing From").child(meter_number_value).set(time_sharing_data))
                                (self.database.child("Remote Energy Multimeter").child("Meters").
                                 child("Meter Group" + num_str).child(meter_number).child(meter_user_name).
                                 update({"Sharing From": 1}))
                            else:
                                receiver_share_status += 1
                                r = receiver_share_status
                                (self.database.child("Remote Energy Multimeter").child("Meters").
                                 child("Meter Group" + num_str).child(meter_number).child(meter_user_name).
                                 update({"Time Share From": r}))
                                (self.database.child("Remote Energy Multimeter").child("Meters").
                                 child("Meter Group" + num_str).child(meter_number).child(meter_user_name).
                                 child("Time Sharing From").child(meter_number_value).set(time_sharing_data))
                        break
        if meter_found:
            pass
        else:
            self.dialog_title = "Meter Number Error!"
            self.dialog_message = "Meter Number Provided Doesn't Exist"
            self.show_dialog(self)

    def get_new_meter(self):
        new_meter_found = False
        count = 0
        login_email_screen = self.root.get_screen('login')
        meter_screen = self.root.get_screen('meter_number')
        new_meter_number = meter_screen.ids.new_meter.text
        user = login_email_screen.ids.login_mail.text
        username = user[0:len(user) - 10]
        # signup_data = {"user_signup": username, "user_phone": phone}
        # self.database.child("Remote Energy Multimeter").child(username).set(signup_data)
        get_meters = (self.database.child("Remote Energy Multimeter").child("Meters").child("Admin Records").
                      child("Meters Addition").get())
        user_phone = (self.database.child("Remote Energy Multimeter").child(username).child("user_phone").get())
        number_of_meters = (self.database.child("Registered Users").child(username).child("Meters Owned").get())

        meters = number_of_meters.val()
        user_mobile = user_phone.val()
        meter_searched = get_meters.val() + 1

        temp_list = [new_meter_number]

        u = meters + 1
        new_user_data = {"Meter Number": new_meter_number, "units": 0.0,
                         "Token Bought": 0.0, "Sharing to": 0, "Sharing From": 0, "Unlimited Share From": 0,
                         "Unlimited Share to": 0, "Time Share to": 0, "Time Share From": 0,
                         "Unlimited Sharing From": "", "unlimited Sharing to": "", "Time Sharing From": "",
                         "Time Sharing to": ""}

        meter_data = {"voltage": 0.0, "current": 0.0, "power": 0, "Meter Availability": 1, "Meter User": username,
                      "Energy Consumed": 0.0, "Power Status": 1, username: ""}

        new_meter_data = {"Meter-1": new_meter_number}

        print(f"New Meter Provided: {new_meter_number}")
        # search for current meter existance
        for y in range(1, meter_searched):
            all_users = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + str(y)).
                         get())
            for user in all_users.each():
                # print(f"KEY ARE FOUND: {user.key()}")
                if user.key() == new_meter_number:
                    new_meter_found = True
                    meter_availability = (self.database.child("Remote Energy Multimeter").child("Meters").
                                          child("Meter Group" + str(y)).child(user.key()).child("Meter Availability")
                                          .get())
                    available_meter = meter_availability.val()
                    if available_meter == 1:
                        (self.database.child("Remote Energy Multimeter").child("Meters").
                         child("Meter Group" + str(y)).child(new_meter_number).
                         update({"Meter Number": new_meter_number}))
                        (self.database.child("Remote Energy Multimeter").child("Meters").
                         child("Meter Group" + str(y)).child(new_meter_number).
                         update({"Meter User": username}))
                        if meters >= 1:
                            for i in range(u):
                                listed_meter = (self.database.child("Registered Users").child(username).
                                                child("Meter Number").child(f"Meter_{i}").child(f"Meter-{i}").get())
                                k = listed_meter.val()
                                if k is not None:
                                    temp_list.append(k)
                                print(f"THIS IS THE LIST :{temp_list}")
                            for h in temp_list:
                                count += 1
                                (self.database.child("Registered Users").child(username).child("Meter Number").
                                 child(f"Meter_{count}").update({f"Meter-{count}": h}))
                                (self.database.child("Remote Energy Multimeter").child("Meters").child
                                 ("Meter Group" + str(y)).child(h).update({"Meter Availability": 0}))
                                (self.database.child("Remote Energy Multimeter").child("Meters").child
                                 ("Meter Group" + str(y)).child(h).update({"Meter User": username}))
                                # (self.database.child("Remote Energy Multimeter").child("Meters").child
                                # ("Meter Group" + str(y)).child(h).set(meter_data))
                                (self.database.child("Remote Energy Multimeter").child("Meters").child
                                 ("Meter Group" + str(y)).child(h).child(username).set(new_user_data))

                            self.database.child("Registered Users").child(username).update({"Meters Owned": count})
                            print(f"THIS IS THE LIST :{temp_list}")
                        else:
                            print(f"Matched Meter Number: {user}")
                            (self.database.child("Remote Energy Multimeter").child("Meters").
                             child("Meter Group" + str(y)).child(new_meter_number).update({"Meter Availability": 0}))
                            # (self.database.child("Remote Energy Multimeter").child("Meters").
                            # child("Meter Group" + str(y)).child(new_meter_number).set(meter_data))
                            self.database.child("Registered Users").child(username).update({"Meters Owned": 1})
                            (self.database.child("Registered Users").child(username).child("Meter Number").
                             child("Meter_1").set(new_meter_data))
                            (self.database.child("Remote Energy Multimeter").child("Meters").
                             child("Meter Group" + str(y)).child(new_meter_number).child(username).set(new_user_data))
                            (self.database.child("Registered Users").child(username).update(
                                {"Active Meter": new_meter_number}))
                        break
                    else:
                        self.dialog_title = "New Meter Error!"
                        self.dialog_message = "Meter Number Provided is Occupied"
                        self.show_dialog(self)
                if new_meter_found:
                    break
        if not new_meter_found:
            self.dialog_title = "New Meter Error!"
            self.dialog_message = "Meter Number Provided Doesn't Exist"
            self.show_dialog(self)
            '''
            self.dialog_title = "New Meter Registration"
            self.dialog_message = "Operation Successful"
            self.show_dialog(self)
            '''

    def token_sharing(self):
        meter_found = False
        sender_num = ""
        tither_screen = self.root.get_screen("tither_token")
        meter_name = tither_screen.ids.search_field
        login_email_screen = self.root.get_screen('login')
        user = login_email_screen.ids.login_mail.text
        username = user[0:len(user) - 10]
        # get the meter number from the input field which token will be shred with
        meter_number = meter_name.text
        token_screen = self.root.get_screen("units_share")
        units = token_screen.ids.units_label
        b = units.text

        user_meter_number = (self.database.child("Registered Users").child(username).child("Active Meter").get())
        meter_number_value = user_meter_number.val()

        if meter_number_value == "":
            self.dialog_title = "Invalid Operation"
            self.dialog_message = "No Meter is Allocated To You Yet"
            self.show_dialog(self)
            return

        meter_str = meter_number
        sender_str = meter_number_value
        str_length = len(meter_str)
        try:
            sender_str_length = len(sender_str)
            d = sender_str_length - 11
            sender_num = sender_str[-d:]
        except TypeError:
            self.dialog_title = "Invalid Operation"
            self.dialog_message = "No Meter is Allocated To You Yet"
            self.show_dialog(self)
            return
        f = str_length - 11
        # Str2 = Str[-N:]
        num_str = meter_str[-f:]
        available_units = 0.0

        if self.shared_units == "Input Units Amount to Share" or self.shared_units == 0:
            self.dialog_title = "Operation Failed"
            self.dialog_message = "Units Shared Can't be 0"
            self.show_dialog(self)
            return

        if meter_number == "":
            # self.dialog_title = "Meter Number Error!"
            self.dialog_message = "Please Enter Meter Number!"
            self.show_dialog(self)
            return
        elif meter_number == meter_number_value:
            self.dialog_title = "Invalid Operation"
            self.dialog_message = "Sharing Between Same Meter Not Allowed"
            self.show_dialog(self)
        else:
            get_meters_groups = (self.database.child("Remote Energy Multimeter").child("Meters").child("Admin Records").
                                 child("Meters Addition").get())
            meter_groups = get_meters_groups.val() + 1

            for x in range(1, meter_groups):
                unit = (self.database.child("Remote Energy Multimeter").child("Meters").
                        child("Meter Group" + str(x)).get())
                for item in unit.each():
                    if item.key() == meter_number_value:
                        meter_user = (self.database.child("Remote Energy Multimeter").child("Meters").
                                      child("Meter Group" + str(x)).child(meter_number_value).child("Meter User").get())
                        user_value = meter_user.val()
                        units = (self.database.child("Remote Energy Multimeter").child("Meters").
                                 child("Meter Group" + str(x)).child(meter_number_value).child(user_value).
                                 child("units").get())
                        available_units = units.val()
                        sender_status = (self.database.child("Remote Energy Multimeter").child("Meters").
                                         child("Meter Group" + str(x)).child(meter_number_value).child(user_value).
                                         child("Sharing From").get())
                        q = sender_status.val()

                        if q == 1:
                            self.dialog_title = "Failed!"
                            self.dialog_message = "Can't Share While Sharing From Other Meters"
                            self.show_dialog(self)
                            return

                        if available_units <= 0.2:
                            self.dialog_title = "Operation Failed! "
                            self.dialog_message = "Insufficient Units, Load Units and Try Again"
                            self.show_dialog(self)
                            return
                        else:
                            pass
            for y in range(1, meter_groups):
                all_meters = (self.database.child("Remote Energy Multimeter").child("Meters").
                              child("Meter Group" + str(y)).get())
                # search for current meter existance
                for m in all_meters.each():
                    print(F"KEY ARE----------------------------{m.key()}")
                    if m.key() == meter_number:
                        meter_found = True
                        meter_availability = (self.database.child("Remote Energy Multimeter").child("Meters").
                                              child("Meter Group" + str(y)).child(m.key()).child("Meter Availability")
                                              .get())
                        available_meter = meter_availability.val()
                        if available_meter == 1:
                            print(F"Meter Number--{m.key()}---{available_meter}--")
                            self.dialog_title = "Unused Meter Number!"
                            self.dialog_message = "Meter Number Provided Has no End User"
                            self.show_dialog(self)
                            return
                        else:
                            meter_user = (self.database.child("Remote Energy Multimeter").child("Meters").
                                          child("Meter Group" + num_str).child(meter_number).child("Meter User").get())
                            meter_user_name = meter_user.val()
                            receiver_unit = (self.database.child("Remote Energy Multimeter").child("Meters").
                                             child("Meter Group" + num_str).child(meter_number).child(meter_user_name).
                                             child("units").get())
                            unit_value = receiver_unit.val()
                            # rounded = round(self.shared_units, 3)
                            total_units = self.shared_units + unit_value
                            rounded_total = round(total_units, 3)
                            s = available_units - self.shared_units
                            rounded = round(s, 3)
                            if s >= 0.2:
                                (self.database.child("Remote Energy Multimeter").child("Meters").
                                 child("Meter Group" + num_str).child(meter_number).child(meter_user_name).
                                 update({"units": rounded_total}))
                                (self.database.child("Remote Energy Multimeter").child("Meters").
                                 child("Meter Group" + sender_num).child(meter_number_value).child(username).
                                 update({"units": rounded}))
                            else:
                                self.dialog_title = "Failed, High Token Value!"
                                self.dialog_message = "Input a Lower Unit Value and Try Again"
                                self.show_dialog(self)
                        break
        if meter_found:
            pass
        else:
            self.dialog_title = "Meter Number Error!"
            self.dialog_message = "Meter Number Provided Doesn't Exist"
            self.show_dialog(self)

    def unlimited_sharing(self):
        # variable to check the state of any sharing activate
        meter_found = False
        sender_num = 0
        # sharing_status = False
        # sender_sharing_status = False
        # senders_number =
        tither_screen = self.root.get_screen("tither_token")
        meter_name = tither_screen.ids.search_field
        login_email_screen = self.root.get_screen('login')
        user = login_email_screen.ids.login_mail.text
        username = user[0:len(user) - 10]
        # get the meter number from the input field which token will be shared with
        meter_number = meter_name.text

        user_meter_number = (self.database.child("Registered Users").child(username).
                             child("Active Meter").get())
        meter_number_value = user_meter_number.val()
        general_share = (self.database.child("Remote Energy Multimeter").child("Meters").child("Admin Records").
                         child("Universal Share").get())
        share_value = general_share.val()
        if meter_number_value == "":
            self.dialog_title = "Invalid Operation"
            self.dialog_message = "No Meter is Allocated To You Yet"
            self.show_dialog(self)
            return

        meter_str = meter_number
        sender_str = meter_number_value
        str_length = len(meter_str)
        try:
            sender_str_length = len(sender_str)
            d = sender_str_length - 11
            sender_num = sender_str[-d:]
        except TypeError:
            self.dialog_title = "Invalid Operation"
            self.dialog_message = "No Meter is Allocated To You Yet"
            self.show_dialog(self)

        f = str_length - 11
        # Str2 = Str[-N:]
        num_str = meter_str[-f:]

        meter_user = (self.database.child("Remote Energy Multimeter").child("Meters").
                      child("Meter Group" + num_str).child(meter_number).child("Meter User").get())
        meter_user_name = meter_user.val()

        sender_code = (self.database.child("Remote Energy Multimeter").child("Meters").
                       child("Meter Group" + sender_num).child(meter_number_value).
                       child("Meter Code").get())
        sender_value = sender_code.val()
        receiver_code = (self.database.child("Remote Energy Multimeter").child("Meters").
                         child("Meter Group" + num_str).child(meter_number).
                         child("Meter Code").get())
        receiver_value = receiver_code.val()
        print(f">>>Meter Code1: {receiver_value} >>>Meter Code2: {sender_value}")
        if receiver_value != sender_value and share_value == 0:
            self.dialog_title = "Failed"
            self.dialog_message = "Universal Sharing is Not Activated"
            self.show_dialog(self)
            return

        if meter_number == "":
            # self.dialog_title = "Meter Number Error!"
            self.dialog_message = "Please Enter Meter Number!"
            self.show_dialog(self)
            return
        elif meter_number == meter_number_value:
            self.dialog_title = "Invalid Operation"
            self.dialog_message = "Sharing Between Same Meter Not Allowed"
            self.show_dialog(self)
        else:
            sent_meter = (self.database.child("Remote Energy Multimeter").child("Meters").
                          child("Meter Group" + sender_num).child(meter_number_value).
                          child(username).child("Time Sharing From").get())
            # m = sent_meter.val()
            get_meters_groups = (self.database.child("Remote Energy Multimeter").child("Meters").child("Admin Records").
                                 child("Meters Addition").get())
            meter_groups = get_meters_groups.val() + 1

            for x in range(1, meter_groups):
                unit = (self.database.child("Remote Energy Multimeter").child("Meters").
                        child("Meter Group" + str(x)).get())
                for item in unit.each():
                    if item.key() == meter_number_value:
                        meter_user = (self.database.child("Remote Energy Multimeter").child("Meters").
                                      child("Meter Group" + str(x)).child(meter_number_value).child("Meter User").get())
                        user_value = meter_user.val()
                        units = (self.database.child("Remote Energy Multimeter").child("Meters").
                                 child("Meter Group" + str(x)).child(meter_number_value).child(user_value).
                                 child("units").get())
                        available_units = units.val()
                        sender_status = (self.database.child("Remote Energy Multimeter").child("Meters").
                                         child("Meter Group" + str(x)).child(meter_number_value).child(user_value).
                                         child("Sharing From").get())
                        q = sender_status.val()

                        if q == 1:
                            self.dialog_title = "Failed!"
                            self.dialog_message = "Can't Share While Sharing From Other Meters"
                            self.show_dialog(self)
                            return

                        if available_units <= 0.1:
                            self.dialog_title = "Operation Failed! "
                            self.dialog_message = "Insufficient Units, Load Units and Try Again"
                            self.show_dialog(self)
                            return
                        else:
                            pass

            for y in range(1, meter_groups):
                all_meters = (self.database.child("Remote Energy Multimeter").child("Meters").
                              child("Meter Group" + str(y)).get())
                # search for current meter existance
                for m in all_meters.each():
                    print(F"KEY ARE----------------------------{m.key()}")
                    if m.key() == meter_number:
                        meter_found = True
                        meter_availability = (self.database.child("Remote Energy Multimeter").child("Meters").
                                              child("Meter Group" + str(y)).child(m.key()).child("Meter Availability")
                                              .get())
                        available_meter = meter_availability.val()
                        if available_meter == 1:
                            self.dialog_title = "Unused Meter Number!"
                            self.dialog_message = "Meter Number Provided Has no End User"
                            self.show_dialog(self)
                            return
                        else:
                            sharing_data = {"Meter-1": meter_number}
                            # print(F"METER NUMBER VALUE-++++++++++++++++++++++++++++++++++{meter_number_value}")
                            receiver_sharing = (self.database.child("Remote Energy Multimeter").child("Meters").
                                                child("Meter Group" + num_str).child(meter_number).
                                                child(meter_user_name).child("Unlimited Share From").get())

                            sender_sharing = (self.database.child("Remote Energy Multimeter").child("Meters").
                                              child("Meter Group" + sender_num).child(meter_number_value).
                                              child(username).child("Unlimited Share to").get())
                            shared_data = {"Meter-1": meter_number_value}
                            sender_share_status = sender_sharing.val()
                            receiver_share_status = receiver_sharing.val()

                            if sender_share_status == 0:
                                (self.database.child("Remote Energy Multimeter").child("Meters").
                                 child("Meter Group" + sender_num).child(meter_number_value).child(username).
                                 update({"Unlimited Share to": 1}))
                                (self.database.child("Remote Energy Multimeter").child("Meters").
                                 child("Meter Group" + sender_num).child(meter_number_value).child(username).
                                 child("Unlimited Sharing to").child("Meter_1").set(sharing_data))
                                (self.database.child("Remote Energy Multimeter").child("Meters").
                                 child("Meter Group" + sender_num).child(meter_number_value).child(username).
                                 update({"Sharing to": 1}))
                                # sender_share_status
                            else:
                                print(f"--------------------------------------------------------{sender_share_status}")
                                v = receiver_share_status + 1
                                d = sender_share_status + 1
                                for e in range(1, d):
                                    print(f"####################################################{e}")
                                    same_meter = (self.database.child("Remote Energy Multimeter").child("Meters").
                                                  child("Meter Group" + sender_num).child(meter_number_value).child
                                                  (username).child("Unlimited Sharing to").child(f"Meter_{e}").
                                                  child(f"Meter-{e}").get())
                                    g = same_meter.val()
                                    if g == meter_number:
                                        self.dialog_title = "Failed!"
                                        self.dialog_message = "You're Already Sharing to " + meter_number
                                        self.show_dialog(self)
                                        return
                                try:
                                    for f in sent_meter.each():
                                        if f.key() == meter_number:
                                            self.dialog_title = "Failed!"
                                            self.dialog_message = "You're Already Sharing To " + meter_number
                                            self.show_dialog(self)
                                            return
                                except TypeError:
                                    pass

                                sender_share_status += 1
                                t = sender_share_status
                                (self.database.child("Remote Energy Multimeter").child("Meters").
                                 child("Meter Group" + sender_num).child(meter_number_value).child(username).
                                 update({"Unlimited Share to": sender_share_status}))
                                (self.database.child("Remote Energy Multimeter").child("Meters").
                                 child("Meter Group" + sender_num).child(meter_number_value).child(username).
                                 child("Unlimited Sharing to").child(f"Meter_{t}").
                                 update({f"Meter-{t}": meter_number}))
                            if receiver_share_status == 0:
                                (self.database.child("Remote Energy Multimeter").child("Meters").
                                 child("Meter Group" + num_str).child(meter_number).child(meter_user_name).
                                 update({"Unlimited Share From": 1}))
                                (self.database.child("Remote Energy Multimeter").child("Meters").
                                 child("Meter Group" + num_str).child(meter_number).child(meter_user_name).
                                 child("Unlimited Sharing From").child("Meter_1").set(shared_data))
                                (self.database.child("Remote Energy Multimeter").child("Meters").
                                 child("Meter Group" + num_str).child(meter_number).child(meter_user_name).
                                 update({"Sharing From": 1}))
                            else:
                                receiver_share_status += 1
                                r = receiver_share_status
                                (self.database.child("Remote Energy Multimeter").child("Meters").
                                 child("Meter Group" + num_str).child(meter_number).child(meter_user_name).
                                 update({"Unlimited Share From": r}))
                                (self.database.child("Remote Energy Multimeter").child("Meters").
                                 child("Meter Group" + num_str).child(meter_number).child(meter_user_name).
                                 child("Unlimited Sharing From").child(f"Meter_{r}").
                                 update({f"Meter-{r}": meter_number_value}))
                        break
        if meter_found:
            pass
        else:
            self.dialog_title = "Meter Number Error!"
            self.dialog_message = "Meter Number Provided Doesn't Exist"
            self.show_dialog(self)

    def clear_login_fields(self):
        login_email_screen = self.root.get_screen('login')
        login_password_screen = self.root.get_screen('login')
        email_login = login_email_screen.ids.login_mail
        password_login = login_password_screen.ids.login_password
        email_login.text = ""
        password_login.text = ""

    def submit_applied_meter(self):
        user_found = False
        current_date = str(datetime.datetime.now())
        date_string = current_date[0:19]
        meter_date = f"  <{date_string}>"
        own_meter_screen = self.root.get_screen("meter_owner")
        added_meters = own_meter_screen.ids.meter_quantity_label
        show_meters = own_meter_screen.ids.meter_number_label
        till = own_meter_screen.ids.till_number
        self.dialog_title = "Meter Numbers Application"
        self.dialog_message = "Meter Numbers Selected Will be Invalidated in 14 Days if Not Used"
        self.show_dialog(self)
        login_email_screen = self.root.get_screen('login')
        email_login = login_email_screen.ids.login_mail
        user = email_login.text
        username = user[0:len(user) - 10]
        owner_till = till.text

        phone = (self.database.child("Registered Users").child(username).child("Phone Number").get())
        phone_value = phone.val()
        a = phone_value[-3:]
        b = username[-3:]
        c = a + b

        all_users = self.database.child("Meter Owners").get()
        for p in all_users.each():
            if p.key() == username:
                if owner_till != "" and self.applied_meters_counter == 0:
                    (self.database.child("Meter Owners").child(username).update({"Till Number": owner_till}))

        meter_data = {"voltage": 0.0, "current": 0.0, "power": 0, "Meter Availability": 1, "Power Limit": 0,
                      "Meter Code": c, "Energy Consumed": 0.0, "Power Status": 0, "Meter User": "", "Meter Number": "",
                      "Meter Counted": 0, "Meter Owner": username, "Sender Online": 0, "Receiver Online": 0,
                      "Shared Units": 0.0}
        if owner_till != "":
            y = owner_till
        else:
            y = 0
        if self.applied_meters_counter > 0:
            meter_groups = (self.database.child("Remote Energy Multimeter").child("Meters").child("Admin Records").
                            child("Meters Addition").get())
            meters_owned = (self.database.child("Meter Owners").child(username).child("Number of Meters").get())
            applications_found = (self.database.child("Meter Owners").child(username).child("Meter Applications").get())
            meters_available = meters_owned.val()
            number_of_applications = applications_found.val()
            add_meters = meter_groups.val()
            add_meters += 1
            if meters_available is None:
                meters_available = 0

            meter_owner = {"Meters": "", "Number of Meters": 0, "Till Number": y, "MTD Payment": 0, "Meter Code": c,
                           "Debit Amount": "", "Credit Amount": "", "Meter Applications": 0, "MTD Consumption": 0.0,
                           "Credit Token": 0}
            # search for current meter existance
            try:
                number_of_applications += 1
                (self.database.child("Meter Owners").child(username).update
                 ({"Meter Applications": number_of_applications}))
                for user in all_users.each():
                    if user.key() == username:
                        user_found = True
                        for item in self.meter_list:
                            meters_available += 1
                            (self.database.child("Meter Owners").child(username).child("Meters").
                             child("Application:" + str(number_of_applications)).
                             update({"Meter-" + str(meters_available): item + " " + meter_date}))
                            (self.database.child("Meter Owners").child(username).
                             update({"Number of Meters": meters_available}))
                    break

            except TypeError:
                pass
            if not user_found:
                if number_of_applications is None:
                    (self.database.child("Meter Owners").child(username).set(meter_owner))
                    number_of_applications = 1
                (self.database.child("Meter Owners").child(username).
                 update({"Meter Applications": number_of_applications}))
                for item in self.meter_list:
                    meters_available += 1
                    (self.database.child("Meter Owners").child(username).child("Meters").
                     child("Application:" + str(number_of_applications)).
                     update({"Meter-" + str(meters_available): item + " " + meter_date}))
                    (self.database.child("Meter Owners").child(username).
                     update({"Number of Meters": meters_available}))
                    (self.database.child("Remote Energy Multimeter").child("Meters").
                     child("Meter Group" + str(add_meters)).update({item: ""}))
                    (self.database.child("Remote Energy Multimeter").child("Meters").
                     child("Meter Group" + str(add_meters)).child(item).set(meter_data))
                (self.database.child("Remote Energy Multimeter").child("Meters").child("Admin Records").
                 update({"Meters Addition": add_meters}))
                (self.database.child("Remote Energy Multimeter").child("Meters").child("Admin Records")
                 .update({"Last Meter": self.end_meter}))
        else:
            self.dialog_title = "Meter Numbers Application Error"
            self.dialog_message = "No Meter Numbers were Selected"
            self.show_dialog(self)
        added_meters.text = 'Quantity of Meters'
        show_meters.text = 'Meter Numbers Selected'
        self.applied_meters_counter = 0
        self.meter_list = []
        self.end_meter = ""
        self.tither_mode = 0

    def unlimited_button(self):
        owner_found = False
        unlimited_screen = self.root.get_screen("sharing")
        shared = unlimited_screen.ids.list_one
        mode = unlimited_screen.ids.Sharing_mode
        login_email_screen = self.root.get_screen('login')
        email_login = login_email_screen.ids.login_mail
        user = email_login.text
        username = user[0:len(user) - 10]
        user_meter_number = (self.database.child("Registered Users").child(username).child("Active Meter").get())
        meter_number_value = user_meter_number.val()
        meter_str = meter_number_value
        # sender_str = meter_number_value
        str_length = len(meter_str)
        f = str_length - 11
        # Str2 = Str[-N:]
        num_str = meter_str[-f:]
        sharing_to = (self.database.child("Remote Energy Multimeter").child("Meters").
                      child("Meter Group" + num_str).child(meter_number_value).child(username).
                      child("Unlimited Share to").get())
        share_to = sharing_to.val()
        sharing_from = (self.database.child("Remote Energy Multimeter").child("Meters").
                        child("Meter Group" + num_str).child(meter_number_value).child(username).
                        child("Unlimited Share From").get())
        share_from = sharing_from.val()

        time_to = (self.database.child("Remote Energy Multimeter").child("Meters").
                   child("Meter Group" + num_str).child(meter_number_value).child(username).
                   child("Time Share to").get())
        time_value_to = time_to.val()
        time_from = (self.database.child("Remote Energy Multimeter").child("Meters").
                     child("Meter Group" + num_str).child(meter_number_value).child(username).
                     child("Time Share From").get())
        time_value_from = time_from.val()
        shared.clear_widgets()
        y = share_to + 1
        z = share_from + 1
        # my_list = ["Leo", "Benjy", "Jemmy", "Ronny"]
        # list_two = ["Anunda", "Omuya", "Marale", "Juma"]
        if self.sharing_button == 1:
            self.end_sharing = True
            if share_to == 0 and share_from == 0:
                mode.text = "No Sharing Data to View"
                self.dialog_message = "You are not sharing to or from anyone in Unlimited mode"
                self.show_dialog(self)
                return

            if share_to >= 1:
                mode.text = "Unlimited Sharing Mode To:"
                for i in range(1, y):
                    meter = (self.database.child("Remote Energy Multimeter").child("Meters").
                             child("Meter Group" + num_str).child(meter_number_value).child(username).
                             child("Unlimited Sharing to").child(f"Meter_{i}").child(f"Meter-{i}").get())
                    meter_value = meter.val()
                    shared.add_widget(TwoLineListItem(text=f"[size=17]{meter_value}[/size]",
                                                      secondary_text="[size=14]Click Red Icon to Cancel[/size]",
                                                      height="42dp",
                                                      _no_ripple_effect=True,
                                                      on_release=lambda x, listed=meter_value: self.get_selected(listed)
                                                      ), )
            if share_from >= 1:
                mode.text = "Unlimited Sharing Mode From:"
                for j in range(1, z):
                    meter_from = (self.database.child("Remote Energy Multimeter").child("Meters").
                                  child("Meter Group" + num_str).child(meter_number_value).child(username).
                                  child("Unlimited Sharing From").child(f"Meter_{j}").child(f"Meter-{j}").get())
                    meter_value = meter_from.val()
                    shared.add_widget(TwoLineListItem(text=f"[size=17]{meter_value}[/size]",
                                                      secondary_text="[size=14]Click Red Icon to Cancel[/size]",
                                                      height="42dp",
                                                      _no_ripple_effect=True,
                                                      on_release=lambda x, listed=meter_value: self.get_selected(listed)
                                                      ), )
        elif self.sharing_button == 0:
            self.end_sharing = False
            # start_time = ""
            # stop_time = ""
            # c = time_value_from + 1
            # d = time_value_to + 1
            if time_value_from == 0 and time_value_to == 0:
                mode.text = "No Sharing Data to View"
                self.dialog_message = "You are not sharing to or from anyone in Time mode"
                self.show_dialog(self)
                return

            if time_value_to >= 1:
                mode.text = "Time Sharing Mode To:"
                to_meters = (self.database.child("Remote Energy Multimeter").child("Meters").
                             child("Meter Group" + num_str).child(meter_number_value).child(username).
                             child("Time Sharing to").get())

                for v in to_meters.each():
                    meter = v.key()
                    start = (self.database.child("Remote Energy Multimeter").child("Meters").
                             child("Meter Group" + num_str).child(meter_number_value).child(username).
                             child("Time Sharing to").child(meter).child("Start Time").get())
                    start_time = start.val()
                    stop = (self.database.child("Remote Energy Multimeter").child("Meters").
                            child("Meter Group" + num_str).child(meter_number_value).child(username).
                            child("Time Sharing to").child(meter).child("Stop Time").get())
                    stop_time = stop.val()
                    shared.add_widget(ThreeLineListItem(text=f"[size=17]{meter}[/size]",
                                                        secondary_text=f"[size=14]Start Time: {start_time}[/size]",
                                                        tertiary_text=f"[size=14]Start Time: {stop_time}[/size]",
                                                        height="54dp",
                                                        _no_ripple_effect=True,
                                                        on_release=lambda x, listed=meter: self.get_selected(listed)
                                                        ), )
            if time_value_from >= 1:
                mode.text = "Time Sharing Mode From:"
                from_meters = (self.database.child("Remote Energy Multimeter").child("Meters").
                               child("Meter Group" + num_str).child(meter_number_value).child(username).
                               child("Time Sharing From").get())

                for v in from_meters.each():
                    meter = v.key()
                    start = (self.database.child("Remote Energy Multimeter").child("Meters").
                             child("Meter Group" + num_str).child(meter_number_value).child(username).
                             child("Time Sharing From").child(meter).child("Start Time").get())
                    start_time = start.val()
                    stop = (self.database.child("Remote Energy Multimeter").child("Meters").
                            child("Meter Group" + num_str).child(meter_number_value).child(username).
                            child("Time Sharing From").child(meter).child("Stop Time").get())
                    stop_time = stop.val()
                    shared.add_widget(ThreeLineListItem(text=f"[size=17]{meter}[/size]",
                                                        secondary_text=f"[size=14]Start Time: {start_time}[/size]",
                                                        tertiary_text=f"[size=14]Start Time: {stop_time}[/size]",
                                                        height="34dp",
                                                        _no_ripple_effect=True,
                                                        on_release=lambda x, listed=meter: self.get_selected(listed)
                                                        ), )
        elif self.sharing_button == 2:
            mode.text = "Your Meters"
            meter_owned = (self.database.child("Registered Users").child(username).child("Meters Owned").get())
            meters_counted = meter_owned.val()
            if meters_counted == 0:
                self.dialog_message = "You Don't Own Any Meter Yet!"
                self.show_dialog(self)
                return
            u = meters_counted + 1
            for v in range(1, u):
                meter = (self.database.child("Registered Users").child(username).child("Meter Number").
                         child(f"Meter_{v}").child(f"Meter-{v}").get())
                meter_value = meter.val()
                if meter_value is not None:
                    shared.add_widget(OneLineListItem(text=f"[size=17]{meter_value}[/size]",
                                                      # secondary_text=f"[size=14]Start Time: {start_time}[/size]",
                                                      # tertiary_text=f"[size=14]Start Time: {stop_time}[/size]",
                                                      height="34dp",
                                                      _no_ripple_effect=True,
                                                      on_release=lambda x, listed=meter_value: self.get_selected(listed)
                                                      ), )
        elif self.sharing_button == 4:
            owner_list = []
            avail = ""
            used = ""
            owners = (self.database.child("Meter Owners").get())
            for users in owners.each():
                if users.key() == username:
                    owner_found = True
                    break
            if owner_found:
                meter_digit = ""
                applications = (self.database.child("Meter Owners").child(username).child("Meter Applications").get())
                applications_value = applications.val()
                owned = (self.database.child("Meter Owners").child(username).child("Number of Meters").get())
                owned_value = owned.val()
                q = applications_value + 1
                owned_value += 1
                for m in range(1, q):
                    meter_num = (self.database.child("Meter Owners").child(username).child("Meters").
                                 child(f"Application:{m}").get())
                    for h in meter_num.each():
                        num = (self.database.child("Meter Owners").child(username).child("Meters").
                               child(f"Application:{m}").child(h.key()).get())
                        num_val = num.val()
                        # owner_list.append(num_val)
                        # if num_val is not None:
                        meter_digit = num_val[0:12]
                        str_length = len(meter_digit)
                        d = str_length - 11
                        group_num = meter_digit[-d:]
                        meter_user = (self.database.child("Remote Energy Multimeter").child("Meters").
                                      child("Meter Group" + group_num).child(meter_digit).child("Meter User").get())
                        user_value = meter_user.val()
                        print(f">>>>>num_val: {num_val}>>>>user_value: {user_value}<<<>>>meter_digit: {meter_digit}<<<"
                              f"group_num: {group_num}")
                        if user_value is None or user_value == "":
                            avail = "Meter is Unoccupied"
                            used = "Meter User : No User"
                        else:
                            user_phone = (self.database.child("Registered Users").child(user_value).
                                          child("Phone Number").get())
                            phone_value = user_phone.val()
                            avail = "Meter Is In Use"
                            used = "User Phone:" + phone_value
                        shared.add_widget(ThreeLineListItem(text=f"[size=14]{num_val}[/size]",
                                                            secondary_text=f"[size=14]{avail}[/size]",
                                                            tertiary_text=f"[size=14]{used}[/size]",
                                                            height="30dp",
                                                            _no_ripple_effect=True,
                                                            # on_release=lambda x, listed=meter: self.get_selected(list)
                                                            ), )

        else:
            self.dialog_title = "Wait a Minute!"
            self.dialog_message = "Sorry, You Don't Own Multiple Meters"
            self.show_dialog(self)

    def set_selection_mode(self, instance_selection_list, mode):
        unlimited_screen = self.root.get_screen("sharing")
        shared = unlimited_screen.ids.list_one
        top_bar = unlimited_screen.ids.toolbar
        if mode:
            md_bg_color = self.overlay_color
            left_action_items = [
                [
                    "close",
                    lambda x: self.selection_callback(),
                ]
            ]
            right_action_items = [["trash-can"], ["dots-vertical", lambda x: self.callback(x), ]]
        else:
            md_bg_color = (0, 0, 0, 1)
            left_action_items = [["arrow-left", lambda x: self.sharing_callback(x)]]
            right_action_items = [["dots-vertical"]]
            top_bar.title = "View Sharing Info"

        Animation(md_bg_color=md_bg_color, d=0.2).start(top_bar)
        top_bar.left_action_items = left_action_items
        top_bar.right_action_items = right_action_items

    def on_selected(self, instance_selection_list, instance_selection_item):
        self.check_selected = True
        unlimited_screen = self.root.get_screen("sharing")
        shared = unlimited_screen.ids.toolbar
        selection = unlimited_screen.ids.list_one
        shared.title = str(len(instance_selection_list.get_selected_list_items()))
        selected = instance_selection_list.get_selected_list_items()
        # for i in selected:
        # print(i)
        # print(dir(i))

    def on_unselected(self, instance_selection_list, instance_selection_item):
        self.check_unselected = True
        unlimited_screen = self.root.get_screen("sharing")
        shared = unlimited_screen.ids.toolbar
        if instance_selection_list.get_selected_list_items():
            shared.title = str(len(instance_selection_list.get_selected_list_items()))
            # y = len(instance_selection_list.get_selected_list_items())

    def sharing_callback(self, button):
        self.root.transition.direction = "right"
        self.root.current = "power"
        self.selected_list = []

    def get_selected(self, listed):
        if self.check_selected:
            self.check_selected = False
            if listed != "":
                self.selected_list.append(listed)
        if self.check_unselected:
            self.check_unselected = False
            if self.selected_list:
                self.selected_list.remove(listed)
        print(self.selected_list)

    # def empty_list(self):
    # self.selected_list = []

    def all_unselected(self):
        unlimited_screen = self.root.get_screen("sharing")
        shared = unlimited_screen.ids.list_one
        shared.unselected_all()

    def selection_callback(self):
        y = ""
        self.all_unselected()
        self.selected_list = []
        self.get_selected(y)

    def end_unlimited_sharing(self):
        login_email_screen = self.root.get_screen('login')
        user = login_email_screen.ids.login_mail.text
        username = user[0:len(user) - 10]
        # get the meter number from the input field which token will be shared with
        # meter_number = meter_name.text

        user_meter_number = (self.database.child("Registered Users").child(username).child("Active Meter").get())
        meter_number_value = user_meter_number.val()
        sender_str = meter_number_value
        str_length = len(sender_str)
        d = str_length - 11
        sender_num = sender_str[-d:]

        counted_meter = (self.database.child("Remote Energy Multimeter").child("Meters").
                         child("Meter Group" + sender_num).child(meter_number_value).child(username).
                         child("Unlimited Share to").get())
        meters_counted = counted_meter.val()
        num = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + sender_num).
               child(meter_number_value).child(username).child("Time Share to").get())
        c = num.val()

        for meters in self.selected_list:
            meter_str = meters
            length_str = len(meter_str)
            j = length_str - 11
            num_str = meter_str[-j:]
            meter_user = (self.database.child("Remote Energy Multimeter").child("Meters").child("Meter Group" + num_str)
                          .child(meters).child("Meter User").get())
            user_value = meter_user.val()
            # u_number = 0
            # y_number = 0
            time_num = 0
            rx_counted = 0
            if self.end_sharing:
                rx_meter = (self.database.child("Remote Energy Multimeter").child("Meters").
                            child("Meter Group" + num_str).child(meters).child(user_value).child("Unlimited Share From")
                            .get())
                rx_counted = rx_meter.val()
                m = rx_counted + 1  # unlimited share from
                n = meters_counted + 1  # unlimited share to
                rx_counted -= 1
                meters_counted -= 1
                (self.database.child("Remote Energy Multimeter").child("Meters").
                 child("Meter Group" + num_str).child(meters).child(user_value).update
                 ({"Unlimited Share From": rx_counted}))
                (self.database.child("Remote Energy Multimeter").child("Meters").
                 child("Meter Group" + sender_num).child(meter_number_value).child(username).update
                 ({"Unlimited Share to": meters_counted}))
                for u in range(1, m):
                    x = (self.database.child("Remote Energy Multimeter").child("Meters").
                         child("Meter Group" + num_str).child(meters).child(user_value).child("Unlimited Sharing From").
                         child(f"Meter_{u}").child(f"Meter-{u}").get())
                    sender_meter = x.val()
                    if sender_meter == meter_number_value:
                        # u_number = u
                        (self.database.child("Remote Energy Multimeter").child("Meters").
                         child("Meter Group" + num_str).child(meters).child(user_value).child("Unlimited Sharing From").
                         child(f"Meter_{u}").child(f"Meter-{u}").get())
                for y in range(1, n):
                    t = (self.database.child("Remote Energy Multimeter").child("Meters").
                         child("Meter Group" + sender_num).child(meter_number_value).child(username).
                         child("Unlimited Sharing to").child(f"Meter_{y}").child(f"Meter-{y}").get())
                    receiver_meter = t.val()
                    if receiver_meter == meters:
                        print(f"****************{meters}*****************")
                        # y_number = y
                        (self.database.child("Remote Energy Multimeter").child("Meters").
                         child("Meter Group" + sender_num).child(meter_number_value).child(username).
                         child("Unlimited Sharing to").child(f"Meter_{y}").child(f"Meter-{y}").remove())

                        (self.database.child("Remote Energy Multimeter").child("Meters").
                         child("Meter Group" + num_str).child(meters).child(user_value).
                         child("Unlimited Sharing From").child(f"Meter_{y}").child(f"Meter-{y}").remove())
            else:
                time_meter = (self.database.child("Remote Energy Multimeter").child("Meters").
                              child("Meter Group" + num_str).child(meters).child(user_value).child("Time Share From")
                              .get())
                time_num = time_meter.val()
                k = (self.database.child("Remote Energy Multimeter").child("Meters").
                     child("Meter Group" + num_str).child(meters).child(user_value).child("Time Sharing From")
                     .get())
                time_num -= 1
                c -= 1
                (self.database.child("Remote Energy Multimeter").child("Meters").
                 child("Meter Group" + num_str).child(meters).child(user_value).update
                 ({"Time Share From": time_num}))
                (self.database.child("Remote Energy Multimeter").child("Meters").
                 child("Meter Group" + sender_num).child(meter_number_value).child(username).update
                 ({"Time Share to": c}))
                for w in k.each():
                    if w.key() == meter_number_value:
                        # u_number = u
                        (self.database.child("Remote Energy Multimeter").child("Meters").
                         child("Meter Group" + num_str).child(meters).child(user_value).child("Time Sharing From").
                         child(w.key()).child("Start Time").remove())
                        (self.database.child("Remote Energy Multimeter").child("Meters").
                         child("Meter Group" + num_str).child(meters).child(user_value).child("Time Sharing From").
                         child(w.key()).child("Stop Time").remove())
                        (self.database.child("Remote Energy Multimeter").child("Meters").
                         child("Meter Group" + sender_num).child(w.key()).child(username).child("Time Sharing to").
                         child(meters).child("Start Time").remove())
                        (self.database.child("Remote Energy Multimeter").child("Meters").
                         child("Meter Group" + sender_num).child(w.key()).child(username).child("Time Sharing to").
                         child(meters).child("Stop Time").remove())
            if rx_counted >= 1:
                # r = rx_counted + 1
                r = 0
                for t in range(1, 2000):
                    g = (self.database.child("Remote Energy Multimeter").child("Meters").
                         child("Meter Group" + num_str).child(meters).child(user_value).
                         child("Unlimited Sharing From").child(f"Meter_{t}").child(f"Meter-{t}").get())
                    h = g.val()
                    if h is not None:
                        r += 1
                        (self.database.child("Remote Energy Multimeter").child("Meters").
                         child("Meter Group" + num_str).child(meters).child(user_value).
                         child("Unlimited Sharing From").child(f"Meter_{r}").update({f"Meter-{r}": h}))
                        if r == rx_counted:
                            break
            if meters_counted >= 1:
                a = 0
                for z in range(1, 2000):
                    k = (self.database.child("Remote Energy Multimeter").child("Meters").
                         child("Meter Group" + sender_num).child(meter_number_value).child(username).
                         child("Unlimited Sharing to").child(f"Meter_{z}").child(f"Meter-{z}").get())
                    b = k.val()
                    if b is not None:
                        a += 1
                        (self.database.child("Remote Energy Multimeter").child("Meters").
                         child("Meter Group" + sender_num).child(meter_number_value).child(username).
                         child("Unlimited Sharing to").child(f"Meter_{a}").update({f"Meter-{a}": b}))
                        if a == meters_counted:
                            break

            if c == 0 and meters_counted == 0:
                (self.database.child("Remote Energy Multimeter").child("Meters").
                 child("Meter Group" + sender_num).child(meter_number_value).child(username).
                 update({"Sharing to": 0}))
            if time_num == 0 and rx_counted == 0:
                (self.database.child("Remote Energy Multimeter").child("Meters").
                 child("Meter Group" + num_str).child(meters).child(user_value).update({"Sharing From": 0}))

    def buy_token(self):
        # till_num = "174379"
        till_num = "888880"
        self.spinner = True
        payment_data = MpesaHandler(till_num)
        login_email_screen = self.root.get_screen('login')
        user = login_email_screen.ids.login_mail.text
        token_screen = self.root.get_screen("token")
        token_amount = token_screen.ids.cash_label
        units_amount = token_screen.ids.units_label
        units_bought = float(units_amount.text)
        cash_paid = int(token_amount.text)
        print(f"units bought={units_amount.text}, cash paid={token_amount.text} ")
        username = user[0:len(user) - 10]
        user_meter_number = (self.database.child("Registered Users").child(username).child("Active Meter").get())
        meter_number_value = user_meter_number.val()
        user_phone = (self.database.child("Registered Users").child(username).child("Phone Number").get())
        phone_value = user_phone.val
        sender_str = meter_number_value
        str_length = len(sender_str)
        d = str_length - 11
        sender_num = sender_str[-d:]
        user_units = (self.database.child("Remote Energy Multimeter").child("Meters").
                      child("Meter Group" + sender_num).child(meter_number_value).child(username).
                      child("Token Bought").get())
        units_value = user_units.val()
        g = units_value + units_bought
        total_units = round(g, 3)
        user_data = {"amount": 1, 'phone_number': "254719795557"}
        get_response = payment_data.make_stk_push(user_data)
        try:
            t = get_response['CheckoutRequestID']
        except KeyError:
            self.dialog_title = "Failed!"
            self.dialog_message = "Merchant does not exist!"
            self.show_dialog(self)
            return
        for i in range(0, 300):
            query_payment_status = payment_data.query_transaction_status(t)
            try:
                r = query_payment_status["ResponseCode"]
                w = query_payment_status["ResultCode"]
                if r == "0" and w == "0":
                    (self.database.child("Remote Energy Multimeter").child("Meters").
                     child("Meter Group" + sender_num).child(meter_number_value).child(username).
                     update({"Token Bought": total_units}))
                    self.spinner = False
                    self.dialog_title = "Successfull!"
                    self.dialog_message = f"Amount Paid: KSh. {cash_paid}, Units Received: {units_bought}KWh"
                    self.show_dialog(self)
                    break
                elif r == "0" and w != "0":
                    self.spinner = False
                    self.dialog_title = "Failed!"
                    self.dialog_message = "Something Went Wrong, Operation Could Not Be Completed!"
                    self.show_dialog(self)
                    break
            except KeyError:
                pass
            print(query_payment_status)
            time.sleep(1)

    def application_approval(self):
        login_email_screen = self.root.get_screen('login')
        user = login_email_screen.ids.login_mail.text
        username = user[0:len(user) - 10]
        user_phone = (self.database.child("Registered Users").child(username).child("Phone Number").get())
        phone_value = user_phone.val()
        request = (self.database.child("Remote Energy Multimeter").child("Meters").child("Admin Records").
                   child("Request Number").get())
        request_value = request.val()
        if request_value >= 1:
            applications = (self.database.child("Remote Energy Multimeter").child("Meters").child("Admin Records").
                            child("Application Request").get())
            for r in applications.each():
                y = (self.database.child("Remote Energy Multimeter").child("Meters").child("Admin Records").
                     child("Application Request").child(r.key()).child("User Email").get())
                user_value = y.val()
                if user_value == username:
                    self.dialog_title = "Failed!"
                    self.dialog_message = "You Still Have a Pending Application"
                    self.show_dialog(self)
                    return

        req_data = {"User Email": username, "User Phone": phone_value}
        u = request_value + 1
        (self.database.child("Remote Energy Multimeter").child("Meters").child("Admin Records").
         child("Application Request").update({f"Application-{u}": req_data}))
        (self.database.child("Remote Energy Multimeter").child("Meters").child("Admin Records").
         update({"Request Number": u}))

        self.dialog_title = "Done!"
        self.dialog_message = "Operation Completed Successfully, You Will be Contacted ASAP"
        self.show_dialog(self)


EnergyMeterApp().run()
