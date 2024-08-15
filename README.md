# eCommerce Clothing Store

## Overview

This is a Django-based eCommerce application designed for managing and selling clothing items. It includes functionalities for product management, a sophisticated AI-driven chatbot for customer support, and is configured for deployment on Heroku with PostgreSQL as the database.

## Features

- **Product Management**: Tools for adding, updating, and managing clothing items.
- **AI-Powered Chatbot**: Advanced chatbot functionality for intelligent customer support.
- **PostgreSQL Database**: Uses PostgreSQL for robust and scalable database management.
- **Heroku Deployment**: Configured for seamless deployment on Heroku.

## Chatbot Functionality

The chatbot enhances customer interactions by leveraging AI and NLP technologies. Key features include:

- **Intelligent Responses**: Provides accurate and contextually relevant answers based on the latest product information.
- **Dynamic Updates**: Regularly updates its knowledge base with the latest product data.
- **Advanced NLP Integration**: Uses sophisticated language models and embeddings to understand and generate human-like responses.

### How It Works

1. **Data Loading**: Retrieves product information from the Django database.
2. **Data Processing**: Converts product data into structured formats suitable for NLP processing.
3. **Embedding Generation**: Utilizes embedding models to transform text into a query-efficient format.
4. **Vector Store Management**: Stores and retrieves embedded data for quick and relevant responses.
5. **Query Handling**: Processes customer queries using advanced language models to generate responses.

### Setup

1. **Install Required Packages**

    Ensure you have the necessary packages listed in `requirements.txt`:

    ```txt
    django
    dj-database-url
    whitenoise
    langchain
    langchain-text-splitters
    langchain-huggingface
    langchain-chroma
    langchain-groq
    groq
    python-decouple
    python-dotenv
    ```

2. **Environment Configuration**

    Create a `.env` file in the root directory of your project and add your API keys and other environment variables:

    ```ini
    SECRET_KEY=your_secret_key
    DATABASE_URL=your_database_url
    GROQ_API_KEY=your_groq_api_key
    ```

3. **Database Setup**

    Ensure your `Product` model in Django is properly configured and populated with data for the chatbot to access.

4. **Run Migrations**

    Apply the database migrations:

    ```bash
    python manage.py migrate
    ```

5. **Run the Server Locally**

    Start the Django development server:

    ```bash
    python manage.py runserver
    ```

## Deployment to Heroku

1. **Prepare for Deployment**

    Ensure you have `Procfile`, `runtime.txt`, and `requirements.txt` in place.

2. **Push to Heroku**

    Deploy the application to Heroku with:

    ```bash
    git push heroku main
    ```

3. **Apply Migrations on Heroku**

    Run migrations on Heroku:

    ```bash
    heroku run python manage.py migrate
    ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Groq**: For providing advanced NLP capabilities.
- **LangChain**: For the framework enabling LLM-based applications.
- **HuggingFace**: For high-quality embeddings and models.

---

Feel free to customize this README further to fit your project's specific requirements and features.
