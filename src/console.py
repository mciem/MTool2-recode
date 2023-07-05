from colorama  import Fore, init
from json      import loads
from threading import RLock
from datetime  import datetime

import pyfiglet
import os

class Console:
    def __init__(self):
        init()

        self.lock = RLock()
        self.banner = pyfiglet.figlet_format("MTool2")
        self.width  = os.get_terminal_size().columns

        with open("config.json", "r") as f:
            data = loads(f.read())
            theme = data["theme_color"]

            #cyan best
            schematic = {
                "magenta": Fore.LIGHTMAGENTA_EX,
                "red": Fore.LIGHTRED_EX,
                "blue": Fore.LIGHTBLUE_EX,
                "green": Fore.LIGHTGREEN_EX,
                "yellow": Fore.LIGHTYELLOW_EX,
                "cyan": Fore.LIGHTCYAN_EX,
            }

            self.main_color = schematic[theme]

    def getTime(self):
        return datetime.now().strftime("%H:%M:%S")
    
    def padRight(self, l):
        maxLength = max(len(x) for x in l)
        return [ x.ljust(maxLength) for x in l]
    
    def reportMenu(self, options):
        data = ""
        nn = {}
        i = 1
        for option in options:
            val = option[0]
            nn[i] = str(option[1])
            data += f"{self.main_color}[{Fore.LIGHTWHITE_EX}{str(i)}{self.main_color}]{Fore.LIGHTWHITE_EX} {val}\n"
            i += 1
        
        print(data)
        
        return nn[int(self.input("Option"))]
    
    def ticketOptions(self, options):
        data = ""
        nn = {}
        i = 1
        for option in options:
            val = option["value"]
            nn[i] = option["value"]
            data += f"{self.main_color}[{Fore.LIGHTWHITE_EX}{str(i)}{self.main_color}]{Fore.LIGHTWHITE_EX} {val}\n"
            i += 1
        
        print(data)
        
        return nn[int(self.input("Option"))]
    
    def options(self):
        print(self.center(f"""
        {self.main_color}[{Fore.LIGHTWHITE_EX}1{self.main_color}]{Fore.LIGHTWHITE_EX} Mass DM              {self.main_color}[{Fore.LIGHTWHITE_EX}9{self.main_color}]{Fore.LIGHTWHITE_EX} Verify Bypass       {self.main_color}[{Fore.LIGHTWHITE_EX}17{self.main_color}]{Fore.LIGHTWHITE_EX} Soundboard 
        {self.main_color}[{Fore.LIGHTWHITE_EX}2{self.main_color}]{Fore.LIGHTWHITE_EX} Scraper              {self.main_color}[{Fore.LIGHTWHITE_EX}10{self.main_color}]{Fore.LIGHTWHITE_EX} Button Clicker     {self.main_color}[{Fore.LIGHTWHITE_EX}18{self.main_color}]{Fore.LIGHTWHITE_EX} Change Display Name
        {self.main_color}[{Fore.LIGHTWHITE_EX}3{self.main_color}]{Fore.LIGHTWHITE_EX} Joiner               {self.main_color}[{Fore.LIGHTWHITE_EX}11{self.main_color}]{Fore.LIGHTWHITE_EX} Forum Flooder      {self.main_color}[{Fore.LIGHTWHITE_EX}19{self.main_color}]{Fore.LIGHTWHITE_EX} ???
        {self.main_color}[{Fore.LIGHTWHITE_EX}4{self.main_color}]{Fore.LIGHTWHITE_EX} Leaver               {self.main_color}[{Fore.LIGHTWHITE_EX}12{self.main_color}]{Fore.LIGHTWHITE_EX} Boost Server       {self.main_color}[{Fore.LIGHTWHITE_EX}20{self.main_color}]{Fore.LIGHTWHITE_EX} ???
        {self.main_color}[{Fore.LIGHTWHITE_EX}5{self.main_color}]{Fore.LIGHTWHITE_EX} Spammers             {self.main_color}[{Fore.LIGHTWHITE_EX}13{self.main_color}]{Fore.LIGHTWHITE_EX} Reaction Adder     {self.main_color}[{Fore.LIGHTWHITE_EX}21{self.main_color}]{Fore.LIGHTWHITE_EX} ???
        {self.main_color}[{Fore.LIGHTWHITE_EX}6{self.main_color}]{Fore.LIGHTWHITE_EX} Checker              {self.main_color}[{Fore.LIGHTWHITE_EX}14{self.main_color}]{Fore.LIGHTWHITE_EX} Onliner            {self.main_color}[{Fore.LIGHTWHITE_EX}22{self.main_color}]{Fore.LIGHTWHITE_EX} ???
        {self.main_color}[{Fore.LIGHTWHITE_EX}7{self.main_color}]{Fore.LIGHTWHITE_EX} VC Joiner            {self.main_color}[{Fore.LIGHTWHITE_EX}15{self.main_color}]{Fore.LIGHTWHITE_EX} Report             {self.main_color}[{Fore.LIGHTWHITE_EX}23{self.main_color}]{Fore.LIGHTWHITE_EX} ???
        {self.main_color}[{Fore.LIGHTWHITE_EX}8{self.main_color}]{Fore.LIGHTWHITE_EX} Nickname Changer     {self.main_color}[{Fore.LIGHTWHITE_EX}16{self.main_color}]{Fore.LIGHTWHITE_EX} PFP changer        {self.main_color}[{Fore.LIGHTWHITE_EX}24{self.main_color}]{Fore.LIGHTWHITE_EX} ???""", True))
        
    def spammer_options(self):
        print(self.center(f"""
        {self.main_color}[{Fore.LIGHTWHITE_EX}1{self.main_color}]{Fore.LIGHTWHITE_EX} Channel Spammer
        {self.main_color}[{Fore.LIGHTWHITE_EX}2{self.main_color}]{Fore.LIGHTWHITE_EX} Threads Spammer
        {self.main_color}[{Fore.LIGHTWHITE_EX}3{self.main_color}]{Fore.LIGHTWHITE_EX} Friend Request Spammer
        {self.main_color}[{Fore.LIGHTWHITE_EX}4{self.main_color}]{Fore.LIGHTWHITE_EX} DM Spammer""", True))

    def clear(self):
        os.system("cls")

    #dont look at this
    #shit was fucked so i had to fix it 🔥
    def center(self, text, options=False):
        nn  = []
        if options:
            spl = self.padRight(text.splitlines())
        else:
            spl = text.splitlines()

        i = 0
        for line in spl:
            line = line.strip("\n")
            if line.count(" ") != len(line):
                if options:
                    dn = ((self.width//2)-len(line)//3)
                else:
                    dn = ((self.width//2)-len(line)//2)

                if i+1 == len(spl):
                    nn.append(f'{dn * " "}{line}')
                else:
                    nn.append(f'{dn * " "}{line}\n')

            i += 1

        return "".join(nn)

    def logo(self):
        print(f"{self.main_color}{self.center(self.banner)}")

    def check(self, text, color):
        spl = text.split("->")
        
        return f"{spl[0]}{color}->{Fore.LIGHTWHITE_EX}{spl[1]}" if len(spl) > 1 else text

    def info(self, text,):
        self.lock.acquire()
        current_time = self.getTime()
        print(f"{Fore.LIGHTWHITE_EX}[{Fore.LIGHTBLACK_EX}{current_time}{Fore.LIGHTWHITE_EX}] {Fore.LIGHTBLUE_EX}INFO {Fore.LIGHTWHITE_EX}{self.check(text, Fore.LIGHTBLUE_EX)}")
        self.lock.release()

    def success(self, text):
        self.lock.acquire()
        current_time = self.getTime()
        print(f"{Fore.LIGHTWHITE_EX}[{Fore.LIGHTBLACK_EX}{current_time}{Fore.LIGHTWHITE_EX}] {Fore.LIGHTGREEN_EX}SUCCESS {Fore.LIGHTWHITE_EX}{self.check(text, Fore.LIGHTGREEN_EX)}")
        self.lock.release()
    
    def error(self, text):
        self.lock.acquire()
        if type(text) == dict:
            if text.get("message"):
                text = text["message"]
        
        current_time = self.getTime()
        print(f"{Fore.LIGHTWHITE_EX}[{Fore.LIGHTBLACK_EX}{current_time}{Fore.LIGHTWHITE_EX}] {Fore.LIGHTRED_EX}ERROR {Fore.LIGHTWHITE_EX}{self.check(text, Fore.LIGHTRED_EX)}")
        self.lock.release()

    def input(self, text):
        current_time = self.getTime()
        print(f"{Fore.LIGHTWHITE_EX}[{Fore.LIGHTBLACK_EX}{current_time}{Fore.LIGHTWHITE_EX}] {Fore.LIGHTCYAN_EX}INPUT {Fore.LIGHTWHITE_EX}{text} > ", end="")
        return input("")
