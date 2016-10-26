import os
import time
from slackclient import SlackClient
from chrisjones import ChrisJones

# constants
READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose

class SlackBot:
    def __init__(self, token, bot_id):
        self.bot_id = bot_id
        self.bot_tag = '<@' + bot_id + '>'
        self.client = SlackClient(token)
        self.controller = ChrisJones()

    def listen(self):
        if self.client.rtm_connect():
            print("StarterBot connected and running!")
            while True:
                command, channel = self.parse_slack_output(self.client.rtm_read())
                if command and channel:
                    self.handle_command(command, channel)
                    time.sleep(READ_WEBSOCKET_DELAY)
        else:
            print("Connection failed. Invalid Slack token or bot ID?")

    def handle_command(self, command, channel):
        """
            Receives commands directed at the bot and determines if they
            are valid commands. If so, then acts on the commands. If not,
            returns back what it needs for clarification.
        """
        response = self.controller.respond(command)
        self.client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

    def parse_slack_output(self, slack_rtm_output):
        """
            The Slack Real Time Messaging API is an events firehose.
            this parsing function returns None unless a message is
            directed at the Bot, based on its ID.
        """
        output_list = slack_rtm_output
        if output_list and len(output_list) > 0:
            for output in output_list:
                if output and 'text' in output and self.bot_tag in output['text']:
                    # return text after the @ mention, whitespace removed
                    return output['text'].split(self.bot_tag)[1].strip().lower(), output['channel']
        return None, None


if __name__ == "__main__":
    bot = SlackBot(os.environ.get('SLACK_BOT_TOKEN'), os.environ.get('SLACK_BOT_ID'))
    bot.listen()
