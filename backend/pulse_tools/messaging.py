import vobject
import pywhatkit
from pulse_ear.speech_handler import speak

def get_vcf_contacts(file_path):
    """
    Parses a .vcf file and returns a dictionary of contacts.
    """
    contacts = {}
    try:
        with open(file_path, 'r') as f:
            for card in vobject.readComponents(f):
                if hasattr(card, 'fn'):
                    name = card.fn.value
                    phone = None
                    if hasattr(card, 'tel'):
                        phone = card.tel.value
                    contacts[name.lower()] = {
                        'name': name,
                        'phone': phone,
                        'email': None
                    }
        return contacts
    except Exception as e:
        print(f"Error parsing VCF file: {e}")
        return {}

def find_contact(name):
    contacts = get_vcf_contacts("contacts.vcf")
    contacts = {**contacts}
    return contacts.get(name.lower())

def send_whatsapp_message(contact_name, message):
    if not contact_name or not message:
        speak("I'm missing some information. Who should I message and what should it say?")
        return

    contact = find_contact(contact_name)
    if contact and contact['phone']:
        full_message = f"{message}\n**Sent by Pulse AI**"
        try:
            pywhatkit.sendwhatmsg_instantly(contact['phone'], full_message)
            speak("Message sent successfully!")
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            speak("Sorry, I couldn't send the message.")
    else:
        speak(f"Sorry, I couldn't find {contact_name} in your contacts.")
