# Blog Server Backend

Welcome to the Blog Server Backend! This project provides a backend server for a blogging platform. It offers API endpoints for user authentication, managing blogs, posts, and likes.

## Setup

### Prerequisites

- Docker

### Configuration

1. **Database Configuration:**
   
   The project uses SQLite as the default database. You can modify the database path in the `database/create_db.py` file if needed.

### Running with Docker

1. **Build Docker Image:**

    Build the Docker image using the provided Dockerfile:

    ```bash
    docker build -t blog-server .
    ```

2. **Run Docker Container:**

    Run the Docker container:

    ```bash
    docker run -d -p 8000:8000 blog-server
    ```

    The server will be accessible at `http://localhost:8000`.

## Usage

1. **Endpoints:**

    - `/login/`: Endpoint for user authentication.
    - `/get_all_blogs/`: Retrieves all blogs.
    - `/create/`: Creates a new blog.
    - `/delete_blog/`: Deletes a blog.
    - `/like/`: Likes a blog.
    - `/unlike/`: Unlikes a blog.
    - `/post/`: Creates a new post.
    - `/delete_post/`: Deletes a post.
    - `/edit_post/`: Edits a post.

## Contributing

Contributions are welcome! If you find any bugs or have suggestions for improvement, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
