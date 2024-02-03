from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from modelsPack.models import Blog, User, Like, Post
from modelsPack.create_db import create_database, DATABASE_URL
from functionality import functions

engine = create_database(DATABASE_URL)
# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

app = FastAPI()


@app.get("/")
def home_page():
    return {"Hello user please login with user name and password on ../login/ page"}


@app.post("/login/")
def login(username: str, password: str):
    user = session.query(User).filter(User.username == username).first()
    if not user:
        new_user = User(username=username, password=password)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return {"message": f"User {username} logged in successfully"}
    else:
        # Invalid credentials
        raise HTTPException(status_code=401, detail="Invalid username or password")


@app.get("/get_all_blogs/")
async def get_all_blogs():
    blogs = session.query(Blog).all()
    blogs_data = []

    for blog in blogs:
        like_count = session.query(Like).filter(Like.blog.__eq__(blog.blog_name), Like.like_or_dis_like == True).count()
        posts_data = session.query(Post).filter(Post.blog_name.__eq__(blog.blog_name)).all()

        blog_data = {
            "blog_name": blog.blog_name,
            "blog_description": blog.blog_description,
            "author": blog.author.username,
            "like_count": like_count,
            "posts": [{"title": post.title, "content": post.content} for post in posts_data]
        }
        blogs_data.append(blog_data)

    return blogs_data


@app.post("/create/")
async def create_blog(blog_name: str, blog_description: str, user_name: str):
    try:
        user = session.query(User).filter(User.username == user_name).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Your not logged in please go to /login/ page")

        new_blog = Blog(blog_name=blog_name, blog_description=blog_description, author=user)
        session.add(new_blog)
        session.commit()
        session.refresh(new_blog)

        new_like = Like(like_user_name=user.username, blog=new_blog.blog_name, like_or_dis_like=False)
        session.add(new_like)
        session.commit()

        return {"message": "Blog created successfully"}
    except IntegrityError:
        session.rollback()
        return {"message": "Error creating blog"}


@app.get("/delete_blog/")
async def delete_blog(blog_name: str, current_user: User = Depends(functions.authentication_user)):
    blog = session.query(Blog).filter(Blog.blog_name == blog_name).first()
    if blog:
        if current_user.username == blog.author_id:
            session.delete(blog)
            session.commit()
            return {"Admin message": f"The blog {blog.blog_name} with ID {blog.id} has deleted successfully"}
        else:
            return HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                 detail=f"{current_user.username}"
                                        f" your not the user so you cant delete '{blog.blog_name}' Blog")
    else:
        raise HTTPException(status_code=404, detail=f"{blog_name} Blog not found")


@app.post("/like/")
async def like_blog(blog_name: str, current_user: User = Depends(functions.authentication_user)):
    favorite_blog = session.query(Blog).filter(Blog.blog_name == blog_name).first()

    if not favorite_blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The blog {blog_name} does not exist")

    # Check if the user has already liked the blog
    existing_like = session.query(Like).filter(
        Like.like_user_name.__eq__(current_user.username),
        Like.blog == blog_name
    ).first()

    if existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already liked this blog."
        )

    new_like = Like(like_user_name=current_user.username, like_or_dis_like=True, blog=blog_name)
    session.add(new_like)
    session.commit()

    favorite_blog.blog_likes += 1
    session.commit()

    return {"message": "Blog liked successfully"}


@app.post("/unlike/")
async def unlike_blog(blog_name: str, current_user: User = Depends(functions.authentication_user)):
    favorite_blog = session.query(Blog).filter(Blog.blog_name == blog_name).first()

    if not favorite_blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The blog {blog_name} does not exist")

    existing_like = session.query(Like).filter(
        Like.like_user_name.__eq__(current_user.username),
        Like.blog == blog_name,
        Like.like_or_dis_like == True
    ).first()

    if not existing_like:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have not liked this blog yet."
        )

    session.delete(existing_like)
    session.commit()
    favorite_blog.blog_likes -= 1
    session.commit()
    return {"message": "Blog unliked successfully"}


@app.post("/post/")
def create_post(blog_name: str, title: str, content: str, current_user: User = Depends(functions.authentication_user)):
    favorite_blog = session.query(Blog).filter(Blog.blog_name == blog_name).first()
    if not favorite_blog:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The blog {blog_name} does not exist")
    existing_post = session.query(Post).filter(
        Post.post_user_name.__eq__(current_user.username),
        Post.title == title
    ).first()

    if existing_post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already posted to this blog.")

    post = Post(post_user_name=current_user.username, title=title, content=content, blog_name=blog_name)
    session.add(post)
    session.commit()
    return {"message": f"Post to {blog_name} wrote successfully"}


@app.post("/delete_post/")
def delete_post(blog_name: str, title: str, current_user: User = Depends(functions.authentication_user)):
    favorite_blog = session.query(Blog).filter(Blog.blog_name == blog_name).first()

    if not favorite_blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The blog {blog_name} does not exist."
        )

    existing_post = session.query(Post).filter(
        Post.post_user_name.__eq__(current_user.username),
        Post.blog == favorite_blog,
        Post.title == title
    ).first()

    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found in the specified blog."
        )

    session.delete(existing_post)
    session.commit()

    return {"message": f"Post '{title}' in blog '{blog_name}' deleted successfully."}


@app.post("/edit_post/")
def edit_post(blog_name: str, from_title: str, title: str, content: str,
              current_user: User = Depends(functions.authentication_user)):
    favorite_blog = session.query(Blog).filter(Blog.blog_name == blog_name).first()

    if not favorite_blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The blog {blog_name} does not exist."
        )

    post_to_edit = session.query(Post).filter(
        Post.post_user_name.__eq__(current_user.username),
        Post.blog == favorite_blog,
        Post.title == from_title
    ).first()

    if not post_to_edit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found in the specified blog."
        )
    post_to_edit.title = title
    post_to_edit.content = content
    session.commit()

    return {"message": "Post updated successfully"}
