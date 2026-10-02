import streamlit as st
import streamlit.components.v1 as components
import os
import requests

# -----------------------------
# CONFIG
# -----------------------------

st.set_page_config(
    page_title="Gesture Naturalness Evaluation",
    page_icon="🎥",
    layout="wide"
)

NUM_VIDEOS = 12

# 12 videos:
# Instances 1-4 × 3 video types
VIDEO_PATHS = [
    "videos/random/instance_2.mp4",
    "videos/combined/instance_11.mp4",
    "videos/random/instance_3.mp4",
    "videos/random/instance_7.mp4",
    "videos/combined/instance_8.mp4",
    "videos/combined/instance_6.mp4",
    "videos/random/instance_4.mp4",
    "videos/combined/instance_10.mp4",
    "videos/random/instance_8.mp4",
    "videos/combined/instance_5.mp4",
    "videos/combined/instance_7.mp4",
    "videos/random/instance_5.mp4",
]

VIDEO_TYPES = [
    "random",    # Video 1
    "original",  # Video 2   
    "random",    # Video 3
    "random",    # Video 4
    "original",  # Video 5
    "original",  # Video 6
    "random",    # Video 7
    "original",  # Video 8
    "random",    # Video 9
    "original",  # Video 10
    "original",  # Video 11
    "random",    # Video 12
]

# -----------------------------
# GOOGLE FORM CONFIG
# -----------------------------

GOOGLE_FORM_ACTION_URL = (
    "https://docs.google.com/forms/d/e/"
    "1FAIpQLSevnERHGWWJ3WwqU8LfOpRGYHxOsD3-swiIZXkMKXho35B2wA/"
    "formResponse"
)

# IMPORTANT:
# Replace these entry IDs with the entry IDs from your NEW Google Form.
#
# You need:
# - participant name
# - naturalness for videos 1-12
# - synchrony for videos 1-12
# - comments for videos 1-12

ENTRY_MAP = {
    "participant_name": "entry.1060400637",

    "video1_naturalness": "entry.1906870714",
    "video1_synchrony": "entry.597971657",
    "video1_comment": "entry.255366240",

    "video2_naturalness": "entry.23650009",
    "video2_synchrony": "entry.433161484",
    "video2_comment": "entry.346418573",

    "video3_naturalness": "entry.821506150",
    "video3_synchrony": "entry.663324970",
    "video3_comment": "entry.831704361",

    "video4_naturalness": "entry.962931535",
    "video4_synchrony": "entry.479476259",
    "video4_comment": "entry.1283587253",

    "video5_naturalness": "entry.1994725445",
    "video5_synchrony": "entry.944911321",
    "video5_comment": "entry.796282885",

    "video6_naturalness": "entry.430771922",
    "video6_synchrony": "entry.46908906",
    "video6_comment": "entry.460488255",

    "video7_naturalness": "entry.797198952",
    "video7_synchrony": "entry.1491102938",
    "video7_comment": "entry.469709548",

    "video8_naturalness": "entry.1857287357",
    "video8_synchrony": "entry.32121396",
    "video8_comment": "entry.2031508538",

    "video9_naturalness": "entry.1425068461",
    "video9_synchrony": "entry.1696387806",
    "video9_comment": "entry.897374875",

    "video10_naturalness": "entry.1481659284",
    "video10_synchrony": "entry.268447108",
    "video10_comment": "entry.1195457340",

    "video11_naturalness": "entry.519884985",
    "video11_synchrony": "entry.550518812",
    "video11_comment": "entry.406724704",

    "video12_naturalness": "entry.647618947",
    "video12_synchrony": "entry.2073875244",
    "video12_comment": "entry.1264999937",
}


def submit_to_google_form(field_values: dict) -> bool:

    form_payload = {
        ENTRY_MAP[field]: value
        for field, value in field_values.items()
    }

    try:
        response = requests.post(
            GOOGLE_FORM_ACTION_URL,
            data=form_payload,
            timeout=10
        )

        return response.status_code == 200

    except requests.RequestException:
        return False


# -----------------------------
# SCROLL TO TOP
# -----------------------------

def scroll_to_top():

    components.html(
        """
        <script>
        setTimeout(() => {

            const main = window.parent.document.querySelector(
                '[data-testid="stMain"]'
            );

            if (main) {
                main.scrollTo({
                    top: 0,
                    behavior: 'instant'
                });
            }

        }, 100);
        </script>
        """,
        height=0,
    )


# -----------------------------
# SESSION STATE
# -----------------------------

if "page" not in st.session_state:
    st.session_state.page = 0

if "participant_name" not in st.session_state:
    st.session_state.participant_name = ""

if "responses" not in st.session_state:
    st.session_state.responses = {}

if "scroll_to_top" not in st.session_state:
    st.session_state.scroll_to_top = False


# -----------------------------
# PARTICIPANT NAME
# -----------------------------

if not st.session_state.participant_name:

    st.title("Gesture Naturalness Evaluation")

    st.write(
        "You will be shown 12 videos, one at a time. "
        "For each video, please rate the naturalness and synchrony "
        "of the gestures and optionally provide a comment."
    )

    participant_name = st.text_input(
        "Name",
        placeholder="Enter your name"
    )

    if st.button("Start Evaluation", type="primary"):

        if participant_name.strip() == "":
            st.warning("Please enter your name.")

        else:

            st.session_state.participant_name = participant_name.strip()

            st.rerun()

    st.stop()


# -----------------------------
# CURRENT VIDEO
# -----------------------------

video_index = st.session_state.page

# Scroll to top after moving to a new page
if st.session_state.scroll_to_top:

    scroll_to_top()

    st.session_state.scroll_to_top = False


# -----------------------------
# VIDEO PAGE
# -----------------------------

st.title(
    f"Video {video_index + 1} of {NUM_VIDEOS}"
)

st.write(
    "Watch the video carefully before providing your ratings."
)

st.divider()


video_path = VIDEO_PATHS[video_index]


# -----------------------------
# DISPLAY VIDEO
# -----------------------------

if os.path.exists(video_path):

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.video(video_path)

else:

    st.error(
        f"Video not found: {video_path}"
    )


st.divider()


# -----------------------------
# LIKERT SCALE
# -----------------------------

st.subheader("Your Evaluation")


NATURALNESS_OPTIONS = [
    "1 — Very unnatural",
    "2 — Somewhat unnatural",
    "3 — Neutral",
    "4 — Natural",
    "5 — Very natural"
]

SYNCHRONY_OPTIONS = [
    "1 — Very poorly synchronized",
    "2 — Poorly synchronized",
    "3 — Neutral",
    "4 — Well synchronized",
    "5 — Very well synchronized"
]


naturalness = st.radio(
    "Naturalness",
    NATURALNESS_OPTIONS,
    index=None,
    key=f"naturalness_{video_index}"
)


synchrony = st.radio(
    "Synchrony",
    SYNCHRONY_OPTIONS,
    index=None,
    key=f"synchrony_{video_index}"
)


comment = st.text_area(
    "Comments (optional)",
    placeholder="Enter any comments about the gestures...",
    key=f"comment_{video_index}"
)


# -----------------------------
# RECORD RESPONSE
# -----------------------------

def record_response():

    st.session_state.responses[video_index] = {

        "video_number": video_index + 1,

        "video_path": video_path,

        "video_type": VIDEO_TYPES[video_index],

        "naturalness": naturalness,

        "synchrony": synchrony,

        "comment": comment

    }


# -----------------------------
# NAVIGATION
# -----------------------------

if video_index < NUM_VIDEOS - 1:

    if st.button(
        "Next",
        type="primary"
    ):

        if naturalness is None or synchrony is None:

            st.warning(
                "Please provide ratings for both Naturalness and Synchrony."
            )

        else:

            record_response()

            st.session_state.page += 1

            st.session_state.scroll_to_top = True

            st.rerun()


else:

    if st.button(
        "Submit Evaluation",
        type="primary"
    ):

        if naturalness is None or synchrony is None:

            st.warning(
                "Please provide ratings for both Naturalness and Synchrony."
            )

        else:

            record_response()

            # -----------------------------
            # BUILD GOOGLE FORM PAYLOAD
            # -----------------------------

            field_values = {
                "participant_name":
                    st.session_state.participant_name
            }

            for i in range(NUM_VIDEOS):

                response = st.session_state.responses[i]

                field_values[
                    f"video{i + 1}_naturalness"
                ] = response["naturalness"]

                field_values[
                    f"video{i + 1}_synchrony"
                ] = response["synchrony"]

                field_values[
                    f"video{i + 1}_comment"
                ] = response["comment"]


            # -----------------------------
            # SUBMIT
            # -----------------------------

            success = submit_to_google_form(
                field_values
            )


            if success:

                st.success(
                    "Thank you! Your evaluation has been recorded."
                )

                st.balloons()

            else:

                st.error(
                    "Something went wrong submitting your evaluation. "
                    "Please check your internet connection and try again."
                )