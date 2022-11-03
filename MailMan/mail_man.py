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
__version__ = "1.0.0"

"""


class MailMan:
    supported_msg_types = [
        "plain",
        "html"
    ]

    def __init__(
            self,
            sender_email: str,
            sender_password: str,
            recipients: list,
            message: str,
            msg_type: str,
            subject: str,
            attachments: list = None,
            encrypt_attachments: bool = False,
            encryption_password: str = None,
            smtp_server: str = "smtp.gmail.com",
            port: int = 465,
    ):

        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipients = recipients
        self.message = message
        self.msg_type = msg_type
        self.subject = subject
        self.attachments = attachments
        self.encrypt_attachments = encrypt_attachments
        self.encryption_password = encryption_password
        self.smtp_server = smtp_server
        self.port = port

        if msg_type not in self.supported_msg_types:
            raise TypeError("\033[91mUnsupported message type\033[0m")

    def __str__(self):

        return f"""\033[95mClass MailMan:\033[0m
\033[92mSender Email:\033[0m {self.sender_email},
\033[92mReceiver Email:\033[0m {self.recipients},
\033[92mMessage Type:\033[0m {self.msg_type},
\033[92mSubject:\033[0m {self.subject},
\033[92mAttachments:\033[0m {self.attachments if self.attachments else None},
\033[92mNo. of attachments:\033[0m {len(self.attachments) if self.attachments else None},
\033[92mEncrypt attachments:\033[0m {self.encrypt_attachments},
\033[92mSMTP server and Port:\033[0m {self.smtp_server, self.port}
        """

    def send_mail(self):
        import smtplib
        import ssl
        import os
        from pyzipper import AESZipFile, ZIP_LZMA, WZ_AES
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from pathlib import Path

        sender_email = self.sender_email
        sender_password = self.sender_password
        recipients = self.recipients

        msg = MIMEMultipart()
        msg["Subject"] = self.subject
        msg["From"] = sender_email
        msg["To"] = ', '.join(recipients)

        msg.attach(MIMEText(self.message, self.msg_type))

        if self.attachments:
            for i in range(len(self.attachments)):
                file_path = self.attachments[i]
                if "/" in file_path:
                    file_name = file_path.split('/')[-1]
                elif "\\" in file_path:
                    file_name = file_path.split('\\')[-1]
                else:
                    print("Invalid File-Path")
                    raise TypeError
                # Open file in binary mode
                with open(file_path, "rb") as attachment:
                    if self.encrypt_attachments:
                        if self.attachments[i].lower().endswith('.pdf'):
                            from PyPDF2 import PdfReader, PdfWriter
                            # Create reader and writer object
                            reader = PdfReader(file_name)
                            writer = PdfWriter()

                            # Add all pages to the writer
                            for page in reader.pages:
                                writer.add_page(page)

                            # Add a password to the new PDF
                            writer.encrypt(self.encryption_password)

                            # Save the new PDF to a file
                            is_dir = os.path.isdir("MailMan_Encrypted_Files")
                            if not is_dir:
                                os.mkdir("MailMan_Encrypted_Files")

                            path = Path(__file__).parent / f"./MailMan_Encrypted_Files/Encrypted_{file_name}"
                            with open(path, "wb+") as f:
                                writer.write(f)

                            with open(path, "rb") as f:
                                self.attach_file(f, f"Encrypted_{file_name}", msg)

                        else:
                            # Save the new PDF to a file
                            is_dir = os.path.isdir("MailMan_Encrypted_Files")
                            if not is_dir:
                                os.mkdir("MailMan_Encrypted_Files")
                            non_pdf_filename = f"{file_name.split('.')[0]}.zip"
                            path = Path(__file__).parent / f"./MailMan_Encrypted_Files/encrypted_{non_pdf_filename}"
                            secret_password = self.encryption_password.encode('utf-8')

                            with AESZipFile(path,
                                            'w',
                                            compression=ZIP_LZMA,
                                            encryption=WZ_AES) as zf:
                                zf.setpassword(secret_password)
                                zf.write(file_path, file_name)
                            with open(path, "rb") as f:
                                self.attach_file(f, f"Encrypted_{non_pdf_filename}", msg)
                    else:
                        self.attach_file(attachment, file_name, msg)

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
            server.login(sender_email, sender_password)
            server.sendmail(
                sender_email, recipients, msg.as_string()
            )

    @staticmethod
    def attach_file(opened_file_object, file_name: str, msg_object):
        from email.mime.base import MIMEBase
        from email import encoders

        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(opened_file_object.read())
        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {file_name}",
        )

        # Add attachment to message and convert message to string
        msg_object.attach(part)
