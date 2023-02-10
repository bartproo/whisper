import whisper
from flask import Flask, render_template, request, jsonify
import json
import os

# Initialize Flask application
app = Flask(__name__)


# Route to render the main HTML template
@app.route("/")
def index():
    return render_template("index.html")


# Route to handle image uploads
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Save audio clip temporarily
        audio_file = request.files['audio_file'].save("temp.wav")
        audio = whisper.load_audio("temp.wav")
        # Remove audio clip saved
        os.remove("temp.wav")
        model = whisper.load_model("base")
        audio = whisper.pad_or_trim(audio)

        # make log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(audio).to(model.device)

        # detect the spoken language
        _, probs = model.detect_language(mel)

        # decode the audio
        options = whisper.DecodingOptions(fp16=False)
        result = whisper.decode(model, mel, options)
        result = {'Result': result.text}
        # Serialize the results
        json_result = json.dumps(result)

        # Return the results as a JSON response
        return jsonify(json.loads(json_result))
    except Exception as e:
        return jsonify({"error": str(e)})


# Main method to run the application
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
