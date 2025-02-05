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


class PyCourier:
    supported_msg_types = (
        "plain",
        "html"
    )

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
            encrypted_files_path: str = None,
            smtp_server: str = "smtp.gmail.com",
            port: int = 465,
    ):

        self.sender_email = sender_email
        self.sender_password = sender_password
        self.recipients = recipients
        self.message = message
        self.msg_type = msg_type
        self.subject = subject
        self.encrypted_files_path = encrypted_files_path
        self.attachments = attachments
        self.encrypt_attachments = encrypt_attachments
        self.encryption_password = encryption_password
        self.smtp_server = smtp_server
        self.port = port

        if msg_type not in self.supported_msg_types:
            raise TypeError("\033[91mUnsupported message type\033[0m")

    def __str__(self):

        return f"""\033[95mClass PyCourier:\033[0m
\033[92mSender Email:\033[0m {self.sender_email},
\033[92mReceiver Email:\033[0m {self.recipients},
\033[92mMessage Type:\033[0m {self.msg_type},
\033[92mSubject:\033[0m {self.subject},
\033[92mAttachments:\033[0m {self.attachments if self.attachments else None},
\033[92mNo. of attachments:\033[0m {len(self.attachments) if self.attachments else None},
\033[92mEncrypt attachments:\033[0m {self.encrypt_attachments},
\033[92mSMTP server and Port:\033[0m {self.smtp_server, self.port}
        """

    def encrypt_attachment(self, file_path: str) -> Path:
        """
        Creates encrypted files directory if it doesn't exist.

        Treats .pdf files differently, encrypts them using PyPDF2
        Rest of the files are zipped and encrypted with AES using
        PyZipper.

        :param file_path: Takes a string i.e. the path of file to be encrypted
        :return: pathlib.Path object of the encrypted file
        """

        if not self.encrypted_files_path:
            # Providing a directory to store encrypted files is required.
            raise ValueError("Expected an encrypted file directory (str format) path got None")

        # path/to/file.extension = > file.extension i.e. The final path component.
        # Gets the name of the file to be encrypted.
        file_name = Path(file_path).name

        # path/to/somewhere/PyCourier_Encrypted_Files
        # Appends `PyCourier_Encrypted_Files` to `encrypted_files_path`.
        # This is where a copy of encrypted files is stored.
        dir_path = Path(self.encrypted_files_path, "PyCourier_Encrypted_Files")

        if not dir_path.is_dir():
            # Will create the directory including its parents.
            # similar to mkdir -p
            dir_path.mkdir(parents=True)

        if file_name.endswith(".pdf"):

            from pypdf import PdfReader, PdfWriter
            # Create reader and writer object
            reader = PdfReader(file_path)
            writer = PdfWriter(clone_from=reader)

            # Add a password to the new PDF
            writer.encrypt(self.encryption_password, algorithm="AES-256-R5")

            # Save the new PDF to a file
            path = Path(dir_path, f"Encrypted_{file_name}")

            with Path.open(path, "wb+") as f:
                writer.write(f)

            return path

        else:
            from pyzipper import AESZipFile, ZIP_LZMA, WZ_AES

            # .stem returns the final path component, minus its last suffix.
            non_pdf_filename = f"{Path(file_path).stem}.zip"
            path = Path(dir_path, f"Encrypted_{non_pdf_filename}")
            secret_password = self.encryption_password.encode('utf-8')

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
        import smtplib
        import ssl

        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        sender_email = self.sender_email
        sender_password = self.sender_password
        recipients = self.recipients

        msg = MIMEMultipart()
        msg["Subject"] = self.subject
        msg["From"] = sender_email
        msg["To"] = ', '.join(recipients)

        msg.attach(MIMEText(self.message, self.msg_type))

        if self.attachments:
            if self.encrypt_attachments:
                for file_path in self.attachments:
                    enc_path = self.encrypt_attachment(file_path)
                    self.attach_file(enc_path, msg)
            else:
                from pathlib import Path
                for file_path in self.attachments:
                    self.attach_file(Path(file_path), msg)

        context = ssl.create_default_context()

        try:
            with smtplib.SMTP_SSL(self.smtp_server, self.port, context=context) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipients, msg.as_string())

        except smtplib.SMTPException as e:
            raise RuntimeError("Failed to send email.") from e
