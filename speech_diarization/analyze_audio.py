import json
from os import getenv, path as ospath
from pathlib import Path

import torch
from dotenv import load_dotenv
from pyannote.audio import Pipeline
from pyannote.audio.pipelines.utils.hook import ProgressHook

from decorators.all_decorators import record_performance

load_dotenv()
script_dir = ospath.dirname(ospath.realpath(__file__))
parent_dir = ospath.join(script_dir, ospath.pardir)
model_path = ospath.normpath(ospath.join(parent_dir, "models"))


@record_performance
def analyze_audio(input_file="", output_file=""):
    # print(torch.cuda.is_available())
    # return

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-3.1",
        # "models/speaker-diarization-3.1",
        use_auth_token=getenv("TOKEN_HUGGING_FACE")
    )

    # send pipeline to GPU (when available)
    pipeline.to(torch.device("cuda"))

    # apply pretrained pipeline
    with ProgressHook() as hook:
        diarization = pipeline(input_file, num_speakers=4, hook=hook)

    results = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        result = {
            "start": round(turn.start, 1),
            "stop": round(turn.end, 1),
            "speaker": f"speaker_{speaker}"
        }
        results.append(result)
        print(f"start={result['start']}s stop={result['stop']}s {result['speaker']}")

    output_file = Path(output_file).with_suffix('.json')
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)

    print(f"Results saved to {output_file}.json")
