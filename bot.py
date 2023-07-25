import smtplib
import os
from email.mime.text import MIMEText

from botbuilder.core import ActivityHandler, MessageFactory, TurnContext
from botbuilder.schema import CardAction, ActionTypes, SuggestedActions

help = False
helpdesk = False

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
        global help, helpdesk
        file = open(MAIN_DIR + r"/buttons/buttons_help.txt", "r", encoding="UTF-8")
        data = file.readlines()
        file.close()
        try:
            for i in data:
                subject = i.split("-")

                if text == "инструкции":
                    help = True
                    return "Выберите нужную инструкцию!"
                elif text == "назад":
                    help = False
                    return "Главное меню"
                elif text == "helpdesk":
                    helpdesk = True
                    return "Напишите сообщение. Для отмены - напишите 'отмена'"
                elif text == subject[0].lower():
                    return self.send_instruction_from_file(subject[1].replace("\n", ""))
        except Exception:
            pass
        return


    async def _send_suggested_actions(self, turn_context: TurnContext):
        reply = MessageFactory.text("")

        if not help:
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
        else:
            file = open(MAIN_DIR + r"/buttons/buttons_help.txt", "r", encoding="UTF-8")
            data = file.readlines()
            file.close()
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

            reply.suggested_actions = SuggestedActions(actions=actions)

        return await turn_context.send_activity(reply)