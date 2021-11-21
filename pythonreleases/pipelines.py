# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os
import logging
import psycopg2
# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import json
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from .items import PythonAuthorItem, PythonPostItem, PythonReleaseItem
from .models import Base, Post, Release, Author

#engine = create_engine('sqlite:///releases.db')#, echo=True)


class PythonreleasesPipeline(object):

    """Tweets pipeline for storing scraped items in the database"""

    def open_spider(self, spider):
        if os.getenv('POSTGRES_HOST'):
            hostname = os.getenv('POSTGRES_HOST')
            username = os.getenv('POSTGRES_USER')
            password = os.getenv('POSTGRES_PASSWORD')
            database = os.getenv('POSTGRES_DB')
            port = os.getenv('POSTGRES_PORT_DB')
            engine = create_engine(
                f"postgresql+psycopg2://{username}:{password}@{hostname}:{port}/{database}",
                isolation_level="SERIALIZABLE",
            )
        else:
            logging.info('SQLITE')
            engine = create_engine('sqlite:///releases.db', echo=True)
        session = sessionmaker(bind=engine)
        session.configure(bind=engine)
        self.db_session = session()
        Base.metadata.create_all(engine)

    def close_spider(self, spider):
        self.db_session.close()

    def process_item(self, item, spider):
        post = item['post']
        author = post['author']
        if self.db_session.query(Author).filter(Author.name == author).count() == 0:
            author = Author(name=author)
            self.db_session.add(author)
            self.db_session.commit()
            logging.info(f'AUTHOR {author.name} created. ID - {author.id}')
        else:
            author = self.db_session.query(Author).filter(Author.name == author).first()
        find_post = self.db_session.query(Post).filter(Post.title == post['title'])
        if find_post.count() == 0:
            post = Post(title=post['title'], date=post['date'], author_id=author.id, text=post['text'])
            self.db_session.add(post)
            self.db_session.commit()
        else:
            post = find_post.first()
        release = Release(name=item['title'], h1=item['h1'], url=item['url'], urls_pep=item['urls_pep'],
                          date=item['date'], text=item['text_release'], post_id=post.id, table_files=item['table_release'])
        self.db_session.add(release)
        self.db_session.commit()
        return f'Item is Post {post.id}, Release {release.id}'
