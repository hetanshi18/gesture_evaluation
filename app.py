import streamlit as st
import os
import random
import requests

# -----------------------------
# CONFIG
# -----------------------------

st.set_page_config(
    page_title="Gesture Naturalness Evaluation",
    page_icon="🎥",
    layout="wide"
)

NUM_INSTANCES = 5

# Folder names for each video type - videos inside are named instance_1.mp4 ... instance_5.mp4
VIDEO_TYPES = ["combined", "pitch_accent", "vowel_onset"]

# -----------------------------
# GOOGLE FORM CONFIG
# -----------------------------

GOOGLE_FORM_ACTION_URL = (
    "https://docs.google.com/forms/d/e/"
    "1FAIpQLSf22dSrCJQCWT60earT-edACr4XhrjsospZMZ1ojWV3f7tP0Q/formResponse"
)

# Maps our internal field names to the Google Form's entry IDs
ENTRY_MAP = {
    "participant_name": "entry.1118831540",

    "instance1_video_A": "entry.1827752055",
    "instance1_video_B": "entry.889265544",
    "instance1_video_C": "entry.1039151512",
    "instance1_choice": "entry.1554871476",
    "instance1_rating": "entry.262817648",

    "instance2_video_A": "entry.951390741",
    "instance2_video_B": "entry.752887444",
    "instance2_video_C": "entry.1325547455",
    "instance2_choice": "entry.545058623",
    "instance2_rating": "entry.1121958934",

    "instance3_video_A": "entry.171459414",
    "instance3_video_B": "entry.2023343460",
    "instance3_video_C": "entry.1040537878",
    "instance3_choice": "entry.1495693522",
    "instance3_rating": "entry.1072339683",

    "instance4_video_A": "entry.386911549",
    "instance4_video_B": "entry.454990217",
    "instance4_video_C": "entry.1541273725",
    "instance4_choice": "entry.954021614",
    "instance4_rating": "entry.1970346573",

    "instance5_video_A": "entry.162603200",
    "instance5_video_B": "entry.829034950",
    "instance5_video_C": "entry.317139658",
    "instance5_choice": "entry.475643716",
    "instance5_rating": "entry.1720762791",
}


def submit_to_google_form(field_values: dict) -> bool:
    """
    Sends field_values (internal field name -> value) to the Google Form.
    Returns True if the request appears to have succeeded.
    """
    form_payload = {
        ENTRY_MAP[field]: value
        for field, value in field_values.items()
    }

    try:
        response = requests.post(GOOGLE_FORM_ACTION_URL, data=form_payload, timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False


# -----------------------------
# SESSION STATE
# -----------------------------

if "page" not in st.session_state:
    st.session_state.page = 1

if "responses" not in st.session_state:
    st.session_state.responses = {}

if "participant_name" not in st.session_state:
    st.session_state.participant_name = ""

if "orderings" not in st.session_state:
    # Precompute a randomized A/B/C -> type mapping for each instance so that
    # order is shuffled per instance and doesn't bias the participant.
    st.session_state.orderings = {}
    for inst in range(1, NUM_INSTANCES + 1):
        shuffled = VIDEO_TYPES.copy()
        random.shuffle(shuffled)
        st.session_state.orderings[inst] = shuffled


# -----------------------------
# PARTICIPANT NAME
# -----------------------------

if not st.session_state.participant_name:

    st.title("Gesture Naturalness Evaluation")

    st.write(
        "You will be shown five sets of three videos. "
        "For each set, please watch all three videos and select "
        "the video in which the gestures appear most natural."
    )

    participant_name = st.text_input(
        "Name",
        placeholder="Enter your name"
    )

    if st.button("Start Evaluation"):

        if participant_name.strip() == "":
            st.warning("Please enter your name.")

        else:
            st.session_state.participant_name = participant_name
            st.rerun()

    st.stop()


# -----------------------------
# CURRENT INSTANCE
# -----------------------------

instance = st.session_state.page

st.title(f"Instance {instance} of {NUM_INSTANCES}")

st.write(
    "Watch all three videos before making your choice."
)

st.divider()


# -----------------------------
# VIDEO PATHS
# -----------------------------

# Randomized mapping of label -> video type for this instance
order = st.session_state.orderings[instance]

video_paths = [
    f"videos/{video_type}/instance_{instance}.mp4"
    for video_type in order
]


# -----------------------------
# DISPLAY VIDEOS
# -----------------------------

cols = st.columns(3)

for i, video_path in enumerate(video_paths):

    with cols[i]:

        st.subheader(f"Video {chr(65+i)}")

        if os.path.exists(video_path):
            st.video(video_path)
        else:
            st.error(f"Video not found: {video_path}")


st.divider()


# -----------------------------
# EVALUATION
# -----------------------------

st.subheader("Your evaluation")

labels = [f"Video {chr(65+i)}" for i in range(len(order))]

choice = st.radio(
    "Which video has the most natural gesture timing and placement?",
    labels,
    key=f"choice_{instance}"
)

rating = st.radio(
    "How natural did the gestures appear overall?",
    [
        "1 — Very unnatural",
        "2 — Somewhat unnatural",
        "3 — Neutral",
        "4 — Natural",
        "5 — Very natural"
    ],
    key=f"rating_{instance}"
)


# -----------------------------
# NEXT / SUBMIT
# -----------------------------

def record_response():
    # Map the chosen label (e.g. "Video A") back to the underlying video type
    chosen_index = labels.index(choice)
    chosen_type = order[chosen_index]

    st.session_state.responses[instance] = {
        "choice_label": choice,
        "choice_type": chosen_type,
        "order": order,
        "rating": rating
    }


if instance < NUM_INSTANCES:

    if st.button("Next", type="primary"):

        record_response()
        st.session_state.page += 1
        st.rerun()

else:

    if st.button("Submit Evaluation", type="primary"):

        record_response()

        # -----------------------------
        # Build the field values for this participant
        # -----------------------------

        field_values = {"participant_name": st.session_state.participant_name}

        for inst in range(1, NUM_INSTANCES + 1):
            response = st.session_state.responses[inst]
            order_for_inst = response["order"]

            field_values[f"instance{inst}_video_A"] = order_for_inst[0]
            field_values[f"instance{inst}_video_B"] = order_for_inst[1]
            field_values[f"instance{inst}_video_C"] = order_for_inst[2]
            field_values[f"instance{inst}_choice"] = response["choice_type"]
            field_values[f"instance{inst}_rating"] = response["rating"]

        # Submit to Google Form (backed by a Google Sheet)
        success = submit_to_google_form(field_values)

        if success:
            st.success(
                "Thank you! Your evaluation has been recorded."
            )
        else:
            st.error(
                "Something went wrong submitting your evaluation. "
                "Please check your internet connection and try again."
            )