"""
Copyright (C) 2022 Mayank Vats
See license.txt

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License v3
along with this program.  If not, see <https://www.gnu.org/licenses/>.

__author__ = "Mayank Vats"
__email__ = "dev-theorist.e5xna@simplelogin.com"
__Description__ = "MailMan: A simple, reliable and fast email package for python"
__version__ = "0.0.1alpha"

"""


class MailMain:
    supported_msg_types = [
        "plain",
        "html"
    ]

    def __init__(
            self,
            sender_email: str,
            sender_password: str,
            receiver_email: str,
            message: str,
            msg_type: str,
            subject: str,
            attachments: list = None
    ):

        self.sender_email = sender_email
        self.sender_password = sender_password
        self.receiver_email = receiver_email
        self.message = message
        self.msg_type = msg_type
        self.subject = subject
        self.attachments = attachments

        if msg_type not in self.supported_msg_types:
            raise TypeError("\033[91mUnsupported message type\033[0m")

    def __str__(self):

        return f"""\033[95mClass MailMan:\033[0m
\033[92mSender Email:\033[0m {self.sender_email},
\033[92mReceiver Email:\033[0m {self.receiver_email},
\033[92mMessage Type:\033[0m {self.msg_type},
\033[92mSubject:\033[0m {self.subject}
        """

    def send_mail(self):
        import smtplib
        import ssl
        from email import encoders
        from email.mime.base import MIMEBase
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        sender_email = self.sender_email
        sender_password = self.sender_password
        receiver_email = self.receiver_email

        msg = MIMEMultipart()
        msg["Subject"] = self.subject
        msg["From"] = sender_email
        msg["To"] = receiver_email

        msg.attach(MIMEText(self.message, self.msg_type))

        if self.attachments:
            for i in range(len(self.attachments)):
                file_path = self.attachments[i]
                file_name = file_path.split('\\')[-1]
                # Open file in binary mode
                with open(file_path, "rb") as attachment:
                    # Add file as application/octet-stream
                    # Email client can usually download this automatically as attachment
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())

                # Encode file in ASCII characters to send by email
                encoders.encode_base64(part)

                # Add header as key/value pair to attachment part
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {file_name}",
                )

                # Add attachment to message and convert message to string
                msg.attach(part)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)
            server.sendmail(
                sender_email, receiver_email, msg.as_string()
            )
