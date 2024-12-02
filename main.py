# %pip install requests openai
import requests
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

print("Hello World")

# Load environment variables from the config.env file
load_dotenv("config.env")
os.environ["OPENAI_API_KEY"] = os.getenv("dictate_key")
BLAND_AI_API_KEY = os.getenv("bland_key")
OPENAI_API_KEY = os.getenv("open_ai_key")
BLAND_AI_BASE_URL = "https://api.bland.ai/v1/calls"


# openai.api_key = OPENAI_API_KEY
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),  # This is the default and can be omitted
)


def initiate_call_with_blandai(
    phone_number, task, voice_id, reference_no, submission_date
):
    """
    Initiates a phone call using Bland.ai.
    """
    url = f"{BLAND_AI_BASE_URL}"
    headers = {
        "Authorization": f"{BLAND_AI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "phone_number": phone_number,
        "task": task,
        "answered_by_enabled": True,
        "reduce_latency": True,
        "voice_id": voice_id,
        "wait_for_greeting": True,
        "first_sentence": f"Hello, I'm calling on behalf of xxxxxxxx Health, to inquire about the status of the Medical appeal. Would you be able to assist me with this? ",
        "record": True,
        # "webhook": "<string>",
        "voice_settings": {"stability": 0.85, "similarity": 0.6, "speed": 0.8},
        # "max_duration": 123,
        "amd": False,
        "interruption_threshold": 45,
        "request_data": {
            "reference_no": reference_no,
            "submission_date": submission_date,
        },
    }
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        response_data = response.json()
        call_id = response_data.get("call_id")
        return response.json(), call_id
    else:
        return None


def generate_call_script(reference_no, submission_date):
    """
    Generates a continuation of the conversation using the OpenAI chat model,
    avoiding direct references to the AI nature of the call.
    """
    introduction = f"""This is a call from xxxxxx  Health regarding a recent medical appeal submission. We are following up on the status of the appeal with reference number {reference_no} submitted on {submission_date}.Would you be able to help?"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful and knowledgeable assistent confirming the status of the medical appeals submitted to the insurance payers",
            },
            {"role": "user", "content": introduction},
        ],
        temperature=0.7,
        max_tokens=300,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )

    return response.choices[0].message["content"]


def generate_call_script(reference_no, submission_date):
    introduction = f"""This is a call from xxxxxx Health regarding a recent medical appeal submission. We are following up on the status of the appeal with reference number {reference_no} submitted on {submission_date}. Would you be able to help?"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": introduction},
        ],
        max_tokens=500,
        temperature=0.7,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
    )
    return response.choices[0].message.content


def save_conversation(conversation, filename="conversation.txt"):
    """
    Saves the conversation to a text file.
    """
    with open(filename, "w") as file:
        file.write(conversation)
        print(f"Conversation saved to {filename}")


def get_call_transcript(call_id, BLAND_AI_API_KEY):
    """
    Retrieves the transcript of a phone call using the Bland.ai API.
    """

    call_id = call_id
    url = "https://api.bland.ai/v1/calls/{call_id}/correct"

    # headers = {"authorization": f'BLAND_AI_API_KEY}'}
    headers = {
        "Authorization": f"{BLAND_AI_API_KEY}",
        "Content-Type": "application/json",
    }
    response = requests.request("GET", url, headers=headers)

    print(response.text)

    if response.status_code == 200:
        return response.text  # Assuming the API returns the transcript in the response
    else:
        print(f"Failed to retrieve transcript. Status code: {response.status_code}")
        return None


# Example usage
def main():
    reference_no = "REF12345"
    submission_date = "January 15th 2024"
    phone_number = "+919930168658"
    task = "On behalf of xxxxxx Health Inquire about medical appeal status"
    voice_id = 1  # Assume a specific voice ID is chosen

    # Generate the call script
    # Initialize conversation log
    conversation_log = ""

    # Generate the call script
    call_script = generate_call_script(reference_no, submission_date)
    print("Generated Call Script:", call_script)
    conversation_log += f"Generated Script:\n{call_script}\n\n"

    # Initiate the call
    call_response, call_id = initiate_call_with_blandai(
        phone_number, task, voice_id, reference_no, submission_date
    )
    if call_response:
        print("Call initiated successfully. Response:", call_response)
        conversation_log += f"Call Response:\n{json.dumps(call_response, indent=2)}\n\n"

        # Retrieve transcript after the call is completed
        transcript_response = get_call_transcript(call_id, BLAND_AI_API_KEY)
        if transcript_response:
            print("Call Transcript:", transcript_response)
            conversation_log += f"Call Transcript:\n{transcript_response}\n\n"
        else:
            print("Failed to retrieve transcript.")
            conversation_log += "Failed to retrieve transcript.\n\n"
    else:
        print("Failed to initiate call.")
        conversation_log += "Failed to initiate call.\n\n"

    # Save the entire conversation log after the call is finished
    save_conversation(conversation_log)


if __name__ == "__main__":
    main()
