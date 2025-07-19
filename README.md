# Face Swap Automation

This project automates the process of swapping faces between two images using the [DeepIMG AI Face Swap](https://deepimg.ai/ai-face-swap/) web service. It leverages Selenium to interact with the website, upload images, and download the result automatically.

## Features
- Uploads a source and target image to DeepIMG AI Face Swap
- Automates the face swap process via browser automation
- Downloads the swapped face image
- Handles errors and retries if the process fails

## Requirements
- Python 3.7+
- [seleniumbase](https://github.com/seleniumbase/SeleniumBase)
- Google Chrome (or compatible browser)

## Installation
1. Clone this repository or copy the files to your local machine.
2. Install dependencies:
   ```powershell
   pip install seleniumbase
   ```
3. Place your source and target images in the project directory as `ben.png` and `scarelet.jpg` (or modify the paths in `main.py`).

## Usage
Run the script with PowerShell or your preferred terminal:
```powershell
python main.py
```

The script will:
- Open the DeepIMG AI Face Swap website
- Upload `ben.png` (source face) and `scarelet.jpg` (target face)
- Start the face swap process
- Download the result (check the website or your browser's download folder)

## Output
Swapped images are typically downloaded to your browser's default download location. You may also find processed images in the `downloaded_files/` directory.

## Troubleshooting
- Ensure both image files exist in the project directory.
- If the script fails, check your internet connection and that Chrome is installed.
- For headless mode, set `headless=True` in `main.py`.

## License
This project is for educational and personal use only. Please respect the terms of service of DeepIMG AI and any other third-party services used.
