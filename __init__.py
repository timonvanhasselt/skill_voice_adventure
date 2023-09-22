from ovos_utils import classproperty
from ovos_utils.intents import IntentBuilder
from ovos_utils.process_utils import RuntimeRequirements
from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill
from mycroft.util.audio_utils import play_audio_file
import threading
import random
import time

url = "https://github.com/timonvanhasselt/skill_voice_adventure/raw/main/"
# Define the audio file paths for question 1
QUESTION_1_AUDIO_PATHS = {
    "question":url+"scene1/q1.mp3",
    "options": [url+"scene1/q1a1.mp3", url+"scene1/q1a2.mp3", url+"scene1/q1a3.mp3", url+"scene1/q1a4.mp3"],
    "correct_answer": url+"scene1/q1correct.mp3",
    "incorrect_answer": url+"scene1/q1incorrect.mp3",
    "intro": url+"scene1/q1intro.mp3",
    "outro": url+"scene1/q1outro.mp3"
}

# Define the audio file paths for question 2
QUESTION_2_AUDIO_PATHS = {
    "question": "q2.mp3",
    "options": ["q2a1.mp3", "q2a2.mp3", "q2a3.mp3", "q2a4.mp3"],
    "correct_answer": "q2correct.mp3",
    "incorrect_answer": "q2incorrect.mp3",
    "intro": "q2intro.mp3",
    "outro": "q2outro.mp3"
}


class VoiceAdventureSkill(OVOSSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.score = 0
        self.current_option_index = 0
        self.background_audio_started = False
        self.current_question_index = 0

    def start_background_audio(self):
        self.background_audio_started = True
        self.background_thread = threading.Thread(target=self.play_background_audio_loop)
        self.background_thread.daemon = True
        self.background_thread.start()

    def play_background_audio_loop(self):
        while self.background_audio_started:
            play_audio_file(url+"BACKGROUND_AUDIO_LOOP.mp3")
            time.sleep(45)

    @classproperty
    def runtime_requirements(self):
        return RuntimeRequirements(
            internet_before_load=False,
            network_before_load=False,
            gui_before_load=False,
            requires_internet=False,
            requires_network=False,
            requires_gui=False,
            no_internet_fallback=True,
            no_network_fallback=True,
            no_gui_fallback=True,
        )

    @intent_handler(IntentBuilder("StartGameIntent").require("StartGameKeyword"))
    def handle_start_game_intent(self, message):
        if not self.background_audio_started:
            self.start_background_audio()
        play_audio_file(QUESTION_1_AUDIO_PATHS["intro"]),
        self.ask_question()

    def ask_question(self):
        question_number = self.current_question_index + 1
        question_key = f"Question {question_number}"
        question_info = globals()[f"QUESTION_{question_number}_AUDIO_PATHS"]

        play_audio_file(question_info["question"]), 

        # Randomize the order of options for the current question
        options = question_info["options"]
        random.shuffle(options)

        # Play the randomized options for the current question
        for option in options:
            play_audio_file(option)

        # Reset the option index for the new question
        self.current_option_index = 0

    @intent_handler(IntentBuilder("AnswerIntent").require("AnswerKeyword"))
    def handle_answer_intent(self, message):
        user_response = message.data.get("AnswerKeyword")
        if user_response == "yes":
            self.handle_answer(True)
        elif user_response == "no":
            self.handle_answer(False)

    def handle_answer(self, is_correct):
        question_number = self.current_question_index + 1
        question_key = f"Question {question_number}"
        question_info = globals()[f"QUESTION_{question_number}_AUDIO_PATHS"]

        if is_correct:
            play_audio_file(question_info["correct_answer"])
            self.score += 1
        else:
            play_audio_file(question_info["incorrect_answer"])

        self.current_question_index += 1
        if self.current_question_index < 10:
            self.ask_question()
        else:
            self.speak_dialog("end_of_game", {"score": self.score})
            self.stop()

    def stop(self):
        self.background_audio_started = False
        if hasattr(self, 'background_thread'):
            self.background_thread.join()
        pass
