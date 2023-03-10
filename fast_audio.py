import gradio as gr
import speech_recognition as sr
import threading

def callback(recognizer, audio):
    try:
        # text = recognizer.recognize_google(audio)
        print("Audio length: {} seconds".format(len(audio.get_raw_data()) / 16000))
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

def background_listen(m, callback, stopper):
    r = sr.Recognizer()
    with m as source:
        r.adjust_for_ambient_noise(source)
    with sr.Microphone() as source:
        r.energy_threshold = 4000
        while not stopper():
            audio = r.listen(source, phrase_time_limit=5)
            callback(r, audio)

stopper = gr.FlaggingCallback()

audio_input = gr.Microphone(label="Record Audio")
text_output = gr.outputs.Textbox()

iface = gr.Interface(fn=None, inputs=audio_input, outputs=text_output, 
                     title='Real-Time Audio Transcription', live=True)

bg_thread = threading.Thread(target=background_listen, args=(sr.Microphone(), callback, stopper))
bg_thread.start()

iface.launch()

stopper.set()  # stop the background thread when the interface is closed
bg_thread.join()