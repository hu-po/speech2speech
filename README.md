# Speech2Speech

Create a conversation with GPT and anyone on any youtube video. You just need 1minute of a youtube video and this app will create a whole conversation for you. Plus you don't interact with text, you interact with SPEECH 😲

Full YouTube vid:

[![IMAGE_ALT](https://img.youtube.com/vi/kHYNoccEyFs/0.jpg)](https://www.youtube.com/live/kHYNoccEyFs)

## Dependencies

- [ElevenLabs](https://elevenlabs.com/)
- [OpenAI](https://openai.com/)
- [Gradio](https://gradio.app/)

## Setup

Make sure to have the following API keys.

```
$ELEVENLABS_API_KEY
$OPENAI_API_KEY
```

Make a python virtual environment and install the requirements.

```
conda create --name speech2speech python=3.10
conda activate speech2speech
pip install -r requirements.txt
```

Run the demo. Open a browser and go to http://127.0.0.1:7860/

```
python gradio_demo.py
```
