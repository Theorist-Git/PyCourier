"""
Copyright (C) 2022-2023 Mayank Vats
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
__Description__ = "PyCourier: A simple, reliable and fast email package for python"
__version__ = "1.2.0"

"""

from pathlib import Path
from os import getenv
from tempfile import TemporaryDirectory

class PyCourier:
    supported_msg_types = (
        "plain",
        "html"
    )

    def __init__(
            self,
            sender_email_env: str,
            sender_password_env: str,
            recipients: list,
            message: str,
            msg_type: str,
            subject: str,
            attachments: list = None,
            encrypt_attachments: bool = False,
            encryption_password_env: str = None,
            smtp_server: str = "smtp.gmail.com",
            port: int = 465,
    ):

        self.sender_email_env = sender_email_env
        self.sender_password_env = sender_password_env
        self.recipients = recipients
        self.message = message
        self.msg_type = msg_type
        self.subject = subject
        self.attachments = attachments
        self.encrypt_attachments = encrypt_attachments
        self.encryption_password_env = encryption_password_env
        self.smtp_server = smtp_server
        self.port = port

        if msg_type not in self.supported_msg_types:
            raise TypeError("Unsupported message type")

        if not sender_email_env:
            raise ValueError("Missing sender email environment variable")

        if not sender_password_env:
            raise ValueError("\Missing sender password environment variable")

        if encrypt_attachments and not encryption_password_env:
            raise ValueError("Missing encryption password environment variable")

    def __str__(self):

        return f"""\033[95mClass PyCourier:\033[0m
\033[92mSender Email:\033[0m {self.sender_email_env},
\033[92mReceiver Email:\033[0m {self.recipients},
\033[92mMessage Type:\033[0m {self.msg_type},
\033[92mSubject:\033[0m {self.subject},
\033[92mAttachments:\033[0m {self.attachments if self.attachments else None},
\033[92mNo. of attachments:\033[0m {len(self.attachments) if self.attachments else None},
\033[92mEncrypt attachments:\033[0m {self.encrypt_attachments},
\033[92mSMTP server and Port:\033[0m {self.smtp_server, self.port}
        """

    @staticmethod
    def _get_env_var(var: str):
        result = getenv(var)

        if not result:
            raise RuntimeError(f"Environment variable {var} not set")

        return result

    def encrypt_attachment(self, file_path: Path, temp_dir: Path) -> Path:
        """
        Creates encrypted files directory if it doesn't exist.

        Treats .pdf files differently, encrypts them using pypdf
        Rest of the files are zipped and encrypted with AES using
        PyZipper.

        :param file_path: Takes a string i.e. the path of file to be encrypted
        :param temp_dir: Takes a string i.e. the path of temp directory to store encrypted files
        :return: pathlib.Path object of the encrypted file
        """

        # path/to/file.extension = > file.extension i.e. The final path component.
        # Gets the name of the file to be encrypted.
        file_name = file_path.name

        if file_name.lower().endswith(".pdf"):

            from pypdf import PdfReader, PdfWriter
            # Create reader and writer object
            reader = PdfReader(file_path)
            writer = PdfWriter(clone_from=reader)

            # Add a password to the new PDF
            writer.encrypt(self._get_env_var(self.encryption_password_env), algorithm="AES-256-R5")

            # Save the new PDF to a file
            path = Path(temp_dir, f"Encrypted_{file_name}")

            with Path.open(path, "wb+") as f:
                writer.write(f)

            return path

        else:
            from pyzipper import AESZipFile, ZIP_LZMA, WZ_AES

            # .stem returns the final path component, minus its last suffix.
            non_pdf_filename = f"{file_path.name}.zip"
            path = Path(temp_dir, f"Encrypted_{non_pdf_filename}")
            secret_password = self._get_env_var(self.encryption_password_env).encode('utf-8')

            with AESZipFile(path,
                            'w',
                            compression=ZIP_LZMA,
                            encryption=WZ_AES) as zf:

                zf.setpassword(secret_password)
                zf.write(file_path, file_name)

            return path

    @staticmethod
    def attach_file(file_path: Path, msg_object) -> None:
        from email.mime.base import MIMEBase
        from email import encoders

        file_name = file_path.name

        with open(file_path, "rb") as f:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            # Encode file in ASCII characters to send by email
            encoders.encode_base64(part)

            # Add header as key/value pair to attachment part
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {file_name}",
            )

            # Add attachment to message and convert message to string
            msg_object.attach(part)

    def send_courier(self) -> None:
        from smtplib import SMTP_SSL, SMTPException
        from ssl import create_default_context

        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        sender_email = self._get_env_var(self.sender_email_env)
        sender_password = self._get_env_var(self.sender_password_env)

        recipients = self.recipients

        msg = MIMEMultipart()
        msg["Subject"] = self.subject
        msg["From"] = sender_email
        msg["To"] = ', '.join(recipients)

        msg.attach(MIMEText(self.message, self.msg_type))

        with TemporaryDirectory() as temp_dir:
            if self.attachments:
                for file_path in self.attachments:
                    if self.encrypt_attachments:
                        file_path = self.encrypt_attachment(Path(file_path), Path(temp_dir))

                    self.attach_file(Path(file_path), msg)

        context = create_default_context()

        try:
            with SMTP_SSL(self.smtp_server, self.port, context=context) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipients, msg.as_string())

        except SMTPException as e:
            raise RuntimeError("Failed to send email.") from e
