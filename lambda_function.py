from gettext import translation
from http import client
from urllib import response
import json
from turtle import pu
from typing import Text
from unittest import result
import boto3
import logging
from botocore.exceptions import ClientError
from lark import logger
from datetime import datetime
from regex import B


# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# Initialize AWS clients
s3 = boto3.client('s3')
translate = boto3.client('translate')
comprehend = boto3.client('comprehend')
cloudwatch = boto3.client('cloudwatch')

# Constants
INPUT_BUCKET = "resilient-translate-input-bucket"
OUTPUT_BUCKET = "resilient-translate-output-bucket"


def publish_metric(metric_name, value, unit='Count'):
    try:
        cloudwatch.put_metric_data(
            Namespace='AWS/Translate',
            MetricData=[{
                'MetricName': metric_name,
                'Dimensions': [
                    {'Name': 'Function', 'Value': 'LanguageTranslator'}
                ],
                'value': value,
                'Unit': unit
            }]
        )
    except Exception as e:
        logger.error(f"Cloudwatch metric error: {e}")



def lambda_handler(event, context):
    try:
        # Validate S3 event
        if not event.get('Records') or len(event['Records']) == 0:
            raise ValueError("No S3 records found in event")
        
        record = event['Records'][0]
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        # Verify input bucket
        if bucket != INPUT_BUCKET:
            raise ValueError(f"Invalid bucket source: {bucket}. Expected: {INPUT_BUCKET}")

        # Get file from S3
        try:
            file = s3.get_object(Bucket=bucket, Key=key)
            data = json.loads(file['Body'].read().decode('utf-8'))
        except ClientError as e:
            logger.error(f"Error getting file from S3: {e}")
            raise

        # Validate input JSON
        required_fields = ['text', 'target_lang']
        if not all(field in data for field in required_fields):
            raise ValueError(f"Missing required fields. Expected: {required_fields}")
        
        # Auto-detect language if not provided
        source_lang = data.get('source_lang')
        if not source_lang:
            try:
                detected_lang = comprehend.detect_dominant_language(
                    Text=data['text']
                )['Languages'][0]['LanguageCode']
                logger.info(f"Detected language: {detected_lang}")
            except ClientError as e:
                logger.error(f"Comprehend error: {e}")
                detected_lang = 'auto'   # This is to Fallback to AWS auto-detection

        # Translate
        try:
            translated = translate.translate_text(
                Text=data['text'],
                SourceLanguageCode=detected_lang,
                TargetLanguageCode=data['target_lang']
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'TextSizeLimitExceededException':
                logger.error("Text exceeds 5000 bytes limit for translation")
                raise ValueError("Text too long (max 5000 bytes)")
            raise

            
        
        # Prepare output
        output = {
            'original_text': data['text'],
            'translated_text': translated['TranslatedText'],
            'source_lang': detected_lang,
            'target_lang': data['target_lang'],
            'timestamp': datetime.now().isoformat()
        }

        # Track metrics
        char_count = len(data['text'])
        publish_metric('CharactersTranslated', char_count)
        publish_metric(f"{detected_lang.upper()}_to_{data['target_lang'].upper()}", 1)

        # Save to output OUTPUT bucket
        try:
            s3.put_object(
                Bucket=OUTPUT_BUCKET,
                Key=f"translations/{key.split('/')[-1]}",
                Body=json.dumps(output),
                ContentType='application/json',
                ACL='bucket-owner-full-control'
            )
        except ClientError as e:
            logger.error(f"S3 PutObject error: {e}")
            raise

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Translation successful',
                'output_location': f"s3://{OUTPUT_BUCKET}/translations/{key.split('/')[-1]}",
            })
        }
    
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'Error processing request',
                'error': str(e)
            })
        }
# This code is a Lambda function that processes S3 events to translate text using AWS Translate and Comprehend.
# It validates the input, detects the source language if not provided, translates the text,
# and uploads the translated text back to S3. It handles errors gracefully and logs them for debugging.
# The function expects the S3 event to contain a JSON file with 'text' and 'target_lang' fields.
# It also includes error handling for common issues like missing fields, S3 access errors, and translation limits.
# Note: Ensure that the Lambda function has the necessary IAM permissions to access S3, Translate, and Comprehend services.