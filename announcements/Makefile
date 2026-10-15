MODEL = higgs
VOICE = $(if $(filter kokoro,$(MODEL)),bm_fable,patrick)
TEXT = Announcements are ready.
PORT = 8765
UVX = uvx --python 3.13 --from 'mlx-audio[server]==0.5.8' --with sentencepiece --with torch \
	--with 'misaki[en]' --with spacy --with num2words --with phonemizer \
	--with 'en-core-web-sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl'
REF_TEXT = "$$(cat voices/$(VOICE).txt 2>/dev/null)"
CLONE = --ref_audio voices/$(VOICE).wav --ref_text $(REF_TEXT)
higgs = --model ../models/higgs_audio_v3 $(CLONE) --temperature 0.8 --top_k 50
chatterbox = --model mlx-community/chatterbox-turbo-fp16 $(CLONE)
kokoro = --model prince-canuma/Kokoro-82M --voice $(VOICE) --speed 0.85
JQ = jq -n --arg input "$(TEXT)" --arg voice $(VOICE) --arg ref_audio $(CURDIR)/voices/$(VOICE).wav --arg ref_text $(REF_TEXT)
higgs_api = {model: "$(abspath ../models/higgs_audio_v3)", $$input, $$ref_audio, $$ref_text, temperature: 0.8, top_k: 50}
chatterbox_api = {model: "mlx-community/chatterbox-turbo-fp16", $$input, $$ref_audio, $$ref_text, temperature: 0.8, top_k: 1000, repetition_penalty: 1.2}
kokoro_api = {model: "prince-canuma/Kokoro-82M", $$input, $$voice, speed: 0.85}
WAV = out/$(MODEL)-$(VOICE)/$(shell md5 -qs "$(TEXT)").wav

.DEFAULT_GOAL := help
.PHONY: help say serve clean

help:
	@echo 'make say TEXT="Build finished."   speak it (MODEL=higgs|chatterbox|kokoro VOICE=patrick)'
	@echo '                                  each text renders once to out/, later calls replay the file'
	@echo 'make serve                        keep models loaded between calls (port $(PORT)); say uses it when up'
	@echo 'make clean                        delete out/'

say: $(WAV)
	afplay $<

$(WAV): $(if $(filter kokoro,$(MODEL)),,voices/$(VOICE).wav) | $(if $(filter higgs,$(MODEL)),../models/higgs_audio_v3)
	@mkdir -p $(@D)
	$(JQ) '$($(MODEL)_api) + {response_format: "wav"}' | curl -sSf -H 'Content-Type: application/json' --data @- -o $@ localhost:$(PORT)/v1/audio/speech \
		|| $(UVX) mlx_audio.tts.generate $($(MODEL)) --text "$(TEXT)" --output_path $(@D) --file_prefix $(basename $(@F)) --join_audio

serve: | ../models/higgs_audio_v3
	$(UVX) mlx_audio.server --port $(PORT) --log-dir out/logs

voices/patrick.wav: voices/patrick_original.mp3
	ffmpeg -hide_banner -loglevel error -y -ss 124.1 -to 136.4 -i $< -ac 1 -ar 24000 $@

# mlx-audio only maps the config's model_type when the path name contains it
../models/higgs_audio_v3:
	$(MAKE) -C .. models/higgs-tts-3/model.safetensors
	ln -s higgs-tts-3 $@

clean:
	rm -rf out
