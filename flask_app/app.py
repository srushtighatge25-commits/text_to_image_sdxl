import io, base64, os
import torch
from flask import Flask, render_template, request, jsonify
from diffusers import DiffusionPipeline

app = Flask(__name__)

MODEL_PATH = os.environ.get("MODEL_PATH", "./local_model/sdxl_base")  # folder saved from Colab
device = "cuda" if torch.cuda.is_available() else "cpu"

print("Loading model from", MODEL_PATH, "on", device)
pipe = DiffusionPipeline.from_pretrained(
    MODEL_PATH,
    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    use_safetensors=True,
)
pipe = pipe.to(device)
print("Model ready.")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(force=True)
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"error": "Please enter a prompt."}), 400

    steps = max(5, min(int(data.get("steps", 30)), 60))
    guidance = max(1.0, min(float(data.get("guidance", 7.5)), 20.0))
    negative = (data.get("negative") or "").strip() or None

    try:
        with torch.inference_mode():
            image = pipe(
                prompt=prompt,
                negative_prompt=negative,
                num_inference_steps=steps,
                guidance_scale=guidance,
            ).images[0]
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
        return jsonify({"image": "data:image/png;base64," + b64})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
