"""arXiv accounts classic models."""

from typing import Any, NewType

from sqlalchemy import BigInteger, Column, DateTime, Enum, \
    ForeignKey, Index, Integer, SmallInteger, String, Text, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TapirUser(Base):  # type: ignore
    """Legacy table that is a foreign key dependency of TapirSession."""

    __tablename__ = 'tapir_users'

    user_id = Column(Integer, primary_key=True)
    first_name = Column(String(50), index=True)
    last_name = Column(String(50), index=True)
    suffix_name = Column(String(50))
    share_first_name = Column(Integer, nullable=False, server_default=text("'1'"))
    share_last_name = Column(Integer, nullable=False, server_default=text("'1'"))
    email = Column(String(255), nullable=False, unique=True, server_default=text("''"))
    share_email = Column(Integer, nullable=False, server_default=text("'8'"))
    email_bouncing = Column(Integer, nullable=False, server_default=text("'0'"))
    policy_class = Column(
        ForeignKey('tapir_policy_classes.class_id'),
        nullable=False, index=True, server_default=text("'0'")
    )
    joined_date = Column(Integer, nullable=False, index=True, server_default=text("'0'"))
    joined_ip_num = Column(String(16), index=True)
    joined_remote_host = Column(String(255), nullable=False, server_default=text("''"))
    flag_internal = Column(Integer, nullable=False, index=True, server_default=text("'0'"))
    flag_edit_users = Column(Integer, nullable=False, index=True, server_default=text("'0'"))
    flag_edit_system = Column(Integer, nullable=False, server_default=text("'0'"))
    flag_email_verified = Column(Integer, nullable=False, server_default=text("'0'"))
    flag_approved = Column(Integer, nullable=False, index=True, server_default=text("'1'"))
    flag_deleted = Column(Integer, nullable=False, index=True, server_default=text("'0'"))
    flag_banned = Column(Integer, nullable=False, index=True, server_default=text("'0'"))
    flag_wants_email = Column(Integer, nullable=False, server_default=text("'0'"))
    flag_html_email = Column(Integer, nullable=False, server_default=text("'0'"))
    tracking_cookie = Column(String(255), nullable=False, index=True, server_default=text("''"))
    flag_allow_tex_produced = Column(Integer, nullable=False, server_default=text("'0'"))

    # TODO: can we use this to simplify username queries?
    # nickname = relationship('TapirUserNickname', back_populates="user_id",
    #                         lazy='joined')


class TapirUserPassword(Base):  # type: ignore
    __tablename__ = 'tapir_users_password'

    user_id = Column(ForeignKey('tapir_users.user_id'), nullable=False,
                     server_default=text("'0'"), primary_key=True)
    password_storage = Column(Integer, nullable=False, index=True,
                              server_default=text("'0'"))
    password_enc = Column(String(16), nullable=False)

    user = relationship('TapirUser')


class TapirPolicyClass(Base):  # type: ignore
    """
    Legacy table that is a foreign key depency of TapirUse.

    TapirUse is itself a dependency of TapirSession.
    """

    __tablename__ = 'tapir_policy_classes'

    class_id = Column(SmallInteger, primary_key=True)
    name = Column(String(64), nullable=False, server_default=text("''"))
    description = Column(Text, nullable=False)
    password_storage = Column(Integer, nullable=False,
                              server_default=text("'0'"))
    recovery_policy = Column(Integer, nullable=False,
                             server_default=text("'0'"))
    permanent_login = Column(Integer, nullable=False,
                             server_default=text("'0'"))


class TapirPermanentToken(Base):  # type: ignore
    """
    Bearer token for user authentication.

    +-------------+-----------------+------+-----+---------+-------+
    | Field       | Type            | Null | Key | Default | Extra |
    +-------------+-----------------+------+-----+---------+-------+
    | user_id     | int(4) unsigned | NO   | PRI | 0       |       |
    | secret      | varchar(32)     | NO   | PRI |         |       |
    | valid       | int(1)          | NO   |     | 1       |       |
    | issued_when | int(4) unsigned | NO   |     | 0       |       |
    | issued_to   | varchar(16)     | NO   |     |         |       |
    | remote_host | varchar(255)    | NO   |     |         |       |
    | session_id  | int(4) unsigned | NO   | MUL | 0       |       |
    +-------------+-----------------+------+-----+---------+-------+
    """

    __tablename__ = 'tapir_permanent_tokens'

    user_id = Column(Integer, primary_key=True)
    secret = Column(String(32), primary_key=True)
    """Token."""
    valid = Column(Integer, nullable=False, server_default=text("'1'"))
    issued_when = Column(Integer, nullable=False, server_default=text("'0'"))
    """Epoch time."""
    issued_to = Column(String(16), nullable=False)
    """IP address of client."""
    remote_host = Column(String(255), nullable=False)
    session_id = Column(Integer, nullable=False, server_default=text("'0'"))


class TapirUserNickname(Base):  # type: ignore
    """
    Users' usernames (because why not have a separate table).

    +--------------+------------------+------+-----+---------+----------------+
    | Field        | Type             | Null | Key | Default | Extra          |
    +--------------+------------------+------+-----+---------+----------------+
    | nick_id      | int(10) unsigned | NO   | PRI | NULL    | auto_increment |
    | nickname     | varchar(20)      | NO   | UNI |         |                |
    | user_id      | int(4) unsigned  | NO   | MUL | 0       |                |
    | user_seq     | int(1) unsigned  | NO   |     | 0       |                |
    | flag_valid   | int(1) unsigned  | NO   | MUL | 0       |                |
    | role         | int(10) unsigned | NO   | MUL | 0       |                |
    | policy       | int(10) unsigned | NO   | MUL | 0       |                |
    | flag_primary | int(1) unsigned  | NO   |     | 0       |                |
    +--------------+------------------+------+-----+---------+----------------+
    """

    __tablename__ = 'tapir_nicknames'

    nick_id = Column(Integer, primary_key=True)
    nickname = Column(String(20), nullable=False, unique=True, index=True)
    user_id = Column(ForeignKey('tapir_users.user_id'), nullable=False,
                     server_default=text("'0'"))
    user_seq = Column(Integer, nullable=False, server_default=text("'0'"))
    flag_valid = Column(Integer, nullable=False, server_default=text("'0'"))
    role = Column(Integer, nullable=False, server_default=text("'0'"))
    policy = Column(Integer, nullable=False, server_default=text("'0'"))
    flag_primary = Column(Integer, nullable=False, server_default=text("'0'"))

    user = relationship('TapirUser')


class Profile(Base):   # type: ignore
    """arXiv user profile."""

    __tablename__ = 'arxiv_demographics'

    TYPE_CHOICES = [
        (1, 'Staff'),
        (2, "Professor"),
        (3, "Post Doc"),
        (4, "Grad Student"),
        (5, "Other")
    ]
    """Legacy ranks in arXiv user profiles."""

    user_id = Column(ForeignKey('tapir_users.user_id'), nullable=False,
                     server_default=text("'0'"), primary_key=True)
    country = Column(String(2), nullable=False)
    affiliation = Column(String(255), nullable=False)
    url = Column(String(255), nullable=False)
    rank = Column('type', SmallInteger, nullable=True, server_default=text("'null'"))
    archive = Column(String(16), nullable=True, server_default=text("'null'"))
    subject_class = Column(String(16), nullable=True, server_default=text("'null'"))
    original_subject_classes = Column(String(255), nullable=False)
    flag_group_physics = Column(Integer, nullable=True, server_default=text("'null'"))
    flag_group_math = Column(Integer, nullable=False, server_default=text("'0'"))
    flag_group_cs = Column(Integer, nullable=False, server_default=text("'0'"))
    flag_group_nlin = Column(Integer, nullable=False, server_default=text("'0'"))
    flag_group_q_bio = Column(Integer, nullable=False, server_default=text("'0'"))
    flag_group_q_fin = Column(Integer, nullable=False, server_default=text("'0'"))
    flag_group_stat = Column(Integer, nullable=False, server_default=text("'0'"))
    # TODO: where are new categories?
    user = relationship('TapirUser')
