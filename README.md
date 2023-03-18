# 🦜Speech2Speech🦜

Have a conversation with anyone from any youtube video. You just need a youtube link (~1minute of audio) and this app will let you talk (with your mouth not your fingers) to that person (or at least their GPT-based AI replica). Create wacky funny conversations with weird zany characters.

Full YouTube vid:

[![IMAGE_ALT](https://img.youtube.com/vi/Kvjd-V8zLtM/0.jpg)](https://www.youtube.com/live/Kvjd-V8zLtM)

## Dependencies

- [ElevenLabs](https://elevenlabs.com/)
- [OpenAI](https://openai.com/)
- [Gradio](https://gradio.app/)

** [Now Available as a 🤗HuggingFace Spaces](https://huggingface.co/spaces/hu-po/speech2speech) **

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
