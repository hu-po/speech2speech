export RELEASE_VERSION=0.1
cp app.py ../hf_speech2speech/app.py
cp -r src/ ../hf_speech2speech/src/
cp default_voices.yaml ../hf_speech2speech/default_voices.yaml
cd ../hf_speech2speech
git add .
git commit -m "release ${RELEASE_VERSION}"
git push
