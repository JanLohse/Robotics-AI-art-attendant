import os

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

AZURE_VOICES = [
    # Way more voices here https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts
    "en-US-DavisNeural",
    "en-US-TonyNeural",
    "en-US-JasonNeural",
    "en-US-GuyNeural",
    "en-US-JaneNeural",
    "en-US-NancyNeural",
    "en-US-JennyNeural",
    "en-US-AriaNeural",
]

AZURE_VOICE_STYLES = [
    # Currently using the 9 of the 11 available voice styles
    # Note that certain styles aren't available on all voices
    "angry",
    "cheerful",
    "excited",
    "hopeful",
    "sad",
    "shouting",
    "terrified",
    "unfriendly",
    "whispering",
    "Newscast",
    "Customer Service",
]


def text_to_speech(text, voice_name="en-US-AriaNeural", voice_style="cheerful"):
    load_dotenv()
    subscription_key = os.getenv('AZURE_SUBSCRIPTION_KEY')
    service_region = "southeastasia"

    speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=service_region)
    speech_config.speech_synthesis_voice_name = voice_name

    ssml_text = f"""
    <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xmlns:mstts='http://www.w3.org/2001/mstts' xml:lang='en-US'>
        <voice name='{voice_name}'>
            <mstts:express-as style='{voice_style}'>
                {text}
            </mstts:express-as>
        </voice>
    </speak>
    """
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
    result = speech_synthesizer.speak_ssml_async(ssml_text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))


if __name__ == "__main__":
    text = "Hello, I am your art Robot! Welcome to our art gallery. Follow me, and you will see all kinds of amazing artwork."
    text_to_speech(text, voice_name="en-US-AriaNeural", voice_style="whispering")
