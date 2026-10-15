HF = uvx --from 'huggingface_hub[hf_xet]' hf download
ENGINES = piper tts_uk styletts2 holos supertonic omnivoice higgs
ENGINE = higgs
VOICE = clone-maks-tsu
ARGS = $(if $(FILE),$(VOICE) -f $(FILE),$(VOICES) $(if $(TEXT),-t "$(TEXT)"))

.DEFAULT_GOAL := help
.PHONY: help all book clones models verbalizer voices index open clean distclean $(ENGINES)

help:
	@echo 'make models                 download all weights (~18 GB, pinned revisions)'
	@echo 'make all                    every engine over inputs/sentences.txt, then outputs/index.html'
	@echo 'make <engine>               one engine: $(ENGINES)'
	@echo '  VOICES="a b"              only these voices'
	@echo '  TEXT="Добрий вечір!"      say this instead of inputs/sentences.txt and play it'
	@echo 'make book FILE=x.txt        text file -> outputs/<engine>/<voice>/x.mp3 (ENGINE=higgs VOICE=clone-maks-tsu SEED=0)'
	@echo 'make clones                 inputs/clones/*.mp3 -> .wav (only missing or older ones)'
	@echo 'make voices                 list the voices of every engine'
	@echo 'make open                   rebuild outputs/index.html and open it'
	@echo 'make clean                  delete outputs/, logs/'
	@echo 'make distclean              clean + delete models/'

all: $(ENGINES)
	$(MAKE) open

# piper and tts_uk download their own weights on first run
$(ENGINES):
	uv run scripts/$@_tts.py $(ARGS)

styletts2: models/styletts2-single/pytorch_model.bin models/styletts2-multi/pytorch_model.bin models/styletts2-multi/voices verbalizer
holos: models/holos/holos.pt verbalizer
supertonic: models/supertonic/onnx/vocoder.onnx
omnivoice: models/omnivoice/model.safetensors
higgs: models/higgs-tts-3/model.safetensors

BOOK = outputs/$(ENGINE)/$(VOICE)/$(basename $(notdir $(FILE)))
book:
	rm -rf $(BOOK)
	$(MAKE) $(ENGINE)
	uv run scripts/audiobook.py $(BOOK)

clones: $(patsubst %.mp3,%.wav,$(wildcard inputs/clones/*.mp3))

inputs/clones/%.wav: inputs/clones/%.mp3
	ffmpeg -hide_banner -loglevel error -y -i $< -c:a pcm_s16le $@

voices:
	@for e in $(ENGINES); do echo "== $$e"; uv run scripts/$${e}_tts.py -h 2>/dev/null | sed -n 's/.*default: //p'; done

index:
	python3 scripts/make_index.py

open: index
	open outputs/index.html

clean:
	rm -rf outputs logs

distclean: clean
	rm -rf models

models: models/styletts2-single/pytorch_model.bin models/styletts2-multi/pytorch_model.bin models/styletts2-multi/voices \
	verbalizer models/holos/holos.pt models/supertonic/onnx/vocoder.onnx models/omnivoice/model.safetensors \
	models/higgs-tts-3/model.safetensors

verbalizer: models/verbalizer-ct2/model.bin models/verbalizer-tokenizer/sentencepiece.bpe.model

models/supertonic/onnx/vocoder.onnx:
	$(HF) Supertone/supertonic-3 --revision 3cadd1ee6394adea1bd021217a0e650ede09a323 --local-dir models/supertonic
models/holos/holos.pt:
	$(HF) patriotyk/HolosTTS --revision 12fbe72269148643b9cf09ab5ad946d5c2304497 --local-dir models/holos
models/styletts2-single/pytorch_model.bin:
	$(HF) patriotyk/styletts2_ukrainian_single --revision 2646553e1f9a8c832480e3ad5ccb6839245af584 --local-dir models/styletts2-single
models/styletts2-multi/pytorch_model.bin:
	$(HF) patriotyk/styletts2_ukrainian_multispeaker_hifigan --revision dcca8ce02382d91d95123c93f8b01bc90fe17cfc --local-dir models/styletts2-multi
models/styletts2-multi/voices:
	$(HF) patriotyk/styletts2-ukrainian --repo-type space --revision b02909e4c9f001865bf71633d76fee7110f657a3 --include "voices/*" --local-dir models/styletts2-multi
models/verbalizer-ct2/model.bin:
	$(HF) skypro1111/m2m100-ukr-verbalization-ct2 --revision ff98ecaacef2058527ed69f381cfe65d40a67333 --local-dir models/verbalizer-ct2
models/verbalizer-tokenizer/sentencepiece.bpe.model:
	$(HF) skypro1111/m2m100-ukr-verbalization --revision 87757c5b2b06b0c6546f8f65fc0f08a3b5c5051b --local-dir models/verbalizer-tokenizer --include "*.json" --include "sentencepiece.bpe.model"
models/omnivoice/model.safetensors:
	$(HF) k2-fsa/OmniVoice --revision c5fdb5ccb189668d56333f77ba2629f4cd7535f4 --local-dir models/omnivoice
models/higgs-tts-3/model.safetensors:
	$(HF) bosonai/higgs-tts-3-4b --revision 239f63fb7b02b1aa085f98d9efae5e35cc5523e8 --local-dir models/higgs-tts-3
