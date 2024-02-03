from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, validates

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=True)
    password = Column(String)

    blogs = relationship("Blog", back_populates="author")


class Blog(Base):
    __tablename__ = "blogs"

    id = Column(Integer, primary_key=True)
    blog_name = Column(String)
    blog_description = Column(String)
    blog_likes = Column(Integer, default=0)
    blog_post = Column(String, default="")

    @validates('blog_name')
    def validate_blog_name(self, key, value):
        return value.strip()

    @validates('blog_post')
    def validate_blog_post(self, key, value):
        return value.strip()[:1000]

    posts = relationship("Post", back_populates="blog", cascade="all, delete-orphan")
    author_id = Column(String, ForeignKey("users.username"))
    author = relationship("User", back_populates="blogs")
    author_like = relationship("Like", back_populates="blogs_like")


class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    like_user_name = Column(String, nullable=False)
    like_or_dis_like = Column(Boolean, default=False)
    blog = Column(String, ForeignKey("blogs.blog_name"),
                  nullable=False)  # Use the id column of blogs as the foreign key
    blogs_like = relationship("Blog", back_populates="author_like")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    post_user_name = Column(String, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)

    @validates('title')
    def validate_title(self, key, value):
        return value.strip()

    @validates('content')
    def validate_content(self, key, value):
        return value.strip()[:1000]

    blog_name = Column(String, ForeignKey("blogs.blog_name"), nullable=False)
    blog = relationship("Blog", back_populates="posts")
