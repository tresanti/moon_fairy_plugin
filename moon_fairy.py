from cat.experimental.form import CatForm, form
from cat.experimental.form import CatFormState
from cat.mad_hatter.decorators import hook
from cat.mad_hatter.decorators import plugin

from cat.plugins.moon_fairy_plugin.email_service import send_smtp_email
from cat.plugins.moon_fairy_plugin.models import  EmailProps, EmptyProps
from cat.plugins.moon_fairy_plugin.settings import FairySettings

from typing import List
from langchain.schema import BaseMessage, HumanMessage, AIMessage

story_characters = 8000
human_message = None

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
def agent_fast_reply(fast_reply, cat):
    langchainfy_chat_history(cat)

    return fast_reply

@hook
def agent_prompt_instructions(instructions, cat):
    instructions += f"""\nRicorda il Formato di output e che la storia sia di almeno di {story_characters} caratteri"""
    return instructions


@hook
def before_cat_sends_message(final_output, cat):
    settings = cat.mad_hatter.get_plugin().load_settings()
    if not settings['use_smtp_email']:
        return final_output
    if 'FINE' in final_output.text:
        final_output.text += '\n\nSe vuoi ricevere la favole via mail, rispondi:\n - Invia mail oppure non inviare.'
    return final_output


@hook
def before_cat_recalls_episodic_memories(episodic_recall_config, cat):
    episodic_recall_config["k"] = 1

    return episodic_recall_config


@form  #
class EmailForm(CatForm):  #
    description = "inviare storia via mail"  #
    model_class = EmailProps  #
    start_examples = [  #
        "send Email",
        "invia mail"
    ]
    stop_examples = [  #
        'non inviare email',
        "not send",
        "not send email",
        "no send email"
    ]
    ask_confirm = True  #

    def submit(self, form_data):  #
        global human_message
       
        response = send_smtp_email('Ti insegno una favola.', str(human_message.content.split('FINE')[0] + 'FINE'), self.extract()['email'], self._cat)
        self._cat.working_memory.agent_input.chat_history = []
        return {
            "output": f"{response}"
        }

    def message(self):  #
        global human_message
        missing_fields: List[str] = self._missing_fields  #
        errors: List[str] = self._errors  #
        out: str = ''
        if human_message.content is None:
            self.check_exit_intent()
            out = 'Ho dimenticato lastoria, ricominciamo ti va?'
            return {
                "output": out
            }
        
        if len(errors) > 0:
            out += f'\nPuoi controllare perchè le informazioni che mi hai dato non sono valise:{errors}'

        if len(missing_fields) > 0:
             out += self._cat.llm('chiedi la mail per inviare la storia, si conciso chiedi e basta non dare conferme o altro devi semplicemente chiedere la mail in modo gentile e chiaro')
        
        if self._state == CatFormState.WAIT_CONFIRM:
            out += "\n Confermi l'invio?"

        return {
            "output": out
        }



def langchainfy_chat_history(self, latest_n: int = 10) :
    global human_message
    chat_history = self.working_memory.history[-latest_n:]
    langchain_chat_history = []
    for message in chat_history:
        if message["role"] != "Human" and 'class="fable"' in message["message"]:
            human_message = HumanMessage(message["message"])

    return langchain_chat_history


@plugin
def settings_model():
    return FairySettings
