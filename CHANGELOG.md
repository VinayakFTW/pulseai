## v1.1.1

**1 - Bug Fixes**
- removal of code that wasn't working and causing the model to crash (placing a call on your mobile using Pulse)<br>
might be added later as a feature in later updates.

## v1.1.0

**1 - Functionality Addition**
- **Added a whatsapp messaging functionality**: the assistant can now send whatsapp messages to your contacts using a vcf file for extracting contact details.

## v1.0.0

**1 - Major Overhaul**
- **Integrated a local LLM (Llama 3.2)**: The assistant now uses a local large language model for more intelligent and context-aware responses, replacing the previous hardcoded conversational responses. This allows for more natural and flexible conversations.
- **New Speech-to-Text Pipeline**: Replaced the previous speech recognition with a local Whisper-based ASR pipeline for improved accuracy and performance.
- **Conversation History**: The assistant now saves and loads conversation history, allowing for more contextually relevant interactions over time.
- **Wake Word**: The wake word has been changed to "Pulse" for a more branded experience.
- **Updated Dependencies**: Added new dependencies to support the new features, including `torch`, `transformers`, `sounddevice`, and `python-dotenv`.

**2 - Bug Fixes**
- **Improved Error Handling**: Added more robust error handling for the LLM and speech-to-text pipelines to prevent crashes and provide better user feedback.

## v0.5.0

**1 - Reformatted code**<br>
  *pressed many keys(a bit too many) here and there to make the code look a bit beautiful(and better)*<br>

**2 - Updated the play_song feature**<br>
  *Now you can play songs on spotify using your voice*<br>

## v0.2.0

**1 - Reformatted code**<br>
  *pressed a few keys here and there to make the code look a bit beautiful*<br>
**2 - Added play songs feature properly**<br>
  *now you can just say "play <song_name>" to play any song you want. If you find inaccuracy try includig the name of the artist along with song name*<br>
**3 - Added a wake up word**<br>
  *whenever you ask the AI to do something it will pause and let you do your work till you ask it anything again after using the wake up words "wake up" or "resume".*<br>

## v0.1.7

**1 - Bug Fixes**<br>
    similar bug to google fall back, when no input would be understood it would ask if we wanted to search an empty string on google<br>
    .Pretty simple fix just added a handler to tell the code if the query was handled or not.<br>

## v0.1.5

**1 - Bug fixes**<br>
    Fallback Google Search: *Added a fallback mechanism for unrecognized commands, asking the user if they’d like to search the query on Google.*<br>
    greet() function logic flaw: *Fixed a a flaw in the logic for greet() where the user would only be greeted during 6am - 12am*<br>

**2 - Reformatted code**<br>
  *pressed a few keys here and there to make the code look a bit beautiful*<br>