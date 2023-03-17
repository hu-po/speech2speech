export RELEASE_VERSION=0.1
cp app.py ../hf_speech2speech/app.py
cp -r src/ ../hf_speech2speech/src/
cp voices.yaml ../hf_speech2speech/voices.yaml
cp requirements.txt ../hf_speech2speech/requirements.txt
cp packages.txt ../hf_speech2speech/packages.txt
cd ../hf_speech2speech
git add .
git commit -m "release ${RELEASE_VERSION}"
git push
