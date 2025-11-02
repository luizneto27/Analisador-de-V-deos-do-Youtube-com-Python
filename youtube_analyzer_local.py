import os
import tempfile
import subprocess
from pathlib import Path
from fpdf import FPDF
import whisper
from transformers import pipeline

def download_audio(url, out_dir):
    output_path = os.path.join(out_dir, "%(title)s.%(ext)s")
    cmd = ["yt-dlp", "-f", "bestaudio", "-o", output_path, url]
    subprocess.run(cmd, check=True)
    files = list(Path(out_dir).glob("*"))
    return str(max(files, key=lambda f: f.stat().st_mtime))

def transcribe_audio(file_path):
    model = whisper.load_model("base")  # use "small" or "medium" for melhor precisão
    print("Transcrevendo áudio...")
    result = model.transcribe(file_path)
    return result["text"]

def summarize_text(text):
    print("Gerando resumo...")
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    summary = ""
    for chunk in chunks:
        summary_piece = summarizer(chunk, max_length=120, min_length=40, do_sample=False)[0]['summary_text']
        summary += summary_piece + " "
    return summary.strip()

def create_pdf(summary, transcript, output_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Resumo do Vídeo do YouTube", ln=True)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, f"Resumo:\n{summary}\n\nTranscrição:\n{transcript}")
    pdf.output(output_path)
    print(f"PDF salvo em: {output_path}")

def main(url):
    with tempfile.TemporaryDirectory() as tmp:
        audio_file = download_audio(url, tmp)
        transcript = transcribe_audio(audio_file)
        summary = summarize_text(transcript)
        create_pdf(summary, transcript, "relatorio.pdf")

if __name__ == "__main__":
    link = input("Insira o link do vídeo do YouTube: ")
    main(link)
