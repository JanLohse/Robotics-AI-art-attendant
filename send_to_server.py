import argparse
import time

import cv2 as cv
import numpy as np
import requests

from TTS_azure import text_to_speech
from find_painting import detect_rectangles
from llmart import LLMModule
from movement import Robot
from speech_to_text import SpeechToText


def create_conversation(texts=["Interpret this artwork for its artistic merit"], images=[True], roles=["user"],
                        shorten=False):
    assert len(images) == len(texts) == len(roles)
    if not shorten:
        conversation = [{"role": role, "content": [{"type": "text", "text": text}, ], } for role, text in
                        zip(roles, texts)]
    else:
        conversation = [
            {"role": role,
             "content": [{"type": "text", "text": text + f". Keep it to {shorten} sentences or less."}, ], } for
            role, text in zip(roles, texts)]

    for sentence, image in zip(conversation, images):
        if image:
            sentence["content"].append({"type": "image"})

    return conversation


def output_voice(text):
    text_to_speech(text, voice_name="en-US-AriaNeural", voice_style="whispering")
    print('>', text)


stt = SpeechToText()


def get_voice():
    try:
        success, x = stt.recognize_speech()
        return success, x
    except Exception as e:
        return False, None


def search_next_painting(camera, robot, angle, max_attempts=30, accepted_delta=.05):
    print("searching for next painting")

    found = False
    counter = 0

    for i in range(20):
        camera.read()
        time.sleep(0.02)

    while not found and counter < max_attempts:
        robot.rotate(-angle)
        time.sleep(3)
        print("stopped rotating")
        for i in range(5):
            check, image = camera.read()
        if check and image is not None and type(image) is np.ndarray:

            found, images, centers = detect_rectangles(image=image, debug=False)
            if found:
                print(f"found {len(images)} paintings")
                time.sleep(2)
                for i in range(5):
                    check_2, image_2 = camera.read()
                found, images_2, centers_2 = detect_rectangles(image=image_2, debug=False)
                if not found:
                    continue
                print(f"found {len(images_2)} more paintings")
                candidates = []
                for center in centers:
                    for index, center_2 in enumerate(centers_2):
                        if np.linalg.norm(center - center_2) < accepted_delta and index not in candidates:
                            candidates.append(index)
                print(f"found {len(candidates)} candidates")
                found = bool(candidates)
        counter += 1

    if not found:
        return False, None, None

    images = [images_2[index] for index in candidates]
    centers = [centers_2[index] for index in candidates]
    distances = [np.linalg.norm(center - np.array([0.5, 0.5])) for center in centers]
    index = np.argmin(distances)
    image = images[index]
    center = centers[index]

    print("found image")

    return True, image, center


def send_message(url, data):
    # Send POST request
    response = requests.post(f"{url}/data", json=data)

    # Print the response
    if response.status_code == 200:
        answer = response.json()['response']
        answer = answer.split("assistant\n")[-1]
        return True, answer
    else:
        print(f"Error: {response.status_code}")
        return False, None


def analyze_question(question, gemini):
    analyzeQuestion = gemini.call_gemini(question)
    userWant = analyzeQuestion["userWant"]
    if userWant == 'unknown':
        if any(substring in question for substring in ['continue', 'next', 'proceed']):
            return 'continue'
        if any(substring in question for substring in ['stop', 'bye', 'finish', 'halt', 'done', 'over']):
            return 'stop'
        return 'askQuestion'
    return userWant


def main(camera, robot, gemini, demo=False, shorten=False):
    output_voice("Hello, I am your personal AI art gallery assistant")

    find_next_painting = True
    while find_next_painting:

        success, image, center = search_next_painting(camera, robot, angle=args.angle / 2)

        if not success:
            output_voice("I'm sorry, I could not find any paintings to comment on")
            break

        rotation_angle = - (center[1] - 0.5) * args.angle
        robot.rotate(rotation_angle)

        # Data to send
        data = {"conversations": [create_conversation(shorten=shorten)], "images": [image.tolist()]}

        while True:
            if not demo:
                success, answer = send_message(args.ngrok_url, data)
            else:
                success, answer = True, "This should be an AI generated answer"

            if not success:
                find_next_painting = False
                break
            output_voice(answer)

            output_voice(
                "Do you have any more questions about this painting or do you want to continue to the next painting?")
            success, question = get_voice()
            if not success:
                find_next_painting = False
                break

            user_want = analyze_question(question, gemini)
            if user_want == 'continue':
                break
            if user_want == 'stop':
                find_next_painting = False
                break
            if user_want == 'askQuestion':
                data = {
                    "conversations": [create_conversation(texts=['regarding this artwork: ' + question], images=[True],
                                                          shorten=shorten)],
                    "images": [image.tolist()]}

    output_voice("Thank you for interacting with me today!")

    camera.release()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="art_attendant")
    parser.add_argument('ngrok_url')
    parser.add_argument('-c', '--camera', type=int, default=0)
    parser.add_argument('-d', '--demo', action='store_true')
    parser.add_argument('-s', '--shorten', type=int, default=0)
    parser.add_argument('-a', '--angle', type=int, default=1.23, help='horizontal angle of view')
    args = parser.parse_args()

    camera = cv.VideoCapture(args.camera)
    camera.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv.CAP_PROP_FRAME_HEIGHT, 1080)

    for i in range(20):
        check, image = camera.read()
        time.sleep(0.1)
    robot = Robot(args.demo)
    gemini = LLMModule()

    print("connected camera and robot")

    while True:
        input('Press ENTER to start the AI gallery assistant.')
        main(camera, robot, gemini, demo=args.demo, shorten=args.shorten)
