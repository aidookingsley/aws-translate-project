# 🌍 AWS File & Text Translator

This project is a **capstone project** for my AWS Cloud Engineering course. It demonstrates how to integrate AWS services with a modern Streamlit application to perform text translations in multiple languages.

Users can input text manually or upload files to be translated automatically using AWS Translate, with results stored securely in S3. The app also provides downloadable results and a session-based translation history.

---

## ✨ Features

✅ **Text & File Translation**  
- Enter text directly or upload `.txt` / `.json` files.  
- Auto-detection of source language.  
- Support for multiple target languages.  

✅ **AWS Integration**  
- **AWS Translate** for machine translation.  
- **Amazon S3** for storing inputs and outputs.  

✅ **User-Friendly Interface**  
- Clean, modern Streamlit UI.  
- Original and translated text displayed side by side.  
- Download buttons for easy retrieval.  
- Session-based translation history.  

✅ **Extensibility**  
- Ready for enhancements like authentication, more languages, and persistent user histories.

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit**
- **Boto3 (AWS SDK for Python)**
- **Amazon Translate**
- **Amazon S3**

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- An AWS account with:
  - S3 buckets created:
    - `resilient-translate-input-bucket`
    - `resilient-translate-output-bucket`
  - AWS Translate permissions
- AWS credentials configured (e.g., via `~/.aws/credentials`)

### Installation

1. **Clone the repository:**

   ```
   git clone https://github.com/your-username/aws-translate-project.git
   cd aws-translate-project

2. **Create and activate a virtual environment:**
    ```
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install dependencies:**
    ```
    pip install -r requirements.txt

4. **Set your AWS credentials if not already configured:**
    ```
    export AWS_ACCESS_KEY_ID=your-access-key
    export AWS_SECRET_ACCESS_KEY=your-secret-key
    export AWS_DEFAULT_REGION=your-region

5. **Run the app:**
    ```
    streamlit run streamlit_app.py

6. **🧭 Usage:**
    ```
    - Launch the app in your browser.

    - Enter text or upload a file.

    - Select the target language.

    - Click Translate.

    - View the original and translated text side by side.

    - Download results or start a new translation.

    - Review your translation history within the session.

7. **📂 Project Structure**
    ```
    aws-translate-project/
    ├── streamlit_app.py      # Main Streamlit app
    ├── requirements.txt      # Python dependencies
    ├── README.md             # Project documentation
    └── main.tf               # IaC module

8. **🎓 Learning Objectives**
    ```
    This project demonstrates:

        - Building cloud-native applications using AWS services.

        - Integrating AWS Translate and Amazon S3 via Boto3.

        - Using Streamlit for rapid web app development.

        - Managing state and session history in a web app.

        - Implementing clean UI and user experience best practices.

9. **📝 Future Improvements**
    ```
    - Persistent user authentication and saved translation history.

    - Support for more file formats (e.g., PDF, DOCX).

    - Usage analytics and logs stored in DynamoDB.

    - Multilingual UI.

    - Dockerization for easier deployment.


10. **📄 License**
    ```
    This project is for educational purposes. Feel free to adapt or reuse the code with attribution.


11. **Capstone Project Group Members**
    ```
    Virginia Ansah
    Emmanuel Ghartey
    Yasir Sani Mohammed
    Yvette Effah-Ntiamoah
    Rabbi Agyei
    James Hada
    Kingsley Mensah Aidoo



