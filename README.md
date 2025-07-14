# Lambda Joiner λ

![Lambda Joiner Demo](https://i.imgur.com/your_demo_link.gif) 
<!-- It's highly recommended to record a short GIF of the app and replace the link above -->

A powerful and feature-rich file joiner built with Python and PyQt5. This tool is designed for educational purposes and security research, allowing you to combine multiple executable files into a single, seamless payload.

---

### ⚠️ Disclaimer: For Educational Use Only ⚠️

This software is intended for educational purposes and ethical security research only. The author is **not responsible** for any malicious use of this program. Creating and distributing malware is illegal and unethical. By using this software, you agree to take full responsibility for your actions. **Use it responsibly.**

---

### ✨ Features

* **Dual Payload Support**: Combine up to two files into a single executable.
* **🔒 XOR Encryption**: Payloads are encrypted with a random XOR key to reduce static detection.
* **🎭 Masquerading**: Change the final executable's icon to disguise it as another application.
* **🕵️ Evasion & Obfuscation**:
    * **Anti-Debugging**: Includes a check to see if a debugger is present.
    * **File Pumping**: Increase the file size to evade some sandbox size restrictions.
    * **UPX Packing**: Optionally pack the final executable with UPX for further obfuscation.
* **🚀 Advanced Execution**:
    * **Process Injection**: Inject the first payload directly into a running process (e.g., `explorer.exe`).
    * **UAC Bypass**: A technique to attempt running a payload with higher privileges without a UAC prompt.
    * **Hidden Launch**: Run payloads silently in the background.
* **🎬 Launch Behavior**:
    * **Custom MessageBox**: Display a fake error or information message upon launch.
    * **Self-Destruct**: The final executable can delete itself after running the payloads.
    * **File Hiding**: Automatically apply the "Hidden" attribute to the file after launch.
* **🌐 Multi-Language GUI**: Modern user interface available in English, Ukrainian, and Russian.

---

### 🛠️ Setup & Installation

To run this project, you'll need Python 3 and the following dependencies.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your_username/lambda-joiner.git](https://github.com/your_username/lambda-joiner.git)
    cd lambda-joiner
    ```

2.  **Install the required libraries:**
    ```bash
    pip install -r requirements.txt
    ```
    Your `requirements.txt` file should contain:
    ```
    PyQt5
    colorama
    playsound
    ```

3.  **Required Tools:**
    The application relies on a few external tools that **must be placed in a `bin` subfolder** within the project directory:
    * `g++.exe` (from a MinGW distribution) for compiling the C++ stub.
    * `upx.exe` (optional, for packing).
    * `rcedit-x64.exe` (for setting the icon).

    Your project structure should look like this:
    ```
    lambda-joiner/
    ├── bin/
    │   ├── g++.exe
    │   ├── rcedit-x64.exe
    │   └── upx.exe
    ├── sounds/
    │   ├── tada.mp3
    │   └── fail.mp3
    ├── main.py
    └── ...
    ```

---

### 🚀 How to Use

1.  Launch the application by running the Python script: `python main.py`.
2.  Select your primary payload (`First Payload`). This is required.
3.  Optionally, select a secondary payload.
4.  Configure the various options in the GUI to your needs (injection, self-destruct, icon, etc.).
5.  Choose an output path and filename for your final executable.
6.  Click **Create λ-Build** and check the execution log for progress!

---

### 🤝 Contributing

Contributions are welcome! If you have ideas for new features or find bugs, feel free to fork the repository and submit a pull request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

---

### 📄 License

This project is distributed under the MIT License. See the `LICENSE` file for more information.

---

