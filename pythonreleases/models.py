from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    posts = relationship("Post", back_populates="author", order_by="Post.id")
    #__table_args__ = (UniqueConstraint('name', ),)


class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    date = Column(DateTime, nullable=True)
    author_id = Column(Integer, ForeignKey('author.id'))
    author = relationship("Author", back_populates="posts")
    text = Column(Text)
    #releases_urls = Column(Text)
    releases = relationship("Release", back_populates="post", order_by="Release.id")


class Release(Base):
    __tablename__ = 'release'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    h1 = Column(String)
    url = Column(String, nullable=True)
    urls_pep = Column(JSON, nullable=True)
    date = Column(String, nullable=True)
    text = Column(String, nullable=True)
    post_id = Column(Integer, ForeignKey('post.id'))
    post = relationship("Post", back_populates="releases")
    table_files = Column(JSON)#relationship("FilesTable", back_populates="release", order_by="FilesTable.id")

"""
class FilesTable(Base):
    __tablename__ = 'filestable'
    id = Column(Integer, primary_key=True)
    version_name = Column(String)
    url_tgz = Column(String)
    operating_system = Column(String)
    description = Column(String, nullable=True)
    md5_sum = Column(String)
    file_size = Column(Integer)
    release_id = Column(Integer, ForeignKey('release.id'))
    release = relationship("Release", back_populates="tables_files")
"""