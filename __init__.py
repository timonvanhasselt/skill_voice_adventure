import random
import threading
import time
import speech_recognition as sr
from pydub import AudioSegment
from pydub.playback import play

QUESTIONS_AUDIO_PATHS = {
    "Question 1": {
        "question": "question1.mp3",
        "correct_answer": "question1_yes.mp3",
        "incorrect_answer": "incorrect_answer.mp3"
    },
    "Question 2": {
        "question": "question2.mp3",
        "correct_answer": "question2_yes.mp3",
        "incorrect_answer": "incorrect_answer.mp3"
    },
    # Add paths for other questions in a similar manner
}

BACKGROUND_AUDIO_LOOP = "background_audio_loop.mp3"

def play_background_audio_loop():
    background_audio = AudioSegment.from_mp3(BACKGROUND_AUDIO_LOOP)
    while True:
        play(background_audio)

def play_audio(file_path):
    audio = AudioSegment.from_mp3(file_path)
    play(audio)

def get_user_response():
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("Please answer with 'yes' or 'no'.")
        audio_response = recognizer.listen(source)
        
    try:
        user_response = recognizer.recognize_google(audio_response).lower()
        return user_response
    except sr.UnknownValueError:
        print("Sorry, couldn't understand the audio.")
        return None

def main():
    score = 0
    question_keys = list(QUESTIONS_AUDIO_PATHS.keys())
    total_questions = len(question_keys)
    current_question_index = 0

    while current_question_index < total_questions:
        question_key = question_keys[current_question_index]
        question_info = QUESTIONS_AUDIO_PATHS[question_key]
        
        print(f"{question_key}:")
        play_audio(question_info["question"])

        # Randomize the order of options for the current question
        options = [question_info["correct_answer"], question_info["incorrect_answer"]]
        random.shuffle(options)
        
        # Play the randomized options for the current question
        for option in options:
            play_audio(option)
        
        # Get user's response
        user_response = get_user_response()

        if user_response is not None and user_response == 'yes':
            print("You chose 'Yes'. That's correct!")
            score += 1
            current_question_index += 1
        elif user_response is not None and user_response == 'no':
            print("You chose 'No'. That's incorrect.")
            play_audio(question_info["incorrect_answer"])
            current_question_index += 1
        else:
            print("Invalid response. Please try again.")
        
        # Display the current score after each question
        print(f"Current Score: {score}")

if __name__ == "__main__":
    main()
