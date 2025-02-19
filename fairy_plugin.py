from cat.experimental.form import CatForm, form
from cat.experimental.form import CatFormState
from cat.mad_hatter.decorators import hook
from cat.mad_hatter.decorators import plugin

from cat.plugins.fairy_moon.email_service import send_smtp_email
from cat.plugins.fairy_moon.models import Fable, EmailProps, EmptyProps
from cat.plugins.fairy_moon.settings import FairySettings

story_characters = 7000


@hook()
def agent_prompt_prefix(prefix, cat):
    prefix = f"""
                        Il tuo nome è [Luna]. Sei un'intelligenza artificiale che crea favole creative e coinvolgenti per bambini partendo da un insegnamento che si vuole dare. Rispondi sempre in Italiano.\n
                    #Regole di comportamento:\n
                     - Puoi rispondere solo a domande su chi sei e cosa puoi fare. [Puoi inviare email]\n
                     - Se la domanda è fuori contesto o irrilevante, rispondi semplicemente presentandoti.\n
                     - Se richiesto, scrivi una favola per bambini con una morale chiara e una lezione utile.\n
                    #Linee guida per le favole:\n
                     - Titolo: Ogni favola deve iniziare con un titolo.\n
                     - Struttura: Dopo il titolo, inizia subito la storia.\n
                     - Linguaggio: Usa un linguaggio semplice e adatto ai bambini.\n
                     - Coinvolgimento: Crea una trama avvincente con personaggi memorabili.\n
                     - Morale: Concludi sempre con una morale chiara, ma senza essere eccessivamente didascalico.\n
                    #Formato di output:\n
                     - La favola deve essere composta da almeno {story_characters} caratteri.\n
                     - Utilizza i seguenti tag per strutturare la risposta:\n
                       <h1> Titolo </h1>>
                        <div class="fable"> Favola </div>
                        <div class="moral"> Morale </div>\n
                     -Ogni favola deve terminare con la parola "<span>FINE</span>".\n
                    #Esempio di risposta:\n
                     <h1>>Il piccolo drago e la luce della luna</h1>  
                        <div class="fable">C'era una volta un piccolo drago che aveva paura del buio... [SVILUPPO DELLA STORIA di 2000 worlds]... Alla fine, capì che la sua paura poteva essere superata con il coraggio e l'amicizia. </div>  
                        <div class="moral">La paura si affronta meglio con il supporto di chi ci vuole bene. </div> <br> <span>FINE</span> \n
                    #Note:\n
                     - Adatta la complessità del racconto in base all'età del pubblico.\n
                     - La morale deve emergere naturalmente dalla storia.\n'
                                           """
    return prefix


@hook
def agent_prompt_instructions(instructions, cat):
    instructions += f"""\nRicorda il Formato di output e che la storia sia di almeno di {story_characters} caratteri"""
    return instructions


@hook
def before_cat_sends_message(final_output, cat):
    settings = cat.mad_hatter.get_plugin().load_settings()
    if not settings['use_smtp_email']:
        return final_output
    if 'class="fable"' in final_output.text:
        Fable.value = final_output.text
    if 'FINE' in final_output.text:
        final_output.text += '\n\nSe vuoi ricevere la favole via mail, rispondi:\n - Invia mail oppure non inviare.'
    return final_output


@hook
def before_cat_recalls_episodic_memories(episodic_recall_config, cat):
    episodic_recall_config["k"] = 3

    return episodic_recall_config


@form  #
class EmailForm(CatForm):  #
    description = "inviare storia via mail"  #
    model_class = EmailProps  #
    start_examples = [  #
        "send Email",
        "invia mail"
        "send email",
        "send Email",
        "Send email",
        "Send mail",
        "Send Mail",
        "send Mail",
        "send mail"
    ]
    stop_examples = [  #
        "no",
        "not send",
        "not send email",
        "no send email"
    ]
    ask_confirm = True  #

    def submit(self, form_data):  #
        return {
            "output": f"{send_smtp_email('Ti insegno una favola.', str(Fable.value), self.extract()['email'], self._cat)}"
        }

    def message(self):  #
        missing_fields: List[str] = self._missing_fields  #
        errors: List[str] = self._errors  #
        out: str = ''
        if len(errors) > 0:
            out += f'\nPuoi controllare perchè le informazioni che mi hai dato non sono valise:{errors}'
        if len(missing_fields) > 0:
            out += f"""\n\nHo bisogno di un email dove pote inviare la storia."""
        if self._state == CatFormState.WAIT_CONFIRM:
            out += "\n Confermi l'invio?"
        return {
            "output": out
        }

    def model_getter(self):
        settings = self._cat.mad_hatter.get_plugin().load_settings()
        if not settings['use_smtp_email']:
            self.model_class = EmptyProps
        else:
            self.model_class = EmailProps

        return self.model_class


@plugin
def settings_model():
    return FairySettings
