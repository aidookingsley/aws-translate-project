import streamlit as st
import boto3
import json
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Fetch credentials from environment
REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
access_key = os.getenv("AWS_ACCESS_KEY_ID")
secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS clients Initialization
try:
    s3 = boto3.client('s3',
                      region_name=REGION,
                     aws_access_key_id=access_key,
                     aws_secret_access_key=secret_key)
    translate = boto3.client('translate',
                              region_name=REGION,
                              aws_access_key_id=access_key,
                              aws_secret_access_key=secret_key)
except Exception as e:
    st.error(f"AWS client initialization failed: {str(e)}")
    st.stop()

# Constants
INPUT_BUCKET = "resilient-translate-input-bucket"
OUTPUT_BUCKET = "resilient-translate-output-bucket"

# Session state initialization
if 'translation_done' not in st.session_state:
    st.session_state.translation_done = False
if 'translation_result' not in st.session_state:
    st.session_state.translation_result = None
if 'original_text' not in st.session_state:
    st.session_state.original_text = ""
if 'translation_history' not in st.session_state:
    st.session_state.translation_history = []
if 'detected_language' not in st.session_state:
    st.session_state.detected_language = ""

# Custom CSS
st.markdown("""
<style>
    .textbox-container {
        position: relative;
        margin-bottom: 1rem;
        border: 1px solid #e0e0e0;
        border-radius: 6px;
        padding: 10px;
    }
    .attach-icon {
        position: absolute;
        bottom: 10px;
        right: 10px;
        background: white;
        border-radius: 50%;
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        z-index: 2;
        border: 1px solid #e0e0e0;
    }
    .attach-icon:hover {
        background: #f5f5f5;
    }
    .hide-uploader div[data-testid="stFileUploader"] > label {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🌍 AWS File & Text Translator")

# Main Translation View
if not st.session_state.translation_done:
    # Input section
    with st.container():
        st.markdown('<div class="textbox-container">', unsafe_allow_html=True)
        user_text = st.text_area(
            "Enter text",
            height=150,
            placeholder="Type or attach file...",
            label_visibility="collapsed",
            key="text_input"
        )
        uploaded_file = st.file_uploader(
            " ",
            type=["json", "txt"],
            label_visibility="collapsed",
            key="file_upload"
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # Language selection
    target_lang = st.selectbox(
        "Target Language",
        ["es", "fr", "de", "en", "zh", "ja", "ru", "sw"],
        index=0
    )

    if st.button("Translate", type="primary"):
        if not user_text and not uploaded_file:
            st.warning("Please enter text or upload a file!")
        else:
            try:
                text = ""
                # Handle uploaded file
                if uploaded_file:
                    try:
                        file_content = uploaded_file.read().decode("utf-8")
                        try:
                            data = json.loads(file_content)
                            text = data.get("text", "")
                            target_lang = data.get("target_lang", target_lang)
                            is_json = True
                        except json.JSONDecodeError:
                            text = file_content
                            is_json = False

                        uploaded_file.seek(0)
                        s3.upload_fileobj(
                            Fileobj=uploaded_file,
                            Bucket=INPUT_BUCKET,
                            Key=f"uploads/{datetime.now().timestamp()}.{'json' if is_json else 'txt'}",
                            ExtraArgs={
                                'ContentType': 'application/json' if is_json else 'text/plain',
                                'ACL': 'bucket-owner-full-control'
                            }
                        )
                    except Exception as file_error:
                        st.error(f"File processing error: {str(file_error)}")
                        logger.error(f"File error: {file_error}")
                        raise

                # Handle plain text input
                elif user_text:
                    text = user_text
                    s3.put_object(
                        Bucket=INPUT_BUCKET,
                        Key=f"text-inputs/{datetime.now().timestamp()}.json",
                        Body=json.dumps({
                            "text": text,
                            "target_lang": target_lang,
                            "source": "text-area"
                        }),
                        ContentType='application/json',
                        ACL='bucket-owner-full-control'
                    )

                # Perform translation
                if text:
                    result = translate.translate_text(
                        Text=text,
                        SourceLanguageCode="auto",
                        TargetLanguageCode=target_lang
                    )

                    detected_lang = result.get("SourceLanguageCode", "unknown")

                    st.session_state.translation_result = result["TranslatedText"]
                    st.session_state.original_text = text
                    st.session_state.detected_language = detected_lang
                    st.session_state.translation_done = True

                    
                    # Save result to S3
                    output_data = {
                        "original": text,
                        "translated": result["TranslatedText"],
                        "target_lang": target_lang,
                        "timestamp": datetime.now().isoformat()
                    }

                    s3.put_object(
                        Bucket=OUTPUT_BUCKET,
                        Key=f"translations/{datetime.now().timestamp()}.json",
                        Body=json.dumps(output_data),
                        ContentType='application/json',
                        ACL='bucket-owner-full-control'
                    )

            except Exception as e:
                st.error(f"Translation failed: {str(e)}")
                logger.error(f"Translation error: {e}", exc_info=True)

# Show translation result and reset button
else:
    st.subheader("Translation Completed")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Original Text:**")
        st.text_area(
            label="Original Text",
            value=st.session_state.original_text,
            height=200,
            disabled=True
        )

    with col2:
        st.markdown("**Translated Text:**")
        st.text_area(
            label="Translated Text",
            value=st.session_state.translation_result,
            height=200,
            disabled=True
        )
    st.markdown(f"**Detected Source Language:** `{st.session_state.detected_language}`")

    st.success("✓ Translation saved to S3!")

    # New Translation button
    if st.button("New Translation", type="primary"):
        st.session_state.translation_done = False
        st.session_state.translation_result = None
        st.session_state.original_text = ""
        st.session_state.detected_language = ""
        st.rerun()

    # Translation history
    if st.session_state.translation_history:
        st.subheader("Translation History")
        for i, item in enumerate(reversed(st.session_state.translation_history), 1):
            with st.expander(f"Translation #{i} ({item['timestamp']})"):
                st.markdown(f"**Detected Language:** `{item['detected_language']}`")
                st.markdown(f"**Target Language:** `{item['target_language']}`")
                st.markdown("**Original Text:**")
                st.code(item['original_text'], language="text")
                st.markdown("**Translated Text:**")
                st.code(item['translated_text'], language="text")

