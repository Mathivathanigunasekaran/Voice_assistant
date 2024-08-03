import tkinter as tk
from tkinter import scrolledtext
import threading
import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime
import wikipedia
import smtplib
import random
import requests
from bs4 import BeautifulSoup

class VoiceAssistantApp:
    def __init__(self, master):
        self.master = master
        master.title("Voice Assistant")
        master.geometry("600x400")
        master.configure(bg='black')  

        self.output_text = scrolledtext.ScrolledText(master, width=50, height=10, font=("Arial", 12), bg='black', fg='white')  # Set background color to black and text color to white
        self.output_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.entry = tk.Entry(master, width=50, font=("Arial", 12))
        self.entry.pack(padx=10, pady=5)

        self.btn_listen = tk.Button(master, text="Listen", command=self.start_listening, font=("Arial", 12), bg='black', fg='white')  # Set background color to black and text color to white
        self.btn_listen.pack(pady=5)

        self.btn_exit = tk.Button(master, text="Exit", command=master.quit, font=("Arial", 12), bg='black', fg='white')  # Set background color to black and text color to white
        self.btn_exit.pack(pady=5)

        self.btn_home = tk.Button(master, text="Home", command=self.go_home, font=("Arial", 12), bg='black', fg='white')  # Set background color to black and text color to white
        self.btn_home.pack(pady=5)

        self.btn_custom_command = tk.Button(master, text="Custom Command", command=self.execute_custom_command, font=("Arial", 12), bg='black', fg='white')  # Set background color to black and text color to white
        self.btn_custom_command.pack(pady=5)

        self.listener = sr.Recognizer()
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty("voices")
        self.engine.setProperty("voice", voices[1].id)

        self.display_home_page()

    def talk(self, text):
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)
        self.engine.say(text)
        self.engine.runAndWait()

    def get_command(self):
        try:
            with sr.Microphone() as source:
                print("Listening.........")
                self.talk("Listening...")
                self.listener.adjust_for_ambient_noise(source)
                voice = self.listener.listen(source)
                command = self.listener.recognize_google(voice)
                command = command.lower()

                if "youtube" in command:
                    command = command.replace("youtube", "")
        except sr.UnknownValueError:
            self.talk("Sorry, I couldn't understand what you said.")
            return ""
        except sr.RequestError:
            self.talk("Sorry, there was an issue with the service.")
            return ""
        return command

    def start_listening(self):
        self.entry.delete(0, tk.END)
        command = self.get_command()
        self.entry.insert(0, command)
        threading.Thread(target=self.process_command, args=(command,)).start()

    def process_command(self, command):
        if "play" in command:
            song = command.replace("play", "")
            pywhatkit.playonyt(song)

        elif "time" in command:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            current_date = datetime.datetime.now().strftime("%A, %B %d, %Y")
            self.talk(f"The current time is {current_time} and today is {current_date}.")

        elif "tell me about" in command:
            about = command.replace("tell me about", "")
            info = wikipedia.summary(about, 1)
            self.talk(info)

        elif "send email" in command:
            self.send_email()

        elif "news" in command:
            self.get_news()

        elif "fact" in command:
            self.get_fact()

        elif "exit" in command:
            self.exit_assistant()

        elif "home" in command:
            self.go_home()

        else:
            self.talk("Sorry, I can't understand. Please try again.")

    def execute_custom_command(self):
        command = self.entry.get().lower()
        self.entry.delete(0, tk.END)
        self.process_command(command)

    def exit_assistant(self):
        self.talk("Goodbye! Have a great day.")
        self.master.quit()

    def go_home(self):
        self.display_home_page()

    def display_home_page(self):
        self.output_text.delete(1.0, tk.END)
        self.entry.delete(0, tk.END)
        self.output_text.insert(tk.END, "Welcome to Voice Assistant!\n\n")
        self.output_text.insert(tk.END, "say something!\n")

    def send_email(self):
        self.talk("Please provide your email address.")
        email = input("Email: ")  
        self.talk("Please provide your email password.")
        password = input("Password: ") 
        try:
            if email and password:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(email, password)
                self.talk("What is the recipient's email address?")
                recipient_email = input("Recipient's Email: ")  
                self.talk("What should be the subject of the email?")
                subject = input("Subject: ") 
                self.talk("What message would you like to send?")
                message = input("Message: ")  
                email_content = f"Subject: {subject}\n\n{message}"
                server.sendmail(email, recipient_email, email_content)
                server.quit()
                self.talk("Email sent successfully!")
            else:
                self.talk("Email or password is missing. Please provide both.")
        except Exception as e:
            print(e)
            self.talk("Sorry, there was an error while sending the email.")

    def get_news(self):
        try:
            url = "https://www.bbc.com/news"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            headlines = soup.find_all("h3", class_="gs-c-promo-heading__title gel-pica-bold nw-o-link-split__text")
            
            print("Number of headlines found:", len(headlines))
            
            self.talk("Here are the latest news headlines.")
            for headline in headlines[:5]:
                print(headline.text.strip())
                self.talk(headline.text.strip())
        except Exception as e:
            print(e)
            self.talk("Sorry, I couldn't fetch the news headlines at the moment.")

    def get_fact(self):
        facts = [
            "The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after 38 minutes.",
            "Bananas are berries, but strawberries are not.",
            "A group of flamingos is called a 'flamboyance'.",
            "The Eiffel Tower can be 15 cm taller during the summer due to thermal expansion of the iron.",
            "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still perfectly edible."
        ]
        fact = random.choice(facts)
        self.talk("Here's a fun fact for you.")
        self.talk(fact)

def main():
    root = tk.Tk()
    app = VoiceAssistantApp(master=root)
    root.mainloop()

if __name__ == "__main__":
    main()
