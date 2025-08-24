from sqlalchemy import Column, Integer, String, ForeignKey, Text, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)

    # For guest users → these can be null
    email = Column(String, unique=True, index=True, nullable=True)
    password = Column(String, nullable=True)

    # Profile fields
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    location = Column(String, nullable=True)
    interests = Column(Text, nullable=True)   # store JSON or comma-separated
    language = Column(String, nullable=True)

    # Track when account/guest was created
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    matches1 = relationship("Match", back_populates="user1",
                            foreign_keys="Match.user1_id", cascade="all, delete")
    matches2 = relationship("Match", back_populates="user2",
                            foreign_keys="Match.user2_id", cascade="all, delete")

    reports_made = relationship("Report", back_populates="reporter",
                                foreign_keys="Report.reporter_id", cascade="all, delete")
    reports_received = relationship("Report", back_populates="reported",
                                    foreign_keys="Report.reported_id", cascade="all, delete")

    friends = relationship("Friend", foreign_keys="Friend.user_id",
                           back_populates="user", cascade="all, delete")
    friend_of = relationship("Friend", foreign_keys="Friend.friend_id",
                             back_populates="friend", cascade="all, delete")


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user2_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    started_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    ended_at = Column(TIMESTAMP(timezone=True), nullable=True)

    user1 = relationship("User", foreign_keys=[user1_id], back_populates="matches1")
    user2 = relationship("User", foreign_keys=[user2_id], back_populates="matches2")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    reported_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    reason = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="reports_made")
    reported = relationship("User", foreign_keys=[reported_id], back_populates="reports_received")


class Friend(Base):
    __tablename__ = "friends"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    friend_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    status = Column(String, default="pending")  # pending, accepted, blocked
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    user = relationship("User", foreign_keys=[user_id], back_populates="friends")
    friend = relationship("User", foreign_keys=[friend_id], back_populates="friend_of")
