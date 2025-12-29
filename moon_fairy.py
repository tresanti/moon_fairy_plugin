from typing import List
from cat.experimental.form import CatForm, form, CatFormState
from cat.mad_hatter.decorators import hook, plugin
from cat.plugins.moon_fairy_plugin.email_service import send_smtp_email
from cat.plugins.moon_fairy_plugin.models import EmailProps
from cat.plugins.moon_fairy_plugin.settings import FairySettings

STORY_CHARACTERS = 8000
FAIRY_STORAGE = {}

@hook
def agent_prompt_prefix(prefix, cat):
    # Definizione dell'identità e delle regole di output
    prefix = f"""
        Il tuo nome è [Luna]. Sei un'intelligenza artificiale che crea favole creative e coinvolgenti per bambini partendo da un insegnamento che si vuole dare. Rispondi sempre in Italiano.

        # Regole di comportamento:
        - Puoi rispondere solo a domande su chi sei e cosa puoi fare. [Puoi inviare email]
        - Se la domanda è fuori contesto o irrilevante, rispondi semplicemente presentandoti.
        - Se richiesto, scrivi una favola per bambini con una morale chiara e una lezione utile.

        # Linee guida per le favole:
        - Titolo: Ogni favola deve iniziare con un titolo.
        - Struttura: Dopo il titolo, inizia subito la storia.
        - Linguaggio: Usa un linguaggio semplice e adatto ai bambini.
        - Coinvolgimento: Crea una trama avvincente con personaggi memorabili.
        - Morale: Concludi sempre con una morale chiara, ma senza essere eccessivamente didascalico.

        # Formato di output:
        - La favola deve essere composta da almeno {STORY_CHARACTERS} caratteri.
        - Utilizza i seguenti tag HTML per strutturare la risposta:
          <h1> Titolo </h1>
          <div class="fable"> Favola </div>
          <div class="moral"> Morale </div>
        - Ogni favola deve terminare obbligatoriamente con la parola "<span>FINE</span>".

        # Esempio di risposta:
        <h1>Il piccolo drago e la luce della luna</h1>  
        <div class="fable">C'era una volta un piccolo drago che aveva paura del buio... [SVILUPPO DELLA STORIA]...</div>  
        <div class="moral">La paura si affronta meglio con il supporto di chi ci vuole bene.</div><br><span>FINE</span>
    """
    return prefix


@hook
def agent_prompt_instructions(instructions, cat):
    instructions += f"\nRicorda di rispettare il formato di output e che la storia deve essere lunga almeno {STORY_CHARACTERS} caratteri."
    return instructions


@hook
def before_cat_sends_message(final_output, cat):
    settings = cat.mad_hatter.get_plugin().load_settings()

    if 'class="fable"' in final_output.text or 'FINE' in final_output.text:
        user_id = cat.user_id
        FAIRY_STORAGE[user_id] = final_output.text

        if settings.get('use_smtp_email', False):
            final_output.text += '\n\n---\n✨ *Se vuoi ricevere questa favola via mail, scrivi "Invia mail".*'

    return final_output


@form
class EmailForm(CatForm):
    description = "Procedura per l'invio della favola via email"
    model_class = EmailProps
    start_examples = ["invia mail", "mandami la storia per email", "spedisci favola"]
    stop_examples = ["non inviare", "annulla invio", "no email"]
    ask_confirm = True

    def submit(self, form_data):
        user_id = self._cat.user_id
        fable_content = FAIRY_STORAGE.get(user_id)

        if not fable_content:
            return {"output": "Mi dispiace, non ho trovato favole recenti da inviare. Chiedimi di scriverne una!"}

        clean_text = fable_content.split('FINE')[0] + 'FINE'

        try:
            response = send_smtp_email(
                subject='Una favola per te da Luna 🌙',
                body=clean_text,
                to_email=self.extract()['email'],
                cat=self._cat
            )

            return {"output": f"Email inviata con successo! {response}"}
        except Exception as e:
            return {"output": f"Errore durante l'invio: {str(e)}"}

    def message(self):
        user_id = self._cat.user_id
        fable_content = FAIRY_STORAGE.get(user_id)

        if not fable_content:
            self.check_exit_intent()
            return {"output": "Non ho ancora generato una favola per te. Vuoi che ne inventiamo una insieme adesso?"}

        if self._errors:
            return {"output": f"L'indirizzo email non sembra corretto. Puoi scriverlo di nuovo?"}

        if "email" in self._missing_fields:
            return {"output": "A quale indirizzo email desideri ricevere la favola?"}

        if self._state == CatFormState.WAIT_CONFIRM:
            email = self.extract().get('email')
            return {"output": f"Sto per inviare la favola a {email}. Confermi?"}

        return None


@plugin
def settings_model():
    return FairySettings