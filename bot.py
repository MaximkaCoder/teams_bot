import smtplib
import os
from email.mime.text import MIMEText

from botbuilder.core import ActivityHandler, MessageFactory, TurnContext
from botbuilder.schema import CardAction, ActionTypes, SuggestedActions

main_menu = True
helpdesk = False
help = False
other = False
is_1c = False
mail = False

MAIN_DIR = os.getcwd()

class EchoBot(ActivityHandler):
    async def on_members_added_activity(self, members_added, turn_context: TurnContext):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                from_property = turn_context.activity.from_property
                await turn_context.send_activity(f"Здравствуйте {from_property.name}! Email ({from_property.aad_object_id}) Чем я могу помочь?")
                await self._send_suggested_actions(turn_context)


    async def on_message_activity(self, turn_context: TurnContext):
        global helpdesk
        if not helpdesk:
            text = turn_context.activity.text.lower()
            response_text = self._process_input(text)

            await turn_context.send_activity(MessageFactory.text(response_text))
            return await self._send_suggested_actions(turn_context)
        else:
            if turn_context.activity.text.lower() != "отмена":
                email = "m.smal@vitmark.com"
                helpdesk_email = "helpdesk@vitmark.com"

                message = MIMEText(turn_context.activity.text)
                message["Subject"] = turn_context.activity.text
                server = smtplib.SMTP('smtp.vitmark.com', 25)
                server.ehlo()
                server.starttls()
                server.sendmail(email, helpdesk_email, message.as_string())
                await turn_context.send_activity("Заявка отправлена!")
                server.quit()
                await self._send_suggested_actions(turn_context)
            else:
                await turn_context.send_activity("Отмена отправки!")
                await self._send_suggested_actions(turn_context)

            helpdesk = False

    def send_instruction_from_file(self, file_name):
        file = open(MAIN_DIR + r"/instructions/" + file_name + ".txt", "r", encoding="UTF-8")
        data = file.readlines()
        file.close()
        text = ""

        for i in data:
            text += i + "\n"
        return text
    

    def _process_input(self, text: str):
        global main_menu, help, helpdesk, other, is_1c, mail

        file = open(MAIN_DIR + r"/buttons/buttons_help.txt", "r", encoding="UTF-8")
        if help:
            file = open(MAIN_DIR + r"/buttons/buttons_other.txt", "r", encoding="UTF-8")
        elif other:
            file = open(MAIN_DIR + r"/buttons/buttons_help.txt", "r", encoding="UTF-8")
        data = file.readlines()
        file.close()

        try:
            for i in data:
                subject = i.split("-")

                if text == "инструкции":
                    help = True
                    main_menu = False
                    return "Выберите нужную инструкцию!"
                elif text == "назад":
                    if other or mail or is_1c:
                        other = False
                        mail = False
                        is_1c = False
                        help = True
                    elif help:
                        help = False
                        main_menu = True
                    else:
                        main_menu = True
                        other = False
                        help = True
                        is_1c = True
                    return
                elif text == "helpdesk":
                    helpdesk = True
                    main_menu = False
                    return "Напишите сообщение. Для отмены - напишите 'отмена'"
                elif text == "прочее":
                    other = True
                    help = False
                    main_menu = False
                elif text == "1c":
                    is_1c = True
                    main_menu = False
                    help = False
                elif text == "почта":
                    mail = True
                    main_menu = False
                    help = False
                elif text == subject[0].lower():
                    return self.send_instruction_from_file(subject[1].replace("\n", ""))
                else:
                    pass
        except Exception:
            pass
        return
    
    def make_buttons(self, data):
        actions = []

        for i in data:
            subject = i.split("-")
            actions += [
                CardAction(
                    title=subject[0],
                    type=ActionTypes.im_back,
                    value=subject[0],
                    image_alt_text=subject[0],
                ),
            ]
        
        return actions


    async def _send_suggested_actions(self, turn_context: TurnContext):
        reply = MessageFactory.text("")

        if main_menu:
            reply.suggested_actions = SuggestedActions(
                actions=[
                    CardAction(
                        title="ИНСТРУКЦИИ",
                        type=ActionTypes.im_back,
                        value="ИНСТРУКЦИИ",
                        image_alt_text="ИНСТРУКЦИИ",
                    ),
                    CardAction(
                        title="HELPDESK",
                        type=ActionTypes.im_back,
                        value="HELPDESK",
                        image_alt_text="HELPDESK",
                    ),
                ]
            )
        elif help:
            file = open(MAIN_DIR + r"/buttons/buttons_other.txt", "r", encoding="UTF-8")
            data = file.readlines()
            file.close()
            reply.suggested_actions = SuggestedActions(actions=self.make_buttons(data))
        elif other:
            file = open(MAIN_DIR + r"/buttons/buttons_help.txt", "r", encoding="UTF-8")
            data = file.readlines()
            file.close()
            reply.suggested_actions = SuggestedActions(actions=self.make_buttons(data))
        elif is_1c:
            file = open(MAIN_DIR + r"/buttons/buttons_1c.txt", "r", encoding="UTF-8")
            data = file.readlines()
            file.close()
            reply.suggested_actions = SuggestedActions(actions=self.make_buttons(data))
        elif mail:
            file = open(MAIN_DIR + r"/buttons/buttons_mail.txt", "r", encoding="UTF-8")
            data = file.readlines()
            file.close()
            reply.suggested_actions = SuggestedActions(actions=self.make_buttons(data))

        return await turn_context.send_activity(reply)