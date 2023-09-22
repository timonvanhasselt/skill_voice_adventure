from ovos_utils import classproperty
from ovos_utils.intents import IntentBuilder
from ovos_utils.process_utils import RuntimeRequirements
from ovos_workshop.decorators import intent_handler
from ovos_workshop.skills import OVOSSkill
from pydub import AudioSegment
from pydub.playback import play
import threading


class VoiceAdventureSkill(OVOSSkill):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.score = 0
        self.question_keys = list(QUESTIONS_AUDIO_PATHS.keys())
        self.total_questions = len(self.question_keys)
        self.current_question_index = 0

        # Start the background audio loop in a separate thread
        self.background_thread = threading.Thread(target=self.play_background_audio_loop)
        self.background_thread.daemon = True
        self.background_thread.start()

   def initialize(self):
        # Initialize the OCP audio service with the bus
        self.audio = OCPInterface(self.bus)

    # Replace with your actual audio file path
BACKGROUND_AUDIO_LOOP = "path/to/background_audio_loop.mp3"

# Replace with your actual audio file paths
QUESTIONS_AUDIO_PATHS = {
    "Question 1": {
        "question": "path/to/question1.mp3",
        "correct_answer": "path/to/question1_yes.mp3",
        "incorrect_answer": "path/to/question1_no.mp3"
    },
    "Question 2": {
        "question": "path/to/question2.mp3",
        "correct_answer": "path/to/question2_yes.mp3",
        "incorrect_answer": "path/to/question2_no.mp3"
    },
    # Add paths for other questions in a similar manner
}
    def play_background_audio_loop(self):
       # background_audio = AudioSegment.from_mp3(BACKGROUND_AUDIO_LOOP)
        background_audio = BACKGROUND_AUDIO_LOOP
        
        while True:
            #play(background_audio)
            self.audio.play(background_audio)

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
        self.speak_dialog("welcome")
        self.ask_question()

    def ask_question(self):
        if self.current_question_index < self.total_questions:
            question_key = self.question_keys[self.current_question_index]
            question_info = QUESTIONS_AUDIO_PATHS[question_key]

            self.speak(question_info["question"])
            self.speak(question_info["correct_answer"])
            self.speak(question_info["incorrect_answer"])

            self.current_question_index += 1
        else:
            self.speak_dialog("end_of_game")
            self.speak(f"Your final score is {self.score}")
            self.stop()

    @intent_handler(IntentBuilder("YesIntent").require("YesKeyword"))
    def handle_yes_intent(self, message):
        self.handle_answer(True)

    @intent_handler(IntentBuilder("NoIntent").require("NoKeyword"))
    def handle_no_intent(self, message):
        self.handle_answer(False)

    def handle_answer(self, is_correct):
        if is_correct:
            self.speak_dialog("correct_answer")
            self.score += 1
        else:
            self.speak_dialog("incorrect_answer")

        self.ask_question()

    def stop(self):
        # Stop the background audio loop thread
        self.background_thread.join()
        pass
