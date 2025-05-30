
![image](https://github.com/user-attachments/assets/7de1254d-b078-401d-9390-f58a10ada536)

# 🧠 NeuroDocForge

[![Project Status](https://img.shields.io/badge/status-in%20development-yellow)](#)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#license)
[![Version](https://img.shields.io/badge/version-1.0-informational)](#)

**NeuroDocForge** is an AI-powered tool that automatically documents source code written in *any* programming language. It leverages state-of-the-art LLMs optimized with **OpenVINO™**, enabling fast, efficient inference on **CPU**, **GPU**, and **NPU** — even on local machines.

---

## ✨ Features

- 🔍 **Language-Agnostic**: Supports code in any programming language.
- ⚙️ **OpenVINO Optimization**: Runs efficiently across hardware architectures (CPU/GPU/NPU).
- 💬 **Chat Interface (Experimental)**: Early interaction model based on conversational prompts.
- 📄 **Code Understanding**: Extracts logic and generates function/class documentation automatically.
- ☁️ **Coming Soon**: Auto-processing upon file upload, no manual input required.

---

## 🚧 Roadmap

| Feature                             | Status        |
|-------------------------------------|---------------|
| Chat-based documentation (MVP)      | ✅ Complete    |
| File upload with auto-processing    | ✅ Complete    |
| UI improvements                     | ✅ Complete    |
| Version 1.0 release (public code)   | ✅ Complete    |

---

## 🧠 Powered By

- [OpenVINO™ Toolkit](https://www.intel.com/openvino)
- Modern open-weight LLMs
- Custom code parsing and generation pipelines

---

## 📦  Dependencies and Installation
```bash
# clone NeuroDocForge repo
$ git clone https://github.com/cabelo/NeuroDocForge/
$ cd NeuroDocForge

# create env
$ python -m venv .venv

# activate env
$ source .venv/bin/activate

# install dependent packages
$ pip install -r requirements.txt

# Convert openVINO model
$ optimum-cli export openvino --trust-remote-code --model meta-llama/Meta-Llama-3-8B-Instruct Meta-Llama-3-8B-Instruct-ov

# Run NeuroDocForge
python neurodocforge.py
```
---

## 📜 License

This project will be licensed under the **MIT License**.



## 🤝 Contributing

We welcome issues, feedback, and collaborators! Please stay tuned for contribution guidelines after the public release.

---

## 📬 Contact

Feel free to open an issue, comment in Discussions, or reach out if you'd like to collaborate.

> *“Because understanding code shouldn’t be harder than writing it.”*

Alessandro de Oliveira Faria (A.K.A. CABELO) - cabelo@opensuse.org

## 🎥 Demo Video

[![Watch the demo](https://img.youtube.com/vi/rB6FqQuwFVQ/hqdefault.jpg)](https://www.youtube.com/watch?v=rB6FqQuwFVQ)


