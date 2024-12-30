import boto3

def synthesize_speech(text, voice_id='Joanna', output_format='mp3', output_file='output.mp3', region_name='us-west-2'):
    # Initialize a session using Amazon Polly
    polly_client = boto3.Session().client('polly', region_name=region_name)

    # Request speech synthesis
    response = polly_client.synthesize_speech(
        Text=text,
        OutputFormat=output_format,
        VoiceId=voice_id
    )

    # Save the audio stream returned by Amazon Polly to a file
    with open(output_file, 'wb') as file:
        file.write(response['AudioStream'].read())

if __name__ == "__main__":
    text_to_synthesize = "Hello, this is a sample text to be synthesized using Amazon Polly."
    synthesize_speech(text_to_synthesize)