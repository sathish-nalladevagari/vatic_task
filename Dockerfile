# Use the official MySQL image from the Docker Hub
FROM mysql:latest

# Set the root password for MySQL (change 'your_password' to a strong, secure password)
ENV MYSQL_ROOT_PASSWORD=password123

# Optionally, set the database, user, and password for a non-root user
ENV MYSQL_DATABASE=users
ENV MYSQL_USER=your_user
ENV MYSQL_PASSWORD=password123
    